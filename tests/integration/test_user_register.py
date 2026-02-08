import pytest
from fastapi import HTTPException

from app.config.settings import settings


@pytest.mark.asyncio
async def test_register_success(async_client):
    payload = {"email": "test1@example.com", "password": "StrongPass123"}
    response = await async_client.post("/api/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["email"] == "test1@example.com"


@pytest.mark.asyncio
async def test_register_duplicate_email(async_client):
    payload = {"email": "duplicate@example.com", "password": "StrongPass123"}
    await async_client.post("/api/register", json=payload)
    response = await async_client.post("/api/register", json=payload)
    assert response.status_code == 409


@pytest.mark.real_rate_limit
@pytest.mark.asyncio
async def test_rate_limit_enforced(async_client):
    payload = {"email": "ratelimit@example.com", "password": "StrongPass123"}

    for _ in range(settings.RATE_LIMIT):
        response = await async_client.post("/api/register", json=payload)
        assert response.status_code in (201, 409)

    with pytest.raises(HTTPException) as exc:
        await async_client.post("/api/register", json=payload)
    assert exc.value.status_code == 429
    assert "too many requests" in exc.value.detail.lower()


@pytest.mark.asyncio
async def test_register_invalid_email(async_client):
    payload = {"email": "invalid-email", "password": "StrongPass123"}
    response = await async_client.post("/api/register", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_short_pass(async_client):
    payload = {"email": "test@example.com", "password": "pass"}
    response = await async_client.post("/api/register", json=payload)
    assert response.status_code == 422
