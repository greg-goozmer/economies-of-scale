import re
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy import case, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from models.cost import Cost
from models.cost_like import CostLike
from models.user import User


BASE_DIR = Path(__file__).resolve().parent.parent
CURRENT_USER_ID = 101
CODE_PATTERN = re.compile(r"^[0-9]+$")
DEFAULT_IMAGE_URL = "/static/media/default_cost.png"
DEFAULT_VIDEO_URL = "/static/media/default_cost.mp4"
MISSING_IMAGE_URL = "http://localhost:9000/costs/missing-image.png"
MISSING_VIDEO_URL = "http://localhost:9000/costs/missing-video.mp4"
BEHAVIOR_LABELS = {
    "fixed": "Постоянные",
    "variable": "Переменные",
}

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def _prepare_cost(cost: Cost, like_count: int = 0) -> dict[str, Any]:
    return {
        "cost_id": cost.cost_id,
        "cost_name": cost.cost_name,
        "cost_description": cost.cost_description or "",
        "cost_status": cost.cost_status,
        "cost_image_url": cost.cost_image_url or DEFAULT_IMAGE_URL,
        "cost_video_url": cost.cost_video_url or DEFAULT_VIDEO_URL,
        "cost_behavior": cost.cost_behavior,
        "cost_behavior_display": BEHAVIOR_LABELS.get(
            cost.cost_behavior,
            "Не указан",
        ),
        "cost_code": cost.cost_code,
        "cost_code_display": (
            f"{cost.cost_code:02d}"
            if cost.cost_code is not None
            else "—"
        ),
        "like_count": like_count,
    }


def _render(
    request: Request,
    template_name: str,
    *,
    active_tab: str,
    status_code: int = 200,
    **context: Any,
) -> HTMLResponse:
    response = templates.TemplateResponse(
        request=request,
        name=template_name,
        context={"active_tab": active_tab, **context},
        status_code=status_code,
    )
    if "cost_user_id" not in request.cookies:
        response.set_cookie("cost_user_id", str(CURRENT_USER_ID), samesite="lax")
    return response


def _parse_next(raw_value: str | None) -> bool:
    if raw_value is None or raw_value == "false":
        return False
    if raw_value == "true":
        return True
    raise ValueError("Параметр next должен быть равен true или false")


def _parse_positive_id(raw_value: str) -> int | None:
    if not CODE_PATTERN.fullmatch(raw_value):
        return None
    value = int(raw_value)
    return value if value > 0 else None


def _parse_filter_code(raw_value: str | None, default: int) -> int:
    if raw_value is None or raw_value.strip() == "":
        return default
    normalized = raw_value.strip()
    if not CODE_PATTERN.fullmatch(normalized):
        raise ValueError("Коды издержек должны быть целыми неотрицательными числами")
    return int(normalized)


async def _current_user_id(request: Request, db: AsyncSession) -> int:
    raw_user_id = request.cookies.get("cost_user_id", str(CURRENT_USER_ID))
    user_id = _parse_positive_id(raw_user_id)
    if user_id is None:
        return CURRENT_USER_ID
    existing_user_id = await db.scalar(
        select(User.user_id).where(User.user_id == user_id).limit(1)
    )
    return existing_user_id or CURRENT_USER_ID


