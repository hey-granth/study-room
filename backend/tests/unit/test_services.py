import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone, timedelta

from app.services.room import RoomService
from app.services.session import SessionService
from app.schemas.room import RoomCreate, RoomUpdate
from app.exceptions import NotFoundError, ForbiddenError, ConflictError, ValidationError
from app.models.room import Room
from app.models.session import StudySession


@pytest.mark.asyncio
async def test_room_service_lifecycle(db: MagicMock, test_user: MagicMock) -> None:
    room_service = RoomService(db)

    # 1. Create Room
    schema = RoomCreate(
        name="Test Room", description="Test Desc", is_public=True, max_participants=10
    )
    room_detail = await room_service.create_room(schema, str(test_user.id))
    assert room_detail.name == "Test Room"
    assert str(room_detail.owner_id) == str(test_user.id)
    assert room_detail.member_count == 1

    room_id = str(room_detail.id)

    # 2. Get Room
    fetched = await room_service.get_room(room_id)
    assert fetched.id == room_detail.id

    with pytest.raises(NotFoundError):
        await room_service.get_room(str(uuid.uuid4()))

    # 3. List Rooms
    rooms_page = await room_service.list_rooms(str(test_user.id), filter_type="all")
    assert rooms_page.total >= 1

    # 4. Update Room
    update_schema = RoomUpdate(name="Updated Room Name")
    updated = await room_service.update_room(room_id, update_schema, str(test_user.id))
    assert updated.name == "Updated Room Name"

    # Update Room Forbidden
    with pytest.raises(ForbiddenError):
        await room_service.update_room(room_id, update_schema, str(uuid.uuid4()))

    # Update Room NotFound
    with pytest.raises(NotFoundError):
        await room_service.update_room(str(uuid.uuid4()), update_schema, str(test_user.id))

    # 5. Regenerate invite code
    old_code = updated.invite_code
    new_code = await room_service.regenerate_invite_code(room_id, str(test_user.id))
    assert new_code != old_code

    with pytest.raises(NotFoundError):
        await room_service.regenerate_invite_code(str(uuid.uuid4()), str(test_user.id))

    with pytest.raises(ForbiddenError):
        await room_service.regenerate_invite_code(room_id, str(uuid.uuid4()))

    # 6. Delete Room Forbidden
    with pytest.raises(ForbiddenError):
        await room_service.delete_room(room_id, str(uuid.uuid4()))

    # Delete Room NotFound
    with pytest.raises(NotFoundError):
        await room_service.delete_room(str(uuid.uuid4()), str(test_user.id))

    # Delete Room Success
    await room_service.delete_room(room_id, str(test_user.id))
    with pytest.raises(NotFoundError):
        await room_service.get_room(room_id)


@pytest.mark.asyncio
async def test_room_service_membership(db: MagicMock, test_user: MagicMock) -> None:
    room_service = RoomService(db)

    # Create public room
    schema = RoomCreate(
        name="Public Room", description="Test Desc", is_public=True, max_participants=2
    )
    room_detail = await room_service.create_room(schema, str(test_user.id))
    room_id = str(room_detail.id)

    # Create another user to join
    from app.repositories.user import UserRepository
    from app.models.user import User

    user_repo = UserRepository(db)
    other_user = User(
        id=str(uuid.uuid4()),
        username="otheruser",
        email="other@example.com",
        hashed_password="...",
        display_name="Other User",
        is_active=True,
    )
    await user_repo.create(other_user)
    other_user_id = str(other_user.id)

    # Join public room
    joined = await room_service.join_room(room_id, other_user_id)
    assert joined.member_count == 2

    # Already a member
    with pytest.raises(ConflictError):
        await room_service.join_room(room_id, other_user_id)

    # Room is full
    third_user = User(
        id=str(uuid.uuid4()),
        username="thirduser",
        email="third@example.com",
        hashed_password="...",
        display_name="Third User",
        is_active=True,
    )
    await user_repo.create(third_user)
    with pytest.raises(ValidationError):
        await room_service.join_room(room_id, str(third_user.id))

    # Join by invite code already member
    joined_again = await room_service.join_by_invite_code(room_detail.invite_code, other_user_id)
    assert joined_again.id == room_detail.id

    # Join by invite code when full
    with pytest.raises(ValidationError):
        await room_service.join_by_invite_code(room_detail.invite_code, str(third_user.id))

    # Leave room
    await room_service.leave_room(room_id, other_user_id)

    # Leave room owner cannot leave
    with pytest.raises(ValidationError):
        await room_service.leave_room(room_id, str(test_user.id))

    # Join by invite code success after space freed
    joined_by_code = await room_service.join_by_invite_code(
        room_detail.invite_code, str(third_user.id)
    )
    assert joined_by_code.member_count == 2

    # Join private room by public join (raises NotFound)
    private_schema = RoomCreate(
        name="Private Room", description="Test", is_public=False, max_participants=5
    )
    private_room = await room_service.create_room(private_schema, str(test_user.id))
    with pytest.raises(NotFoundError):
        await room_service.join_room(str(private_room.id), other_user_id)


@pytest.mark.asyncio
async def test_session_service(
    db: MagicMock, test_user: MagicMock, test_room: MagicMock, test_redis: MagicMock
) -> None:
    # Set override for redis
    import app.redis.client as redis_module

    redis_module._redis_client_override = test_redis

    session_service = SessionService(db)
    room_id = str(test_room.id)
    user_id = str(test_user.id)

    # Start session room not found
    with pytest.raises(NotFoundError):
        await session_service.start_session(str(uuid.uuid4()), user_id)

    # Start session user not member
    with pytest.raises(ForbiddenError):
        await session_service.start_session(room_id, str(uuid.uuid4()))

    # Start session success
    session_resp = await session_service.start_session(room_id, user_id)
    assert str(session_resp.room_id) == room_id
    assert session_resp.is_active is True

    # Start session conflict
    with pytest.raises(ConflictError):
        await session_service.start_session(room_id, user_id)

    # Get active session
    active = await session_service.get_active_session(room_id)
    assert active is not None
    assert active.id == session_resp.id

    # End session user not member
    with pytest.raises(ForbiddenError):
        await session_service.end_session(room_id, str(uuid.uuid4()))

    # End session success
    ended = await session_service.end_session(room_id, user_id)
    assert ended.is_active is False
    assert ended.duration_seconds >= 0

    # End session again (not found/no active session)
    with pytest.raises(NotFoundError):
        await session_service.end_session(room_id, user_id)

    # Get session history
    history = await session_service.get_session_history(room_id)
    assert history.total >= 1

    # Get user stats
    stats = await session_service.get_user_stats(user_id)
    assert stats.total_sessions >= 1

    redis_module._redis_client_override = None
