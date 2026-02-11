import asyncio

from faststream import FastStream
from faststream_app.adapters.kafka import consumers  # noqa
from faststream_app.infrastructure.broker import broker

app = FastStream(broker)


if __name__ == "__main__":
    asyncio.run(app.run())
