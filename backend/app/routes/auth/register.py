# app/routes/auth/register.py

import logging
import re
from fastapi import APIRouter, HTTPException, status
from gotrue.errors import AuthApiError

from app.core.dependencies import DbSession, Supabase
from app.schemas import RegisterRequest, AuthResponse
from app.utils import (
    get_profile_by_email,
    get_profile_by_referral_code,
    create_profile,
    get_profile_by_id
)
from app.routes.auth.helpers import profile_to_response, session_to_tokens

logger = logging.getLogger(__name__)
router = APIRouter()

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@router.post("/register", response_model=AuthResponse)
async def register(
    data: RegisterRequest,
    db: DbSession,
    supabase: Supabase,
):
    """
    Register new user with email and password.
    
    Robust flow:
    1. Validate email format
    2. Check local DB for duplicates.
    3. Create user in Supabase Auth.
    4. Create profile in local DB.
    5. If DB fails -> Delete Supabase Auth user (Cleanup).
    """

    clean_email = data.email.strip().lower()
    clean_full_name = data.full_name.strip() if data.full_name else ""
    
    # --- 0. VALIDATE EMAIL FORMAT ---
    if not validate_email(clean_email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format",
        )
    
    # --- 1. PRE-CHECK LOCAL DB ---
    existing = get_profile_by_email(db, clean_email)
    if existing:
        logger.warning(f"Registration attempt for existing email: {clean_email}")
        if existing.has_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account exists via social login. Please login with your social provider.",
            )

    # --- 2. SUPABASE AUTH SIGNUP ---
    supabase_user_id = None
    try:
        logger.info(f"Attempting Supabase signup for: {clean_email}")
        
        auth_response = supabase.sign_up(
            email=clean_email,
            password=data.password,
            user_metadata={"full_name": clean_full_name},
        )
        
        if not auth_response.user:
            logger.error("Supabase returned no user object")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed at Auth provider",
            )
        
        user = auth_response.user
        supabase_user_id = user.id
        logger.info(f"Supabase user created successfully: {user.id}")

    except AuthApiError as e:
        error_msg = str(e)
        logger.error(f"Supabase Auth Error: {error_msg}")
        
        # Handle specific cases
        if "already registered" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered. Please login.",
            )
        elif "invalid" in error_msg.lower() and "email" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email address. Please check and try again.",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Registration error: {error_msg}",
            )
    except Exception as e:
        logger.error(f"Unexpected error during Supabase signup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during registration",
        )

    # --- 3. PROFILE CREATION (With Rollback Protection) ---
    try:
        # Check for ID collision
        existing_profile = get_profile_by_id(db, user.id)
        if existing_profile:
            logger.error(f"Profile ID collision for user {user.id}")
            raise Exception("Profile ID collision detected.")

        # Handle Referral
        referred_by_id = None
        if data.referral_code:
            referrer = get_profile_by_referral_code(db, data.referral_code)
            if referrer and str(referrer.id) != str(user.id):
                referred_by_id = referrer.id
                logger.info(f"Referral applied: {referrer.id}")

        # Create the profile
        logger.info(f"Creating profile for user: {user.id}")
        email_confirmed_at = getattr(user, 'email_confirmed_at', None)
        profile = create_profile(
            db=db,
            user_id=user.id,
            email=clean_email,
            full_name=clean_full_name,
            is_email_verified=email_confirmed_at is not None,
            has_password=True,
            referred_by=referred_by_id,
        )
        
        # COMMIT THE TRANSACTION
        db.commit()
        db.refresh(profile)
        logger.info(f"Profile created successfully: {profile.id}")

    except Exception as db_error:
        # --- CRITICAL ROLLBACK LOGIC ---
        logger.error(f"DB Error during registration: {db_error}")
        db.rollback()

        # Delete the Supabase user to prevent zombie state
        if supabase_user_id:
            try:
                logger.warning(f"Attempting to cleanup Supabase user {supabase_user_id}")
                supabase.admin_delete_user(supabase_user_id)
                logger.info(f"Successfully cleaned up Supabase user {supabase_user_id}")
            except Exception as cleanup_error:
                logger.critical(
                    f"CRITICAL: Zombie user created! "
                    f"User {supabase_user_id} exists in Auth but DB creation failed. "
                    f"Cleanup failed: {cleanup_error}"
                )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again.",
        )

    # --- 4. SUCCESS RESPONSE ---
    tokens = None
    if auth_response.session:
        tokens = session_to_tokens(auth_response.session)

    return AuthResponse(
        user=profile_to_response(profile),
        tokens=tokens,
        message="Registration successful!" if tokens else "Registration successful. Please check your email to verify.",
    )