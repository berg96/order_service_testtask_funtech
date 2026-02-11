import asyncio
from datetime import UTC, datetime
from uuid import UUID

from faststream.kafka import KafkaBroker

from app.clients.kafka import broker
from app.config.settings import settings


class KafkaProducerAdapter:
    def __init__(self, kafka_broker: KafkaBroker):
        self._broker = kafka_broker
        self._retries = settings.KAFKA_PRODUCER_RETRIES
        self._retry_delay = settings.KAFKA_PRODUCER_RETRY_DELAY

    async def _publish(self, topic: str, message: dict, key: bytes, headers: dict) -> None:
        for attempt in range(self._retries + 1):
            try:
                await self._broker.publish(topic=topic, message=message, key=key, headers=headers)
                return
            except Exception:
                if attempt == self._retries:
                    return
                await asyncio.sleep(self._retry_delay)

    async def notify_new_order(self, order_id: UUID) -> None:
        timestamp = datetime.now(UTC).isoformat()
        message = {"order_id": str(order_id), "timestamp": timestamp}
        headers = {"idempotency-key": f"{order_id}-new_order"}
        await self._publish(
            topic=settings.KAFKA_TOPIC_NEW_ORDER, message=message, key=str(order_id).encode(), headers=headers
        )


kafka_producer = KafkaProducerAdapter(broker)
