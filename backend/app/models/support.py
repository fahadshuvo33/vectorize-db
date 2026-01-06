from typing import Optional, List, Dict, TYPE_CHECKING
from datetime import datetime
from sqlmodel import Field, Relationship, Index, JSON
from sqlalchemy import Column, Enum

from app.models.base import BaseModel
from app.models.enums import TicketCategory, TicketPriority, TicketStatus, SenderType
from app.utils import utc_now

if TYPE_CHECKING:
    from app.models.user import Profile
    from app.models.enums import TicketPriority



# -------------------------------------------
# 1. SUPPORT TICKET (The Chat Thread)
# -------------------------------------------
class SupportTicket(BaseModel, table=True):
    __tablename__ = "support_tickets"
    __table_args__ = (
        Index("idx_ticket_user", "user_id"),
        Index("idx_ticket_status", "status"),
    )

    user_id: str = Field(foreign_key="profiles.id", max_length=50)
    
    subject: str = Field(max_length=255)
    category: TicketCategory = Field(sa_column=Column(Enum(TicketCategory), default=TicketCategory.GENERAL))
    status: TicketStatus = Field(sa_column=Column(Enum(TicketStatus), default=TicketStatus.OPEN))
    priority: TicketPriority = Field(sa_column=Column(Enum(TicketPriority), default=TicketPriority.MEDIUM))
    
    # Optional: Assign to a specific admin
    assigned_to: Optional[str] = Field(default=None, max_length=50) 
    
    last_activity_at: datetime = Field(default_factory=utc_now)
    
    # Relationships
    user: "Profile" = Relationship(back_populates="support_tickets")
    messages: List["TicketMessage"] = Relationship(back_populates="ticket")


# -------------------------------------------
# 2. TICKET MESSAGES (The Chat Bubbles)
# -------------------------------------------
class TicketMessage(BaseModel, table=True):
    __tablename__ = "ticket_messages"
    
    ticket_id: str = Field(foreign_key="support_tickets.id", max_length=50)
    sender_id: str = Field(max_length=50) # Can be Profile ID or Admin ID
    sender_type: SenderType = Field(sa_column=Column(Enum(SenderType), nullable=False))
    
    message: str = Field(description="Content of the message")
    
    # Attachments (List of URLs)
    attachments: Optional[List[str]] = Field(default=None, sa_type=JSON)
    
    is_internal: bool = Field(default=False, description="If true, only admins see this")
    read_at: Optional[datetime] = None

    # Relationship
    ticket: SupportTicket = Relationship(back_populates="messages")


# -------------------------------------------
# 3. APP REVIEW (Public/Private Feedback)
# -------------------------------------------
class AppReview(BaseModel, table=True):
    __tablename__ = "app_reviews"
    
    user_id: str = Field(foreign_key="profiles.id", max_length=50)
    
    rating: int = Field(description="1 to 5 stars")
    comment: Optional[str] = Field(default=None, max_length=1000)
    
    # If users suggest a feature here, you can link it to a ticket later manually
    is_public: bool = Field(default=True)
    
    user: "Profile" = Relationship()