@router.get("/costs/feed", response_class=HTMLResponse)
async def get_cost_feed(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Response:
    try:
        show_next = _parse_next(request.query_params.get("next"))
    except ValueError as error:
        return _render(
            request,
            "cost_feed.html",
            active_tab="feed",
            status_code=400,
            error_message=str(error),
            cost=None,
            next_url=None,
        )

    raw_cost_id = request.query_params.get("cost_id")
    cost_id = None
    if raw_cost_id is not None:
        cost_id = _parse_positive_id(raw_cost_id)
        if cost_id is None:
            return _render(
                request,
                "cost_feed.html",
                active_tab="feed",
                status_code=404,
                error_message="Издержка не найдена",
                show_tiles_link=True,
                cost=None,
                next_url=None,
            )

    like_count = (
        select(func.count(CostLike.cost_like_id))
        .where(CostLike.cost_id == Cost.cost_id)
        .correlate(Cost)
        .scalar_subquery()
    )
    statement = select(Cost, like_count.label("like_count")).where(
        Cost.cost_status == "published"
    )

    if cost_id is None:
        statement = statement.order_by(Cost.cost_id)
    elif show_next:
        current_exists = select(Cost.cost_id).where(
            Cost.cost_id == cost_id,
            Cost.cost_status == "published",
        ).exists()
        statement = statement.where(current_exists).order_by(
            case((Cost.cost_id > cost_id, 0), else_=1),
            Cost.cost_id,
        )
    else:
        statement = statement.where(Cost.cost_id == cost_id)

    row = (await db.execute(statement.limit(1))).one_or_none()
    if row is None and cost_id is not None:
        return RedirectResponse("/costs", status_code=303)
    if row is None:
        return _render(
            request,
            "cost_feed.html",
            active_tab="feed",
            empty_message="Опубликованных издержек пока нет",
            cost=None,
            next_url=None,
        )

    cost, likes = row
    prepared = _prepare_cost(cost, likes)
    return _render(
        request,
        "cost_feed.html",
        active_tab="feed",
        cost=prepared,
        next_url=f"/costs/feed?cost_id={cost.cost_id}&next=true",
    )


@router.get("/costs/draft", response_class=HTMLResponse)
async def get_cost_draft(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> HTMLResponse:
    user_id = await _current_user_id(request, db)
    draft = await db.scalar(
        select(Cost)
        .where(
            Cost.cost_creator_id == user_id,
            Cost.cost_status == "draft",
        )
        .limit(1)
    )
    return _render(
        request,
        "cost_draft.html",
        active_tab="draft",
        draft=_prepare_cost(draft) if draft is not None else None,
        error_message=request.query_params.get("error"),
    )


@router.get("/costs", response_class=HTMLResponse)
async def get_cost_tiles(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> HTMLResponse:
    boundaries = (
        await db.execute(
            select(
                func.min(Cost.cost_code),
                func.max(Cost.cost_code),
            ).where(Cost.cost_status == "published")
        )
    ).one()
    code_minimum = boundaries[0] if boundaries[0] is not None else 0
    code_maximum = boundaries[1] if boundaries[1] is not None else 100
    raw_minimum = request.query_params.get("min_cost_code")
    raw_maximum = request.query_params.get("max_cost_code")

    try:
        selected_minimum = _parse_filter_code(raw_minimum, code_minimum)
        selected_maximum = _parse_filter_code(raw_maximum, code_maximum)
        if selected_minimum > selected_maximum:
            raise ValueError(
                "Минимальный код не может быть больше максимального"
            )
        if selected_minimum < code_minimum or selected_maximum > code_maximum:
            raise ValueError(
                f"Выберите коды в диапазоне от {code_minimum} до {code_maximum}"
            )
    except ValueError as error:
        return _render(
            request,
            "cost_tiles.html",
            active_tab="tiles",
            status_code=400,
            costs=[],
            code_minimum=code_minimum,
            code_maximum=code_maximum,
            selected_minimum=code_minimum,
            selected_maximum=code_maximum,
            filter_applied=True,
            error_message=str(error),
        )

    like_count = (
        select(func.count(CostLike.cost_like_id))
        .where(CostLike.cost_id == Cost.cost_id)
        .correlate(Cost)
        .scalar_subquery()
    )
    rows = (
        await db.execute(
            select(Cost, like_count.label("like_count"))
            .where(
                Cost.cost_status == "published",
                Cost.cost_code >= selected_minimum,
                Cost.cost_code <= selected_maximum,
            )
            .order_by(Cost.cost_id)
        )
    ).all()
    return _render(
        request,
        "cost_tiles.html",
        active_tab="tiles",
        costs=[_prepare_cost(cost, likes) for cost, likes in rows],
        code_minimum=code_minimum,
        code_maximum=code_maximum,
        selected_minimum=selected_minimum,
        selected_maximum=selected_maximum,
        filter_applied=raw_minimum is not None or raw_maximum is not None,
        error_message=None,
    )


@router.post("/costs/draft")
async def create_cost_draft(
    request: Request,
    cost_name: str = Form(...),
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    name = cost_name.strip()
    if not name:
        return RedirectResponse(
            "/costs/draft?error=Укажите+название",
            status_code=303,
        )

    user_id = await _current_user_id(request, db)
    existing_draft = await db.scalar(
        select(Cost.cost_id)
        .where(
            Cost.cost_creator_id == user_id,
            Cost.cost_status == "draft",
        )
        .limit(1)
    )
    if existing_draft is None:
        db.add(
            Cost(
                cost_name=name,
                cost_status="draft",
                cost_creator_id=user_id,
                cost_image_url=MISSING_IMAGE_URL,
                cost_video_url=MISSING_VIDEO_URL,
            )
        )
        await db.commit()
    return RedirectResponse("/costs/draft", status_code=303)


@router.post("/costs/draft/publish")
async def publish_cost_draft(
    request: Request,
    cost_description: str = Form(...),
    cost_behavior: str = Form(...),
    cost_code: int = Form(...),
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    description = cost_description.strip()
    if not description or cost_behavior not in BEHAVIOR_LABELS or cost_code < 0:
        return RedirectResponse(
            "/costs/draft?error=Проверьте+описание+и+параметры",
            status_code=303,
        )

    user_id = await _current_user_id(request, db)
    draft = await db.scalar(
        select(Cost)
        .where(
            Cost.cost_creator_id == user_id,
            Cost.cost_status == "draft",
        )
        .limit(1)
    )
    if draft is not None:
        draft.cost_description = description
        draft.cost_behavior = cost_behavior
        draft.cost_code = cost_code
        draft.cost_status = "published"
        draft.cost_formed_at = func.now()
        await db.commit()
    return RedirectResponse("/costs", status_code=303)


@router.post("/costs/{cost_id}/delete")
async def delete_cost(
    cost_id: int,
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    await db.execute(
        text(
            "UPDATE costs "
            "SET cost_status = 'deleted' "
            "WHERE cost_id = :cost_id "
            "AND cost_status = 'published'"
        ),
        {"cost_id": cost_id},
    )
    await db.commit()
    return RedirectResponse("/costs", status_code=303)
