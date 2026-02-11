from uuid import uuid4

import orjson
import pytest

from app.clients.redis import RedisCache
from app.domain.entities.order import OrderEntity
from app.domain.enums import OrderStatus


@pytest.mark.asyncio
async def test_order_update_status_success(async_client, create_user, auth_headers_with_token, create_order):
    user = await create_user()
    order = await create_order(user.id)
    payload = {"status": OrderStatus.PAID.value}
    response = await async_client.patch(
        f"/api/orders/{order.id}", json=payload, headers=auth_headers_with_token(user.uuid)
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(order.id)
    assert data["status"] != order.status
    assert data["status"] == OrderStatus.PAID.value


@pytest.mark.asyncio
async def test_order_update_status_not_auth(async_client, create_user, create_order):
    user = await create_user()
    order = await create_order(user.id)
    payload = {"status": OrderStatus.PAID.value}
    response = await async_client.patch(
        f"/api/orders/{order.id}", json=payload, headers={"Authorization": "Bearer WrongToken"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_order_update_status_forbidden(async_client, create_user, auth_headers_with_token, create_order):
    user = await create_user()
    order = await create_order(user.id)
    another_user = await create_user("another_user@example.com")
    payload = {"status": OrderStatus.PAID.value}
    response = await async_client.patch(
        f"/api/orders/{order.id}", json=payload, headers=auth_headers_with_token(another_user.uuid)
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_order_update_status_not_found(async_client, create_user, auth_headers_with_token):
    user = await create_user()
    payload = {"status": OrderStatus.PAID.value}
    response = await async_client.patch(
        f"/api/orders/{uuid4()}", json=payload, headers=auth_headers_with_token(user.uuid)
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_order_update_status_invalid_order_uuid(async_client, create_user, auth_headers_with_token):
    user = await create_user()
    payload = {"status": OrderStatus.PAID.value}
    response = await async_client.patch(
        "/api/orders/not-a-uuid", json=payload, headers=auth_headers_with_token(user.uuid)
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_order_update_status_not_body(async_client, create_user, auth_headers_with_token, create_order):
    user = await create_user()
    order = await create_order(user.id)
    response = await async_client.patch(f"/api/orders/{order.id}", headers=auth_headers_with_token(user.uuid))
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_order_update_status_invalid_status(async_client, create_user, auth_headers_with_token, create_order):
    user = await create_user()
    order = await create_order(user.id)
    payload = {"status": "Awaiting"}
    response = await async_client.patch(
        f"/api/orders/{order.id}", json=payload, headers=auth_headers_with_token(user.uuid)
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_order_update_status_invalid_order_status_transition(
    async_client, create_user, auth_headers_with_token, create_order
):
    user = await create_user()
    order = await create_order(user.id)
    payload = {"status": OrderStatus.CANCELED.value}
    response = await async_client.patch(
        f"/api/orders/{order.id}", json=payload, headers=auth_headers_with_token(user.uuid)
    )
    assert response.status_code == 200

    payload = {"status": OrderStatus.PAID.value}
    response = await async_client.patch(
        f"/api/orders/{order.id}", json=payload, headers=auth_headers_with_token(user.uuid)
    )
    assert response.status_code == 409


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "from_status,to_status,expected_code",
    [
        (OrderStatus.PENDING, OrderStatus.PAID, 200),
        (OrderStatus.PAID, OrderStatus.SHIPPED, 200),
        (OrderStatus.PENDING, OrderStatus.CANCELED, 200),
        (OrderStatus.SHIPPED, OrderStatus.PAID, 409),
    ],
)
async def test_order_update_status_transitions(
    async_client, create_user, auth_headers_with_token, create_order, from_status, to_status, expected_code
):
    user = await create_user()
    order = await create_order(user.id, status=from_status)
    payload = {"status": to_status.value}
    response = await async_client.patch(
        f"/api/orders/{order.id}", json=payload, headers=auth_headers_with_token(user.uuid)
    )
    assert response.status_code == expected_code


@pytest.mark.real_redis
@pytest.mark.asyncio
async def test_order_update_status_cache(
    async_client, create_user, create_order, auth_headers_with_token, redis_client
):
    user = await create_user()
    order = await create_order(user.id)
    response = await async_client.get(f"/api/orders/{order.id}", headers=auth_headers_with_token(user.uuid))
    assert response.status_code == 200

    cache = RedisCache(redis_client)
    cached_order = OrderEntity.from_dict(orjson.loads(await cache.get(f"order:{order.id}")))

    payload = {"status": OrderStatus.CANCELED.value}
    response = await async_client.patch(
        f"/api/orders/{order.id}", json=payload, headers=auth_headers_with_token(user.uuid)
    )
    assert response.status_code == 200

    new_cached_order = OrderEntity.from_dict(orjson.loads(await cache.get(f"order:{order.id}")))
    assert new_cached_order.id == cached_order.id == order.id
    assert cached_order.status != new_cached_order.status
    assert new_cached_order.status == OrderStatus.CANCELED
