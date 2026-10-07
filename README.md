# Масштаб — лабораторная работа №3: REST API

Ветка `rest_api`. Предметная сущность — издержка (`cost`); кофейные позиции служат примерами данных. ЛР3 продолжает ветку `database`, но вместо HTML-шаблонов предоставляет JSON-сервис для будущего SPA. Авторизация появится в ЛР4.

## Запуск

Нужны Python 3.12 и Docker Desktop. Скопируйте `.env.example` в `.env`, задайте собственные пароли, затем:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
docker compose up -d
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Если БД пустая, загрузите демонстрационные строки через Adminer (`http://localhost:8081`) из `db/seed.sql` либо командой:

```powershell
docker compose cp db/seed.sql postgres:/tmp/cost_seed.sql
docker compose exec postgres psql -U cost_app -d cost_scale_db -f /tmp/cost_seed.sql
```

MinIO Console: `http://localhost:9001`. Объекты помещаются в публичный для чтения бакет `costs`. Локальный REST API: `http://localhost:8000/api`. Для проверки импортируйте коллекцию `docs/postman/lab3_costs.postman_collection.json` в Postman или Insomnia; примеры файлов — в `docs/postman/fixtures/`.

## Методы API

| Метод | URL | Вход | Результат |
|---|---|---|---|
| GET | `/api/costs` | Необязательные `min_cost_code`, `max_cost_code` (целые числа) | Список только опубликованных издержек; `is_owner` = 0/1. |
| GET | `/api/costs/feed` | Необязательные `cost_id`, `next=true` | Одна опубликованная издержка; `is_liked` = 0/1. При `next` переход по кругу. |
| GET | `/api/costs/draft` | — | Один черновик текущего пользователя либо `null`. |
| POST | `/api/costs` | `multipart/form-data`: `cost_name`, файлы `image`, `video` | Создаёт черновик (`201`); файлы сохраняются в MinIO под латинскими именами. |
| PUT | `/api/costs/{cost_id}` | JSON: `cost_description`, `cost_behavior` (`fixed`/`variable`), `cost_code` (число ≥ 0) | Публикует только свой черновик. |
| DELETE | `/api/costs/{cost_id}` | — | Логически удаляет только свою запись; `204`. |
| POST | `/api/costs/{cost_id}/likes` | JSON: `is_liked` = 0 или 1 | Отменяет или ставит лайк опубликованной издержке. |
| POST | `/api/users` | JSON: `user_name`, `password` | Регистрирует пользователя (`201`), хранит хеш пароля. |
| POST | `/api/users/auth` | JSON: `user_name`, `password` | Заглушка ЛР4; `204`, сессию не создаёт. |
| POST | `/api/users/logout` | — | Заглушка ЛР4; `204`. |

Ответы `GET` и создания/публикации имеют единый набор полей: `cost_id`, `cost_name`, `cost_description`, `cost_status`, `cost_image_url`, `cost_video_url`, `cost_behavior`, `cost_code`, `cost_created_at`, `cost_creator_id`, `cost_formed_at`, `like_count`, `is_owner`, `is_liked`. Системные поля нельзя задавать в запросах создания/публикации. Удалённые записи не выдаются в списке, ленте и черновике. Повторно опубликовать карточку или вернуть её в черновик нельзя. Если не найден указанный `cost_id`, ответ `404`.

Текущий создатель временно зафиксирован как `101` в singleton-функции `api/current_user.py`; все методы, где нужен пользователь, используют эту функцию через `Depends`. Это именно временное требование ЛР3, а не действующая авторизация.

## Таблицы и диаграммы

| Таблица | Поля |
|---|---|
| `users` | `user_id` PK; `user_name` уникальное; `user_password_hash` обязательное. |
| `costs` | `cost_id` PK; `cost_name`; `cost_description`; `cost_status` (`draft`/`published`/`deleted`); обязательные `cost_image_url`, `cost_video_url`; `cost_behavior` (`fixed`/`variable`); `cost_code`; `cost_created_at`; `cost_creator_id` FK → `users.user_id`; `cost_formed_at`. |
| `cost_likes` | `cost_like_id` PK; `user_id` FK → `users.user_id`; `cost_id` FK → `costs.cost_id`; пара (`user_id`, `cost_id`) уникальна. |

У одного пользователя не более одного черновика (частичный уникальный индекс). Каскадное удаление не используется. ORM-модели лежат в `models/`, Pydantic-сериализаторы — в `schemas/`, обработчики HTTP — в `api/`. В `docs/costs_database.mdj` находятся ER-диаграмма и диаграмма классов StarUML в одном проекте; на диаграмме классов показаны домены REST, модели, таблицы и четыре будущие страницы SPA. Конспект и контрольные вопросы — `docs/lab3_notes.md`.

Для проверки изменений в БД можно выполнить:

```sql
SELECT cost_id, cost_name, cost_status, cost_image_url, cost_video_url FROM costs ORDER BY cost_id DESC;
SELECT cost_like_id, user_id, cost_id FROM cost_likes ORDER BY cost_like_id DESC;
SELECT user_id, user_name, user_password_hash FROM users ORDER BY user_id DESC;
```

Исправления предыдущей работы находятся в ветке `database`; мини-отчёт — `docs/lab2_corrections_report.docx`.
