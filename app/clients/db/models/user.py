import uuid as uuid_module

from sqlalchemy import UUID, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.clients.db.base import Base


class User(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uuid: Mapped[uuid_module.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid_module.uuid4, unique=True, index=True, nullable=False
    )
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
