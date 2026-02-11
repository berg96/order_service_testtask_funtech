import time

from .celery_app import celery_app


@celery_app.task(name="process_order")
def process_order(order_id: str):
    print(f"Start processing order {order_id}")
    time.sleep(2)
    print(f"Order {order_id} processed")
    return {"status": "done", "order_id": order_id}
