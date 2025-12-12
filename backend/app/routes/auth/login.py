"""
Login/Logout Endpoints
"""

import logging

from fastapi import APIRouter, HTTPException, status
from gotrue.errors import AuthApiError

from app.core.config import settings
from app.core.dependencies import DbSession, Supabase, CurrentUser
from app.schemas import (
    LoginRequest,
    RefreshTokenRequest,
    AuthResponse,
    TokensResponse,
    MessageResponse,
)
from app.utils import get_profile_by_id, create_profile
from app.routes.auth.helpers import profile_to_response, session_to_tokens

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/login", response_model=AuthResponse)
async def login(
    data: LoginRequest,
    db: DbSession,
    supabase: Supabase,
):
    """
    Login with email and password.

    - Validates credentials with Supabase
    - Checks email verification status
    - Returns user data and tokens
    """
    try:
        auth_response = supabase.sign_in_with_password(data.email, data.password)

        if not auth_response.user or not auth_response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        user = auth_response.user
        session = auth_response.session

        # Get or create profile
        profile = get_profile_by_id(db, user.id)

        if not profile:
            # Edge case: Supabase user exists but no profile
            profile = create_profile(
                db=db,
                user_id=user.id,
                email=data.email,
                is_email_verified=user.email_confirmed_at is not None,
                has_password=True,
            )
        else:
            # Sync verification status from Supabase
            is_verified = user.email_confirmed_at is not None
            if profile.is_email_verified != is_verified:
                profile.is_email_verified = is_verified
                db.add(profile)
                db.commit()
                db.refresh(profile)

        # Check email verification
        if settings.REQUIRE_EMAIL_VERIFICATION and not profile.is_email_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please verify your email before logging in",
            )

        return AuthResponse(
            user=profile_to_response(profile),
            tokens=session_to_tokens(session),
            message="Login successful",
        )

    except HTTPException:
        raise
    except AuthApiError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed",
        )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    user: CurrentUser,
    supabase: Supabase,
):
    """
    Logout current user.

    Invalidates the session on Supabase.
    """
    try:
        supabase.sign_out()
        return MessageResponse(success=True, message="Logged out successfully")
    except Exception as e:
        logger.error(f"Logout error: {e}")
        # Still return success - client should clear tokens anyway
        return MessageResponse(success=True, message="Logged out")


@router.post("/refresh", response_model=TokensResponse)
async def refresh_token(
    data: RefreshTokenRequest,
    supabase: Supabase,
):
    """
    Refresh access token using refresh token.
    """
    try:
        auth_response = supabase.refresh_session(data.refresh_token)

        if not auth_response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        return session_to_tokens(auth_response.session)

    except HTTPException:
        raise
    except AuthApiError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    except Exception as e:
        logger.error(f"Refresh token error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed",
        )