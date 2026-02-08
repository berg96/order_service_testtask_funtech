from urllib.parse import quote_plus

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_TITLE: str = Field("Orders", description="Название приложения")
    APP_DESCRIPTION: str = Field("Сервис управления заказами", description="Описание приложения")

    DB_TYPE: str = Field("postgresql", description="Тип БД")
    DB_CONNECTOR: str = Field("asyncpg", description="Коннектор к БД")
    POSTGRES_DB: str = Field(..., description="Название БД")
    POSTGRES_USER: str = Field(..., description="Имя пользователя БД")
    POSTGRES_PASSWORD: str = Field(..., description="Пароль БД")
    POSTGRES_CONTAINER: str = Field("localhost", description="Имя контейнера с БД")
    POSTGRES_PORT: int = Field(5432, description="Порт БД")

    DB_SCHEMA: str = Field("orders", description="Имя схемы БД")

    REDIS_URL: str = Field(..., description="URL подключения к Redis")

    RATE_LIMIT: int = Field(10, description="Допустимое количество запросов")
    RATE_LIMIT_TTL: int = Field(10, description="Время жизни счётчика rate limiting в секундах")

    JWT_SECRET: str = Field(..., description="Секретный ключ для кодирования/декодирования jwt")
    JWT_EXPIRES_MINUTES: int = Field(10, description="Время жизни Access токена")
    JWT_REFRESH_EXPIRES_MINUTES: int = Field(4320, description="Время жизни Refresh токена (3 суток по умолчанию)")
    USER_CACHE_TTL: int = Field(60, description="Время жизни данных о пользователе в кэше")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def get_db_url(self):
        encoded_password = quote_plus(self.POSTGRES_PASSWORD)
        return (
            f"{self.DB_TYPE}+{self.DB_CONNECTOR}://"
            f"{self.POSTGRES_USER}:{encoded_password}@"
            f"{self.POSTGRES_CONTAINER}:{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )


settings = Settings()
