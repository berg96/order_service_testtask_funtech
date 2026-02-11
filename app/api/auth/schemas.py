from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class TokenUser(BaseModel):
    id: int = Field(..., description="Идентификатор записи в БД")
    uuid: UUID = Field(..., description="Уникальный идентификатор пользователя")
    email: EmailStr = Field(..., description="Email пользователя")
    created_at: datetime = Field(..., description="Дата и время регистрации пользователя")


class TokenRoles(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"
