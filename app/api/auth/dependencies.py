import jwt
import orjson
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.clients.db import get_async_session
from app.clients.db.repositories.user import UserRepository
from app.clients.redis import RedisCache, get_redis
from app.config.settings import settings

from .exceptions import JWTExpired, WrongJWTData
from .jwt import JWTToken
from .schemas import TokenRoles, TokenUser

bearer_scheme = HTTPBearer()


class TokenVerifyService:
    @classmethod
    def verify(cls):
        async def dependency(
            token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
            session=Depends(get_async_session),
            redis=Depends(get_redis),
        ) -> TokenUser:
            try:
                payload = JWTToken().decode(token.credentials)
            except jwt.ExpiredSignatureError:
                raise JWTExpired
            except jwt.PyJWTError:
                raise WrongJWTData

            if payload.get("role") != TokenRoles.ACCESS.value:
                raise WrongJWTData

            cache = RedisCache(redis)
            if cached := await cache.get(f"user:{payload["uuid"]}"):
                return TokenUser(**orjson.loads(cached))

            user = await UserRepository(session).get_by_uuid(payload["uuid"], return_none=True)
            if not user:
                raise WrongJWTData
            user_model = TokenUser(
                id=user.id,
                uuid=user.uuid,
                email=user.email,
                created_at=user.created_at,
            )
            await cache.set(
                key=f"user:{user.uuid}",
                value=orjson.dumps(user_model.model_dump(mode="json")).decode(),
                ttl=settings.USER_CACHE_TTL,
            )
            return user_model

        return dependency


verify_token = TokenVerifyService.verify()
