from fastapi import Request
from redis.asyncio import Redis


def get_redis(request: Request) -> Redis:
    return request.app.state.redis


class RedisCache:
    def __init__(self, redis_client: Redis):
        self._client = redis_client

    async def get(self, key: str):
        return await self._client.get(key)

    async def set(self, key: str, value: str, ttl: int):
        await self._client.set(key, value, ex=ttl)
