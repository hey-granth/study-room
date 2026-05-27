"""Study session API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import WSMessageType
from app.core.ws_manager import make_ws_message, manager
from app.db.base import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import Page
from app.schemas.session import StudySessionResponse, UserSessionStats
from app.services.session import SessionService

router = APIRouter()


@router.post("/rooms/{room_id}/start", response_model=StudySessionResponse, status_code=201)
async def start_session(
    room_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> StudySessionResponse:
    """Start a study session in a room. Only one active session is allowed."""
    svc = SessionService(db)
    session = await svc.start_session(room_id, str(current_user.id))

    # Broadcast to room
    await manager.broadcast_to_room(
        room_id,
        make_ws_message(
            WSMessageType.SESSION_STARTED,
            {
                "session_id": str(session.id),
                "started_by": str(current_user.id),
                "started_at": session.started_at.isoformat(),
            },
        ),
    )
    return session


@router.post("/rooms/{room_id}/end", response_model=StudySessionResponse)
async def end_session(
    room_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> StudySessionResponse:
    """End the active study session in a room."""
    svc = SessionService(db)
    session = await svc.end_session(room_id, str(current_user.id))

    await manager.broadcast_to_room(
        room_id,
        make_ws_message(
            WSMessageType.SESSION_ENDED,
            {
                "session_id": str(session.id),
                "ended_by": str(current_user.id),
                "duration_seconds": session.duration_seconds,
            },
        ),
    )
    return session


@router.get("/rooms/{room_id}/active", response_model=StudySessionResponse | None)
async def get_active_session(
    room_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> StudySessionResponse | None:
    """Return the currently active session for a room, or null."""
    svc = SessionService(db)
    return await svc.get_active_session(room_id)


@router.get("/rooms/{room_id}/history", response_model=Page[StudySessionResponse])
async def get_session_history(
    room_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
) -> Page[StudySessionResponse]:
    """Return paginated session history for a room."""
    svc = SessionService(db)
    return await svc.get_session_history(room_id, page=page, size=size)


@router.get("/me/stats", response_model=UserSessionStats)
async def get_my_stats(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserSessionStats:
    """Return the authenticated user's aggregated session statistics."""
    svc = SessionService(db)
    return await svc.get_user_stats(str(current_user.id))
