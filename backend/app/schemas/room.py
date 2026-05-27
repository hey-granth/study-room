"""Room Pydantic schemas."""

import uuid

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserResponse


class RoomCreate(BaseModel):
    """Payload for creating a new room."""

    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    is_public: bool = True
    max_participants: int = Field(default=20, ge=2, le=100)


class RoomUpdate(BaseModel):
    """Payload for updating room metadata (owner only)."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    is_public: bool | None = None
    max_participants: int | None = Field(None, ge=2, le=100)


class RoomSummary(BaseModel):
    """Lightweight room info for list views."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None
    is_public: bool
    max_participants: int
    invite_code: str
    owner_id: uuid.UUID
    member_count: int = 0
    has_active_session: bool = False


class RoomDetail(BaseModel):
    """Full room info including members."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None
    is_public: bool
    max_participants: int
    invite_code: str
    owner_id: uuid.UUID
    owner: UserResponse
    members: list[UserResponse]
    member_count: int = 0


class PresenceUser(BaseModel):
    """A user currently present in a room (from Redis)."""

    user_id: str
    username: str
    display_name: str
    avatar_url: str | None = None
    joined_at: str


class InviteCodeResponse(BaseModel):
    """Response containing a new invite code."""

    invite_code: str
