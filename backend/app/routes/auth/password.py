"""
Password Management Endpoints
"""

import logging

from fastapi import APIRouter, HTTPException, status
from gotrue.errors import AuthApiError

from app.core.dependencies import DbSession, Supabase, CurrentUserStrict
from app.schemas import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    SetPasswordRequest,
    ChangePasswordRequest,
    MessageResponse,
)
from app.utils import get_profile_by_id

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    data: ForgotPasswordRequest,
    supabase: Supabase,
):
    """
    Send password reset email.
    """
    try:
        supabase.reset_password_email(data.email)
    except Exception as e:
        logger.error(f"Forgot password error: {e}")

    # Always return success (don't reveal if email exists)
    return MessageResponse(
        success=True,
        message="If that email exists, a password reset link has been sent.",
    )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    data: ResetPasswordRequest,
    db: DbSession,
    supabase: Supabase,
):
    """
    Reset password using token from email.
    """
    try:
        # Set session from recovery token
        supabase.client.auth.set_session(data.token, "")

        # Update password
        response = supabase.update_user({"password": data.new_password})

        if response.user:
            # Update profile
            profile = get_profile_by_id(db, response.user.id)

            if profile:
                profile.has_password = True
                db.add(profile)
                db.commit()

            return MessageResponse(
                success=True,
                message="Password reset successfully",
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset failed",
        )

    except HTTPException:
        raise
    except AuthApiError as e:
        logger.error(f"Reset password error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )
    except Exception as e:
        logger.error(f"Reset password error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed",
        )


@router.post("/set-password", response_model=MessageResponse)
async def set_password(
    data: SetPasswordRequest,
    user: CurrentUserStrict,
    db: DbSession,
    supabase: Supabase,
):
    """
    Set password for social-only account.

    Allows users who signed up via social login to add a password
    so they can also login with email/password.
    """
    profile = get_profile_by_id(db, user["id"])

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    if profile.has_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password already set. Use /change-password instead.",
        )

    try:
        # Update password in Supabase
        response = supabase.update_user({"password": data.password})

        if response.user:
            profile.has_password = True
            db.add(profile)
            db.commit()

            return MessageResponse(
                success=True,
                message="Password set successfully. You can now login with email/password.",
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to set password",
        )

    except HTTPException:
        raise
    except AuthApiError as e:
        logger.error(f"Set password error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.message),
        )
    except Exception as e:
        logger.error(f"Set password error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to set password",
        )


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    data: ChangePasswordRequest,
    user: CurrentUserStrict,
    db: DbSession,
    supabase: Supabase,
):
    """
    Change password for users who already have a password.

    Requires current password for verification.
    """
    profile = get_profile_by_id(db, user["id"])

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    if not profile.has_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No password set. Use /set-password instead.",
        )

    try:
        # Verify current password by attempting login
        try:
            supabase.sign_in_with_password(profile.email, data.current_password)
        except AuthApiError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        # Update to new password
        response = supabase.update_user({"password": data.new_password})

        if response.user:
            return MessageResponse(
                success=True,
                message="Password changed successfully",
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to change password",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Change password error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password",
        )