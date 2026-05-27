"""Integration tests for room CRUD and membership routes."""

import pytest
from httpx import AsyncClient

from app.models.user import User


@pytest.mark.asyncio
class TestRoomCRUD:
    """Test room creation, retrieval, update, and deletion."""

    async def test_create_room(
        self, async_client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Valid room creation returns 201 with RoomDetail."""
        resp = await async_client.post(
            "/api/v1/rooms/",
            json={"name": "Study Room 1", "is_public": True, "max_participants": 10},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Study Room 1"
        assert "invite_code" in data
        assert len(data["invite_code"]) == 8

    async def test_list_rooms(
        self, async_client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Room list returns paginated response."""
        resp = await async_client.get("/api/v1/rooms/", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data

    async def test_get_room(
        self,
        async_client: AsyncClient,
        auth_headers: dict[str, str],
        test_room: object,
    ) -> None:
        """GET /rooms/{id} returns 200 with room detail."""
        room_id = str(getattr(test_room, "id", ""))
        resp = await async_client.get(f"/api/v1/rooms/{room_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == room_id

    async def test_delete_room_non_owner(
        self, async_client: AsyncClient, test_room: object, db: object
    ) -> None:
        """Non-owner cannot delete a room — expects 403."""
        from app.core.security import create_access_token, hash_password
        from app.models.user import User
        from app.repositories.user import UserRepository
        import uuid

        user = User(
            id=str(uuid.uuid4()),
            email=f"other_{uuid.uuid4().hex[:6]}@example.com",
            username=f"other_{uuid.uuid4().hex[:6]}",
            hashed_password=hash_password("OtherPass1"),
            display_name="Other",
            is_active=True,
        )
        repo = UserRepository(db)  # type: ignore[arg-type]
        user = await repo.create(user)

        headers = {"Authorization": f"Bearer {create_access_token(str(user.id))}"}
        room_id = str(getattr(test_room, "id", ""))
        resp = await async_client.delete(f"/api/v1/rooms/{room_id}", headers=headers)
        assert resp.status_code == 403

    async def test_no_auth_returns_403(self, async_client: AsyncClient) -> None:
        """Unauthenticated request to rooms returns 403."""
        resp = await async_client.get("/api/v1/rooms/")
        assert resp.status_code == 403
