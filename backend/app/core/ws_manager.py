"""WebSocket connection manager with Redis pub/sub for multi-instance broadcasting."""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import WebSocket
from redis.asyncio import Redis

from app.constants import REDIS_WS_CHANNEL, WSMessageType
from app.redis.client import get_redis_client

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and distributes messages via Redis pub/sub.

    This design ensures correctness across multiple server instances:
    each message is published to Redis, and every instance delivers
    to its locally-connected WebSockets.
    """

    def __init__(self) -> None:
        # room_id → {user_id → WebSocket}
        self._connections: dict[str, dict[str, WebSocket]] = {}
        self._pubsub_task: asyncio.Task[None] | None = None

    async def connect(self, websocket: WebSocket, room_id: str, user_id: str) -> None:
        """Accept a WebSocket connection and register it.

        Args:
            websocket: The FastAPI WebSocket object.
            room_id: Room UUID string.
            user_id: User UUID string.
        """
        await websocket.accept()
        if room_id not in self._connections:
            self._connections[room_id] = {}
            await self._subscribe_to_room(room_id)
        self._connections[room_id][user_id] = websocket
        logger.info(f"WS connected: user={user_id} room={room_id}")

    async def disconnect(self, room_id: str, user_id: str) -> None:
        """Remove a WebSocket connection.

        Args:
            room_id: Room UUID string.
            user_id: User UUID string.
        """
        if room_id in self._connections:
            self._connections[room_id].pop(user_id, None)
            if not self._connections[room_id]:
                del self._connections[room_id]
        logger.info(f"WS disconnected: user={user_id} room={room_id}")

    async def broadcast_to_room(self, room_id: str, message: dict[str, Any]) -> None:
        """Publish a message to all connections in a room via Redis pub/sub.

        Args:
            room_id: Room UUID string.
            message: Message dict (will be serialised to JSON).
        """
        redis = get_redis_client()
        channel = REDIS_WS_CHANNEL.format(room_id=room_id)
        payload = json.dumps({"room_id": room_id, "data": message})
        await redis.publish(channel, payload)

    async def send_personal(self, user_id: str, room_id: str, message: dict[str, Any]) -> None:
        """Send a message directly to a specific user's WebSocket.

        Args:
            user_id: User UUID string.
            room_id: Room UUID string.
            message: Message dict.
        """
        ws = self._connections.get(room_id, {}).get(user_id)
        if ws:
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send personal message to {user_id}: {e}")

    async def _deliver_to_room(self, room_id: str, data: dict[str, Any]) -> None:
        """Deliver a message to all locally-connected WebSockets for a room.

        Args:
            room_id: Room UUID string.
            data: Parsed message dict.
        """
        connections = dict(self._connections.get(room_id, {}))
        dead: list[str] = []
        for user_id, ws in connections.items():
            try:
                await ws.send_json(data)
            except Exception as e:
                logger.warning(f"Failed to deliver to {user_id}: {e}")
                dead.append(user_id)
        for uid in dead:
            self._connections.get(room_id, {}).pop(uid, None)

    async def _subscribe_to_room(self, room_id: str) -> None:
        """Subscribe to the Redis pub/sub channel for a room.

        Called when the first WebSocket joins a room. The subscription
        is handled by the persistent pub/sub listener task.

        Args:
            room_id: Room UUID string.
        """
        # Subscription is managed by start_pubsub_listener
        pass

    async def start_pubsub_listener(self) -> None:
        """Background task: subscribe to all room channels and deliver messages.

        Uses a pattern subscription to receive messages from all room channels.
        Should be started as a background task during app lifespan.
        """
        redis: Redis[Any] = get_redis_client()
        pubsub = redis.pubsub()
        pattern = REDIS_WS_CHANNEL.format(room_id="*")
        await pubsub.psubscribe(pattern)
        logger.info(f"PubSub listener started on pattern: {pattern}")

        try:
            async for raw_message in pubsub.listen():
                if raw_message["type"] != "pmessage":
                    continue
                try:
                    envelope = json.loads(raw_message["data"])
                    room_id: str = envelope["room_id"]
                    data: dict[str, Any] = envelope["data"]
                    await self._deliver_to_room(room_id, data)
                except Exception as e:
                    logger.error(f"PubSub message processing error: {e}")
        except asyncio.CancelledError:
            logger.info("PubSub listener cancelled")
        finally:
            await pubsub.punsubscribe(pattern)
            await pubsub.aclose()


def make_ws_message(msg_type: WSMessageType, payload: dict[str, Any]) -> dict[str, Any]:
    """Build a standardised WebSocket message dict.

    Args:
        msg_type: The WSMessageType enum value.
        payload: The message payload.

    Returns:
        Message dict with type, payload, and timestamp.
    """
    return {
        "type": msg_type,
        "payload": payload,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# Singleton manager instance
manager = ConnectionManager()
