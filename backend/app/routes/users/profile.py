"""
User Profile Endpoints
"""

import logging

from fastapi import APIRouter, HTTPException, status
from gotrue.errors import AuthApiError

from app.core.dependencies import (
    DbSession,
    Supabase,
    CurrentUser,
    CurrentUserStrict,
)
from app.schemas import (
    UserResponse,
    UserProfileResponse,
    UpdateProfileRequest,
    ChangeEmailRequest,
    DeleteAccountRequest,
    MessageResponse,
)
from app.utils import (
    get_profile_by_id,
    get_profile_by_email,
    get_user_social_accounts,
)
from app.routes.users.helpers import (
    profile_to_user_response,
    profile_to_full_response,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    user: CurrentUser,
    db: DbSession,
):
    """
    Get current user's full profile.

    Includes linked social accounts.
    """
    profile = get_profile_by_id(db, user["id"])

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    social_accounts = get_user_social_accounts(db, user["id"])

    return profile_to_full_response(profile, social_accounts)


@router.patch("/me", response_model=UserResponse)
async def update_profile(
    data: UpdateProfileRequest,
    user: CurrentUser,
    db: DbSession,
):
    """
    Update current user's profile.

    Updatable fields:
    - full_name
    - avatar_url
    """
    profile = get_profile_by_id(db, user["id"])

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    # Update fields if provided
    if data.full_name is not None:
        profile.full_name = data.full_name

    if data.avatar_url is not None:
        profile.avatar_url = data.avatar_url

    try:
        db.add(profile)
        db.commit()
        db.refresh(profile)

        return profile_to_user_response(profile)

    except Exception as e:
        logger.error(f"Update profile error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile",
        )


@router.post("/me/change-email", response_model=MessageResponse)
async def request_email_change(
    data: ChangeEmailRequest,
    user: CurrentUserStrict,
    db: DbSession,
    supabase: Supabase,
):
    """
    Request email change.

    - Requires password verification
    - Sends confirmation email to new address
    - Email is updated after confirmation
    """
    profile = get_profile_by_id(db, user["id"])

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    # Check if new email already exists
    existing = get_profile_by_email(db, data.new_email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already in use",
        )

    # Verify password if user has one
    if profile.has_password:
        try:
            supabase.sign_in_with_password(profile.email, data.password)
        except AuthApiError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is incorrect",
            )

    try:
        # Request email change via Supabase
        supabase.update_user({"email": data.new_email})

        return MessageResponse(
            success=True,
            message="Confirmation email sent to your new email address. Please verify to complete the change.",
        )

    except AuthApiError as e:
        logger.error(f"Change email error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.message),
        )
    except Exception as e:
        logger.error(f"Change email error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change email",
        )


@router.delete("/me", response_model=MessageResponse)
async def delete_account(
    data: DeleteAccountRequest,
    user: CurrentUserStrict,
    db: DbSession,
    supabase: Supabase,
):
    """
    Delete current user's account.

    - Requires typing "DELETE" as confirmation
    - Requires password if user has one
    - Permanently deletes all user data
    """
    profile = get_profile_by_id(db, user["id"])

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    # Verify confirmation text
    if data.confirmation != "DELETE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please type 'DELETE' to confirm account deletion",
        )

    # Verify password if user has one
    if profile.has_password:
        if not data.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is required to delete account",
            )

        try:
            supabase.sign_in_with_password(profile.email, data.password)
        except AuthApiError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is incorrect",
            )

    try:
        # Delete social accounts first (foreign key constraint)
        social_accounts = get_user_social_accounts(db, user["id"])
        for account in social_accounts:
            db.delete(account)

        # Delete profile
        db.delete(profile)
        db.commit()

        # Delete from Supabase Auth (requires admin client)
        try:
            supabase.admin_delete_user(user["id"])
        except Exception as e:
            logger.error(f"Failed to delete Supabase user: {e}")
            # Continue - profile is already deleted

        return MessageResponse(
            success=True,
            message="Account deleted successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete account error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account",
        )


@router.get("/me/referrals", response_model=dict)
async def get_referrals(
    user: CurrentUser,
    db: DbSession,
):
    """
    Get users referred by current user.
    """
    from sqlmodel import select
    from app.models.user import Profile

    profile = get_profile_by_id(db, user["id"])

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    # Get referred users
    referred_users = db.exec(
        select(Profile).where(Profile.referred_by == user["id"])
    ).all()

    return {
        "referral_code": profile.referral_code,
        "total_referrals": len(referred_users),
        "referrals": [
            {
                "id": u.id,
                "email": u.email,
                "full_name": u.full_name,
                "created_at": u.created_at,
            }
            for u in referred_users
        ],
    }