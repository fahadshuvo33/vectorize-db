from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel
from app.models.enums.support import TicketCategory, TicketStatus, TicketPriority, SenderType

# ==========================================
# MESSAGE SCHEMAS
# ==========================================
class TicketMessageBase(SQLModel):
    message: str
    attachments: Optional[List[str]] = None

class TicketMessageCreate(TicketMessageBase):
    # Sender info is handled by backend based on logged in user
    pass

class TicketMessageRead(TicketMessageBase):
    id: str
    sender_type: SenderType
    created_at: datetime
    # We might want to show sender name if it's an agent

# ==========================================
# TICKET SCHEMAS
# ==========================================
class SupportTicketBase(SQLModel):
    subject: str
    category: TicketCategory
    priority: TicketPriority = TicketPriority.MEDIUM

class SupportTicketCreate(SupportTicketBase):
    # Initial message to start the thread
    initial_message: str

class SupportTicketUpdate(SQLModel):
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None

class SupportTicketRead(SupportTicketBase):
    id: str
    status: TicketStatus
    created_at: datetime
    last_activity_at: datetime

# ==========================================
# CHAT VIEW (Ticket + Messages)
# ==========================================
class SupportTicketChatRead(SupportTicketRead):
    # This includes the conversation history
    messages: List[TicketMessageRead] = []

# ==========================================
# APP REVIEW SCHEMAS
# ==========================================
class AppReviewCreate(SQLModel):
    rating: int
    comment: Optional[str] = None

class AppReviewRead(AppReviewCreate):
    id: str
    user_id: str
    created_at: datetime