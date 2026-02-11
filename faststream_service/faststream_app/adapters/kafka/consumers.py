from faststream import Context
from faststream_app.infrastructure.broker import broker


@broker.subscriber("new_order", group_id="order-service")
async def handle_new_order(msg: dict, headers: dict = Context("message.headers")):
    order_id = msg.get("order_id", "")
    print(order_id)
