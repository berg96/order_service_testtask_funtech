from typing import Any, Optional
from uuid import UUID

import pytest_asyncio
from fakeredis.aioredis import FakeRedis
from httpx import ASGITransport, AsyncClient
from passlib.context import CryptContext
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.auth.jwt import JWTToken
from app.clients.db import Order, User, get_async_session
from app.config.settings import settings
from app.domain.enums import OrderStatus
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
async def async_client(request):
    transport = ASGITransport(app=app)
    if "real_redis" in request.keywords:
        app.state.redis = Redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    else:
        app.state.redis = FakeRedis()
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def redis_client(async_client):
    client = async_client._transport.app.state.redis
    yield client


@pytest_asyncio.fixture
async def create_user(async_session):
    async def _create(email: Optional[str] = "test1@example.com", password: Optional[str] = "StrongPass123") -> User:
        user = User(email=email, hashed_password=CryptContext(schemes=["argon2"], deprecated="auto").hash(password))
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)
        return user

    return _create


@pytest_asyncio.fixture
def auth_headers_with_token():
    def _create(user_uuid: UUID) -> dict[str, str]:
        return {"Authorization": f"Bearer {JWTToken().encode({"uuid": str(user_uuid)})}"}

    return _create


@pytest_asyncio.fixture
async def create_order(async_session):
    async def _create(
        user_id: int,
        items: Optional[list[dict[str, Any]]] = None,
        total_price: Optional[float] = 100,
        status: Optional[OrderStatus] = OrderStatus.PENDING,
    ) -> Order:
        if not items:
            items = [{"name": "Молоко", "count": 1}, {"product_id": 5, "price": 50}]
        order = Order(user_id=user_id, items=items, total_price=total_price, status=status)
        async_session.add(order)
        await async_session.commit()
        await async_session.refresh(order)
        return order

    return _create
