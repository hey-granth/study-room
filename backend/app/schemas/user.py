"""User Pydantic schemas."""

import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserResponse(BaseModel):
    """Public user data returned from API."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    username: str
    display_name: str
    avatar_url: str | None
    is_active: bool


class UserUpdate(BaseModel):
    """Fields a user may update on their profile."""

    display_name: str | None = Field(None, min_length=1, max_length=100)
    avatar_url: str | None = Field(None, max_length=500)


class UserStats(BaseModel):
    """Aggregated statistics for a user."""

    user_id: uuid.UUID
    total_sessions: int
    total_study_seconds: int
    rooms_joined: int
    sessions_this_week: int
    streak_days: int


class UserWithToken(BaseModel):
    """User data combined with a token pair (returned on register/login)."""

    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
