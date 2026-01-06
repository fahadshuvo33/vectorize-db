# backend/app/core/dependencies.py
"""
FastAPI Dependencies for authentication and resource injection.

This module provides:
- Authentication dependencies (get_current_user, etc.)
- Database session dependency
- Supabase client dependency
- Type aliases for cleaner route definitions

Usage:
    from app.core.dependencies import CurrentUser, DbSession
    
    @router.get("/me")
    async def get_me(user: CurrentUser, db: DbSession):
        return user
"""

import logging
from typing import Optional, Dict, Any, Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from jose import JWTError

from app.core.config import settings
from app.core.database import get_db
from app.core.security import verify_token
from app.core.supabase import get_supabase_client, SupabaseService
from app.models.user import Profile

logger = logging.getLogger(__name__)


# ==================================================
#  Security Schemes
# ==================================================

class OptionalHTTPBearer(HTTPBearer):
    """Custom HTTPBearer that doesn't raise error when token is missing."""
    
    async def __call__(self, request) -> Optional[HTTPAuthorizationCredentials]:
        try:
            return await super().__call__(request)
        except HTTPException:
            return None


# Token extractors
bearer_scheme = HTTPBearer(
    scheme_name="JWT",
    description="Enter your access token",
)

optional_bearer_scheme = OptionalHTTPBearer(
    scheme_name="JWT",
    description="Optional access token",
    auto_error=False,
)


# ==================================================
#  Helper Functions
# ==================================================

def profile_to_dict(profile: Profile) -> Dict[str, Any]:
    """Convert Profile model to dictionary."""
    return {
        "id": profile.id,
        "email": profile.email,
        "full_name": profile.full_name,
        "avatar_url": profile.avatar_url,
        "is_email_verified": profile.is_email_verified,
        "has_password": profile.has_password,
        "referral_code": profile.referral_code,
        "referred_by": profile.referred_by,
        "created_at": profile.created_at.isoformat() if profile.created_at else None,
        "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
    }


def get_profile_by_id(db: Session, user_id: str) -> Optional[Profile]:
    """Fetch user profile from database."""
    # return db.exec(select(Profile).where(Profile.id == user_id)).first()
    profile = db.exec(select(Profile).where(Profile.id == user_id)).first()
    return profile


# ==================================================
#  Authentication Dependencies
# ==================================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get current authenticated user from JWT token.
    
    Verifies the token locally using JWT secret/JWKS and fetches
    the user profile from the database.
    
    Args:
        credentials: Bearer token from Authorization header
        db: Database session
        
    Returns:
        Dict containing:
            - id: User ID (from token)
            - email: User email (from token)
            - email_verified: Whether email is verified
            - role: User role (from token)
            - profile: Profile data (from database) or None
            - token: The access token (for downstream use)
            
    Raises:
        HTTPException 401: If token is missing, invalid, or expired
    """
    token = credentials.credentials
    
    try:
        # Verify token
        payload = await verify_token(token)
        
        # Extract user info from token
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Fetch profile from database
        profile = get_profile_by_id(db, user_id)
        
        email_confirmed_at = payload.get("email_confirmed_at")
        return {
            "id": user_id,
            "email": payload.get("email"),
            "email_verified": email_confirmed_at is not None,
            "role": payload.get("role", "authenticated"),
            "profile": profile_to_dict(profile) if profile else None,
            "token": token,
        }
        
    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_strict(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
    supabase: SupabaseService = Depends(get_supabase_client),
) -> Dict[str, Any]:
    """
    Get current user with STRICT verification via Supabase API.
    
    Unlike get_current_user which verifies locally, this calls Supabase
    to verify the token is still valid (not revoked/signed out).
    
    Use this for sensitive operations:
        - Password change
        - Email change  
        - Account deletion
        - Payment operations
    """
    token = credentials.credentials
    
    try:
        # Verify with Supabase API (slower but checks revocation)
        response = supabase.get_user(token)
        
        if not response or not response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or revoked token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = response.user
        
        # Fetch profile
        profile = get_profile_by_id(db, str(user.id))
        
        email_confirmed_at = getattr(user, 'email_confirmed_at', None)
        return {
            "id": str(user.id),
            "email": user.email,
            "email_verified": email_confirmed_at is not None,
            "role": user.role or "authenticated",
            "profile": profile_to_dict(profile) if profile else None,
            "token": token,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Strict auth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_verified_user(
    user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get current user and require email verification.
    
    Use this for features that require verified email:
        - Posting content
        - Messaging
        - Premium features
    """
    if settings.REQUIRE_EMAIL_VERIFICATION and not user.get("email_verified"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required. Please verify your email to continue.",
        )
    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_bearer_scheme),
    db: Session = Depends(get_db),
) -> Optional[Dict[str, Any]]:
    """
    Optionally get current user. Returns None if not authenticated.
    
    Use this for endpoints that work for both auth and anonymous users:
        - Public content with personalization
        - Like counts (show if current user liked)
        - Comments (show user's own comments differently)
    """
    if not credentials:
        return None
    
    try:
        payload = await verify_token(credentials.credentials)
        user_id = payload.get("sub")
        
        if not user_id:
            return None
        
        profile = get_profile_by_id(db, user_id)
        
        email_confirmed_at = payload.get("email_confirmed_at")
        return {
            "id": user_id,
            "email": payload.get("email"),
            "email_verified": email_confirmed_at is not None,
            "role": payload.get("role", "authenticated"),
            "profile": profile_to_dict(profile) if profile else None,
            "token": credentials.credentials,
        }
        
    except Exception as e:
        logger.debug(f"Optional auth failed (this is fine): {e}")
        return None


async def get_admin_user(
    user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get current user and require admin privileges.
    
    Admin is determined by:
        1. Supabase role = 'service_role'
        2. Or custom is_admin flag in profile (you can add this to Profile model)
    """
    # Check Supabase role
    if user.get("role") == "service_role":
        return user
    
    # Check custom admin flag in profile
    # Note: Add `is_admin: bool = Field(default=False)` to your Profile model
    profile = user.get("profile")
    if profile and profile.get("is_admin"):
        return user
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Admin access required",
    )


# ==================================================
#  Type Aliases for Clean Route Definitions
# ==================================================

# Database
DbSession = Annotated[Session, Depends(get_db)]

# Supabase Client
Supabase = Annotated[SupabaseService, Depends(get_supabase_client)]

# User Dependencies
CurrentUser = Annotated[Dict[str, Any], Depends(get_current_user)]
CurrentUserStrict = Annotated[Dict[str, Any], Depends(get_current_user_strict)]
VerifiedUser = Annotated[Dict[str, Any], Depends(get_verified_user)]
OptionalUser = Annotated[Optional[Dict[str, Any]], Depends(get_optional_user)]
AdminUser = Annotated[Dict[str, Any], Depends(get_admin_user)]


# ==================================================
#  Utility Dependencies
# ==================================================

async def get_user_profile(
    user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Profile:
    """
    Get current user's Profile model instance.
    
    Use when you need the actual SQLModel object for updates.
    """
    profile = get_profile_by_id(db, user["id"])
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please complete your profile setup.",
        )
    
    return profile


UserProfile = Annotated[Profile, Depends(get_user_profile)]