from datetime import UTC, datetime, timedelta

import pytest

from app.api.auth.jwt import JWTToken
from app.api.auth.schemas import TokenRoles
from app.config.settings import settings


@pytest.mark.asyncio
async def test_token_success(async_client, create_user):
    email = "test1@example.com"
    password = "StrongPass123"
    user = await create_user(email, password)
    payload = {"email": email, "password": password}
    response = await async_client.post("/api/token", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    decode_access_token = JWTToken().decode(data["access_token"])
    assert decode_access_token.get("role") == TokenRoles.ACCESS.value
    assert decode_access_token.get("uuid") == str(user.uuid)
    expired_time = datetime.fromtimestamp(decode_access_token.get("exp"), tz=UTC)
    assert expired_time > datetime.now(UTC)
    assert expired_time - datetime.now(UTC).replace(microsecond=0) == timedelta(minutes=settings.JWT_EXPIRES_MINUTES)

    assert "refresh_token" in data
    decode_refresh_token = JWTToken().decode(data["refresh_token"])
    assert decode_refresh_token.get("role") == TokenRoles.REFRESH.value
    assert decode_refresh_token.get("uuid") == str(user.uuid)
    expired_time = datetime.fromtimestamp(decode_refresh_token.get("exp"), tz=UTC)
    assert expired_time > datetime.now(UTC)
    assert expired_time - datetime.now(UTC).replace(microsecond=0) == timedelta(
        minutes=settings.JWT_REFRESH_EXPIRES_MINUTES
    )


@pytest.mark.asyncio
async def test_token_wrong_pass(async_client, create_user):
    email = "wrong_pass@example.com"
    password = "StrongPass123"
    await create_user(email, password)
    payload = {"email": email, "password": "WrongPass"}
    response = await async_client.post("/api/token", json=payload)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_token_nonexistent_email(async_client, create_user):
    email = "existent@example.com"
    password = "StrongPass123"
    await create_user(email, password)
    payload = {"email": "non-existent@example.com", "password": password}
    response = await async_client.post("/api/token", json=payload)
    assert response.status_code == 401
