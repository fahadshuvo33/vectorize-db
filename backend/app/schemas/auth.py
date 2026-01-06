"""
Auth schemas - Registration, Login, Password management.
"""

import re
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.user import UserResponse


# ==================================================
#  Password Validator
# ==================================================

def validate_password(password: str) -> str:
    """Validate password strength."""
    errors = []
    
    if len(password) < 8:
        errors.append("at least 8 characters")
    if not re.search(r"[A-Z]", password):
        errors.append("an uppercase letter")
    if not re.search(r"[a-z]", password):
        errors.append("a lowercase letter")
    if not re.search(r"\d", password):
        errors.append("a number")
    
    if errors:
        raise ValueError(f"Password must contain {', '.join(errors)}")
    
    return password


# ==================================================
#  Requests
# ==================================================

def clean_email_str(v: str) -> str:
    """Strip whitespace and lowercase email."""
    return v.strip().lower()

# ==================================================
#  Requests
# ==================================================

class RegisterRequest(BaseModel):
    """Email/password registration."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    referral_code: Optional[str] = Field(None, max_length=20)

    # 1. ADD THIS TO FIX YOUR ERROR
    @field_validator("email")
    @classmethod
    def clean_email(cls, v):
        return clean_email_str(v)

    @field_validator("password")
    @classmethod
    def check_password(cls, v):
        return validate_password(v)


class LoginRequest(BaseModel):
    """Email/password login."""
    email: EmailStr
    password: str

    # 2. ADD THIS
    @field_validator("email")
    @classmethod
    def clean_email(cls, v):
        return clean_email_str(v)


class ForgotPasswordRequest(BaseModel):
    """Request password reset."""
    email: EmailStr

    # 3. ADD THIS
    @field_validator("email")
    @classmethod
    def clean_email(cls, v):
        return clean_email_str(v)


class ResetPasswordRequest(BaseModel):
    """Reset password with token."""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @field_validator("new_password")
    @classmethod
    def check_password(cls, v):
        return validate_password(v)


class SetPasswordRequest(BaseModel):
    """Set password for social-only account."""
    password: str = Field(..., min_length=8, max_length=100)

    @field_validator("password")
    @classmethod
    def check_password(cls, v):
        return validate_password(v)


class ChangePasswordRequest(BaseModel):
    """Change existing password."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @field_validator("new_password")
    @classmethod
    def check_password(cls, v):
        return validate_password(v)


class RefreshTokenRequest(BaseModel):
    """Refresh access token."""
    refresh_token: str


class ResendVerificationRequest(BaseModel):
    """Resend verification email."""
    email: EmailStr
    
    # 4. ADD THIS
    @field_validator("email")
    @classmethod
    def clean_email(cls, v):
        return clean_email_str(v)



# ==================================================
#  Responses
# ==================================================

class TokensResponse(BaseModel):
    """JWT tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    expires_at: int


class AuthResponse(BaseModel):
    """Auth success response with user and tokens."""
    user: UserResponse
    tokens: Optional[TokensResponse] = None
    message: str = "Success"


class OAuthURLResponse(BaseModel):
    """OAuth redirect URL."""
    url: str
    provider: str