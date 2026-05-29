"""Message repository."""

from sqlalchemy import and_, func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import Message
from app.repositories.base import BaseRepository


class MessageRepository(BaseRepository[Message]):
    """Repository for Message model queries."""

    model = Message

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def list_by_room(
        self, room_id: str, skip: int = 0, limit: int = 50
    ) -> tuple[list[Message], int]:
        """List messages for a room (oldest first within page).

        Args:
            room_id: Room UUID string.
            skip: Pagination offset.
            limit: Maximum messages to return.

        Returns:
            Tuple of (message list, total count).
        """
        base_q = (
            select(Message).options(selectinload(Message.user)).where(Message.room_id == room_id)
        )
        count_result = await self.db.execute(select(func.count()).select_from(base_q.subquery()))
        total = count_result.scalar_one() or 0

        result = await self.db.execute(
            base_q.order_by(Message.sent_at.asc()).offset(skip).limit(limit)
        )
        return list(result.scalars().all()), total
