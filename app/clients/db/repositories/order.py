from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.db import Order
from app.domain.entities.order import OrderEntity
from app.domain.enums import OrderStatus
from app.domain.exceptions import OrderNotFound


class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    async def _raise_if_none(order: Optional[Order], identifier: str, return_none: bool) -> Optional[OrderEntity]:
        if order is None:
            if return_none:
                return None
            raise OrderNotFound(identifier=identifier)
        return OrderEntity.from_orm(order)

    async def create(
        self,
        user_id: int,
        items: list[dict[str, Any]],
        total_price: float,
        status: Optional[OrderStatus] = OrderStatus.PENDING,
    ) -> OrderEntity:
        order = Order(user_id=user_id, items=items, total_price=total_price, status=status)
        self.session.add(order)
        await self.session.commit()
        await self.session.refresh(order)
        return OrderEntity.from_orm(order)

    async def get(self, order_id: str, return_none: bool = False) -> Optional[OrderEntity]:
        result = await self.session.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        return await self._raise_if_none(order, identifier=order_id, return_none=return_none)

    async def update_status(self, order_id: str, new_status: OrderStatus) -> OrderEntity:
        result = await self.session.execute(select(Order).where(Order.id == order_id).with_for_update())
        order = result.scalar_one_or_none()
        if order is None:
            raise OrderNotFound(identifier=order_id)
        order.status = new_status
        await self.session.commit()
        await self.session.refresh(order)
        return OrderEntity.from_orm(order)

    async def get_user_orders(self, user_id: int) -> list[OrderEntity]:
        result = await self.session.execute(select(Order).where(Order.user_id == user_id).order_by(Order.created_at))
        return [OrderEntity.from_orm(order) for order in result.scalars().all()]
