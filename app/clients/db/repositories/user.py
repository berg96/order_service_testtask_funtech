from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.db import User
from app.domain.entities.user import UserEntity
from app.domain.exceptions import UserNotFound


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    async def _raise_if_none(user: Optional[User], identifier: str, return_none: bool) -> Optional[UserEntity]:
        if user is None:
            if return_none:
                return None
            raise UserNotFound(identifier=identifier)
        return UserEntity.from_orm(user)

    async def create(self, email: str, hashed_password: str) -> UserEntity:
        user = User(email=email, hashed_password=hashed_password)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return UserEntity.from_orm(user)

    async def get_by_email(self, email: str, return_none: bool = False) -> Optional[UserEntity]:
        result = await self.session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        return await self._raise_if_none(user, identifier=email, return_none=return_none)

    async def get_by_uuid(self, uuid: str, return_none: bool = False) -> Optional[UserEntity]:
        result = await self.session.execute(select(User).where(User.uuid == uuid))
        user = result.scalar_one_or_none()
        return await self._raise_if_none(user, identifier=uuid, return_none=return_none)
