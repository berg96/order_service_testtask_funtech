from faststream.kafka import KafkaBroker

from .config import settings

broker = KafkaBroker(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS, acks=settings.KAFKA_PRODUCER_ACKS)
