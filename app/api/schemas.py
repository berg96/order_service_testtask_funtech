from typing import Optional

from pydantic import BaseModel, Field


class SuccessResponse(BaseModel):
    detail: Optional[str] = Field("Success", description="Успешный результат")
    user_message: Optional[str] = Field(None, description="Дополнительное сообщение")


class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Сообщение об ошибке")
