"""Generate the Lab4 collection; no real cookie or password is exported."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
items = []


def request(name, method, path, *, cookie=False, body=None, files=False, save_id=False):
    headers = [{"key": "Cookie", "value": "cost_session={{session_cookie}}"}] if cookie else []
    spec = {"name": name, "protocolProfileBehavior": {"disableCookies": True},
        "request": {"method": method, "header": headers,
                    "url": "{{base_url}}"+path, "auth": {"type": "noauth"}}, "response": []}
    if body is not None:
        headers.append({"key": "Content-Type", "value": "application/json"})
        spec["request"]["body"] = {"mode": "raw", "raw": json.dumps(body, ensure_ascii=False, indent=2),
                                      "options": {"raw": {"language": "json"}}}
    if files:
        spec["request"]["body"] = {"mode": "formdata", "formdata": [
            {"key": "cost_name", "value": "Аренда кофемашины ЛР4", "type": "text"},
            {"key": "image", "type": "file", "src": ""},
            {"key": "video", "type": "file", "src": ""}]}
    if save_id:
        spec["event"] = [{"listen": "test", "script": {"type": "text/javascript", "exec": [
            "if (pm.response.code < 300) {", "  const card = pm.response.json();",
            "  if (card && card.cost_id) pm.collectionVariables.set('cost_id', String(card.cost_id));", "}"]}}]
    items.append(spec)


credentials = {"user_name": "{{user_name}}", "password": "{{password}}"}
publication = {"cost_description": "Постоянные издержки на аренду оборудования",
               "cost_behavior": "fixed", "cost_code": 31}
request("Подготовка — регистрация", "POST", "/api/users", body=credentials)
request("01 Вход (для скрина выполнить в Swagger)", "POST", "/api/users/auth", body=credentials)
request("04 Список с cookie", "GET", "/api/costs?min_cost_code=20&max_cost_code=40", cookie=True)
request("05 Список без cookie", "GET", "/api/costs?min_cost_code=20&max_cost_code=40")
request("Подготовка — свой черновик", "GET", "/api/costs/draft", cookie=True, save_id=True)
request("Подготовка — создать черновик (выбрать 2 файла)", "POST", "/api/costs", cookie=True, files=True, save_id=True)
request("06 Публикация без cookie", "PUT", "/api/costs/{{cost_id}}", body=publication)
request("07 Публикация с cookie", "PUT", "/api/costs/{{cost_id}}", cookie=True, body=publication)
request("Лента без ID", "GET", "/api/costs/feed", cookie=True)
request("Следующая издержка", "GET", "/api/costs/feed?cost_id={{cost_id}}&next=true", cookie=True)
request("Лайк", "POST", "/api/costs/{{cost_id}}/likes", cookie=True, body={"is_liked": 1})
request("Отмена лайка", "POST", "/api/costs/{{cost_id}}/likes", cookie=True, body={"is_liked": 0})
request("Удаление СВОЕЙ тестовой карточки (soft delete)", "DELETE", "/api/costs/{{cost_id}}", cookie=True)
request("Выход — после всех скринов", "POST", "/api/users/logout", cookie=True)
collection = {"info": {"name": "ЛР4 — Издержки — cookie и Redis",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
    "description": "Cookie скопировать из Application браузера в session_cookie вручную. Не запускать всю коллекцию Runner: публикация/удаление меняют собственную тестовую карточку. Файлы выбрать в form-data."},
    "variable": [{"key": key, "value": value, "type": "string"} for key, value in
                 (("base_url", "http://localhost:8000"), ("session_cookie", ""), ("cost_id", ""),
                  ("user_name", "student4"), ("password", "Lab4-demo-2026!"))],
    "item": items}
path = ROOT / "docs/postman/lab4_costs.postman_collection.json"
path.write_text(json.dumps(collection, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(path)
