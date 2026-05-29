"""Message ORM model."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import UUIDMixin
from app.constants import MessageType


class Message(Base, UUIDMixin):
    """Represents a chat or system message in a room."""

    __tablename__ = "messages"
    __table_args__ = (Index("ix_messages_room_sent", "room_id", "sent_at"),)

    room_id: Mapped[uuid.UUID] = mapped_column(
        String(36), ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    message_type: Mapped[MessageType] = mapped_column(
        Enum(MessageType), default=MessageType.CHAT, nullable=False
    )
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    room: Mapped["Room"] = relationship("Room", back_populates="messages")  # type: ignore[name-defined]  # noqa: F821
    user: Mapped["User"] = relationship("User", back_populates="messages")  # type: ignore[name-defined]  # noqa: F821

    def __repr__(self) -> str:
        return f"<Message id={self.id} room_id={self.room_id} type={self.message_type}>"
