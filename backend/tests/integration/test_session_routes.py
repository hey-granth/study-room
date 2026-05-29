import pytest
from httpx import AsyncClient
from app.models.room import Room


@pytest.mark.asyncio
class TestSessionRoutes:
    """Test study session start, end, active, history, and stats endpoints."""

    async def test_session_lifecycle_flow(
        self, async_client: AsyncClient, auth_headers: dict[str, str], test_room: Room
    ) -> None:
        room_id = str(test_room.id)

        # 1. Get active session (should be None/null)
        resp = await async_client.get(
            f"/api/v1/sessions/rooms/{room_id}/active", headers=auth_headers
        )
        assert resp.status_code == 200
        assert resp.json() is None

        # 2. Start session (should succeed with 201)
        resp = await async_client.post(
            f"/api/v1/sessions/rooms/{room_id}/start", headers=auth_headers
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["room_id"] == room_id
        assert data["is_active"] is True
        session_id = data["id"]

        # 3. Get active session again (should return the session)
        resp = await async_client.get(
            f"/api/v1/sessions/rooms/{room_id}/active", headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == session_id
        assert data["is_active"] is True

        # 4. End session (should succeed with 200)
        resp = await async_client.post(
            f"/api/v1/sessions/rooms/{room_id}/end", headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == session_id
        assert data["is_active"] is False

        # 5. Get active session again (should be None/null)
        resp = await async_client.get(
            f"/api/v1/sessions/rooms/{room_id}/active", headers=auth_headers
        )
        assert resp.status_code == 200
        assert resp.json() is None

        # 6. Get session history
        resp = await async_client.get(
            f"/api/v1/sessions/rooms/{room_id}/history", headers=auth_headers
        )
        assert resp.status_code == 200
        history = resp.json()
        assert history["total"] >= 1
        assert history["items"][0]["id"] == session_id

        # 7. Get user stats
        resp = await async_client.get("/api/v1/sessions/me/stats", headers=auth_headers)
        assert resp.status_code == 200
        stats = resp.json()
        assert stats["total_sessions"] >= 1
