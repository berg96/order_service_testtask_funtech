import pytest
from fastapi import HTTPException

from app.config.settings import settings


@pytest.mark.real_redis
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
async def test_cors_preflight(async_client):
    headers = {
        "Origin": "http://example.com",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "authorization,content-type",
    }
    response = await async_client.options("/api/register", headers=headers)

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://example.com"
    assert "POST" in response.headers["access-control-allow-methods"]
    assert "authorization" in response.headers["access-control-allow-headers"].lower()
    assert response.headers["access-control-allow-credentials"] == "true"


@pytest.mark.asyncio
async def test_cors_allowed_origin(async_client):
    payload = {"email": "cors@example.com", "password": "StrongPass123"}
    headers = {"Origin": "http://example.com"}
    response = await async_client.post(
        "/api/register",
        json=payload,
        headers=headers,
    )
    assert response.headers["access-control-allow-origin"] == "http://example.com"


@pytest.mark.asyncio
async def test_cors_disallowed_origin(async_client):
    payload = {"email": "evil@example.com", "password": "StrongPass123"}
    headers = {"Origin": "http://evil.com"}
    response = await async_client.post(
        "/api/register",
        json=payload,
        headers=headers,
    )
    assert "access-control-allow-origin" not in response.headers
