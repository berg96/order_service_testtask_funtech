from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_order_get_user_orders_success(async_client, create_user, auth_headers_with_token, create_order):
    user = await create_user()
    order1 = await create_order(user.id)
    order2 = await create_order(user.id)
    another_user = await create_user("another_user@example.com")
    order3 = await create_order(another_user.id)
    response = await async_client.get(f"/api/orders/user/{user.id}", headers=auth_headers_with_token(user.uuid))
    assert response.status_code == 200
    data = response.json()
    items = data["items"]

    assert len(items) == data["count"] == 2
    assert items[0]["created_at"] <= items[1]["created_at"]
    assert all([order["user_id"] == user.id for order in items])
    order_ids = {order["id"] for order in items}
    assert str(order1.id) in order_ids and str(order2.id) in order_ids and not str(order3.id) in order_ids


@pytest.mark.asyncio
async def test_order_get_user_orders_empty_items(async_client, create_user, auth_headers_with_token):
    user = await create_user()
    response = await async_client.get(f"/api/orders/user/{user.id}", headers=auth_headers_with_token(user.uuid))
    assert response.status_code == 200
    data = response.json()

    assert len(data["items"]) == data["count"] == 0


@pytest.mark.asyncio
async def test_order_get_user_orders_not_auth(async_client, create_user, create_order):
    user = await create_user()
    response = await async_client.get(f"/api/orders/user/{user.id}", headers={"Authorization": "Bearer WrongToken"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_order_get_user_orders_forbidden(async_client, create_user, auth_headers_with_token):
    user = await create_user()
    another_user = await create_user("another_user@example.com")
    response = await async_client.get(f"/api/orders/user/{user.id}", headers=auth_headers_with_token(another_user.uuid))
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_order_get_user_orders_random_token(async_client, create_user, auth_headers_with_token):
    response = await async_client.get("/api/orders/user/9999", headers=auth_headers_with_token(uuid4()))
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_order_get_user_orders_invalid_id(async_client, create_user, auth_headers_with_token):
    user = await create_user()
    response = await async_client.get(f"/api/orders/user/{uuid4()}", headers=auth_headers_with_token(user.uuid))
    assert response.status_code == 422
