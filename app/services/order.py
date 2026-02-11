from typing import Any, Optional
from uuid import UUID

import orjson
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.db.repositories.order import OrderRepository
from app.clients.kafka.producer import kafka_producer
from app.clients.redis import RedisCache
from app.config.settings import settings
from app.domain.entities.order import OrderEntity
from app.domain.enums import OrderStatus
from app.domain.exceptions import OrderNotFound, PermissionDenied
from app.domain.policies import OrderStatusPolicy


class OrderService:
    def __init__(self, session: AsyncSession, redis: Optional[Redis] = None):
        self.session = session
        self.repo = OrderRepository(session)
        self.cache = RedisCache(redis)
        self.kafka_producer = kafka_producer

    async def _update_cache(self, order: OrderEntity):
        await self.cache.set(
            key=f"order:{order.id}",
            value=orjson.dumps(order.to_dict()).decode(),
            ttl=settings.ORDER_CACHE_TTL,
        )

    @staticmethod
    def check_permission(order: OrderEntity, user_id: int):
        if order.user_id != user_id:
            raise PermissionDenied(f"User {user_id} cannot access order {order.id}")

    async def create_order(self, user_id: int, items: list[dict[str, Any]], total_price: float) -> OrderEntity:
        order = await self.repo.create(user_id=user_id, items=items, total_price=total_price)
        await self._update_cache(order)
        await self.kafka_producer.notify_new_order(order.id)
        return order

    async def get_order(self, order_id: UUID, user_id: int) -> Optional[OrderEntity]:
        order: OrderEntity | None
        cached = await self.cache.get(f"order:{order_id}")
        if cached:
            order = OrderEntity.from_dict(orjson.loads(cached))
        else:
            order = await self.repo.get(order_id=str(order_id))
            if order is None:
                raise OrderNotFound(identifier=str(order_id))
            await self._update_cache(order)
        self.check_permission(order, user_id)
        return order

    async def update_order_status(self, order_id: UUID, new_status: OrderStatus, user_id: int) -> Optional[OrderEntity]:
        if not (order := await self.get_order(order_id, user_id)):
            raise OrderNotFound(identifier=str(order_id))
        OrderStatusPolicy.validate_transition(order.status, new_status)
        order = await self.repo.update_status(str(order_id), new_status)
        await self._update_cache(order)
        return order

    async def get_user_orders(self, user_id: int) -> list[OrderEntity]:
        return await self.repo.get_user_orders(user_id)
