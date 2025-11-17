from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, UUID4, Field
from .enums import (
    TicketStatus, TicketPriority, TicketCategory,
    EmailStatus, NotificationType
)

# ============================================
# SUPPORT TICKETS
# ============================================
class SupportTicketBase(BaseModel):
    subject: str = Field(min_length=5, max_length=200)
    description: str = Field(min_length=10, max_length=5000)
    priority: TicketPriority = TicketPriority.MEDIUM
    category: TicketCategory

class SupportTicketCreate(SupportTicketBase):
    user_id: UUID4

class SupportTicketUpdate(BaseModel):
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    assigned_to: Optional[UUID4] = None

class SupportTicketInDB(SupportTicketBase):
    id: UUID4
    user_id: UUID4
    status: TicketStatus = TicketStatus.OPEN
    assigned_to: Optional[UUID4] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ============================================
# SUPPORT TICKET MESSAGES
# ============================================
class SupportTicketMessageInDB(SupportTicketMessageBase):
    id: UUID4
    ticket_id: UUID4
    user_id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True

# ============================================
# NOTIFICATIONS
# ============================================
class NotificationBase(BaseModel):
    type: NotificationType
    title: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1, max_length=1000)
    action_url: Optional[str] = None
    action_label: Optional[str] = None

class NotificationCreate(NotificationBase):
    user_id: UUID4

class NotificationUpdate(BaseModel):
    read: bool

class NotificationInDB(NotificationBase):
    id: UUID4
    user_id: UUID4
    read: bool = False
    created_at: datetime

    class Config:
        from_attributes = True

# ============================================
# EMAIL TEMPLATES
# ============================================
class EmailTemplateBase(BaseModel):
    name: str
    slug: str = Field(pattern=r'^[a-z_]+$')
    subject: str
    body_html: str
    body_text: str
    variables: Optional[dict] = None
    category: str
    is_active: bool = True

class EmailTemplateCreate(EmailTemplateBase):
    pass

class EmailTemplateUpdate(BaseModel):
    subject: Optional[str] = None
    body_html: Optional[str] = None
    body_text: Optional[str] = None
    is_active: Optional[bool] = None

class EmailTemplateInDB(EmailTemplateBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ============================================
# NOTIFICATION TEMPLATES
# ============================================
class NotificationTemplateBase(BaseModel):
    name: str
    slug: str = Field(pattern=r'^[a-z_]+$')
    type: NotificationType
    title_template: str
    message_template: str
    action_url_template: Optional[str] = None
    action_label: Optional[str] = None
    variables: Optional[dict] = None
    is_active: bool = True

class NotificationTemplateCreate(NotificationTemplateBase):
    pass

class NotificationTemplateUpdate(BaseModel):
    title_template: Optional[str] = None
    message_template: Optional[str] = None
    is_active: Optional[bool] = None

class NotificationTemplateInDB(NotificationTemplateBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ============================================
# EMAIL LOGS
# ============================================
class EmailLogBase(BaseModel):
    email_to: EmailStr
    subject: str
    status: EmailStatus = EmailStatus.PENDING

class EmailLogCreate(EmailLogBase):
    user_id: UUID4
    template_id: Optional[UUID4] = None
    provider_id: Optional[str] = None

class EmailLogUpdate(BaseModel):
    status: Optional[EmailStatus] = None
    error_message: Optional[str] = None
    sent_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None

class EmailLogInDB(EmailLogBase):
    id: UUID4
    user_id: UUID4
    template_id: Optional[UUID4] = None
    provider_id: Optional[str] = None
    error_message: Optional[str] = None
    sent_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

# ============================================
# BLOG POSTS
# ============================================
class BlogPostBase(BaseModel):
    slug: str = Field(pattern=r'^[a-z0-9-]+$')
    title: str = Field(min_length=5, max_length=200)
    content_html: str
    excerpt: Optional[str] = Field(None, max_length=500)
    published: bool = False

class BlogPostCreate(BlogPostBase):
    author_id: UUID4

class BlogPostUpdate(BaseModel):
    title: Optional[str] = None
    content_html: Optional[str] = None
    excerpt: Optional[str] = None
    published: Optional[bool] = None
    published_at: Optional[datetime] = None

class BlogPostInDB(BlogPostBase):
    id: UUID4
    author_id: UUID4
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True