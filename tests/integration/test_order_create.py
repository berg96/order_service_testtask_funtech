import pytest

from app.domain.enums import OrderStatus


@pytest.mark.asyncio
async def test_order_create_success(async_client, create_user, auth_headers_with_token):
    user = await create_user()
    product1 = {"name": "Молоко", "count": 1}
    product2 = {"product_id": 5, "price": 50}
    items = [product1, product2]
    total_price = 100
    payload = {"items": items, "total_price": total_price}
    response = await async_client.post("/api/orders", json=payload, headers=auth_headers_with_token(user.uuid))
    assert response.status_code == 201
    data = response.json()

    assert "id" in data
    assert data["user_id"] == user.id
    assert data["status"] == OrderStatus.PENDING.value
    assert data["total_price"] == total_price
    assert product1 in data["items"]


@pytest.mark.asyncio
async def test_order_create_not_auth(async_client):
    product1 = {"name": "Молоко", "count": 1}
    product2 = {"product_id": 5, "price": 50}
    items = [product1, product2]
    total_price = 100
    payload = {"items": items, "total_price": total_price}
    response = await async_client.post("/api/orders", json=payload, headers={"Authorization": "Bearer WrongToken"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_order_create_invalid_total_price(async_client, create_user, auth_headers_with_token):
    user = await create_user()
    product1 = {"name": "Молоко", "count": 1}
    product2 = {"product_id": 5, "price": 50}
    items = [product1, product2]
    total_price = -100
    payload = {"items": items, "total_price": total_price}
    response = await async_client.post("/api/orders", json=payload, headers=auth_headers_with_token(user.uuid))
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_order_create_invalid_items(async_client, create_user, auth_headers_with_token):
    user = await create_user()
    items = []
    total_price = 100
    payload = {"items": items, "total_price": total_price}
    response = await async_client.post("/api/orders", json=payload, headers=auth_headers_with_token(user.uuid))
    assert response.status_code == 422
