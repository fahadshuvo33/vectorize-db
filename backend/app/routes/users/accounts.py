"""
Linked Accounts Endpoints

Manage social accounts linked to user profile.
"""

import logging
from typing import List

from fastapi import APIRouter, HTTPException, status, Query

from app.core.config import settings
from app.core.dependencies import DbSession, Supabase, CurrentUser, CurrentUserStrict
from app.schemas import (
    MessageResponse,
    LinkedAccountsResponse,
    SocialAccountResponse,
    OAuthURLResponse,
)
from app.utils import (
    get_profile_by_id,
    get_user_social_accounts,
    get_social_account,
)
from app.routes.users.helpers import (
    social_account_to_response,
    get_linked_accounts_response,
)

logger = logging.getLogger(__name__)
router = APIRouter()

SUPPORTED_PROVIDERS = ["google", "github", "discord"]


@router.get("/me/linked-accounts", response_model=LinkedAccountsResponse)
async def get_linked_accounts_summary(
    user: CurrentUser,
    db: DbSession,
):
    """
    Get summary of linked login methods.

    Shows:
    - Whether user has password set
    - List of linked social providers
    - Total number of social accounts
    """
    profile = get_profile_by_id(db, user["id"])

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    social_accounts = get_user_social_accounts(db, user["id"])

    return get_linked_accounts_response(profile, social_accounts)


@router.get("/me/social-accounts", response_model=List[SocialAccountResponse])
async def get_social_accounts(
    user: CurrentUser,
    db: DbSession,
):
    """
    Get all linked social accounts with details.
    """
    social_accounts = get_user_social_accounts(db, user["id"])

    return [social_account_to_response(acc) for acc in social_accounts]


@router.get("/me/link/{provider}", response_model=OAuthURLResponse)
async def get_link_account_url(
    provider: str,
    user: CurrentUser,
    db: DbSession,
    supabase: Supabase,
    redirect_url: str = Query(None, description="Custom redirect URL after linking"),
):
    """
    Get OAuth URL to link a new social account.

    Use this to add additional social login methods to existing account.
    """
    if provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider. Supported: {', '.join(SUPPORTED_PROVIDERS)}",
        )

    # Check if provider already linked
    social_accounts = get_user_social_accounts(db, user["id"])
    linked_providers = [acc.provider for acc in social_accounts]

    if provider in linked_providers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{provider.title()} account already linked",
        )

    try:
        # Get OAuth URL for linking
        response = supabase.get_oauth_url(
            provider=provider,
            redirect_to=redirect_url or f"{settings.FRONTEND_URL}/settings/accounts",
        )

        return OAuthURLResponse(url=response.url, provider=provider)

    except Exception as e:
        logger.error(f"Link account URL error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get {provider} link URL",
        )


@router.delete("/me/social-accounts/{provider}", response_model=MessageResponse)
async def unlink_social_account(
    provider: str,
    user: CurrentUserStrict,
    db: DbSession,
):
    """
    Unlink a social account from profile.

    Requirements:
    - Cannot unlink if it's the only login method
    - Must have password OR another social account
    """
    profile = get_profile_by_id(db, user["id"])

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    social_accounts = get_user_social_accounts(db, user["id"])

    # Find the account to unlink
    account_to_unlink = None
    for acc in social_accounts:
        if acc.provider == provider:
            account_to_unlink = acc
            break

    if not account_to_unlink:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No {provider} account linked",
        )

    # Check if user will still have a login method
    remaining_social_accounts = len(social_accounts) - 1
    has_other_login = profile.has_password or remaining_social_accounts > 0

    if not has_other_login:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot unlink. You must have at least one login method (password or social account).",
        )

    try:
        db.delete(account_to_unlink)
        db.commit()

        return MessageResponse(
            success=True,
            message=f"{provider.title()} account unlinked successfully",
        )

    except Exception as e:
        logger.error(f"Unlink account error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unlink account",
        )


@router.get("/me/can-unlink/{provider}", response_model=dict)
async def check_can_unlink(
    provider: str,
    user: CurrentUser,
    db: DbSession,
):
    """
    Check if a social account can be unlinked.

    Returns whether unlinking is allowed and reason if not.
    """
    profile = get_profile_by_id(db, user["id"])

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    social_accounts = get_user_social_accounts(db, user["id"])

    # Check if provider is linked
    provider_linked = any(acc.provider == provider for acc in social_accounts)

    if not provider_linked:
        return {
            "can_unlink": False,
            "reason": f"No {provider} account linked",
        }

    # Check if user will still have a login method
    remaining_social_accounts = len(social_accounts) - 1
    has_other_login = profile.has_password or remaining_social_accounts > 0

    if not has_other_login:
        return {
            "can_unlink": False,
            "reason": "This is your only login method. Set a password or link another account first.",
        }

    return {
        "can_unlink": True,
        "reason": None,
    }


@router.get("/me/available-providers", response_model=dict)
async def get_available_providers(
    user: CurrentUser,
    db: DbSession,
):
    """
    Get list of social providers that can be linked.

    Shows which providers are already linked and which are available.
    """
    social_accounts = get_user_social_accounts(db, user["id"])
    linked_providers = [acc.provider for acc in social_accounts]

    available = [p for p in SUPPORTED_PROVIDERS if p not in linked_providers]
    linked = [p for p in SUPPORTED_PROVIDERS if p in linked_providers]

    return {
        "supported": SUPPORTED_PROVIDERS,
        "linked": linked,
        "available": available,
    }