from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, UUID4, Field
from app.models.enums import SessionType, MessageRole

# ============================================
# CHAT REQUESTS
# ============================================
class StartChatRequest(BaseModel):
    converted_file_id: str  # UUID as string
    session_type: SessionType = SessionType.USER

class SendMessageRequest(BaseModel):
    session_id: str  # UUID as string
    message: str = Field(min_length=1, max_length=2000)

class UpdateChatTitleRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)

# ============================================
# CHAT RESPONSES
# ============================================
class ChatSessionResponse(BaseModel):
    session_id: UUID4
    session_type: SessionType
    title: Optional[str] = None
    message_count: int
    expires_at: datetime
    time_remaining_seconds: int
    messages_remaining: Optional[int] = None  # For free tier
    is_expired: bool
    created_at: datetime
    last_active: datetime

class ChatMessageResponse(BaseModel):
    id: UUID4
    role: MessageRole
    content: str
    created_at: datetime

class SendMessageResponse(BaseModel):
    """Response after sending a message"""
    message: ChatMessageResponse
    session: ChatSessionResponse
    upgrade_required: bool = False
    upgrade_reason: Optional[str] = None

class ChatHistoryResponse(BaseModel):
    session: ChatSessionResponse
    messages: List[ChatMessageResponse]

class ChatListResponse(BaseModel):
    """List of user's chat sessions"""
    sessions: List[ChatSessionResponse]
    total: int