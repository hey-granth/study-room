"""Application-wide constants and enumerations."""

from enum import StrEnum


class MessageType(StrEnum):
    """Chat message types."""

    CHAT = "chat"
    SYSTEM = "system"


class WSMessageType(StrEnum):
    """WebSocket message type discriminators."""

    # Client → Server
    CHAT_MESSAGE = "chat_message"
    PING = "ping"

    # Server → Client
    CHAT_MESSAGE_BROADCAST = "chat_message_broadcast"
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    SESSION_STARTED = "session_started"
    SESSION_ENDED = "session_ended"
    PARTICIPANTS_UPDATE = "participants_update"
    PONG = "pong"
    ERROR = "error"


# Redis key patterns
REDIS_ROOM_PARTICIPANTS_KEY = "room:{room_id}:participants"
REDIS_ACTIVE_SESSION_KEY = "room:{room_id}:active_session"
REDIS_TOKEN_BLACKLIST_KEY = "token:blacklist:{jti}"
REDIS_RATE_LIMIT_KEY = "rate_limit:{ip}:{minute}"
REDIS_WS_CHANNEL = "ws:room:{room_id}"

# Invite code
INVITE_CODE_LENGTH = 8
INVITE_CODE_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Presence TTL in seconds (24 hours)
PRESENCE_TTL_SECONDS = 86400

# Session
MAX_PARTICIPANTS_DEFAULT = 20

# Message
MESSAGE_MAX_LENGTH = 2000
