"""Build the ten-request Postman collection for the LR3 demonstration."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/postman/lab3_costs.postman_collection.json"
FIXTURES = ROOT / "docs/postman/fixtures"


def request(name, method, path, *, raw=None, form=None, test=None):
    item = {"name": name, "request": {
        "method": method,
        "header": ([{"key": "Content-Type", "value": "application/json"}]
                   if raw is not None else []),
        "url": "{{baseUrl}}" + path,
    }}
    if raw is not None:
        item["request"]["body"] = {"mode": "raw", "raw": json.dumps(raw, ensure_ascii=False),
                                   "options": {"raw": {"language": "json"}}}
    if form is not None:
        item["request"]["body"] = {"mode": "formdata", "formdata": form}
    if test:
        item["event"] = [{"listen": "test", "script": {
            "type": "text/javascript", "exec": [test]}}]
    return item


collection = {
    "info": {"name": "ЛР3 — Издержки: 10 запросов",
             "description": "Выполнять по порядку. Файлы в запросе 3 можно повторно выбрать из docs/postman/fixtures.",
             "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"},
    "variable": [
        {"key": "baseUrl", "value": "http://127.0.0.1:8000"},
        {"key": "costId", "value": ""},
        {"key": "feedId", "value": ""},
    ],
    "item": [
        request("01 Список всех опубликованных", "GET", "/api/costs"),
        request("02 Фильтрация по коду", "GET", "/api/costs?min_cost_code=20&max_cost_code=26"),
        request("03 Создать черновик с файлами", "POST", "/api/costs", form=[
            {"key": "cost_name", "value": "Тестовая издержка ЛР3", "type": "text"},
            {"key": "image", "src": str(FIXTURES / "example_cost.png"), "type": "file"},
            {"key": "video", "src": str(FIXTURES / "example_cost.mp4"), "type": "file"},
        ], test="pm.collectionVariables.set('costId', pm.response.json().cost_id);"),
        request("04 Получить свой черновик", "GET", "/api/costs/draft"),
        request("05 Опубликовать черновик", "PUT", "/api/costs/{{costId}}", raw={
            "cost_description": "Проверка публикации карточки",
            "cost_behavior": "fixed", "cost_code": 31,
        }),
        request("06 Лента без ID", "GET", "/api/costs/feed",
                test="pm.collectionVariables.set('feedId', pm.response.json().cost_id);"),
        request("07 Следующая карточка", "GET", "/api/costs/feed?cost_id={{feedId}}&next=true"),
        request("08 Поставить лайк", "POST", "/api/costs/{{costId}}/likes",
                raw={"is_liked": 1}),
        request("09 Логически удалить свою карточку", "DELETE", "/api/costs/{{costId}}"),
        request("10 Зарегистрировать пользователя", "POST", "/api/users",
                raw={"user_name": "lab3_demo_{{$timestamp}}", "password": "DemoPass123"}),
    ],
}

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps(collection, ensure_ascii=False, indent=2) + "\n",
                  encoding="utf-8")
print(OUTPUT)
