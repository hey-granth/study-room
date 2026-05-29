"""
Load test scenarios using Locust for the Collaborative Study Room Platform.

This test suite simulates realistic user behavior:
- Registers and authenticates once per user.
- Stops execution if authentication fails to prevent artificial failure metrics.
- Simulates realistic workflows: browsing rooms, joining rooms, starting sessions.
- Balances task weights so heavy/frequent endpoints (like browsing) are tested
  more often than rare operations (like creating rooms).
- Uses catch_response to validate status codes properly.
"""

import logging
import random
import time
import uuid

from locust import HttpUser, between, task
from locust.exception import StopUser

# Optional WebSocket support for load testing real-time features
try:
    import websocket
    HAS_WEBSOCKET = True
except ImportError:
    HAS_WEBSOCKET = False
    logging.warning("websocket-client not installed. WebSocket load testing is disabled. "
                    "To enable, run: uv pip install websocket-client")


class StudyRoomUser(HttpUser):
    """Simulates a typical study room user performing realistic operations."""

    # Realistic wait times between tasks (users read pages, think, then click)
    wait_time = between(2.0, 10.0)

    token: str = ""
    known_rooms: list[str] = []

    def on_start(self) -> None:
        """
        Executed when a user starts. We use this to register and log in.
        If registration/login fails, we halt the user to prevent polluting
        metrics with artificial 401 Unauthorized errors.
        """
        # Ensure completely unique credentials to avoid database constraints/churn
        unique_id = uuid.uuid4().hex[:8]
        username = f"user_{unique_id}"
        password = "LoadTestPassword123!"

        # 1. Register User
        with self.client.post(
            "/api/v1/auth/register",
            json={
                "email": f"{username}@test.com",
                "username": username,
                "password": password,
                "display_name": f"User {unique_id}",
            },
            catch_response=True,
            name="Auth: Register"
        ) as reg_resp:
            if reg_resp.status_code == 201:
                reg_resp.success()
                data = reg_resp.json()
                self.token = data.get("access_token", "")
            else:
                reg_resp.failure(f"Registration failed: {reg_resp.status_code} - {reg_resp.text}")
                # Critical: Stop this user so they don't spam 401s on other endpoints
                raise StopUser("Registration failed, stopping user.")

        # Ensure token was acquired
        if not self.token:
            raise StopUser("No token acquired, stopping user.")

    @property
    def auth_headers(self) -> dict[str, str]:
        """Return the Bearer token authorization header."""
        return {"Authorization": f"Bearer {self.token}"}

    @task(10)
    def browse_rooms(self) -> None:
        """
        High Frequency: Users browse public rooms frequently.
        """
        with self.client.get(
            "/api/v1/rooms/",
            headers=self.auth_headers,
            catch_response=True,
            name="Rooms: List Public Rooms"
        ) as resp:
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("items", [])
                # Cache available room IDs for other tasks to use realistically
                if items:
                    self.known_rooms = [r["id"] for r in items]
                resp.success()
            else:
                resp.failure(f"Failed to fetch rooms: {resp.status_code}")

    @task(5)
    def fetch_profile_and_stats(self) -> None:
        """
        Medium Frequency: Users check their profile and session stats.
        """
        with self.client.get("/api/v1/users/me", headers=self.auth_headers, catch_response=True, name="Users: Get Me") as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Failed to fetch profile: {resp.status_code}")

        with self.client.get("/api/v1/sessions/me/stats", headers=self.auth_headers, catch_response=True, name="Sessions: Get Stats") as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Failed to fetch stats: {resp.status_code}")

    @task(5)
    def interact_with_room(self) -> None:
        """
        Medium Frequency: Join and view a specific room.
        """
        if not self.known_rooms:
            return

        room_id = random.choice(self.known_rooms)

        # 1. Join room (Required to see details or start sessions)
        with self.client.post(
            f"/api/v1/rooms/{room_id}/join",
            headers=self.auth_headers,
            catch_response=True,
            name="Rooms: Join Room"
        ) as resp:
            # 200 OK or 400 Bad Request (Already a member) are both successful test outcomes
            if resp.status_code in (200, 400):
                resp.success()
            else:
                resp.failure(f"Failed to join room: {resp.status_code}")

        # 2. View Room Details
        with self.client.get(
            f"/api/v1/rooms/{room_id}",
            headers=self.auth_headers,
            catch_response=True,
            name="Rooms: Get Room Detail"
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Failed to fetch room detail: {resp.status_code}")

    @task(2)
    def study_session_workflow(self) -> None:
        """
        Low Frequency: Simulates a user starting a study session, studying, and ending it.
        """
        if not self.known_rooms:
            return

        room_id = random.choice(self.known_rooms)

        # 1. Start Session
        with self.client.post(
            f"/api/v1/sessions/rooms/{room_id}/start",
            headers=self.auth_headers,
            catch_response=True,
            name="Sessions: Start"
        ) as resp:
            # 201 Created or 400 (Active session exists) or 403 (Not a member yet)
            if resp.status_code in (201, 400, 403):
                resp.success()
                if resp.status_code == 403:
                    return # Can't continue session workflow if not a member
            else:
                resp.failure(f"Failed to start session: {resp.status_code}")
                return

        # 2. Simulate studying time
        time.sleep(random.uniform(2, 5))

        # 3. End Session
        with self.client.post(
            f"/api/v1/sessions/rooms/{room_id}/end",
            headers=self.auth_headers,
            catch_response=True,
            name="Sessions: End"
        ) as resp:
            if resp.status_code in (200, 404): # 404 means no active session to end, which is fine
                resp.success()
            else:
                resp.failure(f"Failed to end session: {resp.status_code}")

    @task(1)
    def create_room(self) -> None:
        """
        Very Low Frequency: Users rarely create new rooms.
        Reduces DB churn and clutter.
        """
        unique_id = uuid.uuid4().hex[:4]
        with self.client.post(
            "/api/v1/rooms/",
            json={
                "name": f"Study Room {unique_id}",
                "is_public": True,
                "max_participants": 10
            },
            headers=self.auth_headers,
            catch_response=True,
            name="Rooms: Create Room"
        ) as resp:
            if resp.status_code == 201:
                # Add to known rooms so others can join it
                self.known_rooms.append(resp.json()["id"])
                resp.success()
            else:
                resp.failure(f"Failed to create room: {resp.status_code}")

    @task(2)
    def test_websocket_connection(self) -> None:
        """
        Low Frequency: Tests the WebSockets infrastructure.
        Requires the websocket-client package.
        """
        if not HAS_WEBSOCKET or not self.known_rooms or not self.token:
            return

        room_id = random.choice(self.known_rooms)

        # Determine ws:// or wss:// based on current host
        host = self.host.replace("http://", "ws://").replace("https://", "wss://")
        ws_url = f"{host}/api/v1/ws/rooms/{room_id}?token={self.token}"

        start_time = time.time()
        try:
            # Attempt connection
            ws = websocket.create_connection(ws_url, timeout=3.0)
            ws.settimeout(2.0)
            try:
                # Wait for any welcome messages or broadcasts
                ws.recv()
            except websocket.WebSocketTimeoutException:
                pass # Timeout is fine, just means quiet room

            ws.close()

            # Manually fire success event for Locust
            total_time = int((time.time() - start_time) * 1000)
            self.environment.events.request.fire(
                request_type="WSS",
                name="WebSocket: Connect & Listen",
                response_time=total_time,
                response_length=0,
                exception=None,
            )
        except Exception as e:
            # Fire failure event
            total_time = int((time.time() - start_time) * 1000)
            self.environment.events.request.fire(
                request_type="WSS",
                name="WebSocket: Connect & Listen",
                response_time=total_time,
                response_length=0,
                exception=e,
            )

    @task(1)
    def health_check(self) -> None:
        """
        Very Low Frequency: Health endpoint shouldn't dominate metrics.
        """
        with self.client.get("/health", catch_response=True, name="System: Health") as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Healthcheck failed: {resp.status_code}")
