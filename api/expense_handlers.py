import re
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from data.expense_items import BASE_OUTPUT_UNITS, expense_items


BASE_DIR = Path(__file__).resolve().parent.parent
CODE_PATTERN = re.compile(r"^[0-9]+$")
BEHAVIOR_LABELS = {
    "fixed": "Постоянные",
    "variable": "Переменные",
}

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def _prepare_expense(expense: dict[str, Any]) -> dict[str, Any]:
    prepared = dict(expense)
    prepared["like_count"] = len(expense["expense_liked_by"])
    prepared["expense_behavior_display"] = BEHAVIOR_LABELS[
        expense["expense_behavior"]
    ]
    prepared["expense_code_display"] = f"{expense['expense_code']:02d}"
    prepared["source_checked_display"] = expense[
        "expense_source_checked_on"
    ].strftime("%d.%m.%Y")
    return prepared


def _published_expenses() -> list[dict[str, Any]]:
    return sorted(
        (
            expense
            for expense in expense_items
            if expense["expense_status"] == "published"
        ),
        key=lambda expense: expense["expense_id"],
    )


def _render(
    request: Request,
    template_name: str,
    *,
    active_tab: str,
    status_code: int = 200,
    **context: Any,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name=template_name,
        context={
            "active_tab": active_tab,
            "base_output_units": BASE_OUTPUT_UNITS,
            **context,
        },
        status_code=status_code,
    )


def _parse_next(raw_value: str | None) -> bool:
    if raw_value is None or raw_value == "false":
        return False
    if raw_value == "true":
        return True
    raise ValueError("Параметр next должен быть равен true или false")


def _parse_expense_id(raw_value: str) -> int | None:
    if not CODE_PATTERN.fullmatch(raw_value):
        return None

    expense_id = int(raw_value)
    return expense_id if expense_id > 0 else None


def _parse_filter_code(raw_value: str | None, default: int) -> int:
    if raw_value is None or raw_value.strip() == "":
        return default

    normalized = raw_value.strip()
    if not CODE_PATTERN.fullmatch(normalized):
        raise ValueError("Коды издержек должны быть целыми неотрицательными числами")
    return int(normalized)


@router.get("/expenses/feed", response_class=HTMLResponse)
async def get_expense_feed(request: Request) -> HTMLResponse:
    raw_next = request.query_params.get("next")
    try:
        show_next = _parse_next(raw_next)
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

    published = _published_expenses()
    raw_expense_id = request.query_params.get("expense_id")

    if raw_expense_id is None:
        if not published:
            return _render(
                request,
                "expense_feed.html",
                active_tab="feed",
                empty_message="Опубликованных издержек пока нет",
                expense=None,
                next_url=None,
            )
        selected = published[0]
    else:
        expense_id = _parse_expense_id(raw_expense_id)
        selected_index = next(
            (
                index
                for index, expense in enumerate(published)
                if expense["expense_id"] == expense_id
            ),
            None,
        )
        if selected_index is None:
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

        if show_next:
            selected_index = (selected_index + 1) % len(published)
        selected = published[selected_index]

    prepared_expense = _prepare_expense(selected)
    return _render(
        request,
        "expense_feed.html",
        active_tab="feed",
        expense=prepared_expense,
        next_url=(
            "/expenses/feed"
            f"?expense_id={prepared_expense['expense_id']}&next=true"
        ),
    )


@router.get("/expenses/draft", response_class=HTMLResponse)
async def get_expense_draft(request: Request) -> HTMLResponse:
    draft = next(
        (
            expense
            for expense in expense_items
            if expense["expense_status"] == "draft"
        ),
        None,
    )
    return _render(
        request,
        "expense_draft.html",
        active_tab="draft",
        draft=_prepare_expense(draft) if draft is not None else None,
        empty_message="Черновик отсутствует" if draft is None else None,
    )


@router.get("/expenses", response_class=HTMLResponse)
async def get_expense_tiles(request: Request) -> HTMLResponse:
    published = _published_expenses()
    available_codes = [expense["expense_code"] for expense in published]
    code_minimum = min(available_codes, default=0)
    code_maximum = max(available_codes, default=100)
    raw_minimum = request.query_params.get("min_expense_code")
    raw_maximum = request.query_params.get("max_expense_code")

    try:
        selected_minimum = _parse_filter_code(raw_minimum, code_minimum)
        selected_maximum = _parse_filter_code(raw_maximum, code_maximum)
        if selected_minimum > selected_maximum:
            raise ValueError("Минимальный код не может быть больше максимального")
        if (
            selected_minimum < code_minimum
            or selected_maximum > code_maximum
        ):
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

    filtered = [
        expense
        for expense in published
        if selected_minimum <= expense["expense_code"] <= selected_maximum
    ]
    return _render(
        request,
        "expense_tiles.html",
        active_tab="tiles",
        expenses=[_prepare_expense(expense) for expense in filtered],
        code_minimum=code_minimum,
        code_maximum=code_maximum,
        selected_minimum=selected_minimum,
        selected_maximum=selected_maximum,
        filter_applied=raw_minimum is not None or raw_maximum is not None,
        error_message=None,
    )
