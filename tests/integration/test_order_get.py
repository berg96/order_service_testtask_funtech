from uuid import uuid4

import pytest

from app.domain.enums import OrderStatus


@pytest.mark.asyncio
async def test_order_get_success(async_client, create_user, auth_headers_with_token, create_order):
    user = await create_user()
    product1 = {"name": "Молоко", "count": 1}
    product2 = {"product_id": 5, "price": 50}
    items = [product1, product2]
    total_price = 100
    order = await create_order(user.id, items, total_price)
    response = await async_client.get(f"/api/orders/{order.id}", headers=auth_headers_with_token(user.uuid))
    assert response.status_code == 200
    data = response.json()

    assert "id" in data
    assert data["user_id"] == user.id
    assert data["status"] == OrderStatus.PENDING.value
    assert data["total_price"] == total_price
    assert product1 in data["items"]


@pytest.mark.asyncio
async def test_order_get_not_auth(async_client, create_user, create_order):
    user = await create_user()
    order = await create_order(user.id)
    response = await async_client.get(f"/api/orders/{order.id}", headers={"Authorization": "Bearer WrongToken"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_order_get_forbidden(async_client, create_user, auth_headers_with_token, create_order):
    user = await create_user()
    order = await create_order(user.id)
    another_user = await create_user("another_user@example.com")
    response = await async_client.get(f"/api/orders/{order.id}", headers=auth_headers_with_token(another_user.uuid))
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_order_get_not_found(async_client, create_user, auth_headers_with_token):
    user = await create_user()
    response = await async_client.get(f"/api/orders/{uuid4()}", headers=auth_headers_with_token(user.uuid))
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_order_get_invalid_order_uuid(async_client, create_user, auth_headers_with_token):
    user = await create_user()
    response = await async_client.get("/api/orders/not-a-uuid", headers=auth_headers_with_token(user.uuid))
    assert response.status_code == 422
