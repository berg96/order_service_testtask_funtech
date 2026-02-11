import asyncio

from faststream.kafka import KafkaBroker
from redis.asyncio import Redis

from .config import settings


async def check_kafka():
    broker = KafkaBroker(settings.KAFKA_BOOTSTRAP_SERVERS)
    try:
        await broker.connect()
        await broker.stop()
        return True
    except Exception:
        return False


async def check_redis():
    client = await Redis.from_url(settings.REDIS_BROKER_URL)
    try:
        await client.ping()
        return True
    except Exception:
        return False


async def run_health_check():
    results = await asyncio.gather(check_kafka(), check_redis())
    if not all(results):
        return False
    return True
