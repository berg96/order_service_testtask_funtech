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
    def from_orm(user: Optional[User], return_none: bool = False) -> Optional[UserEntity]:
        if user is None:
            if return_none:
                return None
            else:
                raise UserNotFound
        return UserEntity(
            id=user.id,
            uuid=user.uuid,
            email=user.email,
            hashed_password=user.hashed_password,
            created_at=user.created_at,
        )

    async def create(self, email: str, hashed_password: str) -> Optional[UserEntity]:
        user = User(email=email, hashed_password=hashed_password)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return self.from_orm(user)

    async def get_by_email(self, email: str, return_none: bool = False) -> Optional[UserEntity]:
        result = await self.session.execute(select(User).where(User.email == email))
        return self.from_orm(result.scalar_one_or_none(), return_none)

    async def get_by_uuid(self, uuid: str, return_none: bool = False) -> Optional[UserEntity]:
        result = await self.session.execute(select(User).where(User.uuid == uuid))
        return self.from_orm(result.scalar_one_or_none(), return_none)
