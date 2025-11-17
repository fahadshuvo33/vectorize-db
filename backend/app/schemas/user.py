from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, HttpUrl, UUID4, Field
from app.models.enums import PlanType

# ============================================
# AUTH REQUESTS
# ============================================
class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    full_name: Optional[str] = Field(None, max_length=100)
    referral_code: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ResetPasswordRequest(BaseModel):
    email: EmailStr

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8, max_length=100)

class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[HttpUrl] = None

# ============================================
# AUTH RESPONSES
# ============================================
class UserResponse(BaseModel):
    id: UUID4
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None
    current_plan: PlanType
    plan_ends_at: Optional[datetime] = None
    referral_code: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class ProfileResponse(UserResponse):
    """Extended user info for profile page"""
    referred_by: Optional[UUID4] = None
    total_referrals: int = 0

# ============================================
# USAGE RESPONSES
# ============================================
class UsageResponse(BaseModel):
    conversions_used: int
    conversions_limit: int
    chats_used: int
    chats_limit: int
    api_requests: int
    api_limit: int
    app_bot_messages: int
    app_bot_limit: int
    resets_at: datetime

class UsageStatsResponse(BaseModel):
    """Historical usage stats"""
    date: datetime
    conversions_used: int
    chats_used: int
    api_requests: int
    app_bot_messages: int