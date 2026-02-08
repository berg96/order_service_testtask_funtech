class NotFoundError(Exception):
    resource: str = "Resource"
    message_template: str = "{resource} not found"

    def __init__(self, *, resource: str | None = None, identifier: str | int | None = None):
        self.resource = resource or self.resource
        self.identifier = identifier

    @property
    def message(self) -> str:
        if self.identifier is not None:
            return f"{self.resource} not found id={self.identifier}"
        return f"{self.resource} not found"


class UserNotFound(NotFoundError):
    resource = "User"


class UserAlreadyExists(Exception):
    pass
