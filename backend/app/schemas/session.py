"""StudySession Pydantic schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StudySessionResponse(BaseModel):
    """Full study session data."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    room_id: uuid.UUID
    started_by: uuid.UUID
    started_at: datetime
    ended_at: datetime | None
    duration_seconds: int | None
    is_active: bool


class UserSessionStats(BaseModel):
    """Aggregated session statistics for the current user."""

    total_sessions: int
    total_study_seconds: int
    sessions_this_week: int
    average_session_seconds: int
    longest_session_seconds: int
