from unittest.mock import AsyncMock

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.clients.db import get_async_session
from app.config.settings import settings
from app.main import app


@pytest_asyncio.fixture
async def async_engine():
    DATABASE_URL = settings.get_db_url()
    engine = create_async_engine(DATABASE_URL)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def async_session(async_engine):
    async with async_engine.connect() as conn:
        trans = await conn.begin()
        async_session_maker = async_sessionmaker(
            bind=conn,
            expire_on_commit=False,
        )
        session = async_session_maker()
        yield session
        await session.close()
        await trans.rollback()


@pytest_asyncio.fixture(autouse=True)
async def override_get_async_session(async_session):
    async def _override():
        yield async_session

    app.dependency_overrides[get_async_session] = _override
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture(autouse=True)
async def disable_rate_limit(request, monkeypatch):
    if "real_rate_limit" in request.keywords:
        yield  # не мокаем Redis
        return

    fake_redis = AsyncMock()
    fake_redis.incr.return_value = 1
    fake_redis.expire.return_value = True
    fake_redis.get.return_value = None
    fake_redis.set.return_value = True

    async def fake_redis_gen():
        yield fake_redis

    monkeypatch.setattr("app.config.rate_limit.get_redis_client", lambda: fake_redis_gen())

    yield
