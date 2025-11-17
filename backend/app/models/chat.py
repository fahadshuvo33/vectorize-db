from datetime import datetime
from typing import Optional
from pydantic import BaseModel, UUID4, Field
from .enums import SessionType, MessageRole

# ============================================
# CHAT SESSIONS
# ============================================
class ChatSessionBase(BaseModel):
    session_type: SessionType
    title: Optional[str] = None
    is_visible: bool = True

class ChatSessionCreate(ChatSessionBase):
    user_id: UUID4
    converted_file_id: UUID4
    expires_at: datetime

class ChatSessionUpdate(BaseModel):
    title: Optional[str] = None
    is_visible: Optional[bool] = None

class ChatSessionInDB(ChatSessionBase):
    id: UUID4
    user_id: UUID4
    converted_file_id: UUID4
    message_count: int = 0
    expires_at: datetime
    created_at: datetime
    last_active: datetime

    class Config:
        from_attributes = True

# ============================================
# CHAT MESSAGES
# ============================================
class ChatMessageBase(BaseModel):
    role: MessageRole
    content: str = Field(min_length=1, max_length=10000)

class ChatMessageCreate(ChatMessageBase):
    session_id: UUID4

class ChatMessageInDB(ChatMessageBase):
    id: UUID4
    session_id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True