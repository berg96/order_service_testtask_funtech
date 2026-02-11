import uuid
from datetime import UTC, datetime, timedelta

import jwt

from app.config.settings import settings

from .schemas import TokenRoles


class JWTToken:
    __secret: str = settings.JWT_SECRET
    __algorithm: str = "HS256"
    __expires_delta: int = settings.JWT_EXPIRES_MINUTES
    __refresh_expires_delta: int = settings.JWT_REFRESH_EXPIRES_MINUTES

    def create_refresh_token(self, user_uuid: uuid.UUID) -> str:
        return self.encode(payload={"uuid": str(user_uuid)}, role=TokenRoles.REFRESH)

    def encode(self, payload: dict, role: TokenRoles = TokenRoles.ACCESS) -> str:
        if role == TokenRoles.REFRESH:
            expires_delta = self.__refresh_expires_delta
        else:
            expires_delta = self.__expires_delta

        payload["exp"] = datetime.now(UTC) + timedelta(minutes=expires_delta)
        payload["role"] = role.value

        return jwt.encode(payload, self.__secret, algorithm=self.__algorithm)

    def decode(self, jwt_token: str) -> dict:
        payload = jwt.decode(jwt_token, self.__secret, algorithms=[self.__algorithm], options={"require": ["exp"]})
        return payload
