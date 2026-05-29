"""StudySession repository."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import StudySession
from app.repositories.base import BaseRepository


class SessionRepository(BaseRepository[StudySession]):
    """Repository for StudySession model queries."""

    model = StudySession

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def get_active_session(self, room_id: str) -> StudySession | None:
        """Fetch the currently active session for a room.

        Args:
            room_id: Room UUID string.

        Returns:
            Active StudySession or None.
        """
        result = await self.db.execute(
            select(StudySession).where(
                and_(StudySession.room_id == room_id, StudySession.is_active == True)  # noqa: E712
            )
        )
        return result.scalar_one_or_none()

    async def list_by_room(
        self, room_id: str, skip: int = 0, limit: int = 20
    ) -> tuple[list[StudySession], int]:
        """List past sessions for a room (most recent first).

        Args:
            room_id: Room UUID string.
            skip: Pagination offset.
            limit: Maximum sessions to return.

        Returns:
            Tuple of (session list, total count).
        """
        base_q = (
            select(StudySession)
            .where(StudySession.room_id == room_id)
            .order_by(StudySession.started_at.desc())
        )
        count_result = await self.db.execute(select(func.count()).select_from(base_q.subquery()))
        total = count_result.scalar_one() or 0
        result = await self.db.execute(base_q.offset(skip).limit(limit))
        return list(result.scalars().all()), total

    async def get_user_total_seconds(self, user_id: str) -> int:
        """Sum all completed session durations for a user.

        Args:
            user_id: User UUID string.

        Returns:
            Total seconds studied.
        """
        result = await self.db.execute(
            select(func.coalesce(func.sum(StudySession.duration_seconds), 0)).where(
                and_(
                    StudySession.started_by == user_id,
                    StudySession.is_active == False,  # noqa: E712
                )
            )
        )
        return result.scalar_one() or 0

    async def get_sessions_this_week(self, user_id: str) -> int:
        """Count sessions started by user in the last 7 days.

        Args:
            user_id: User UUID string.

        Returns:
            Session count.
        """
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        result = await self.db.execute(
            select(func.count())
            .select_from(StudySession)
            .where(
                and_(
                    StudySession.started_by == user_id,
                    StudySession.started_at >= week_ago,
                )
            )
        )
        return result.scalar_one() or 0

    async def get_daily_seconds(self, user_id: str, days: int = 7) -> list[dict[str, object]]:
        """Get study seconds per day for the last N days.

        Args:
            user_id: User UUID string.
            days: Number of days to look back.

        Returns:
            List of dicts with 'date' and 'seconds' keys.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        result = await self.db.execute(
            select(
                func.date(StudySession.started_at).label("date"),
                func.coalesce(func.sum(StudySession.duration_seconds), 0).label("seconds"),
            )
            .where(
                and_(
                    StudySession.started_by == user_id,
                    StudySession.started_at >= cutoff,
                    StudySession.is_active == False,  # noqa: E712
                )
            )
            .group_by(func.date(StudySession.started_at))
            .order_by(func.date(StudySession.started_at))
        )
        return [{"date": str(row.date), "seconds": row.seconds} for row in result]
