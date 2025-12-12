"""
Email Verification Endpoints
"""

import logging

from fastapi import APIRouter, HTTPException, status, Query

from app.core.config import settings
from app.core.dependencies import DbSession, Supabase
from app.schemas import ResendVerificationRequest, MessageResponse
from app.utils import get_profile_by_id

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification(
    data: ResendVerificationRequest,
    supabase: Supabase,
):
    """
    Resend email verification link.
    """
    try:
        supabase.client.auth.resend(
            type="signup",
            email=data.email,
            options={"email_redirect_to": settings.email_confirm_url},
        )
    except Exception as e:
        logger.error(f"Resend verification error: {e}")

    # Don't reveal if email exists (security)
    return MessageResponse(
        success=True,
        message="If that email exists, a verification link has been sent.",
    )


@router.get("/verify-email", response_model=MessageResponse)
async def verify_email(
    token: str = Query(..., description="Verification token from email"),
    type: str = Query(..., description="Token type (e.g., 'signup', 'email')"),
    db: DbSession = None,
    supabase: Supabase = None,
):
    """
    Verify email with token from email link.

    Called when user clicks the verification link in their email.
    """
    try:
        response = supabase.client.auth.verify_otp({
            "token_hash": token,
            "type": type,
        })

        if response.user:
            # Update profile verification status
            profile = get_profile_by_id(db, response.user.id)

            if profile:
                profile.is_email_verified = True
                db.add(profile)
                db.commit()

            return MessageResponse(
                success=True,
                message="Email verified successfully. You can now login.",
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Verify email error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email verification failed. Token may be invalid or expired.",
        )


@router.get("/verification-status", response_model=MessageResponse)
async def check_verification_status(
    email: str = Query(..., description="Email to check"),
    db: DbSession = None,
):
    """
    Check if an email is verified.

    Useful for frontend to show appropriate UI.
    """
    from app.utils import get_profile_by_email

    profile = get_profile_by_email(db, email)

    if not profile:
        # Don't reveal if email exists
        return MessageResponse(
            success=False,
            message="Unable to check verification status",
        )

    return MessageResponse(
        success=profile.is_email_verified,
        message="Email is verified" if profile.is_email_verified else "Email is not verified",
    )