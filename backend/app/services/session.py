"""Study session business logic service."""

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import REDIS_ACTIVE_SESSION_KEY
from app.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError
from app.models.session import StudySession
from app.redis.client import get_redis_client
from app.repositories.room import RoomRepository
from app.repositories.session import SessionRepository
from app.schemas.common import Page
from app.schemas.session import StudySessionResponse, UserSessionStats

logger = logging.getLogger(__name__)


class SessionService:
    """Handles study session lifecycle within rooms."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.session_repo = SessionRepository(db)
        self.room_repo = RoomRepository(db)
        self.redis = get_redis_client()

    async def start_session(self, room_id: str, user_id: str) -> StudySessionResponse:
        """Start a new study session for a room.

        Args:
            room_id: UUID of the room.
            user_id: UUID of the user starting the session.

        Returns:
            The new StudySessionResponse.

        Raises:
            NotFoundError: Room not found.
            ForbiddenError: User is not a member.
            ConflictError: A session is already active.
        """
        room = await self.room_repo.get(room_id)
        if not room:
            raise NotFoundError("Room")

        if not await self.room_repo.is_member(room_id, user_id):
            raise ForbiddenError("You must be a room member to start a session")

        existing = await self.session_repo.get_active_session(room_id)
        if existing:
            raise ConflictError("A study session is already active in this room")

        now = datetime.now(timezone.utc)
        session = StudySession(
            id=str(uuid.uuid4()),
            room_id=room_id,
            started_by=user_id,
            started_at=now,
            is_active=True,
        )
        session = await self.session_repo.create(session)

        # Cache session start time in Redis for live timer
        redis_key = REDIS_ACTIVE_SESSION_KEY.format(room_id=room_id)
        await self.redis.set(redis_key, str(session.id), ex=86400)

        logger.info(f"Session started: room={room_id} by user={user_id}")
        return StudySessionResponse.model_validate(session)

    async def end_session(self, room_id: str, user_id: str) -> StudySessionResponse:
        """End the active study session for a room.

        Args:
            room_id: UUID of the room.
            user_id: UUID of the user ending the session.

        Returns:
            The completed StudySessionResponse with duration.

        Raises:
            NotFoundError: No active session.
            ForbiddenError: User is not a member.
        """
        if not await self.room_repo.is_member(room_id, user_id):
            raise ForbiddenError("You must be a room member to end a session")

        session = await self.session_repo.get_active_session(room_id)
        if not session:
            raise NotFoundError("No active session in this room")

        now = datetime.now(timezone.utc)
        started = session.started_at.replace(tzinfo=timezone.utc) if session.started_at.tzinfo is None else session.started_at
        duration = int((now - started).total_seconds())

        updated = await self.session_repo.update(session, {
            "ended_at": now,
            "duration_seconds": duration,
            "is_active": False,
        })

        # Clear Redis key
        redis_key = REDIS_ACTIVE_SESSION_KEY.format(room_id=room_id)
        await self.redis.delete(redis_key)

        logger.info(f"Session ended: room={room_id} duration={duration}s")
        return StudySessionResponse.model_validate(updated)

    async def get_active_session(self, room_id: str) -> StudySessionResponse | None:
        """Return the active session for a room if one exists.

        Args:
            room_id: UUID of the room.

        Returns:
            StudySessionResponse or None.
        """
        session = await self.session_repo.get_active_session(room_id)
        return StudySessionResponse.model_validate(session) if session else None

    async def get_session_history(
        self, room_id: str, page: int = 1, size: int = 20
    ) -> Page[StudySessionResponse]:
        """List completed sessions for a room.

        Args:
            room_id: UUID of the room.
            page: Page number.
            size: Page size.

        Returns:
            Paginated page of StudySessionResponse.
        """
        skip = (page - 1) * size
        sessions, total = await self.session_repo.list_by_room(room_id, skip=skip, limit=size)
        return Page.create(
            items=[StudySessionResponse.model_validate(s) for s in sessions],
            total=total,
            page=page,
            size=size,
        )

    async def get_user_stats(self, user_id: str) -> UserSessionStats:
        """Compute aggregated session statistics for a user.

        Args:
            user_id: UUID of the user.

        Returns:
            UserSessionStats.
        """
        total_seconds = await self.session_repo.get_user_total_seconds(user_id)
        sessions_week = await self.session_repo.get_sessions_this_week(user_id)
        sessions_all, _ = await self.session_repo.get_multi(skip=0, limit=1)
        all_sessions_count = (await self.session_repo.get_multi(skip=0, limit=10000))[1]

        return UserSessionStats(
            total_sessions=all_sessions_count,
            total_study_seconds=total_seconds,
            sessions_this_week=sessions_week,
            average_session_seconds=total_seconds // max(all_sessions_count, 1),
            longest_session_seconds=0,  # TODO: add dedicated query
        )
