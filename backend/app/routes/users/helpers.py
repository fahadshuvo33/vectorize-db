"""
User-specific helper functions.
"""

from typing import List

from app.models.user import Profile, SocialAccount
from app.schemas import (
    UserResponse,
    UserProfileResponse,
    SocialAccountResponse,
    LinkedAccountsResponse,
)


def profile_to_user_response(profile: Profile) -> UserResponse:
    """Convert Profile model to basic UserResponse."""
    return UserResponse(
        id=profile.id,
        email=profile.email,
        full_name=profile.full_name,
        avatar_url=profile.avatar_url,
        is_email_verified=profile.is_email_verified,
        has_password=profile.has_password,
        referral_code=profile.referral_code,
        created_at=profile.created_at,
    )


def social_account_to_response(account: SocialAccount) -> SocialAccountResponse:
    """Convert SocialAccount model to SocialAccountResponse."""
    return SocialAccountResponse(
        id=account.id,
        provider=account.provider,
        email=account.email,
        name=account.name,
        avatar_url=account.avatar_url,
        created_at=account.created_at,
    )


def profile_to_full_response(
    profile: Profile,
    social_accounts: List[SocialAccount],
) -> UserProfileResponse:
    """Convert Profile model to full UserProfileResponse with social accounts."""
    return UserProfileResponse(
        id=profile.id,
        email=profile.email,
        full_name=profile.full_name,
        avatar_url=profile.avatar_url,
        is_email_verified=profile.is_email_verified,
        has_password=profile.has_password,
        referral_code=profile.referral_code,
        referred_by=profile.referred_by,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
        social_accounts=[
            social_account_to_response(acc) for acc in social_accounts
        ],
    )


def get_linked_accounts_response(
    profile: Profile,
    social_accounts: List[SocialAccount],
) -> LinkedAccountsResponse:
    """Get summary of linked login methods."""
    providers = list(set(acc.provider for acc in social_accounts))

    return LinkedAccountsResponse(
        has_password=profile.has_password,
        providers=providers,
        total_social_accounts=len(social_accounts),
    )