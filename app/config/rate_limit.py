from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware

from .settings import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        redis_client = request.app.state.redis
        client_ip = request.client.host
        path = request.url.path
        key = f"rate_limit:{client_ip}:{path}"
        current = await redis_client.incr(key)

        # если первый запрос с этого ip, то задаём время жизни счётчика
        if current == 1:
            await redis_client.expire(key, settings.RATE_LIMIT_TTL)

        if current > settings.RATE_LIMIT:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests, slow down",
            )

        return await call_next(request)
