import secrets

from fastapi import APIRouter, Depends, HTTPException, Request, Response, Security, status
from fastapi.concurrency import run_in_threadpool
from redis.asyncio import Redis
from redis.exceptions import RedisError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from db.redis import get_redis
from api.current_user import cost_cookie, session_key
from core.config import settings
from core.passwords import hash_password, verify_password
from models.user import User
from schemas.user import UserCredentials, UserRead, UserRegister


router = APIRouter(prefix="/api/users", tags=["users"])
DUMMY_HASH = hash_password("not-a-real-user-password")


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED,
             summary="Регистрация пользователя", operation_id="register_user",
             description="Сохраняет PBKDF2-хеш пароля. Сессию не создаёт.",
             responses={409: {"description": "Имя уже занято"}})
async def register_user(payload: UserRegister, db: AsyncSession = Depends(get_db)):
    user_name = payload.user_name.strip()
    if not user_name:
        raise HTTPException(422, "User name is required")
    user = User(user_name=user_name,
                user_password_hash=await run_in_threadpool(hash_password, payload.password))
    try:
        db.add(user)
        await db.commit()
        await db.refresh(user)
    except IntegrityError as error:
        await db.rollback()
        raise HTTPException(409, "User name already exists") from error
    return UserRead(user_id=user.user_id, user_name=user.user_name)


@router.post("/auth", response_model=UserRead, summary="Вход и создание cookie-сессии",
             operation_id="authenticate_user",
             description="Проверяет пароль. Возвращает пользователя и Set-Cookie: cost_session. "
                         "ID пользователя хранится в Redis в течение SESSION_TTL_SECONDS.",
             responses={401: {"description": "Неверное имя или пароль"},
                        503: {"description": "Redis недоступен"}})
async def authenticate_user(
    payload: UserCredentials, response: Response, request: Request,
    db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis),
):
    user = await db.scalar(select(User).where(User.user_name == payload.user_name.strip()))
    valid = await run_in_threadpool(
        verify_password, payload.password, user.user_password_hash if user else DUMMY_HASH,
    )
    if user is None or not valid:
        raise HTTPException(401, "Invalid user name or password")
    token = secrets.token_hex(32)
    old_token = request.cookies.get(settings.SESSION_COOKIE_NAME)
    try:
        await redis.set(session_key(token), str(user.user_id), ex=settings.SESSION_TTL_SECONDS)
        if old_token:
            await redis.delete(session_key(old_token))
    except RedisError as error:
        raise HTTPException(503, "Session storage is unavailable") from error
    response.set_cookie(
        settings.SESSION_COOKIE_NAME, token, max_age=settings.SESSION_TTL_SECONDS,
        httponly=True, secure=settings.SESSION_COOKIE_SECURE, samesite="lax", path="/",
    )
    return UserRead(user_id=user.user_id, user_name=user.user_name)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT,
             summary="Выход и удаление сессии", operation_id="logout_user",
             description="Удаляет сессию из Redis и cookie из браузера. Повторный выход допустим.")
async def logout_user(
    response: Response, token: str | None = Security(cost_cookie),
    redis: Redis = Depends(get_redis),
):
    if token:
        try:
            await redis.delete(session_key(token))
        except RedisError as error:
            raise HTTPException(503, "Session storage is unavailable") from error
    response.delete_cookie(settings.SESSION_COOKIE_NAME, path="/",
                           httponly=True, secure=settings.SESSION_COOKIE_SECURE, samesite="lax")
