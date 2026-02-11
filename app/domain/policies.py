from app.domain.enums import OrderStatus
from app.domain.exceptions import InvalidOrderStatusTransition


class OrderStatusPolicy:
    FLOW = (OrderStatus.PENDING, OrderStatus.PAID, OrderStatus.SHIPPED, OrderStatus.CANCELED)

    @classmethod
    def validate_transition(cls, current: OrderStatus, target: OrderStatus) -> None:
        if target not in cls.FLOW:
            raise InvalidOrderStatusTransition(current, target)
        if cls.FLOW.index(target) <= cls.FLOW.index(current):
            raise InvalidOrderStatusTransition(current, target)
