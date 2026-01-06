"""
Auth-specific helper functions.
"""

from app.models.user import Profile
from app.schemas import UserResponse, TokensResponse


def profile_to_response(profile: Profile) -> UserResponse:
    """Convert Profile model to UserResponse schema."""
    return UserResponse(
        id=str(profile.id),
        email=profile.email,
        full_name=profile.full_name,
        avatar_url=profile.avatar_url,
        is_email_verified=profile.is_email_verified,
        has_password=profile.has_password,
        referral_code=profile.referral_code,
        created_at=profile.created_at,
    )


def session_to_tokens(session) -> TokensResponse:
    """Convert Supabase session to TokensResponse schema."""
    return TokensResponse(
        access_token=session.access_token,
        refresh_token=session.refresh_token,
        token_type="bearer",
        expires_in=session.expires_in,
        expires_at=session.expires_at,
    )