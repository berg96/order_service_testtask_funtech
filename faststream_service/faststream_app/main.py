import asyncio

from faststream import FastStream
from faststream_app.adapters.kafka import consumers  # noqa
from faststream_app.infrastructure.broker import broker
from faststream_app.infrastructure.health import run_health_check

app = FastStream(broker)


@app.on_startup
async def setup():
    if not await run_health_check():
        exit(1)


if __name__ == "__main__":
    asyncio.run(app.run())
