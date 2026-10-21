# Масштаб — ЛР4 Авторизация

Ветка `authentication` продолжает ЛР3 (`rest_api`). FastAPI использует **cookie и серверную сессию Redis**, не JWT. PostgreSQL хранит пользователей, издержки и лайки, MinIO — изображения и видео.

## Запуск

Python 3.12, Docker Desktop. Скопируйте `.env.example` в `.env`, задайте свои пароли:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
docker compose up -d
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Swagger: http://localhost:8000/docs, OpenAPI: http://localhost:8000/openapi.json. Adminer: http://localhost:8081, MinIO Console: http://localhost:9001. Redis доступен приложению на `127.0.0.1:16379`, внутри контейнера — `6379`. В браузере и Postman используйте один хост `localhost`, не чередуйте с `127.0.0.1`.

Для пустой БД доступны строки `db/seed.sql`:

```powershell
docker compose cp db/seed.sql postgres:/tmp/cost_seed.sql
docker compose exec postgres psql -U cost_app -d cost_scale_db -f /tmp/cost_seed.sql
```

Seed-пользователи с хешем `!` не имеют пароля для входа. Зарегистрируйте своего через API. Настоящий пользователь больше не подменяется константой 101.

## Вход и права

1. POST `/api/users`: `{"user_name":"student4","password":"Lab4-demo-2026!"}` — регистрация без входа.
2. POST `/api/users/auth`: тот же JSON — `200`, пользователь и `Set-Cookie: cost_session=…`.
3. Браузер отправляет cookie сам. Для показа в Postman добавьте **Headers → Cookie → `cost_session=ЗНАЧЕНИЕ`**. Не Authorization.
4. POST `/api/users/logout` удаляет сессию Redis и cookie. Старый скопированный токен также перестаёт работать.

Cookie содержит 32 случайных байта в hex, а не ID пользователя. Redis хранит ID по ключу `cost_session:<SHA256 токена>` с TTL 3600 секунд. Cookie имеет `HttpOnly`, `SameSite=Lax`, `Path=/`. `SESSION_COOKIE_SECURE=false` — только для локального HTTP; для HTTPS включается `true`. Срок задаётся `SESSION_TTL_SECONDS`. Пароли хешируются PBKDF2-SHA256 с солью.

Гость читает опубликованные список и ленту. Черновик, создание, публикация, удаление и лайк требуют сессии (`401` без неё). Публикация и удаление только своих карточек; чужая — `404`. При недоступности Redis проверка сессии возвращает `503`, права не предоставляются.

## Все 10 методов

| Метод | URL | Вход | Выход |
|---|---|---|---|
| GET | `/api/costs` | Query: необязательные `min_cost_code`, `max_cost_code` ≥0 | `200`, опубликованные карточки, `is_owner` 0/1; гость разрешён |
| GET | `/api/costs/feed` | Query: необязательные `cost_id`, `next=true` | `200`, одна карточка или `null`, `is_liked` 0/1; гость разрешён |
| GET | `/api/costs/draft` | Cookie | `200`, свой черновик или `null` |
| POST | `/api/costs` | Form-data: `cost_name` (Text), `image` (File), `video` (File); Cookie | `201`, черновик и URL файлов в MinIO; второй черновик `409` |
| PUT | `/api/costs/{cost_id}` | JSON: `cost_description`, `cost_behavior` (`fixed`/`variable`), `cost_code` ≥0; Cookie | `200`, публикация своего черновика |
| DELETE | `/api/costs/{cost_id}` | ID в пути; Cookie | `204`, статус deleted, строка и файлы остаются |
| POST | `/api/costs/{cost_id}/likes` | JSON: `is_liked` 0/1; Cookie | `200`: `cost_id`, `is_liked`, `like_count` |
| POST | `/api/users` | JSON: `user_name`, `password` 8–128 символов | `201`: `user_id`, `user_name`; занятое имя `409` |
| POST | `/api/users/auth` | JSON: `user_name`, `password` | `200`, пользователь и Set-Cookie; неверный пароль `401` |
| POST | `/api/users/logout` | Cookie, если есть | `204`, сессия отозвана и cookie очищена |

При создании **три поля**: название и два файла. При публикации **три поля JSON**, ID в URL, cookie в заголовке. Статус, даты и пользователя сервер задаёт сам; лишние/неверные поля дают `422`.

Ответ карточки — 14 **выходных** полей: `cost_id`, `cost_name`, `cost_description`, `cost_status`, `cost_image_url`, `cost_video_url`, `cost_behavior`, `cost_code`, `cost_created_at`, `cost_creator_id`, `cost_formed_at`, `like_count`, `is_owner`, `is_liked`. Удалённые записи не выдаются. Опубликованную запись нельзя вернуть в черновик или опубликовать повторно. Следующая карточка ленты выбирается по кругу.

## Таблицы

| Таблица | Поля |
|---|---|
| `users` | `user_id` PK; уникальное `user_name`; `user_password_hash` |
| `costs` | `cost_id` PK; `cost_name`; `cost_description`; `cost_status`; `cost_image_url`; `cost_video_url`; `cost_behavior`; `cost_code`; `cost_created_at`; `cost_creator_id` FK → users; `cost_formed_at` |
| `cost_likes` | `cost_like_id` PK; `user_id` FK → users; `cost_id` FK → costs; пара (`user_id`, `cost_id`) уникальна |

У пользователя не более одного черновика (частичный уникальный индекс). Каскадного удаления нет. В ЛР4 схема PostgreSQL не меняется; сессии находятся отдельно в Redis.

## Материалы ЛР4

- `docs/costs_database.mdj`: ER, классов и последовательности **в одном StarUML-проекте**. Восемь сообщений-запросов ссылаются через `signature` на операции доменов. Вход/выход передан в `arguments`.
- [ТЗ](docs/lab4_specification.md), [порядок 9 скриншотов](docs/lab4_screenshots.md), [ответы и конспект](docs/lab4_notes.md).
- `docs/postman/lab4_costs.postman_collection.json`: Import → выбрать **файл**, не вставлять путь как cURL. Два файла для создания — `docs/postman/fixtures/`.
- Word-отчёт сохраняется на рабочем столе и не коммитится. Источник генерации — `tools/build_lab4_report.py`. React-интерфейс относится к следующим лабораторным и в ТЗ описан как планируемый.

Содержимое Redis для защиты:

```powershell
docker compose exec redis redis-cli --scan --pattern 'cost_session:*'
docker compose exec redis redis-cli GET cost_session:ХЕШ_ИЗ_ПЕРВОЙ_КОМАНДЫ
docker compose exec redis redis-cli TTL cost_session:ХЕШ_ИЗ_ПЕРВОЙ_КОМАНДЫ
```

GET возвращает ID пользователя; ключ Redis не является самим значением cookie.

## Тесты

```powershell
python -m unittest discover -s tests -v
python -m tools.check_lab4_live http://localhost:8000
```

Вторая команда требует запущенные API и три хранилища. Создаёт отдельные тестовые аккаунты/карточку, проверяет файлы и права, затем логически удаляет только свою тестовую карточку. Результат: `local_lab_artifacts/lab4/live_checks.json` (не Git).

Основание: [ЛР4 преподавателя](https://github.com/iu5git/Web#лабораторная-4), [Redis](https://github.com/iu5git/Web/tree/main/tutorials/redis), лекции [6](https://github.com/iu5git/Web/blob/main/lectures/Lecture_6_Authorization.pdf) и [7](https://github.com/iu5git/Web/blob/main/lectures/Lecture_7_jwt.pdf). Для FastAPI применяется вариант cookie/Redis, не JWT из примера Go.
