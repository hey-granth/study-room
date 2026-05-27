"""StudySession ORM model."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDMixin


class StudySession(Base, UUIDMixin, TimestampMixin):
    """Represents a timed study session within a room."""

    __tablename__ = "study_sessions"

    room_id: Mapped[uuid.UUID] = mapped_column(
        String(36), ForeignKey("rooms.id", ondelete="CASCADE"), index=True, nullable=False
    )
    started_by: Mapped[uuid.UUID] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)

    # Relationships
    room: Mapped["Room"] = relationship("Room", back_populates="sessions")  # type: ignore[name-defined]  # noqa: F821
    starter: Mapped["User"] = relationship("User", back_populates="sessions_started")  # type: ignore[name-defined]  # noqa: F821

    def __repr__(self) -> str:
        return f"<StudySession id={self.id} room_id={self.room_id} active={self.is_active}>"
