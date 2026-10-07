from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy import case, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.current_user import current_user_id
from api.media import remove_cost_media, upload_cost_media
from db.session import get_db
from models.cost import Cost
from models.cost_like import CostLike
from schemas.cost import CostLikeChange, CostLikeRead, CostPublish, CostRead


router = APIRouter(prefix="/api/costs", tags=["costs"])


def _cost_query(user_id: int):
    like_count = (select(func.count(CostLike.cost_like_id))
                  .where(CostLike.cost_id == Cost.cost_id)
                  .correlate(Cost).scalar_subquery())
    liked = (select(func.count(CostLike.cost_like_id))
             .where(CostLike.cost_id == Cost.cost_id, CostLike.user_id == user_id)
             .correlate(Cost).scalar_subquery())
    return select(Cost, like_count.label("like_count"), liked.label("liked"))


def _read(row, user_id: int) -> CostRead:
    cost, like_count, liked = row
    return CostRead(
        cost_id=cost.cost_id,
        cost_name=cost.cost_name,
        cost_description=cost.cost_description,
        cost_status=cost.cost_status,
        cost_image_url=cost.cost_image_url,
        cost_video_url=cost.cost_video_url,
        cost_behavior=cost.cost_behavior,
        cost_code=cost.cost_code,
        cost_created_at=cost.cost_created_at,
        cost_creator_id=cost.cost_creator_id,
        cost_formed_at=cost.cost_formed_at,
        like_count=like_count,
        is_owner=int(cost.cost_creator_id == user_id),
        is_liked=int(liked > 0),
    )


async def _get_read(db: AsyncSession, cost_id: int, user_id: int) -> CostRead:
    row = (await db.execute(_cost_query(user_id).where(Cost.cost_id == cost_id))).one()
    return _read(row, user_id)


@router.get("", response_model=list[CostRead])
async def list_costs(
    min_cost_code: int | None = Query(None, ge=0),
    max_cost_code: int | None = Query(None, ge=0),
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(current_user_id),
):
    if min_cost_code is not None and max_cost_code is not None and min_cost_code > max_cost_code:
        raise HTTPException(422, "Minimum cost code exceeds maximum")
    statement = _cost_query(user_id).where(Cost.cost_status == "published")
    if min_cost_code is not None:
        statement = statement.where(Cost.cost_code >= min_cost_code)
    if max_cost_code is not None:
        statement = statement.where(Cost.cost_code <= max_cost_code)
    rows = (await db.execute(statement.order_by(Cost.cost_id))).all()
    return [_read(row, user_id) for row in rows]


@router.get("/feed", response_model=CostRead | None)
async def get_cost_feed(
    cost_id: int | None = Query(None, ge=1),
    next: bool = False,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(current_user_id),
):
    statement = _cost_query(user_id).where(Cost.cost_status == "published")
    if cost_id is None:
        statement = statement.order_by(Cost.cost_id)
    elif next:
        exists = select(Cost.cost_id).where(
            Cost.cost_id == cost_id, Cost.cost_status == "published"
        ).exists()
        statement = statement.where(exists).order_by(
            case((Cost.cost_id > cost_id, 0), else_=1), Cost.cost_id
        )
    else:
        statement = statement.where(Cost.cost_id == cost_id)
    row = (await db.execute(statement.limit(1))).one_or_none()
    if row is None and cost_id is not None:
        raise HTTPException(404, "Cost not found")
    return _read(row, user_id) if row is not None else None


@router.get("/draft", response_model=CostRead | None)
async def get_cost_draft(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(current_user_id),
):
    row = (await db.execute(
        _cost_query(user_id).where(
            Cost.cost_status == "draft", Cost.cost_creator_id == user_id
        ).limit(1)
    )).one_or_none()
    return _read(row, user_id) if row is not None else None


@router.post("", response_model=CostRead, status_code=status.HTTP_201_CREATED)
async def create_cost(
    cost_name: str = Form(min_length=1, max_length=100),
    image: UploadFile = File(),
    video: UploadFile = File(),
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(current_user_id),
):
    cost_name = cost_name.strip()
    if not cost_name:
        raise HTTPException(422, "Cost name is required")
    existing = await db.scalar(select(Cost.cost_id).where(
        Cost.cost_creator_id == user_id, Cost.cost_status == "draft"
    ).limit(1))
    if existing is not None:
        raise HTTPException(409, "A draft already exists")
    media_urls = await run_in_threadpool(upload_cost_media, image, video)
    cost = Cost(cost_name=cost_name, cost_status="draft",
                cost_image_url=media_urls[0], cost_video_url=media_urls[1],
                cost_creator_id=user_id)
    try:
        db.add(cost)
        await db.commit()
        await db.refresh(cost)
    except Exception as error:
        await db.rollback()
        await run_in_threadpool(remove_cost_media, media_urls)
        if isinstance(error, IntegrityError):
            raise HTTPException(409, "A draft already exists") from error
        raise
    return await _get_read(db, cost.cost_id, user_id)


@router.put("/{cost_id}", response_model=CostRead)
async def publish_cost(
    cost_id: int,
    payload: CostPublish,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(current_user_id),
):
    cost = await db.scalar(select(Cost).where(
        Cost.cost_id == cost_id, Cost.cost_creator_id == user_id,
        Cost.cost_status == "draft"
    ).limit(1))
    if cost is None:
        raise HTTPException(404, "Draft not found")
    description = payload.cost_description.strip()
    if not description:
        raise HTTPException(422, "Description is required")
    cost.cost_description = description
    cost.cost_behavior = payload.cost_behavior
    cost.cost_code = payload.cost_code
    cost.cost_status = "published"
    cost.cost_formed_at = datetime.now(timezone.utc)
    await db.commit()
    return await _get_read(db, cost_id, user_id)


@router.delete("/{cost_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cost(
    cost_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(current_user_id),
):
    cost = await db.scalar(select(Cost).where(
        Cost.cost_id == cost_id, Cost.cost_creator_id == user_id,
        Cost.cost_status != "deleted"
    ).limit(1))
    if cost is None:
        raise HTTPException(404, "Cost not found")
    cost.cost_status = "deleted"
    await db.commit()


@router.post("/{cost_id}/likes", response_model=CostLikeRead)
async def change_cost_like(
    cost_id: int,
    payload: CostLikeChange,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(current_user_id),
):
    exists = await db.scalar(select(Cost.cost_id).where(
        Cost.cost_id == cost_id, Cost.cost_status == "published"
    ).limit(1))
    if exists is None:
        raise HTTPException(404, "Cost not found")
    like = await db.scalar(select(CostLike).where(
        CostLike.cost_id == cost_id, CostLike.user_id == user_id
    ).limit(1))
    if payload.is_liked == 1 and like is None:
        db.add(CostLike(cost_id=cost_id, user_id=user_id))
    elif payload.is_liked == 0 and like is not None:
        await db.delete(like)
    await db.commit()
    count = await db.scalar(select(func.count(CostLike.cost_like_id)).where(
        CostLike.cost_id == cost_id
    ))
    return CostLikeRead(cost_id=cost_id, is_liked=payload.is_liked,
                        like_count=count or 0)
