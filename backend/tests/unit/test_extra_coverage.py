import uuid
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from app.utils.datetime import utcnow, utc_from_timestamp
from app.schemas.message import MessageCreate, MessageResponse
from app.constants import MessageType
from app.exceptions import (
    NotFoundError,
    UnauthorizedError,
    ForbiddenError,
    ConflictError,
    ValidationError,
    RateLimitError,
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    generic_exception_handler,
)
from app.redis.client import ping_redis, close_redis_pool, get_redis
from app.db.base import check_db_connection, get_db
from app.services.presence import PresenceService
from app.repositories.message import MessageRepository
from app.repositories.session import SessionRepository
from app.models.message import Message
from app.models.session import StudySession


@pytest.mark.asyncio
async def test_datetime_utils() -> None:
    now = utcnow()
    assert isinstance(now, datetime)
    assert now.tzinfo == timezone.utc

    ts = 1716584400.0
    dt = utc_from_timestamp(ts)
    assert dt.tzinfo == timezone.utc
    assert dt.timestamp() == ts


@pytest.mark.asyncio
async def test_message_schemas() -> None:
    create = MessageCreate(content="hello")
    assert create.content == "hello"
    assert create.message_type == MessageType.CHAT

    resp = MessageResponse(
        id=uuid.uuid4(),
        room_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        content="hello",
        message_type=MessageType.CHAT,
        sent_at=utcnow(),
        username="test",
        display_name="Test",
    )
    assert resp.content == "hello"


@pytest.mark.asyncio
async def test_exceptions_and_handlers() -> None:
    # Test exceptions
    assert NotFoundError("User").status_code == 404
    assert UnauthorizedError("No").status_code == 401
    assert ForbiddenError("No").status_code == 403
    assert ConflictError("Yes").status_code == 409
    assert ValidationError("Oops").status_code == 422
    assert RateLimitError().status_code == 429

    # Mock Request
    request = MagicMock()

    # Test handlers
    resp1 = await app_exception_handler(request, NotFoundError("User"))
    assert resp1.status_code == 404

    from fastapi import HTTPException

    resp2 = await http_exception_handler(request, HTTPException(status_code=400, detail="bad"))
    assert resp2.status_code == 400

    from fastapi.exceptions import RequestValidationError

    resp3 = await validation_exception_handler(request, RequestValidationError([]))
    assert resp3.status_code == 422

    from sqlalchemy.exc import SQLAlchemyError

    resp4 = await sqlalchemy_exception_handler(request, SQLAlchemyError())
    assert resp4.status_code == 500

    resp5 = await generic_exception_handler(request, Exception("oops"))
    assert resp5.status_code == 500


@pytest.mark.asyncio
async def test_redis_utils(test_redis: MagicMock) -> None:
    # Test ping_redis with mock client
    with patch("app.redis.client.get_redis_pool") as mock_pool:
        mock_client = AsyncMock()
        mock_client.ping.return_value = True
        with patch("app.redis.client.aioredis.Redis", return_value=mock_client):
            res = await ping_redis()
            assert res is True
            mock_client.ping.side_effect = Exception("failed")
            res2 = await ping_redis()
            assert res2 is False

    # Test close_redis_pool
    mock_pool_obj = AsyncMock()
    with patch("app.redis.client._redis_pool", mock_pool_obj):
        import app.redis.client as redis_client

        redis_client._redis_pool = mock_pool_obj
        await close_redis_pool()
        mock_pool_obj.aclose.assert_called_once()
        assert redis_client._redis_pool is None

    # Test get_redis dependency (uses _redis_client_override in tests)
    import app.redis.client as redis_module

    redis_module._redis_client_override = test_redis
    try:
        async for client in get_redis():
            assert client == test_redis
    finally:
        redis_module._redis_client_override = None


@pytest.mark.asyncio
async def test_db_utils(db: MagicMock) -> None:
    # check_db_connection
    res = await check_db_connection()
    assert res is True

    # get_db dependency
    generator = get_db()
    session = await anext(generator)
    assert session is not None
    # clean up generator
    try:
        await anext(generator)
    except StopAsyncIteration:
        pass


@pytest.mark.asyncio
async def test_presence_service(test_redis: MagicMock) -> None:
    # We set the override for get_redis_client()
    import app.redis.client as redis_module

    redis_module._redis_client_override = test_redis

    service = PresenceService()
    room_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    await service.join_room(room_id, user_id, "user1", "User One")

    is_in = await service.is_user_in_room(room_id, user_id)
    assert is_in is True

    participants = await service.get_room_participants(room_id)
    assert len(participants) == 1
    assert participants[0].username == "user1"

    await service.refresh_ttl(room_id)

    await service.leave_room(room_id, user_id)
    is_in = await service.is_user_in_room(room_id, user_id)
    assert is_in is False

    redis_module._redis_client_override = None


@pytest.mark.asyncio
async def test_repositories(db: MagicMock, test_user: MagicMock, test_room: MagicMock) -> None:
    # MessageRepository
    msg_repo = MessageRepository(db)
    msg = Message(
        id=str(uuid.uuid4()),
        room_id=test_room.id,
        user_id=test_user.id,
        content="Hello repository",
        message_type=MessageType.CHAT,
        sent_at=utcnow(),
    )
    db.add(msg)
    await db.flush()

    messages, total = await msg_repo.list_by_room(str(test_room.id))
    assert total == 1
    assert messages[0].content == "Hello repository"

    # SessionRepository
    session_repo = SessionRepository(db)
    session = StudySession(
        id=str(uuid.uuid4()),
        room_id=test_room.id,
        started_by=test_user.id,
        started_at=utcnow(),
        is_active=True,
    )
    db.add(session)
    await db.flush()

    active = await session_repo.get_active_session(str(test_room.id))
    assert active is not None
    assert active.id == session.id

    # Stop session
    session.is_active = False
    session.duration_seconds = 120
    await db.flush()

    active_after = await session_repo.get_active_session(str(test_room.id))
    assert active_after is None

    sessions, total_sessions = await session_repo.list_by_room(str(test_room.id))
    assert total_sessions == 1

    sec = await session_repo.get_user_total_seconds(str(test_user.id))
    assert sec == 120

    weekly = await session_repo.get_sessions_this_week(str(test_user.id))
    assert weekly == 1

    daily = await session_repo.get_daily_seconds(str(test_user.id))
    assert len(daily) == 1
    assert daily[0]["seconds"] == 120
