from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio import Redis

from api.cost_api import router as cost_router
from api.user_api import router as user_router
from core.config import settings
from db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.cost_sessions = Redis.from_url(settings.REDIS_URL, decode_responses=True,
                                             socket_connect_timeout=3, socket_timeout=3)
    try:
        yield
    finally:
        await app.state.cost_sessions.aclose()
        await engine.dispose()

app = FastAPI(
    title="Масштаб — API издержек",
    description="ЛР4. Гость читает опубликованные издержки. После POST /api/users/auth "
                "браузер автоматически отправляет HttpOnly cookie cost_session. "
                "Создание, черновик, публикация, удаление и лайки требуют сессии Redis.",
    version="4.0.0", lifespan=lifespan,
    swagger_ui_parameters={"withCredentials": True},
)

app.include_router(cost_router)
app.include_router(user_router)
