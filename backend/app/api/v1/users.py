"""User profile API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.repositories.user import UserRepository
from app.repositories.session import SessionRepository
from app.schemas.user import UserResponse, UserStats, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    """Return the currently authenticated user's profile."""
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
async def update_me(
    schema: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    """Update the currently authenticated user's profile fields."""
    repo = UserRepository(db)
    updates = schema.model_dump(exclude_none=True)
    updated = await repo.update(current_user, updates)
    return UserResponse.model_validate(updated)


@router.get("/{user_id}/stats", response_model=UserStats)
async def get_user_stats(
    user_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserStats:
    """Return aggregated study statistics for a user."""
    session_repo = SessionRepository(db)
    total_seconds = await session_repo.get_user_total_seconds(user_id)
    sessions_week = await session_repo.get_sessions_this_week(user_id)
    _, total_sessions = await session_repo.get_multi(skip=0, limit=1)

    return UserStats(
        user_id=user_id,
        total_sessions=total_sessions,
        total_study_seconds=total_seconds,
        rooms_joined=0,
        sessions_this_week=sessions_week,
        streak_days=0,
    )
