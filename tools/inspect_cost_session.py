"""Inspect a demonstration session without logging its secret token."""
import asyncio
from getpass import getpass

from redis.asyncio import Redis

from api.current_user import session_key
from core.config import settings


async def main():
    token = getpass("Cookie cost_session (hidden): ").strip()
    if token.startswith("cost_session="):
        token = token.split("=", 1)[1].split(";", 1)[0]
    if len(token) != 64 or any(c not in "0123456789abcdef" for c in token):
        raise SystemExit("Expected a 64-character hex cookie value")
    redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        key = session_key(token)
        print("Redis key:", key)
        print("User ID:", await redis.get(key))
        print("TTL seconds:", await redis.ttl(key))
    finally:
        await redis.aclose()


if __name__ == "__main__":
    asyncio.run(main())
