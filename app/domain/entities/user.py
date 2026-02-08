from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class UserEntity:
    id: int
    uuid: UUID
    email: str
    hashed_password: str
    created_at: datetime
