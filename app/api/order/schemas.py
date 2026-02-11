from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import OrderStatus


class OrderCreate(BaseModel):
    items: list[dict[str, Any]] = Field(..., min_length=1, description="Список товаров в заказе")
    total_price: float = Field(..., gt=0, description="Сумма заказа (положительное число)")


class OrderFromDB(BaseModel):
    id: UUID = Field(..., description="Идентификатор записи в БД")
    user_id: int = Field(..., description="Уникальный идентификатор пользователя")
    items: list[dict[str, Any]] = Field(..., min_length=1, description="Список товаров в заказе")
    total_price: float = Field(..., gt=0, description="Сумма заказа (положительное число)")
    status: OrderStatus = Field(..., description="Статус заказа (PENDING, PAID, SHIPPED, CANCELED)")
    created_at: datetime = Field(..., description="Дата и время создания заказа")

    model_config = ConfigDict(from_attributes=True)


class OrdersList(BaseModel):
    items: list[OrderFromDB] = Field(..., description="Список заказов")
    count: int = Field(..., ge=0, description="Количество заказов")


class OrderStatusUpdate(BaseModel):
    status: OrderStatus = Field(..., description="Статус заказа (PENDING, PAID, SHIPPED, CANCELED)")
