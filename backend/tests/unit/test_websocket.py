import asyncio
import json
import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import WebSocket
from app.core.ws_manager import ConnectionManager, make_ws_message
from app.constants import WSMessageType, REDIS_WS_CHANNEL


@pytest.mark.asyncio
async def test_make_ws_message() -> None:
    msg = make_ws_message(WSMessageType.CHAT_MESSAGE, {"text": "hello"})
    assert msg["type"] == WSMessageType.CHAT_MESSAGE
    assert msg["payload"] == {"text": "hello"}
    assert "timestamp" in msg


@pytest.mark.asyncio
async def test_connection_manager_lifecycle(test_redis: MagicMock) -> None:
    # Set override for redis
    import app.redis.client as redis_module

    redis_module._redis_client_override = test_redis

    manager = ConnectionManager()

    # Mock WebSockets without spec to avoid strict typing or async issues
    ws1 = AsyncMock()
    ws2 = AsyncMock()

    room_id = str(uuid.uuid4())
    user1 = str(uuid.uuid4())
    user2 = str(uuid.uuid4())

    # 1. Connect first user
    await manager.connect(ws1, room_id, user1)
    ws1.accept.assert_called_once()
    assert room_id in manager._connections
    assert manager._connections[room_id][user1] == ws1

    # 2. Connect second user
    await manager.connect(ws2, room_id, user2)
    ws2.accept.assert_called_once()
    assert manager._connections[room_id][user2] == ws2

    # 3. Send personal message
    await manager.send_personal(user1, room_id, {"msg": "private"})
    ws1.send_json.assert_called_once_with({"msg": "private"})
    ws2.send_json.assert_not_called()

    # 3.5. Send personal message exception path
    ws1.send_json.reset_mock()
    ws1.send_json.side_effect = Exception("WS write failed")
    # Should not raise exception
    await manager.send_personal(user1, room_id, {"msg": "failing"})
    ws1.send_json.assert_called_once()

    # 4. Disconnect user 1
    await manager.disconnect(room_id, user1)
    assert user1 not in manager._connections[room_id]
    assert user2 in manager._connections[room_id]

    # 5. Disconnect user 2
    await manager.disconnect(room_id, user2)
    assert room_id not in manager._connections

    # Cleanup override
    redis_module._redis_client_override = None


@pytest.mark.asyncio
async def test_connection_manager_broadcast(test_redis: MagicMock) -> None:
    import app.redis.client as redis_module

    redis_module._redis_client_override = test_redis

    manager = ConnectionManager()
    room_id = str(uuid.uuid4())

    # Test broadcast_to_room
    with patch.object(test_redis, "publish", new_callable=AsyncMock) as mock_publish:
        mock_publish.return_value = 1
        await manager.broadcast_to_room(room_id, {"event": "test"})
        channel = REDIS_WS_CHANNEL.format(room_id=room_id)
        mock_publish.assert_called_once()
        args, kwargs = mock_publish.call_args
        assert args[0] == channel
        payload = json.loads(args[1])
        assert payload["room_id"] == room_id
        assert payload["data"] == {"event": "test"}

    # Cleanup override
    redis_module._redis_client_override = None


@pytest.mark.asyncio
async def test_connection_manager_pubsub(test_redis: MagicMock) -> None:
    import app.redis.client as redis_module

    redis_module._redis_client_override = test_redis

    manager = ConnectionManager()
    room_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    user_id_fail = str(uuid.uuid4())

    ws = AsyncMock()
    ws_fail = AsyncMock()
    ws_fail.send_json.side_effect = Exception("connection lost")

    await manager.connect(ws, room_id, user_id)
    await manager.connect(ws_fail, room_id, user_id_fail)

    # Mock pubsub
    pubsub_mock = AsyncMock()

    # Mock pubsub.listen() as an async generator yielding messages
    async def mock_listen():
        # First message is non-pmessage
        yield {"type": "subscribe", "pattern": None, "channel": b"ch", "data": 1}
        # Second message is pmessage but with malformed data to test exception path
        yield {"type": "pmessage", "pattern": b"ch*", "channel": b"ch1", "data": "invalid json"}
        # Third message is a valid message, which will be sent to both ws and ws_fail (ws_fail will throw)
        valid_envelope = json.dumps({"room_id": room_id, "data": {"event": "hello"}})
        yield {"type": "pmessage", "pattern": b"ch*", "channel": b"ch1", "data": valid_envelope}
        # Final message raises CancelledError to end the loop gracefully
        raise asyncio.CancelledError()

    pubsub_mock.listen = mock_listen

    with patch.object(test_redis, "pubsub", return_value=pubsub_mock):
        # Run the listener, it should exit due to CancelledError
        await manager.start_pubsub_listener()

    # Verify that the websocket received the valid JSON message
    ws.send_json.assert_called_once_with({"event": "hello"})
    ws_fail.send_json.assert_called_once_with({"event": "hello"})

    # ws_fail should have been removed from connections list because it failed
    assert user_id_fail not in manager._connections[room_id]
    assert user_id in manager._connections[room_id]

    pubsub_mock.psubscribe.assert_called_once()
    pubsub_mock.punsubscribe.assert_called_once()
    pubsub_mock.aclose.assert_called_once()

    # Cleanup override
    redis_module._redis_client_override = None
