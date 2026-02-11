import datetime

from sqlalchemy import DateTime, MetaData, func, inspect
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

from app.config.settings import settings


class Base(DeclarativeBase):
    metadata = MetaData(schema=settings.DB_SCHEMA)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower() + "s"

    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self, exclude_none: bool = False):
        data = {column.key: getattr(self, column.key) for column in inspect(self).mapper.column_attrs}
        if exclude_none:
            data = {key: value for key, value in data.items() if value is not None}
        return data
