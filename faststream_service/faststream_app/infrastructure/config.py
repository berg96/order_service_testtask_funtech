from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    KAFKA_BOOTSTRAP_SERVERS: str = Field(..., description="Адреса Kafka брокеров через запятую")
    KAFKA_PRODUCER_ACKS: str = Field("all", description="Гарантия доставки сообщений (all, 1, 0)")
    KAFKA_PRODUCER_RETRIES: int = Field(3, description="Количество попыток повторной отправки при ошибке")
    KAFKA_PRODUCER_RETRY_DELAY: int = Field(1, description="Задержка между попытками публикации сообщений, сек")
    KAFKA_TOPIC_NEW_ORDER: str = Field("new_order", description="Топик для событий созданий нового заказа")

    REDIS_BROKER_URL: str = Field(..., description="Брокер задач для Celery")
    REDIS_BACKEND_URL: str = Field(..., description="Брокер ответов после выполнения задач из Celery")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
