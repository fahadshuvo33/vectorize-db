from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, HttpUrl, UUID4, Field
from .enums import PlanType

# ============================================
# PROFILES
# ============================================
class ProfileBase(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None

class ProfileCreate(ProfileBase):
    id: UUID4  # Must match auth.users.id

class ProfileUpdate(ProfileBase):
    pass

class ProfileInDB(ProfileBase):
    id: UUID4
    current_plan: PlanType = PlanType.BASIC
    plan_ends_at: Optional[datetime] = None
    referral_code: Optional[str] = None
    referred_by: Optional[UUID4] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ============================================
# SOCIAL LOGINS
# ============================================
class SocialLoginBase(BaseModel):
    provider: str  # google, github, etc.
    provider_id: str
    email: EmailStr
    name: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None

class SocialLoginCreate(SocialLoginBase):
    user_id: UUID4
    access_token: str
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    raw_data: Optional[dict] = None

class SocialLoginInDB(SocialLoginBase):
    id: UUID4
    user_id: UUID4
    access_token: str
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    raw_data: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True

# ============================================
# USAGE STATS
# ============================================
class UsageStatsBase(BaseModel):
    conversions_used: int = 0
    chats_used: int = 0
    api_requests: int = 0
    app_bot_messages: int = 0

class UsageStatsCreate(UsageStatsBase):
    user_id: UUID4
    date: datetime

class UsageStatsUpdate(UsageStatsBase):
    pass

class UsageStatsInDB(UsageStatsBase):
    id: UUID4
    user_id: UUID4
    date: datetime
    updated_at: datetime

    class Config:
        from_attributes = True