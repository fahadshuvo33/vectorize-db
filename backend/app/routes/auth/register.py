"""
Registration Endpoints
"""

import logging

from fastapi import APIRouter, HTTPException, status
from gotrue.errors import AuthApiError

from app.core.dependencies import DbSession, Supabase
from app.schemas import RegisterRequest, AuthResponse
from app.utils import (
    get_profile_by_email,
    get_profile_by_referral_code,
    create_profile,
)
from app.routes.auth.helpers import profile_to_response, session_to_tokens

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/register", response_model=AuthResponse)
async def register(
    data: RegisterRequest,
    db: DbSession,
    supabase: Supabase,
):
    """
    Register new user with email and password.

    - Creates user in Supabase Auth
    - Creates profile in database
    - Sends verification email
    - Email must be verified before login (if REQUIRE_EMAIL_VERIFICATION=True)
    """
    # Check if email already exists
    existing = get_profile_by_email(db, data.email)

    if existing:
        if existing.has_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account exists via social login. Login with your social provider and set a password.",
            )

    try:
        # Create user in Supabase Auth
        auth_response = supabase.sign_up(
            email=data.email,
            password=data.password,
            user_metadata={"full_name": data.full_name},
        )

        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed",
            )

        user = auth_response.user

        # Find referrer
        referred_by = None
        if data.referral_code:
            referrer = get_profile_by_referral_code(db, data.referral_code)
            if referrer:
                referred_by = referrer.id

        # Create profile
        profile = create_profile(
            db=db,
            user_id=user.id,
            email=data.email,
            full_name=data.full_name,
            is_email_verified=False,
            has_password=True,
            referred_by=referred_by,
        )

        # Build response
        tokens = None
        if auth_response.session:
            tokens = session_to_tokens(auth_response.session)

        return AuthResponse(
            user=profile_to_response(profile),
            tokens=tokens,
            message="Registration successful. Please check your email to verify.",
        )

    except HTTPException:
        raise
    except AuthApiError as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.message),
        )
    except Exception as e:
        logger.error(f"Registration error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed",
        )