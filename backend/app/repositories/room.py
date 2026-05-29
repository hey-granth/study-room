"""Room repository — DB access layer for rooms."""

import uuid

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.room import Room, room_members
from app.models.user import User
from app.repositories.base import BaseRepository


class RoomRepository(BaseRepository[Room]):
    """Repository for Room model queries."""

    model = Room

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def get_with_members(self, room_id: str) -> Room | None:
        """Fetch a room with owner and members eagerly loaded.

        Args:
            room_id: UUID string of the room.

        Returns:
            Room with relationships populated, or None.
        """
        result = await self.db.execute(
            select(Room)
            .options(selectinload(Room.owner), selectinload(Room.members))
            .where(Room.id == room_id)
        )
        return result.scalar_one_or_none()

    async def get_by_invite_code(self, code: str) -> Room | None:
        """Fetch a room by its invite code.

        Args:
            code: The 8-character invite code.

        Returns:
            Room instance or None.
        """
        result = await self.db.execute(select(Room).where(Room.invite_code == code))
        return result.scalar_one_or_none()

    async def list_accessible(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        search: str | None = None,
        filter_type: str = "all",
    ) -> tuple[list[Room], int]:
        """List rooms accessible to a user: public + joined.

        Args:
            user_id: The requesting user's UUID string.
            skip: Pagination offset.
            limit: Maximum rooms to return.
            search: Optional name search string.
            filter_type: 'all', 'owned', or 'joined'.

        Returns:
            Tuple of (room list, total count).
        """
        member_subq = select(room_members.c.room_id).where(room_members.c.user_id == user_id)

        if filter_type == "owned":
            condition = Room.owner_id == user_id
        elif filter_type == "joined":
            condition = and_(Room.id.in_(member_subq), Room.owner_id != user_id)
        else:
            condition = or_(Room.is_public == True, Room.id.in_(member_subq))  # noqa: E712

        base_q = select(Room).options(selectinload(Room.owner)).where(condition)
        if search:
            base_q = base_q.where(Room.name.ilike(f"%{search}%"))

        count_result = await self.db.execute(select(func.count()).select_from(base_q.subquery()))
        total = count_result.scalar_one() or 0

        result = await self.db.execute(
            base_q.order_by(Room.created_at.desc()).offset(skip).limit(limit)
        )
        return list(result.scalars().all()), total

    async def is_member(self, room_id: str, user_id: str) -> bool:
        """Check if a user is a member of the room.

        Args:
            room_id: Room UUID string.
            user_id: User UUID string.

        Returns:
            True if the user is a member.
        """
        result = await self.db.execute(
            select(func.count())
            .select_from(room_members)
            .where(
                and_(
                    room_members.c.room_id == room_id,
                    room_members.c.user_id == user_id,
                )
            )
        )
        return (result.scalar_one() or 0) > 0

    async def add_member(self, room_id: str, user_id: str) -> None:
        """Add a user to a room's member list.

        Args:
            room_id: Room UUID string.
            user_id: User UUID string.
        """
        await self.db.execute(room_members.insert().values(room_id=room_id, user_id=user_id))
        await self.db.flush()

    async def remove_member(self, room_id: str, user_id: str) -> None:
        """Remove a user from a room's member list.

        Args:
            room_id: Room UUID string.
            user_id: User UUID string.
        """
        await self.db.execute(
            room_members.delete().where(
                and_(
                    room_members.c.room_id == room_id,
                    room_members.c.user_id == user_id,
                )
            )
        )
        await self.db.flush()

    async def get_member_count(self, room_id: str) -> int:
        """Count members of a room.

        Args:
            room_id: Room UUID string.

        Returns:
            Number of members.
        """
        result = await self.db.execute(
            select(func.count()).select_from(room_members).where(room_members.c.room_id == room_id)
        )
        return result.scalar_one() or 0
