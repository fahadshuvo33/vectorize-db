from datetime import datetime, date
from typing import Optional, List, Dict, TYPE_CHECKING
from pydantic import EmailStr
from sqlmodel import Field, Relationship, JSON
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.subscription import (
        CustomPlan, Subscription, SubscriptionUsage, 
        UpgradeRequest, BillingHistory, InAppNotification,SupportTicket
    )

# ============================================
#  PROFILE (Public Schema)
# ============================================
class Profile(BaseModel, table=True):
    __tablename__ = "profiles"  # Standard Supabase naming convention

    # This ID is NOT generated here. It matches auth.users.id
    id: str = Field(primary_key=True, max_length=50)
    
    # We store a copy of email here for easy querying, but auth.users is the source of truth
    email: EmailStr = Field(index=True, unique=True)
    
    full_name: str = Field(default=None, max_length=255)
    avatar_url: Optional[str] = Field(default=None, max_length=500)
    
    is_email_verified: bool = Field(default=False)
    has_password: bool = Field(default=False)
    
    referral_code: Optional[str] = Field(default=None, index=True, max_length=20)
    referred_by: Optional[str] = Field(default=None, max_length=50)

    # Relationships
    social_accounts: List["SocialAccount"] = Relationship(back_populates="user")
    usage_stats: List["UsageStats"] = Relationship(back_populates="user")
    
    # Subscription Relationships
    # Note: We keep the relationship attribute name as "custom_plans" etc.
    custom_plans: List["CustomPlan"] = Relationship(back_populates="user")
    subscriptions: List["Subscription"] = Relationship(back_populates="user")
    subscription_usage: List["SubscriptionUsage"] = Relationship(back_populates="user")
    upgrade_requests: List["UpgradeRequest"] = Relationship(back_populates="user")
    billing_history: List["BillingHistory"] = Relationship(back_populates="user")
    notifications: List["InAppNotification"] = Relationship(back_populates="user")
    support_tickets: List["SupportTicket"] = Relationship(back_populates="user")


class SocialAccount(BaseModel, table=True):
    __tablename__ = "social_accounts"
    
    # Inherits id, created_at, updated_at from BaseModel
    
    # Foreign key points to profiles.id
    user_id: str = Field(foreign_key="profiles.id", index=True, max_length=50)
    
    provider: str = Field(max_length=50)
    provider_id: str = Field(max_length=255)
    email: EmailStr
    
    name: Optional[str] = Field(default=None, max_length=255)
    avatar_url: Optional[str] = Field(default=None, max_length=500)
    
    access_token: str = Field(sa_type=JSON) 
    refresh_token: Optional[str] = Field(default=None)
    token_expires_at: Optional[datetime] = None
    raw_data: Optional[Dict] = Field(default=None, sa_type=JSON)
    
    # Relationship back to Profile
    user: Optional["Profile"] = Relationship(back_populates="social_accounts")


class UsageStats(BaseModel, table=True):
    __tablename__ = "usage_stats"
    
    # Inherits id, created_at, updated_at from BaseModel
    
    user_id: str = Field(foreign_key="profiles.id", index=True, max_length=50)
    stats_date: date = Field(default_factory=date.today, index=True)
    
    conversions_used: int = Field(default=0)
    chats_used: int = Field(default=0)
    api_requests: int = Field(default=0)
    app_bot_messages: int = Field(default=0)
    
    user: Optional["Profile"] = Relationship(back_populates="usage_stats")