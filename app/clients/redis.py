import redis

from app.config.settings import settings


async def get_redis_client():
    redis_client = redis.asyncio.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )
    try:
        yield redis_client
    finally:
        await redis_client.aclose()


class RedisCache:
    def __init__(self, redis_client):
        self._client = redis_client

    async def get(self, key: str):
        return await self._client.get(key)

    async def set(self, key: str, value: str, ttl: int):
        await self._client.set(key, value, ex=ttl)
