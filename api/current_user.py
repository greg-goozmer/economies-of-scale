"""Resolve the current user from an opaque cookie and its Redis session."""
import hashlib
import re

from fastapi import Depends, HTTPException, Request, Security
from fastapi.security import APIKeyCookie
from redis.asyncio import Redis
from redis.exceptions import RedisError

from core.config import settings
from db.redis import get_redis


cost_cookie = APIKeyCookie(
    name=settings.SESSION_COOKIE_NAME, auto_error=False, scheme_name="CostSession",
    description="Cookie выдаётся POST /api/users/auth и проверяется по сессии Redis. "
                "В Swagger выполните auth: браузер отправит cookie автоматически.",
)


def session_key(token: str) -> str:
    return "cost_session:" + hashlib.sha256(token.encode()).hexdigest()


async def session_user_id(token: str | None, redis: Redis) -> int | None:
    if not token or not re.fullmatch(r"[0-9a-f]{64}", token):
        return None
    try:
        stored = await redis.get(session_key(token))
    except RedisError as error:
        raise HTTPException(503, "Session storage is unavailable") from error
    if stored is None:
        return None
    try:
        user_id = int(stored)
        return user_id if user_id > 0 else None
    except (ValueError, TypeError):
        return None


async def optional_user_id(request: Request, redis: Redis = Depends(get_redis)) -> int | None:
    return await session_user_id(request.cookies.get(settings.SESSION_COOKIE_NAME), redis)


async def current_user_id(
    token: str | None = Security(cost_cookie), redis: Redis = Depends(get_redis),
) -> int:
    user_id = await session_user_id(token, redis)
    if user_id is None:
        raise HTTPException(401, "Authentication required")
    return user_id
