"""
User schemas - Profile, Social accounts.
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field, HttpUrl


# ==================================================
#  Responses
# ==================================================

class UserResponse(BaseModel):
    """Basic user info (used in auth responses)."""
    id: str
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_email_verified: bool
    has_password: bool
    referral_code: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SocialAccountResponse(BaseModel):
    """Social account info."""
    id: str
    provider: str
    email: EmailStr
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    """Full user profile with social accounts."""
    id: str
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_email_verified: bool
    has_password: bool
    referral_code: Optional[str] = None
    referred_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    social_accounts: List[SocialAccountResponse] = []

    class Config:
        from_attributes = True


class LinkedAccountsResponse(BaseModel):
    """Summary of linked login methods."""
    has_password: bool
    providers: List[str]  # ["google", "github", "discord"]
    total_social_accounts: int


# ==================================================
#  Requests
# ==================================================

class UpdateProfileRequest(BaseModel):
    """Update user profile."""
    full_name: Optional[str] = Field(None, max_length=255)
    avatar_url: Optional[str] = Field(None, max_length=500)


class ChangeEmailRequest(BaseModel):
    """Request email change."""
    new_email: EmailStr
    password: str  # Require password to change email


class DeleteAccountRequest(BaseModel):
    """Delete account confirmation."""
    password: Optional[str] = None  # Required if has_password
    confirmation: str = Field(..., pattern=r"^DELETE$")  # Must type "DELETE"