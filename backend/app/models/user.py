"""User ORM model."""

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDMixin


class User(Base, UUIDMixin, TimestampMixin):
    """Represents a registered user in the platform."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships (back-populated)
    owned_rooms: Mapped[list["Room"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Room", back_populates="owner", foreign_keys="Room.owner_id"
    )
    rooms: Mapped[list["Room"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Room", secondary="room_members", back_populates="members"
    )
    sessions_started: Mapped[list["StudySession"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "StudySession", back_populates="starter"
    )
    messages: Mapped[list["Message"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Message", back_populates="user"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username}>"
