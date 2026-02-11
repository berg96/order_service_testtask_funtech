from celery import Celery
from faststream_app.infrastructure.config import settings

celery_app = Celery(
    "order_service",
    broker=settings.REDIS_BROKER_URL,
    backend=settings.REDIS_BACKEND_URL,
    include=["faststream_app.infrastructure.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
