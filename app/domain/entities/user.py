from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.clients.db import User


@dataclass
class UserEntity:
    id: int
    uuid: UUID
    email: str
    hashed_password: str
    created_at: datetime

    @classmethod
    def from_orm(cls, user: User) -> "UserEntity":
        return cls(
            id=user.id,
            uuid=user.uuid,
            email=user.email,
            hashed_password=user.hashed_password,
            created_at=user.created_at,
        )
