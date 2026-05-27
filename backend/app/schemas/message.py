"""Message Pydantic schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.constants import MessageType


class MessageCreate(BaseModel):
    """Payload for creating a chat message."""

    content: str = Field(min_length=1, max_length=2000)
    message_type: MessageType = MessageType.CHAT


class MessageResponse(BaseModel):
    """Chat message returned from API or WebSocket."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    room_id: uuid.UUID
    user_id: uuid.UUID
    content: str
    message_type: MessageType
    sent_at: datetime
    username: str = ""
    display_name: str = ""
