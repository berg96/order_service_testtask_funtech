from faststream import Context
from faststream_app.infrastructure.broker import broker
from faststream_app.infrastructure.tasks.order import process_order


@broker.subscriber("new_order", group_id="order-service")
async def handle_new_order(msg: dict, headers: dict = Context("message.headers")):
    order_id = msg.get("order_id", "")
    process_order.delay(order_id)
