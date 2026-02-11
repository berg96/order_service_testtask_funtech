from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from app.clients.db import Order
from app.domain.enums import OrderStatus


@dataclass
class OrderEntity:
    id: UUID
    user_id: int
    items: list[dict[str, Any]]
    total_price: float
    status: OrderStatus
    created_at: datetime

    @classmethod
    def from_orm(cls, order: Order) -> "OrderEntity":
        return cls(
            id=order.id,
            user_id=order.user_id,
            items=order.items,
            total_price=order.total_price,
            status=order.status,
            created_at=order.created_at,
        )

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "user_id": self.user_id,
            "items": self.items,
            "total_price": self.total_price,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "OrderEntity":
        return cls(
            id=UUID(data["id"]),
            user_id=data["user_id"],
            items=data["items"],
            total_price=float(data["total_price"]),
            status=OrderStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
        )
