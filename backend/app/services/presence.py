"""Redis-backed room presence management service."""

import json
import logging
from datetime import datetime, timezone

from app.constants import PRESENCE_TTL_SECONDS, REDIS_ROOM_PARTICIPANTS_KEY
from app.redis.client import get_redis_client
from app.schemas.room import PresenceUser

logger = logging.getLogger(__name__)


class PresenceService:
    """Manages who is currently online in each room using Redis hashes."""

    def __init__(self) -> None:
        self.redis = get_redis_client()

    def _key(self, room_id: str) -> str:
        """Build the Redis hash key for a room's participants.

        Args:
            room_id: UUID string of the room.

        Returns:
            Redis key string.
        """
        return REDIS_ROOM_PARTICIPANTS_KEY.format(room_id=room_id)

    async def join_room(
        self,
        room_id: str,
        user_id: str,
        username: str,
        display_name: str,
        avatar_url: str | None = None,
    ) -> None:
        """Add a user to the room's presence set.

        Args:
            room_id: UUID string of the room.
            user_id: UUID string of the user.
            username: User's unique username.
            display_name: User's display name.
            avatar_url: Optional avatar URL.
        """
        presence = PresenceUser(
            user_id=user_id,
            username=username,
            display_name=display_name,
            avatar_url=avatar_url,
            joined_at=datetime.now(timezone.utc).isoformat(),
        )
        key = self._key(room_id)
        await self.redis.hset(key, user_id, presence.model_dump_json())
        await self.redis.expire(key, PRESENCE_TTL_SECONDS)
        logger.debug(f"User {username} joined room {room_id}")

    async def leave_room(self, room_id: str, user_id: str) -> None:
        """Remove a user from the room's presence set.

        Args:
            room_id: UUID string of the room.
            user_id: UUID string of the user.
        """
        key = self._key(room_id)
        await self.redis.hdel(key, user_id)
        logger.debug(f"User {user_id} left room {room_id}")

    async def get_room_participants(self, room_id: str) -> list[PresenceUser]:
        """Retrieve all currently online users in a room.

        Args:
            room_id: UUID string of the room.

        Returns:
            List of PresenceUser objects.
        """
        key = self._key(room_id)
        raw = await self.redis.hgetall(key)
        participants = []
        for value in raw.values():
            try:
                participants.append(PresenceUser.model_validate_json(value))
            except Exception as e:
                logger.warning(f"Failed to parse presence entry: {e}")
        return participants

    async def is_user_in_room(self, room_id: str, user_id: str) -> bool:
        """Check if a user is currently in a room.

        Args:
            room_id: UUID string of the room.
            user_id: UUID string of the user.

        Returns:
            True if the user is present.
        """
        key = self._key(room_id)
        return bool(await self.redis.hexists(key, user_id))

    async def refresh_ttl(self, room_id: str) -> None:
        """Reset the TTL on a room's presence key (activity heartbeat).

        Args:
            room_id: UUID string of the room.
        """
        key = self._key(room_id)
        await self.redis.expire(key, PRESENCE_TTL_SECONDS)
