"""
Social OAuth Endpoints
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Query
from gotrue.errors import AuthApiError

from app.core.config import settings
from app.core.dependencies import DbSession, Supabase
from app.schemas import AuthResponse, OAuthURLResponse
from app.utils import (
    get_profile_by_id,
    get_profile_by_email,
    get_social_account,
    create_profile,
    create_social_account,
    update_social_account_tokens,
)
from app.routes.auth.helpers import profile_to_response, session_to_tokens

logger = logging.getLogger(__name__)
router = APIRouter()

SUPPORTED_PROVIDERS = ["google", "github", "discord"]


@router.get("/oauth/{provider}", response_model=OAuthURLResponse)
async def get_oauth_url(
    provider: str,
    supabase: Supabase,
    redirect_url: Optional[str] = Query(None, description="Custom redirect URL after auth"),
):
    """
    Get OAuth authorization URL for social login.

    Supported providers: google, github, discord
    """
    if provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider. Supported: {', '.join(SUPPORTED_PROVIDERS)}",
        )

    try:
        response = supabase.get_oauth_url(
            provider=provider,
            redirect_to=redirect_url or settings.email_confirm_url,
        )

        return OAuthURLResponse(url=response.url, provider=provider)

    except Exception as e:
        logger.error(f"OAuth URL error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get {provider} login URL",
        )


@router.get("/oauth/callback", response_model=AuthResponse)
async def oauth_callback(
    code: str = Query(..., description="OAuth authorization code"),
    db: DbSession = None,
    supabase: Supabase = None,
):
    """
    Handle OAuth callback from provider.

    Account Linking Logic:
    1. If social account exists → Login to linked profile
    2. If email exists → Link social to existing profile (same email = same account)
    3. Otherwise → Create new profile

    Note: Social login = Auto verified email, no password initially
    """
    try:
        # Exchange code for session
        auth_response = supabase.exchange_code_for_session(code)

        if not auth_response.user or not auth_response.session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OAuth authentication failed",
            )

        user = auth_response.user
        session = auth_response.session

        # Extract provider info from user metadata
        provider = user.app_metadata.get("provider", "unknown")
        provider_id = user.app_metadata.get("provider_id") or user.id
        email = user.email
        full_name = (
            user.user_metadata.get("full_name")
            or user.user_metadata.get("name")
            or user.user_metadata.get("preferred_username")
        )
        avatar_url = (
            user.user_metadata.get("avatar_url")
            or user.user_metadata.get("picture")
        )

        # 1. Check if social account already exists
        existing_social = get_social_account(db, provider, provider_id)

        if existing_social:
            # Existing social login - get linked profile
            profile = get_profile_by_id(db, existing_social.user_id)

            if not profile:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Profile not found for social account",
                )

            # Update tokens
            update_social_account_tokens(
                db=db,
                social_account=existing_social,
                access_token={"token": session.access_token},
                refresh_token=session.refresh_token,
            )

        else:
            # 2. Check if email already exists (link accounts)
            profile = get_profile_by_email(db, email)

            if profile:
                # Link social account to existing profile
                logger.info(f"Linking {provider} to existing account: {email}")
            else:
                # 3. Create new profile
                profile = create_profile(
                    db=db,
                    user_id=user.id,
                    email=email,
                    full_name=full_name,
                    avatar_url=avatar_url,
                    is_email_verified=True,  # Social = verified
                    has_password=False,
                )

            # Create social account link
            create_social_account(
                db=db,
                user_id=profile.id,
                provider=provider,
                provider_id=provider_id,
                email=email,
                name=full_name,
                avatar_url=avatar_url,
                access_token={"token": session.access_token},
                refresh_token=session.refresh_token,
            )

        # Update profile if missing info
        updated = False

        if not profile.avatar_url and avatar_url:
            profile.avatar_url = avatar_url
            updated = True

        if not profile.full_name and full_name:
            profile.full_name = full_name
            updated = True

        if not profile.is_email_verified:
            profile.is_email_verified = True
            updated = True

        if updated:
            db.add(profile)
            db.commit()
            db.refresh(profile)

        return AuthResponse(
            user=profile_to_response(profile),
            tokens=session_to_tokens(session),
            message="Login successful",
        )

    except HTTPException:
        raise
    except AuthApiError as e:
        logger.error(f"OAuth callback error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.message),
        )
    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Social login failed",
        )