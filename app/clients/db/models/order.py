import uuid

from sqlalchemy import JSON, UUID, Enum, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.clients.db import Base
from app.domain.enums import OrderStatus


class Order(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    items: Mapped[list[dict]] = mapped_column(JSON, nullable=False)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, name="order_status"),
        nullable=False,
        default=OrderStatus.PENDING,
    )
