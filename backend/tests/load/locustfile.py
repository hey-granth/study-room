"""Load test scenarios using Locust."""

from locust import HttpUser, between, task


class StudyRoomUser(HttpUser):
    """Simulates a typical study room user performing REST operations."""

    wait_time = between(1, 3)
    token: str = ""
    room_id: str = ""

    def on_start(self) -> None:
        """Register and login to obtain a JWT token before running tasks."""
        import uuid

        username = f"user_{uuid.uuid4().hex[:8]}"
        reg = self.client.post(
            "/api/v1/auth/register",
            json={
                "email": f"{username}@test.com",
                "username": username,
                "password": "LoadTest1",
                "display_name": "Load Test User",
            },
        )
        if reg.status_code == 201:
            data = reg.json()
            self.token = data["access_token"]
            # Create a room
            room_resp = self.client.post(
                "/api/v1/rooms/",
                json={"name": "Load Test Room", "is_public": True},
                headers={"Authorization": f"Bearer {self.token}"},
            )
            if room_resp.status_code == 201:
                self.room_id = room_resp.json()["id"]

    @property
    def auth_headers(self) -> dict[str, str]:
        """Return authorization headers."""
        return {"Authorization": f"Bearer {self.token}"}

    @task(3)
    def list_rooms(self) -> None:
        """List public rooms."""
        self.client.get("/api/v1/rooms/", headers=self.auth_headers)

    @task(2)
    def get_room_detail(self) -> None:
        """Fetch room details."""
        if self.room_id:
            self.client.get(f"/api/v1/rooms/{self.room_id}", headers=self.auth_headers)

    @task(1)
    def start_and_end_session(self) -> None:
        """Start then immediately end a session."""
        if self.room_id:
            self.client.post(
                f"/api/v1/sessions/rooms/{self.room_id}/start",
                headers=self.auth_headers,
            )
            self.client.post(
                f"/api/v1/sessions/rooms/{self.room_id}/end",
                headers=self.auth_headers,
            )

    @task(1)
    def get_me(self) -> None:
        """Fetch current user profile."""
        self.client.get("/api/v1/users/me", headers=self.auth_headers)

    @task(1)
    def health_check(self) -> None:
        """Ping the health endpoint."""
        self.client.get("/health")
