from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, EmailStr


class TokenUser(BaseModel):
    id: int
    uuid: UUID
    email: EmailStr
    created_at: datetime


class TokenRoles(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"
