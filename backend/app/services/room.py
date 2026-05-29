"""Room business logic service."""

import logging
import random
import string
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import INVITE_CODE_CHARS, INVITE_CODE_LENGTH
from app.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError
from app.models.room import Room
from app.repositories.room import RoomRepository
from app.schemas.common import Page
from app.schemas.room import RoomCreate, RoomDetail, RoomSummary, RoomUpdate
from app.schemas.user import UserResponse

logger = logging.getLogger(__name__)


def _generate_invite_code() -> str:
    """Generate a random 8-character alphanumeric invite code."""
    return "".join(random.choices(INVITE_CODE_CHARS, k=INVITE_CODE_LENGTH))


class RoomService:
    """Handles all room lifecycle operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = RoomRepository(db)

    async def create_room(self, schema: RoomCreate, owner_id: str) -> RoomDetail:
        """Create a new room and add the owner as a member.

        Args:
            schema: Room creation payload.
            owner_id: UUID of the creating user.

        Returns:
            Fully-populated RoomDetail.
        """
        code = _generate_invite_code()
        # Ensure uniqueness
        while await self.repo.get_by_invite_code(code) is not None:
            code = _generate_invite_code()

        room = Room(
            id=str(uuid.uuid4()),
            name=schema.name,
            description=schema.description,
            is_public=schema.is_public,
            max_participants=schema.max_participants,
            owner_id=owner_id,
            invite_code=code,
        )
        room = await self.repo.create(room)
        # Auto-join as member
        await self.repo.add_member(str(room.id), owner_id)

        room = await self.repo.get_with_members(str(room.id))
        assert room is not None
        return self._to_detail(room)

    async def get_room(self, room_id: str) -> RoomDetail:
        """Fetch full room details.

        Args:
            room_id: UUID of the room.

        Returns:
            RoomDetail.

        Raises:
            NotFoundError: If the room does not exist.
        """
        room = await self.repo.get_with_members(room_id)
        if not room:
            raise NotFoundError("Room")
        return self._to_detail(room)

    async def list_rooms(
        self,
        user_id: str,
        page: int = 1,
        size: int = 20,
        search: str | None = None,
        filter_type: str = "all",
    ) -> Page[RoomSummary]:
        """List accessible rooms with pagination.

        Args:
            user_id: Requesting user's ID.
            page: Page number (1-indexed).
            size: Results per page.
            search: Optional name filter.
            filter_type: 'all', 'owned', 'joined'.

        Returns:
            Paginated page of RoomSummary.
        """
        skip = (page - 1) * size
        rooms, total = await self.repo.list_accessible(
            user_id=user_id, skip=skip, limit=size, search=search, filter_type=filter_type
        )
        summaries = [
            RoomSummary(
                id=room.id,
                name=room.name,
                description=room.description,
                is_public=room.is_public,
                max_participants=room.max_participants,
                invite_code=room.invite_code,
                owner_id=room.owner_id,
                member_count=await self.repo.get_member_count(str(room.id)),
            )
            for room in rooms
        ]
        return Page.create(items=summaries, total=total, page=page, size=size)

    async def update_room(self, room_id: str, schema: RoomUpdate, user_id: str) -> RoomDetail:
        """Update room metadata (owner only).

        Args:
            room_id: UUID of the room.
            schema: Update payload.
            user_id: Requesting user's ID.

        Returns:
            Updated RoomDetail.

        Raises:
            NotFoundError: If room not found.
            ForbiddenError: If user is not the owner.
        """
        room = await self.repo.get_with_members(room_id)
        if not room:
            raise NotFoundError("Room")
        if str(room.owner_id) != user_id:
            raise ForbiddenError("Only the room owner can update the room")

        updates = schema.model_dump(exclude_none=True)
        room = await self.repo.update(room, updates)
        room = await self.repo.get_with_members(str(room.id))
        assert room is not None
        return self._to_detail(room)

    async def delete_room(self, room_id: str, user_id: str) -> None:
        """Delete a room (owner only).

        Args:
            room_id: UUID of the room.
            user_id: Requesting user's ID.

        Raises:
            NotFoundError: If room not found.
            ForbiddenError: If user is not the owner.
        """
        room = await self.repo.get(room_id)
        if not room:
            raise NotFoundError("Room")
        if str(room.owner_id) != user_id:
            raise ForbiddenError("Only the room owner can delete the room")
        await self.repo.delete(room)

    async def join_room(self, room_id: str, user_id: str) -> RoomDetail:
        """Join a public room directly.

        Args:
            room_id: UUID of the room.
            user_id: Requesting user's ID.

        Returns:
            RoomDetail of joined room.

        Raises:
            NotFoundError: Room not found or not public.
            ConflictError: Already a member.
            ValidationError: Room is full.
        """
        room = await self.repo.get_with_members(room_id)
        if not room or not room.is_public:
            raise NotFoundError("Room")

        if await self.repo.is_member(room_id, user_id):
            raise ConflictError("You are already a member of this room")

        member_count = await self.repo.get_member_count(room_id)
        if member_count >= room.max_participants:
            raise ValidationError("Room is full")

        await self.repo.add_member(room_id, user_id)
        self.db.expire(room, ["members"])
        room = await self.repo.get_with_members(room_id)
        assert room is not None
        return self._to_detail(room)

    async def join_by_invite_code(self, code: str, user_id: str) -> RoomDetail:
        """Join a room via invite code.

        Args:
            code: 8-character invite code.
            user_id: Requesting user's ID.

        Returns:
            RoomDetail of joined room.

        Raises:
            NotFoundError: Invalid invite code.
            ConflictError: Already a member.
            ValidationError: Room is full.
        """
        room = await self.repo.get_by_invite_code(code.upper())
        if not room:
            raise NotFoundError("Invalid invite code")

        if await self.repo.is_member(str(room.id), user_id):
            # Return current state without error if already member
            room = await self.repo.get_with_members(str(room.id))
            assert room is not None
            return self._to_detail(room)

        member_count = await self.repo.get_member_count(str(room.id))
        if member_count >= room.max_participants:
            raise ValidationError("Room is full")

        await self.repo.add_member(str(room.id), user_id)
        self.db.expire(room, ["members"])
        room = await self.repo.get_with_members(str(room.id))
        assert room is not None
        return self._to_detail(room)

    async def leave_room(self, room_id: str, user_id: str) -> None:
        """Leave a room.

        Args:
            room_id: UUID of the room.
            user_id: Requesting user's ID.

        Raises:
            NotFoundError: Room not found.
            ValidationError: Owner cannot leave their own room.
        """
        room = await self.repo.get(room_id)
        if not room:
            raise NotFoundError("Room")
        if str(room.owner_id) == user_id:
            raise ValidationError("Room owner cannot leave. Transfer ownership or delete the room.")
        await self.repo.remove_member(room_id, user_id)
        self.db.expire(room, ["members"])

    async def regenerate_invite_code(self, room_id: str, owner_id: str) -> str:
        """Regenerate the invite code for a room.

        Args:
            room_id: UUID of the room.
            owner_id: Must match room owner.

        Returns:
            New invite code string.

        Raises:
            NotFoundError: Room not found.
            ForbiddenError: User is not owner.
        """
        room = await self.repo.get(room_id)
        if not room:
            raise NotFoundError("Room")
        if str(room.owner_id) != owner_id:
            raise ForbiddenError("Only the room owner can regenerate the invite code")

        new_code = _generate_invite_code()
        while await self.repo.get_by_invite_code(new_code) is not None:
            new_code = _generate_invite_code()

        await self.repo.update(room, {"invite_code": new_code})
        return new_code

    def _to_detail(self, room: Room) -> RoomDetail:
        """Convert a Room ORM object to RoomDetail schema.

        Args:
            room: Room model with relationships loaded.

        Returns:
            RoomDetail Pydantic model.
        """
        return RoomDetail(
            id=room.id,
            name=room.name,
            description=room.description,
            is_public=room.is_public,
            max_participants=room.max_participants,
            invite_code=room.invite_code,
            owner_id=room.owner_id,
            owner=UserResponse.model_validate(room.owner),
            members=[UserResponse.model_validate(m) for m in room.members],
            member_count=len(room.members),
        )
