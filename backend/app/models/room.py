"""Room ORM model and room_members association table."""

import uuid

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDMixin

# Association table for Room ↔ User many-to-many
room_members = Table(
    "room_members",
    Base.metadata,
    Column("room_id", String(36), ForeignKey("rooms.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)


class Room(Base, UUIDMixin, TimestampMixin):
    """Represents a collaborative study room."""

    __tablename__ = "rooms"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    invite_code: Mapped[str] = mapped_column(
        String(8), unique=True, index=True, nullable=False
    )
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    max_participants: Mapped[int] = mapped_column(Integer, default=20, nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    # Relationships
    owner: Mapped["User"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "User", back_populates="owned_rooms", foreign_keys=[owner_id]
    )
    members: Mapped[list["User"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "User", secondary=room_members, back_populates="rooms"
    )
    sessions: Mapped[list["StudySession"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "StudySession", back_populates="room", order_by="StudySession.started_at.desc()"
    )
    messages: Mapped[list["Message"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Message", back_populates="room"
    )

    def __repr__(self) -> str:
        return f"<Room id={self.id} name={self.name}>"
