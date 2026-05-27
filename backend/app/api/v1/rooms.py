"""Room CRUD and membership API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import Page
from app.schemas.room import (
    InviteCodeResponse,
    PresenceUser,
    RoomCreate,
    RoomDetail,
    RoomSummary,
    RoomUpdate,
)
from app.services.presence import PresenceService
from app.services.room import RoomService

router = APIRouter()


@router.get("/", response_model=Page[RoomSummary])
async def list_rooms(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None),
    filter_type: str = Query(default="all", pattern="^(all|owned|joined)$"),
) -> Page[RoomSummary]:
    """List accessible rooms (public + joined) with optional filters."""
    svc = RoomService(db)
    return await svc.list_rooms(
        user_id=str(current_user.id),
        page=page,
        size=size,
        search=search,
        filter_type=filter_type,
    )


@router.post("/", response_model=RoomDetail, status_code=201)
async def create_room(
    schema: RoomCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RoomDetail:
    """Create a new study room."""
    svc = RoomService(db)
    return await svc.create_room(schema, str(current_user.id))


@router.get("/{room_id}", response_model=RoomDetail)
async def get_room(
    room_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RoomDetail:
    """Fetch full room details including members."""
    svc = RoomService(db)
    return await svc.get_room(room_id)


@router.patch("/{room_id}", response_model=RoomDetail)
async def update_room(
    room_id: str,
    schema: RoomUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RoomDetail:
    """Update room metadata. Owner only."""
    svc = RoomService(db)
    return await svc.update_room(room_id, schema, str(current_user.id))


@router.delete("/{room_id}", status_code=204)
async def delete_room(
    room_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a room. Owner only."""
    svc = RoomService(db)
    await svc.delete_room(room_id, str(current_user.id))


@router.post("/{room_id}/join", response_model=RoomDetail)
async def join_room(
    room_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RoomDetail:
    """Join a public room directly."""
    svc = RoomService(db)
    return await svc.join_room(room_id, str(current_user.id))


@router.post("/join/invite/{invite_code}", response_model=RoomDetail)
async def join_by_invite(
    invite_code: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RoomDetail:
    """Join a room using an invite code."""
    svc = RoomService(db)
    return await svc.join_by_invite_code(invite_code, str(current_user.id))


@router.delete("/{room_id}/leave", status_code=204)
async def leave_room(
    room_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Leave a room."""
    svc = RoomService(db)
    await svc.leave_room(room_id, str(current_user.id))


@router.post("/{room_id}/invite/regenerate", response_model=InviteCodeResponse)
async def regenerate_invite(
    room_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> InviteCodeResponse:
    """Generate a new invite code for a room. Owner only."""
    svc = RoomService(db)
    code = await svc.regenerate_invite_code(room_id, str(current_user.id))
    return InviteCodeResponse(invite_code=code)


@router.get("/{room_id}/participants", response_model=list[PresenceUser])
async def get_participants(
    room_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[PresenceUser]:
    """Return the list of users currently online in a room."""
    svc = PresenceService()
    return await svc.get_room_participants(room_id)
