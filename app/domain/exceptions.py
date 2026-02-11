from app.domain.enums import OrderStatus


class NotFoundError(Exception):
    resource: str = "Resource"
    message_template: str = "{resource} not found"

    def __init__(self, *, resource: str | None = None, identifier: str | int | None = None):
        self.resource = resource or self.resource
        self.identifier = identifier
        message = self.message_template.format(resource=self.resource)
        if identifier is not None:
            message += f" id={identifier}"
        super().__init__(message)


class UserNotFound(NotFoundError):
    resource = "User"


class UserAlreadyExists(Exception):
    pass


class AuthenticationError(Exception):
    pass


class OrderNotFound(NotFoundError):
    resource = "Order"


class PermissionDenied(Exception):
    pass


class InvalidOrderStatusTransition(Exception):
    def __init__(self, from_status: OrderStatus, to_status: OrderStatus):
        self.from_status = from_status
        self.to_status = to_status
        super().__init__(f"Cannot change order status from {from_status} to {to_status}")
