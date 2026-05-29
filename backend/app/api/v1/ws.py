"""WebSocket endpoint — real-time room communication."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from jose import JWTError

from app.constants import WSMessageType, MESSAGE_MAX_LENGTH
from app.core.security import decode_token
from app.core.ws_manager import make_ws_message, manager
from app.db.base import AsyncSessionLocal
from app.exceptions import UnauthorizedError
from app.models.message import Message
from app.repositories.message import MessageRepository
from app.repositories.room import RoomRepository
from app.repositories.user import UserRepository
from app.redis.client import get_redis_client
from app.constants import REDIS_TOKEN_BLACKLIST_KEY
from app.services.presence import PresenceService

logger = logging.getLogger(__name__)
router = APIRouter()


async def _authenticate_ws(token: str) -> str:
    """Validate a JWT token for a WebSocket connection.

    Args:
        token: JWT access token string.

    Returns:
        User ID from token subject.

    Raises:
        ValueError: If the token is invalid or blacklisted.
    """
    try:
        payload = decode_token(token)
    except JWTError as e:
        raise ValueError(f"Invalid token: {e}") from e

    if payload.get("type") != "access":
        raise ValueError("Token type must be 'access'")

    user_id: str = payload.get("sub", "")
    jti: str = payload.get("jti", "")

    redis = get_redis_client()
    if await redis.exists(REDIS_TOKEN_BLACKLIST_KEY.format(jti=jti)):
        raise ValueError("Token has been revoked")

    return user_id


@router.websocket("/rooms/{room_id}")
async def websocket_room(
    websocket: WebSocket,
    room_id: str,
    token: str = Query(...),
) -> None:
    """WebSocket endpoint for real-time room communication.

    Protocol:
    - Client sends: {type: "chat_message", payload: {content: str}} or {type: "ping"}
    - Server sends: chat_message_broadcast, user_joined, user_left,
                    session_started, session_ended, participants_update, pong, error
    """
    # Auth
    try:
        user_id = await _authenticate_ws(token)
    except ValueError as e:
        await websocket.accept()
        await websocket.send_json(make_ws_message(WSMessageType.ERROR, {"message": str(e)}))
        await websocket.close(code=4001)
        return

    async with AsyncSessionLocal() as db:
        user_repo = UserRepository(db)
        room_repo = RoomRepository(db)

        user = await user_repo.get(user_id)
        if not user or not user.is_active:
            await websocket.accept()
            await websocket.send_json(
                make_ws_message(WSMessageType.ERROR, {"message": "User not found"})
            )
            await websocket.close(code=4003)
            return

        room = await room_repo.get(room_id)
        if not room:
            await websocket.accept()
            await websocket.send_json(
                make_ws_message(WSMessageType.ERROR, {"message": "Room not found"})
            )
            await websocket.close(code=4004)
            return

        # Connect
        await manager.connect(websocket, room_id, user_id)
        presence = PresenceService()
        await presence.join_room(
            room_id=room_id,
            user_id=user_id,
            username=user.username,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
        )

        # Broadcast user_joined
        await manager.broadcast_to_room(
            room_id,
            make_ws_message(
                WSMessageType.USER_JOINED,
                {
                    "user_id": user_id,
                    "username": user.username,
                    "display_name": user.display_name,
                },
            ),
        )

        # Send participants update
        participants = await presence.get_room_participants(room_id)
        await manager.broadcast_to_room(
            room_id,
            make_ws_message(
                WSMessageType.PARTICIPANTS_UPDATE,
                {"participants": [p.model_dump() for p in participants]},
            ),
        )

        try:
            while True:
                try:
                    data: dict[str, Any] = await websocket.receive_json()
                except Exception:
                    break

                msg_type = data.get("type", "")

                if msg_type == WSMessageType.PING:
                    await presence.refresh_ttl(room_id)
                    await manager.send_personal(
                        user_id,
                        room_id,
                        make_ws_message(WSMessageType.PONG, {}),
                    )

                elif msg_type == WSMessageType.CHAT_MESSAGE:
                    content = str(data.get("payload", {}).get("content", "")).strip()
                    if not content or len(content) > MESSAGE_MAX_LENGTH:
                        await manager.send_personal(
                            user_id,
                            room_id,
                            make_ws_message(
                                WSMessageType.ERROR,
                                {"message": "Message content is empty or too long"},
                            ),
                        )
                        continue

                    # Persist message
                    async with AsyncSessionLocal() as msg_db:
                        msg_repo = MessageRepository(msg_db)
                        msg = Message(
                            id=str(uuid.uuid4()),
                            room_id=room_id,
                            user_id=user_id,
                            content=content,
                            sent_at=datetime.now(timezone.utc),
                        )
                        msg = await msg_repo.create(msg)
                        await msg_db.commit()

                    await manager.broadcast_to_room(
                        room_id,
                        make_ws_message(
                            WSMessageType.CHAT_MESSAGE_BROADCAST,
                            {
                                "id": str(msg.id),
                                "user_id": user_id,
                                "username": user.username,
                                "display_name": user.display_name,
                                "content": content,
                                "sent_at": msg.sent_at.isoformat(),
                            },
                        ),
                    )

                else:
                    await manager.send_personal(
                        user_id,
                        room_id,
                        make_ws_message(
                            WSMessageType.ERROR,
                            {"message": f"Unknown message type: {msg_type}"},
                        ),
                    )

        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected: user={user_id} room={room_id}")
        except Exception as e:
            logger.error(f"WebSocket error: user={user_id} room={room_id}: {e}", exc_info=True)
        finally:
            await manager.disconnect(room_id, user_id)
            await presence.leave_room(room_id, user_id)

            await manager.broadcast_to_room(
                room_id,
                make_ws_message(
                    WSMessageType.USER_LEFT,
                    {"user_id": user_id, "username": user.username},
                ),
            )
            participants = await presence.get_room_participants(room_id)
            await manager.broadcast_to_room(
                room_id,
                make_ws_message(
                    WSMessageType.PARTICIPANTS_UPDATE,
                    {"participants": [p.model_dump() for p in participants]},
                ),
            )
