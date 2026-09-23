import re
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import case, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from models.expense_item import ExpenseItem
from models.expense_like import ExpenseLike
from models.user import User


BASE_DIR = Path(__file__).resolve().parent.parent
CURRENT_USER_ID = 101
CODE_PATTERN = re.compile(r"^[0-9]+$")
DEFAULT_IMAGE_URL = "/static/media/default_expense.png"
DEFAULT_VIDEO_URL = "/static/media/default_expense.mp4"
BEHAVIOR_LABELS = {
    "fixed": "Постоянные",
    "variable": "Переменные",
}

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def _prepare_expense(expense: ExpenseItem, like_count: int = 0) -> dict[str, Any]:
    return {
        "expense_id": expense.expense_id,
        "expense_name": expense.expense_name,
        "expense_description": expense.expense_description or "",
        "expense_status": expense.expense_status,
        "expense_image_url": expense.expense_image_url or DEFAULT_IMAGE_URL,
        "expense_video_url": expense.expense_video_url or DEFAULT_VIDEO_URL,
        "expense_behavior": expense.expense_behavior,
        "expense_behavior_display": BEHAVIOR_LABELS.get(
            expense.expense_behavior,
            "Не указан",
        ),
        "expense_code": expense.expense_code,
        "expense_code_display": (
            f"{expense.expense_code:02d}"
            if expense.expense_code is not None
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
    if "expense_user_id" not in request.cookies:
        response.set_cookie("expense_user_id", str(CURRENT_USER_ID), samesite="lax")
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
    raw_user_id = request.cookies.get("expense_user_id", str(CURRENT_USER_ID))
    user_id = _parse_positive_id(raw_user_id)
    if user_id is None:
        return CURRENT_USER_ID
    existing_user_id = await db.scalar(
        select(User.user_id).where(User.user_id == user_id).limit(1)
    )
    return existing_user_id or CURRENT_USER_ID


@router.get("/expenses/feed", response_class=HTMLResponse)
async def get_expense_feed(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> HTMLResponse:
    try:
        show_next = _parse_next(request.query_params.get("next"))
    except ValueError as error:
        return _render(
            request,
            "expense_feed.html",
            active_tab="feed",
            status_code=400,
            error_message=str(error),
            expense=None,
            next_url=None,
        )

    raw_expense_id = request.query_params.get("expense_id")
    expense_id = None
    if raw_expense_id is not None:
        expense_id = _parse_positive_id(raw_expense_id)
        if expense_id is None:
            return _render(
                request,
                "expense_feed.html",
                active_tab="feed",
                status_code=404,
                error_message="Издержка не найдена",
                show_tiles_link=True,
                expense=None,
                next_url=None,
            )

    like_count = (
        select(func.count(ExpenseLike.expense_like_id))
        .where(ExpenseLike.expense_id == ExpenseItem.expense_id)
        .correlate(ExpenseItem)
        .scalar_subquery()
    )
    statement = select(ExpenseItem, like_count.label("like_count")).where(
        ExpenseItem.expense_status == "published"
    )

    if expense_id is None:
        statement = statement.order_by(ExpenseItem.expense_id)
    elif show_next:
        current_exists = select(ExpenseItem.expense_id).where(
            ExpenseItem.expense_id == expense_id,
            ExpenseItem.expense_status == "published",
        ).exists()
        statement = statement.where(current_exists).order_by(
            case((ExpenseItem.expense_id > expense_id, 0), else_=1),
            ExpenseItem.expense_id,
        )
    else:
        statement = statement.where(ExpenseItem.expense_id == expense_id)

    row = (await db.execute(statement.limit(1))).one_or_none()
    if row is None:
        return _render(
            request,
            "expense_feed.html",
            active_tab="feed",
            status_code=404 if expense_id is not None else 200,
            error_message="Издержка не найдена" if expense_id is not None else None,
            empty_message=(
                None if expense_id is not None else "Опубликованных издержек пока нет"
            ),
            show_tiles_link=expense_id is not None,
            expense=None,
            next_url=None,
        )

    expense, likes = row
    prepared = _prepare_expense(expense, likes)
    return _render(
        request,
        "expense_feed.html",
        active_tab="feed",
        expense=prepared,
        next_url=f"/expenses/feed?expense_id={expense.expense_id}&next=true",
    )


@router.get("/expenses/draft", response_class=HTMLResponse)
async def get_expense_draft(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> HTMLResponse:
    user_id = await _current_user_id(request, db)
    draft = await db.scalar(
        select(ExpenseItem)
        .where(
            ExpenseItem.expense_creator_id == user_id,
            ExpenseItem.expense_status == "draft",
        )
        .limit(1)
    )
    return _render(
        request,
        "expense_draft.html",
        active_tab="draft",
        draft=_prepare_expense(draft) if draft is not None else None,
        error_message=request.query_params.get("error"),
    )


@router.get("/expenses", response_class=HTMLResponse)
async def get_expense_tiles(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> HTMLResponse:
    boundaries = (
        await db.execute(
            select(
                func.min(ExpenseItem.expense_code),
                func.max(ExpenseItem.expense_code),
            ).where(ExpenseItem.expense_status == "published")
        )
    ).one()
    code_minimum = boundaries[0] if boundaries[0] is not None else 0
    code_maximum = boundaries[1] if boundaries[1] is not None else 100
    raw_minimum = request.query_params.get("min_expense_code")
    raw_maximum = request.query_params.get("max_expense_code")

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
            "expense_tiles.html",
            active_tab="tiles",
            status_code=400,
            expenses=[],
            code_minimum=code_minimum,
            code_maximum=code_maximum,
            selected_minimum=code_minimum,
            selected_maximum=code_maximum,
            filter_applied=True,
            error_message=str(error),
        )

    like_count = (
        select(func.count(ExpenseLike.expense_like_id))
        .where(ExpenseLike.expense_id == ExpenseItem.expense_id)
        .correlate(ExpenseItem)
        .scalar_subquery()
    )
    rows = (
        await db.execute(
            select(ExpenseItem, like_count.label("like_count"))
            .where(
                ExpenseItem.expense_status == "published",
                ExpenseItem.expense_code >= selected_minimum,
                ExpenseItem.expense_code <= selected_maximum,
            )
            .order_by(ExpenseItem.expense_id)
        )
    ).all()
    return _render(
        request,
        "expense_tiles.html",
        active_tab="tiles",
        expenses=[_prepare_expense(expense, likes) for expense, likes in rows],
        code_minimum=code_minimum,
        code_maximum=code_maximum,
        selected_minimum=selected_minimum,
        selected_maximum=selected_maximum,
        filter_applied=raw_minimum is not None or raw_maximum is not None,
        error_message=None,
    )


@router.post("/expenses/draft")
async def create_expense_draft(
    request: Request,
    expense_name: str = Form(...),
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    name = expense_name.strip()
    if not name:
        return RedirectResponse(
            "/expenses/draft?error=Укажите+название",
            status_code=303,
        )

    user_id = await _current_user_id(request, db)
    existing_draft = await db.scalar(
        select(ExpenseItem.expense_id)
        .where(
            ExpenseItem.expense_creator_id == user_id,
            ExpenseItem.expense_status == "draft",
        )
        .limit(1)
    )
    if existing_draft is None:
        db.add(
            ExpenseItem(
                expense_name=name,
                expense_status="draft",
                expense_creator_id=user_id,
            )
        )
        await db.commit()
    return RedirectResponse("/expenses/draft", status_code=303)


@router.post("/expenses/draft/publish")
async def publish_expense_draft(
    request: Request,
    expense_description: str = Form(...),
    expense_behavior: str = Form(...),
    expense_code: int = Form(...),
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    description = expense_description.strip()
    if not description or expense_behavior not in BEHAVIOR_LABELS or expense_code < 0:
        return RedirectResponse(
            "/expenses/draft?error=Проверьте+описание+и+параметры",
            status_code=303,
        )

    user_id = await _current_user_id(request, db)
    draft = await db.scalar(
        select(ExpenseItem)
        .where(
            ExpenseItem.expense_creator_id == user_id,
            ExpenseItem.expense_status == "draft",
        )
        .limit(1)
    )
    if draft is not None:
        draft.expense_description = description
        draft.expense_behavior = expense_behavior
        draft.expense_code = expense_code
        draft.expense_status = "published"
        draft.expense_formed_at = func.now()
        await db.commit()
    return RedirectResponse("/expenses", status_code=303)


@router.post("/expenses/{expense_id}/delete")
async def delete_expense(
    expense_id: int,
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    await db.execute(
        text(
            "UPDATE expense_items "
            "SET expense_status = 'deleted' "
            "WHERE expense_id = :expense_id "
            "AND expense_status = 'published'"
        ),
        {"expense_id": expense_id},
    )
    await db.commit()
    return RedirectResponse("/expenses", status_code=303)
