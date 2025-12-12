from typing import Optional, List, Dict, TYPE_CHECKING
from sqlmodel import Field, Relationship, Index, JSON
from sqlalchemy import Column, Enum

from app.models.base import BaseModel
from app.models.enums.notification import NotificationType, NotificationCategory, EmailStatus
if TYPE_CHECKING:
    from app.models.user import Profile

# -------------------------------------------
# 1. TEMPLATES (The Blueprints)
# -------------------------------------------
class NotificationTemplate(BaseModel, table=True):
    """
    Stores text templates with placeholders.
    Example Slug: 'subscription_success'
    Example Body: 'Hi {name}, you have successfully subscribed to {plan}.'
    """
    __tablename__ = "notification_templates"
    __table_args__ = (
        Index("idx_template_slug", "slug", "type", unique=True),
    )

    slug: str = Field(max_length=50, description="Unique key to identify template in code")
    type: NotificationType = Field(sa_column=Column(Enum(NotificationType), nullable=False))
    category: NotificationCategory = Field(sa_column=Column(Enum(NotificationCategory), default=NotificationCategory.SYSTEM))
    
    # For Emails
    subject_template: Optional[str] = Field(default=None, max_length=255)
    
    # For Emails (HTML) and In-App (Text)
    body_template: str = Field(description="Content with {{variable}} placeholders")
    
    is_active: bool = Field(default=True)


# -------------------------------------------
# 2. IN-APP NOTIFICATIONS (User's Inbox)
# -------------------------------------------
class InAppNotification(BaseModel, table=True):
    """
    The actual notifications displayed in the user's dashboard bell icon.
    """
    __tablename__ = "in_app_notifications"
    __table_args__ = (
        Index("idx_notif_user_read", "user_id", "is_read"),
    )

    user_id: str = Field(foreign_key="profiles.id", max_length=50)
    
    category: NotificationCategory = Field(sa_column=Column(Enum(NotificationCategory), nullable=False))
    
    title: str = Field(max_length=100)
    message: str = Field(description="The rendered message")
    
    # Action link (e.g., clicking takes them to billing page)
    action_link: Optional[str] = Field(default=None, max_length=255)
    
    is_read: bool = Field(default=False)
    read_at: Optional[str] = None # Using string ISO format or datetime if preferred
    
    # Metadata for frontend logic (e.g., icon color, specific ID reference)
    data: Optional[Dict] = Field(default=None, sa_type=JSON)

    # Relationships
    user: "Profile" = Relationship() # Add back_populates="notifications" in user.py if needed


# -------------------------------------------
# 3. EMAIL LOGS (Audit Trail)
# -------------------------------------------
class EmailLog(BaseModel, table=True):
    """
    Keeps track of every email sent to avoid disputes and for debugging.
    """
    __tablename__ = "email_logs"
    
    user_id: str = Field(foreign_key="profiles.id", max_length=50)
    template_id: Optional[str] = Field(default=None, foreign_key="notification_templates.id")
    
    recipient_email: str = Field(max_length=255)
    subject: str = Field(max_length=255)
    
    status: EmailStatus = Field(sa_column=Column(Enum(EmailStatus), default=EmailStatus.PENDING))
    
    # IMPORTANT: The JSON context used to fill the template
    # Example: {"name": "John", "plan": "Pro", "amount": "$50"}
    context_data: Optional[Dict] = Field(default=None, sa_type=JSON)
    
    provider_response: Optional[Dict] = Field(default=None, sa_type=JSON, description="Response from SendGrid/AWS")
    error_message: Optional[str] = None
    
    sent_at: Optional[str] = None

    # Relationships
    user: "Profile" = Relationship()