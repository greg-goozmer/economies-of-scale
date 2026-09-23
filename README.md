# Масштаб — лабораторная работа №2 по РИП

Ветка `database`. Предметная сущность приложения — издержка, а кофейные позиции используются как примеры. ЛР2 продолжает исправленную ЛР1 и добавляет PostgreSQL, SQLAlchemy, Alembic и Adminer.

## Что реализовано

- Три таблицы: `users`, `expense_items`, `expense_likes`.
- Три `GET`-метода: лента, черновик и плитка.
- `POST` создания черновика и `POST` публикации через ORM SQLAlchemy.
- `POST` логического удаления через сырой SQL `UPDATE`.
- В ленте запрос к БД всегда ограничен одной строкой через `LIMIT 1`.
- Лайки только отображаются; менять их во второй лабораторной нельзя.
- Одновременно у пользователя может быть не больше одного черновика.
- Удалённые записи остаются в БД со статусом `deleted` и не показываются.
- Пустые URL медиа заменяются файлами по умолчанию с SSR-сервера.
- Новые фото и видео выбираются в форме, но в ЛР2 не передаются и не сохраняются.
- Интерфейс ЛР1 остаётся фиксированным, 360 × 704 px, без JavaScript.

## Запуск

Нужны Python 3.12 и Docker Desktop.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
docker compose up -d
.\.venv\Scripts\python.exe -m alembic upgrade head
```

Стартовые данные можно выполнить в Adminer из файла `db/seed.sql` или загрузить командой:

```powershell
docker compose cp db/seed.sql postgres:/tmp/expense_seed.sql
docker compose exec postgres psql -U expense_app -d expense_scale_db -f /tmp/expense_seed.sql
```

Запуск FastAPI:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Адреса:

- лента: <http://localhost:8000/expenses/feed>;
- добавление: <http://localhost:8000/expenses/draft>;
- плитка: <http://localhost:8000/expenses>;
- Adminer: <http://localhost:8081>;
- MinIO Console: <http://localhost:9001>.

Для входа в Adminer: система `PostgreSQL`, сервер `postgres`, пользователь, пароль и база — значения `DB_USER`, `DB_PASSWORD`, `DB_NAME` из `.env`. Внешний порт PostgreSQL — `15432`, потому что стандартный `5432` на рабочем компьютере занят другим контейнером.

## Ровно шесть прикладных методов

| Метод | Адрес | Назначение |
|---|---|---|
| `GET` | `/expenses/feed` | Получить одну опубликованную издержку. |
| `GET` | `/expenses/draft` | Получить черновик текущего пользователя. |
| `GET` | `/expenses` | Получить плитку с фильтром по коду. |
| `POST` | `/expenses/draft` | Создать черновик через ORM. |
| `POST` | `/expenses/draft/publish` | Опубликовать черновик через ORM. |
| `POST` | `/expenses/{expense_id}/delete` | Логически удалить запись сырым SQL. |

Переход по ленте: `/expenses/feed?expense_id=3&next=true`. Фильтрация: `/expenses?min_expense_code=20&max_expense_code=26`.

## База данных

ER-диаграмма находится в `docs/expense_database.drawio` и открывается в draw.io. Каскадное удаление не используется. Связь пользователей и лайков к издержкам реализована отдельной таблицей многие-ко-многим.

DDL создаётся миграцией Alembic:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic current
```

Модели находятся в `models/`, подключение — в `db/session.py`, параметры — в `core/config.py`. Начальные строки для демонстрации хранятся в `db/seed.sql`; приложение не использует Python-коллекцию из ЛР1.

## Что показать на защите

1. Ветку `database` и перенос исправлений ЛР1.
2. ER-диаграмму, три таблицы и данные через Adminer.
3. Alembic-миграцию и SQLAlchemy-модели.
4. Все три страницы и шесть методов в `api/expense_handlers.py`.
5. Что лента выполняет запрос с `LIMIT 1`.
6. Создание черновика кнопкой «Далее», затем публикацию.
7. Логическое удаление: строка остаётся в БД со статусом `deleted`.
8. Файл `docs/lab2_notes.md` с конспектом и ответами на контрольные вопросы.

Остановить контейнеры без удаления данных:

```powershell
docker compose down
```
