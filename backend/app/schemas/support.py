from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, UUID4, Field
from app.models.enums import (
    TicketStatus, TicketPriority, TicketCategory,
    NotificationType
)

# ============================================
# SUPPORT REQUESTS
# ============================================
class CreateTicketRequest(BaseModel):
    subject: str = Field(min_length=5, max_length=200)
    description: str = Field(min_length=10, max_length=5000)
    category: TicketCategory
    priority: TicketPriority = TicketPriority.MEDIUM

class ReplyTicketRequest(BaseModel):
    message: str = Field(min_length=1, max_length=5000)

class UpdateTicketRequest(BaseModel):
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None

# ============================================
# SUPPORT RESPONSES
# ============================================
class TicketResponse(BaseModel):
    id: UUID4
    subject: str
    status: TicketStatus
    priority: TicketPriority
    category: TicketCategory
    message_count: int
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None

class TicketMessageResponse(BaseModel):
    id: UUID4
    message: str
    is_staff_reply: bool
    created_at: datetime
    author_name: Optional[str] = None
    attachments: Optional[dict] = None

class TicketDetailResponse(BaseModel):
    ticket: TicketResponse
    messages: List[TicketMessageResponse]

class TicketListResponse(BaseModel):
    tickets: List[TicketResponse]
    total: int
    open_count: int
    resolved_count: int

# ============================================
# NOTIFICATION RESPONSES
# ============================================
class NotificationResponse(BaseModel):
    id: UUID4
    type: NotificationType
    title: str
    message: str
    read: bool
    action_url: Optional[str] = None
    action_label: Optional[str] = None
    created_at: datetime

class NotificationCountResponse(BaseModel):
    total: int
    unread: int

class MarkNotificationReadRequest(BaseModel):
    notification_ids: List[str]  # UUIDs as strings

# ============================================
# EMAIL RESPONSES
# ============================================
class EmailTemplateResponse(BaseModel):
    id: UUID4
    name: str
    slug: str
    subject: str
    category: str
    variables: Optional[dict] = None
    is_active: bool

class EmailLogResponse(BaseModel):
    id: UUID4
    email_to: str
    subject: str
    status: str
    sent_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime