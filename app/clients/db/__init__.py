from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config.settings import settings

from .base import Base
from .models.order import Order
from .models.user import User

DATABASE_URL = settings.get_db_url()
engine = create_async_engine(DATABASE_URL, poolclass=NullPool)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session():
    async with async_session_maker() as async_session:
        yield async_session


__all__ = [
    "Base",
    "Order",
    "User",
    "get_async_session",
]
