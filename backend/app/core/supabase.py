# backend/app/core/supabase.py


"""
Supabase client wrapper for authentication and database operations.
"""

from typing import Dict, Any, Optional
from functools import lru_cache
from supabase import create_client, Client
from gotrue.types import AuthResponse, UserResponse
from gotrue.errors import AuthApiError

from app.core.config import settings

import logging

logger = logging.getLogger(__name__)


class SupabaseService:
    """
    Supabase client wrapper with common operations.
    Provides both public (anon) and admin (service role) clients.
    """

    def __init__(self):
        if not settings.SUPABASE_URL:
            raise ValueError("SUPABASE_URL must be configured")

        # Use the property that handles both naming conventions
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY  # ← Uses the property
        )

        self._admin_client: Optional[Client] = None
        if settings.SUPABASE_SERVICE_ROLE_KEY:
            self._admin_client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_ROLE_KEY
            )


    @property
    def admin(self) -> Client:
        """Get admin client. Raises error if not configured."""
        if not self._admin_client:
            raise RuntimeError(
                "Admin client not configured. Set SUPABASE_SERVICE_ROLE_KEY."
            )
        return self._admin_client

    # ============================================
    #  Authentication Methods
    # ============================================
    
    def sign_up(
        self, 
        email: str, 
        password: str, 
        user_metadata: Optional[Dict[str, Any]] = None
    ) -> AuthResponse:
        """Register a new user with email and password."""
        return self.client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": user_metadata or {},
                "email_redirect_to": settings.email_confirm_url
            }
        })

    def sign_in_with_password(self, email: str, password: str) -> AuthResponse:
        """Sign in with email and password."""
        return self.client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

    def sign_in_with_otp(self, email: str) -> AuthResponse:
        """Send magic link / OTP to email."""
        return self.client.auth.sign_in_with_otp({
            "email": email,
            "options": {
                "email_redirect_to": settings.email_confirm_url
            }
        })

    def verify_otp(self, email: str, token: str, type: str = "email") -> AuthResponse:
        """Verify OTP token."""
        return self.client.auth.verify_otp({
            "email": email,
            "token": token,
            "type": type
        })

    def sign_out(self) -> None:
        """Sign out current user."""
        self.client.auth.sign_out()

    def get_user(self, access_token: str) -> UserResponse:
        """Get user from access token."""
        return self.client.auth.get_user(access_token)

    def refresh_session(self, refresh_token: str) -> AuthResponse:
        """Refresh the session using refresh token."""
        return self.client.auth.refresh_session(refresh_token)

    def reset_password_email(self, email: str) -> None:
        """Send password reset email."""
        self.client.auth.reset_password_email(
            email,
            options={
                "redirect_to": settings.password_reset_url
            }
        )

    def update_user(self, attributes: Dict[str, Any]) -> UserResponse:
        """Update user attributes (password, email, metadata)."""
        return self.client.auth.update_user(attributes)

    def set_session(self, access_token: str, refresh_token: str) -> AuthResponse:
        """Set the session manually."""
        return self.client.auth.set_session(access_token, refresh_token)

    def get_oauth_url(self, provider: str, redirect_to: Optional[str] = None):
        """Get OAuth authorization URL."""
        return self.client.auth.sign_in_with_oauth({
            "provider": provider,
            "options": {
                "redirect_to": redirect_to or settings.email_confirm_url
            }
        })

    def exchange_code_for_session(self, auth_code: str) -> AuthResponse:
        """Exchange OAuth code for session."""
        return self.client.auth.exchange_code_for_session({
            "auth_code": auth_code
        })

    # ============================================
    #  Admin Auth Methods (requires service role)
    # ============================================

    def admin_get_user(self, user_id: str) -> UserResponse:
        """Get user by ID using admin privileges."""
        return self.admin.auth.admin.get_user_by_id(user_id)

    def admin_delete_user(self, user_id: str) -> None:
        """Delete user using admin privileges."""
        self.admin.auth.admin.delete_user(user_id)

    def admin_update_user(self, user_id: str, attributes: Dict[str, Any]) -> UserResponse:
        """Update user using admin privileges."""
        return self.admin.auth.admin.update_user_by_id(user_id, attributes)

    # ============================================
    #  Profile Methods (Database)
    # ============================================

    def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile from profiles table."""
        try:
            response = (
                self.client.table("profiles")
                .select("*")
                .eq("id", user_id)
                .single()
                .execute()
            )
            return response.data
        except Exception as e:
            logger.warning(f"Failed to get profile for user {user_id}: {e}")
            return None

    def create_profile(self, profile_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create user profile. Uses admin client to bypass RLS.
        """
        try:
            response = (
                self.admin.table("profiles")
                .insert(profile_data)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Failed to create profile: {e}")
            return None

    def update_profile(
        self, 
        user_id: str, 
        profile_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update user profile."""
        try:
            response = (
                self.client.table("profiles")
                .update(profile_data)
                .eq("id", user_id)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Failed to update profile for user {user_id}: {e}")
            return None


@lru_cache()
def get_supabase_client() -> SupabaseService:
    """Get cached Supabase client instance."""
    return SupabaseService()


# Global instance for convenience
supabase_client = get_supabase_client()
