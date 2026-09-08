import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from data.coffee_costs import BASE_CUPS_PER_MONTH, coffee_costs


BASE_DIR = Path(__file__).resolve().parent.parent
MONEY_PATTERN = re.compile(r"^[0-9]+(?:[.,][0-9]{1,2})?$")
BEHAVIOR_LABELS = {
    "fixed": "Постоянные",
    "variable": "Переменные",
}

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def _format_money(value: Decimal) -> str:
    formatted = f"{value:,.2f}"
    return formatted.replace(",", "\N{NO-BREAK SPACE}").replace(".", ",")


def _prepare_cost(cost: dict[str, Any]) -> dict[str, Any]:
    prepared = dict(cost)
    prepared["like_count"] = len(cost["cost_liked_by"])
    prepared["cost_behavior_display"] = BEHAVIOR_LABELS[cost["cost_behavior"]]
    prepared["monthly_cost_display"] = _format_money(cost["monthly_cost_rub"])
    prepared["monthly_cost_input"] = f"{cost['monthly_cost_rub']:.2f}"
    prepared["source_checked_display"] = cost["cost_source_checked_on"].strftime(
        "%d.%m.%Y"
    )
    return prepared


def _published_costs() -> list[dict[str, Any]]:
    return sorted(
        (cost for cost in coffee_costs if cost["cost_status"] == "published"),
        key=lambda cost: cost["cost_id"],
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
            "base_cups_per_month": BASE_CUPS_PER_MONTH,
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


def _parse_cost_id(raw_value: str) -> int | None:
    if not re.fullmatch(r"[0-9]+", raw_value):
        return None

    cost_id = int(raw_value)
    return cost_id if cost_id > 0 else None


def _parse_max_monthly_cost(raw_value: str) -> Decimal | None:
    normalized = raw_value.strip()
    if normalized == "":
        return None
    if not MONEY_PATTERN.fullmatch(normalized):
        raise ValueError

    try:
        value = Decimal(normalized.replace(",", "."))
    except InvalidOperation as error:
        raise ValueError from error

    if not value.is_finite() or value < 0:
        raise ValueError
    return value


@router.get("/costs/feed", response_class=HTMLResponse)
async def get_cost_feed(request: Request) -> HTMLResponse:
    raw_next = request.query_params.get("next")
    try:
        show_next = _parse_next(raw_next)
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

    published = _published_costs()
    raw_cost_id = request.query_params.get("cost_id")

    if raw_cost_id is None:
        if not published:
            return _render(
                request,
                "cost_feed.html",
                active_tab="feed",
                empty_message="Опубликованных издержек пока нет",
                cost=None,
                next_url=None,
            )
        selected = published[0]
    else:
        cost_id = _parse_cost_id(raw_cost_id)
        selected_index = next(
            (
                index
                for index, cost in enumerate(published)
                if cost["cost_id"] == cost_id
            ),
            None,
        )
        if selected_index is None:
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

        if show_next:
            selected_index = (selected_index + 1) % len(published)
        selected = published[selected_index]

    prepared_cost = _prepare_cost(selected)
    return _render(
        request,
        "cost_feed.html",
        active_tab="feed",
        cost=prepared_cost,
        next_url=f"/costs/feed?cost_id={prepared_cost['cost_id']}&next=true",
    )


@router.get("/costs/draft", response_class=HTMLResponse)
async def get_cost_draft(request: Request) -> HTMLResponse:
    draft = next(
        (cost for cost in coffee_costs if cost["cost_status"] == "draft"),
        None,
    )
    return _render(
        request,
        "cost_draft.html",
        active_tab="draft",
        draft=_prepare_cost(draft) if draft is not None else None,
        empty_message="Черновик отсутствует" if draft is None else None,
    )


@router.get("/costs", response_class=HTMLResponse)
async def get_cost_tiles(request: Request) -> HTMLResponse:
    raw_maximum = request.query_params.get("max_monthly_cost")
    input_value = raw_maximum if raw_maximum is not None else ""
    published = _published_costs()

    try:
        maximum = (
            None
            if raw_maximum is None
            else _parse_max_monthly_cost(raw_maximum)
        )
    except ValueError:
        return _render(
            request,
            "cost_tiles.html",
            active_tab="tiles",
            status_code=400,
            costs=[],
            filter_value=input_value,
            filter_applied=True,
            error_message="Введите неотрицательную сумму с точностью до копеек",
        )

    filtered = (
        published
        if maximum is None
        else [
            cost
            for cost in published
            if cost["monthly_cost_rub"] <= maximum
        ]
    )
    return _render(
        request,
        "cost_tiles.html",
        active_tab="tiles",
        costs=[_prepare_cost(cost) for cost in filtered],
        filter_value=input_value,
        filter_applied=raw_maximum is not None and raw_maximum.strip() != "",
        error_message=None,
    )
