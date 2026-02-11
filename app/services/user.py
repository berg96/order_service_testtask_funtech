from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.db.repositories.user import UserRepository
from app.domain.entities.user import UserEntity
from app.domain.exceptions import AuthenticationError, UserAlreadyExists


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = UserRepository(session)
        self.pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

    def _hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    async def register_user(self, email: str, password: str) -> UserEntity:
        if await self.repo.get_by_email(email, return_none=True):
            raise UserAlreadyExists
        return await self.repo.create(
            email=email,
            hashed_password=self._hash_password(password),
        )

    async def authenticate_user(self, email: str, password: str) -> UserEntity:
        user = await self.repo.get_by_email(email, return_none=True)
        if not user or not self._verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid credentials")
        return user
