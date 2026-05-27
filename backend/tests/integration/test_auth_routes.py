"""Integration tests for authentication API routes."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestRegister:
    """Test POST /api/v1/auth/register."""

    async def test_register_success(self, async_client: AsyncClient) -> None:
        """Valid registration returns 201 with tokens."""
        resp = await async_client.post(
            "/api/v1/auth/register",
            json={
                "email": "new@example.com",
                "username": "newuser1",
                "password": "SecurePass1",
                "display_name": "New User",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == "new@example.com"

    async def test_register_duplicate_email(self, async_client: AsyncClient) -> None:
        """Duplicate email returns 409."""
        payload = {
            "email": "dup@example.com",
            "username": "dupuser1",
            "password": "SecurePass1",
            "display_name": "Dup User",
        }
        await async_client.post("/api/v1/auth/register", json=payload)
        resp = await async_client.post(
            "/api/v1/auth/register",
            json={**payload, "username": "dupuser2"},
        )
        assert resp.status_code == 409
        assert resp.json()["code"] == "CONFLICT"

    async def test_register_weak_password(self, async_client: AsyncClient) -> None:
        """Weak password returns 422."""
        resp = await async_client.post(
            "/api/v1/auth/register",
            json={
                "email": "weak@example.com",
                "username": "weakuser1",
                "password": "password",
                "display_name": "Weak User",
            },
        )
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestLogin:
    """Test POST /api/v1/auth/login."""

    async def test_login_success(self, async_client: AsyncClient) -> None:
        """Valid credentials return 200 with tokens."""
        await async_client.post(
            "/api/v1/auth/register",
            json={
                "email": "login@example.com",
                "username": "loginuser1",
                "password": "SecurePass1",
                "display_name": "Login User",
            },
        )
        resp = await async_client.post(
            "/api/v1/auth/login",
            json={"email": "login@example.com", "password": "SecurePass1"},
        )
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    async def test_login_wrong_password(self, async_client: AsyncClient) -> None:
        """Wrong password returns 401."""
        await async_client.post(
            "/api/v1/auth/register",
            json={
                "email": "loginbad@example.com",
                "username": "loginbaduser1",
                "password": "SecurePass1",
                "display_name": "Bad User",
            },
        )
        resp = await async_client.post(
            "/api/v1/auth/login",
            json={"email": "loginbad@example.com", "password": "WrongPass1"},
        )
        assert resp.status_code == 401

    async def test_login_no_token_on_protected(self, async_client: AsyncClient) -> None:
        """Protected endpoint without token returns 403."""
        resp = await async_client.get("/api/v1/users/me")
        assert resp.status_code == 403


@pytest.mark.asyncio
class TestTokenRefresh:
    """Test POST /api/v1/auth/refresh."""

    async def test_refresh_success(self, async_client: AsyncClient) -> None:
        """Valid refresh token returns new token pair."""
        reg = await async_client.post(
            "/api/v1/auth/register",
            json={
                "email": "refresh@example.com",
                "username": "refreshuser1",
                "password": "SecurePass1",
                "display_name": "Refresh User",
            },
        )
        refresh_token = reg.json()["refresh_token"]
        resp = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    async def test_refresh_invalid_token(self, async_client: AsyncClient) -> None:
        """Invalid refresh token returns 401."""
        resp = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "not.a.real.token"},
        )
        assert resp.status_code == 401
