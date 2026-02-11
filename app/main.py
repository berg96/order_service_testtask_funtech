from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio import Redis

from .api.exception_handlers import setup_exception_handlers
from .api.router import main_router
from .clients.kafka import broker
from .config.middleware import setup_middleware
from .config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = Redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )
    await broker.start()
    yield
    await app.state.redis.close()
    await broker.stop()


app = FastAPI(title=settings.APP_TITLE, description=settings.APP_DESCRIPTION, lifespan=lifespan)

setup_middleware(app)
app.include_router(main_router)
setup_exception_handlers(app)
