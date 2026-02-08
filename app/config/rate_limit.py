from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.clients.redis import get_redis_client

from .settings import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        path = request.url.path
        key = f"rate_limit:{client_ip}:{path}"
        redis_client = await get_redis_client().__anext__()
        current = await redis_client.incr(key)

        if current == 1:
            await redis_client.expire(key, settings.RATE_LIMIT_TTL)

        if current > settings.RATE_LIMIT:
            raise HTTPException(
                status_code=429,
                detail="Too many requests, slow down",
            )

        return await call_next(request)
