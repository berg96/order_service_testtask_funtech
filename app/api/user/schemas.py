from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.config.settings import settings


class UserRegister(BaseModel):
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(
        ..., min_length=settings.PASS_MIN_LENGTH, max_length=settings.PASS_MAX_LENGTH, description="Пароль пользователя"
    )


class UserFromDB(BaseModel):
    id: int = Field(..., description="Идентификатор записи в БД")
    uuid: UUID = Field(..., description="Уникальный идентификатор пользователя")
    email: EmailStr = Field(..., description="Email пользователя")
    created_at: datetime = Field(..., description="Дата и время регистрации пользователя")

    model_config = ConfigDict(from_attributes=True)


class RefreshToken(BaseModel):
    refresh_token: str = Field(..., description="Токен для обновления access_token")


class Token(RefreshToken):
    access_token: str = Field(..., description="Токен для доступа к запросам API")
