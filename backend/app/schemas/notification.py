from typing import Optional, List, Dict
from datetime import datetime
from sqlmodel import SQLModel
from app.models.enums.notification import NotificationType, NotificationCategory, EmailStatus

# ==========================================
# 1. TEMPLATES (Admin Only)
# ==========================================
class TemplateBase(SQLModel):
    slug: str
    type: NotificationType
    category: NotificationCategory = NotificationCategory.SYSTEM
    subject_template: Optional[str] = None
    body_template: str
    is_active: bool = True

class TemplateCreate(TemplateBase):
    pass

class TemplateUpdate(SQLModel):
    subject_template: Optional[str] = None
    body_template: Optional[str] = None
    is_active: Optional[bool] = None

class TemplateRead(TemplateBase):
    id: str
    created_at: datetime

# ==========================================
# 2. IN-APP NOTIFICATIONS (User Facing)
# ==========================================
class InAppNotificationRead(SQLModel):
    id: str
    category: NotificationCategory
    title: str
    message: str
    action_link: Optional[str]
    is_read: bool
    read_at: Optional[str] # Or datetime
    created_at: datetime
    data: Optional[Dict] = None

class InAppNotificationUpdate(SQLModel):
    # Used when user clicks "Mark as read"
    is_read: bool = True

# ==========================================
# 3. EMAIL LOGS (Admin/Debug)
# ==========================================
class EmailLogRead(SQLModel):
    id: str
    recipient_email: str
    subject: str
    status: EmailStatus
    sent_at: Optional[str]
    created_at: datetime
    error_message: Optional[str]