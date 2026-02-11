import pytest

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


@pytest.mark.asyncio
async def test_register_invalid_email(async_client):
    payload = {"email": "invalid-email", "password": "StrongPass123"}
    response = await async_client.post("/api/register", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_short_pass(async_client):
    payload = {"email": "test@example.com", "password": "p" * (settings.PASS_MIN_LENGTH - 1)}
    response = await async_client.post("/api/register", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_long_pass(async_client):
    payload = {"email": "test@example.com", "password": "p" * (settings.PASS_MAX_LENGTH + 1)}
    response = await async_client.post("/api/register", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_null_pass(async_client):
    payload = {"email": "test@example.com", "password": " " * (settings.PASS_MIN_LENGTH - 1)}
    response = await async_client.post("/api/register", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_missing_password(async_client):
    payload = {"email": "no-pass@example.com"}
    response = await async_client.post("/api/register", json=payload)
    assert response.status_code == 422
