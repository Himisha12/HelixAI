from typing import Dict
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient) -> None:
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_demo_user_login(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/api/v1/auth/token",
        data={"username": "demo_user", "password": "demo123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_invalid_login(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/api/v1/auth/token",
        data={"username": "demo_user", "password": "wrongpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_user_registration(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/api/v1/auth/register",
        json={"username": "test_user_new", "email": "newuser@test.com", "password": "password123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "test_user_new"
    assert data["email"] == "newuser@test.com"


@pytest.mark.asyncio
async def test_get_me_profile(async_client: AsyncClient, auth_headers: Dict[str, str]) -> None:
    response = await async_client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["username"] == "demo_user"
    assert "usage_metrics" in data
