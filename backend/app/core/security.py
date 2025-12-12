# backend/app/core/security.py
"""
Security utilities for JWT verification.

Since we use Supabase Auth, this file mainly handles:
- JWT token verification (validating Supabase-issued tokens)
- Optional: Password hashing (only if you need custom auth)
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

import httpx
from jose import jwt, JWTError
from jose.backends.rsa_backend import RSAKey

from app.core.config import settings

logger = logging.getLogger(__name__)


# ==================================================
#  JWKS Cache (for RS256 token verification)
# ==================================================

class JWKSCache:
    """
    Cache for Supabase JWKS (JSON Web Key Set).
    Avoids fetching JWKS on every request.
    """
    
    def __init__(self, cache_duration_hours: int = 1):
        self._cache: Optional[Dict[str, Any]] = None
        self._expiry: Optional[datetime] = None
        self._duration = timedelta(hours=cache_duration_hours)
    
    @property
    def is_valid(self) -> bool:
        return self._cache is not None and self._expiry is not None and datetime.utcnow() < self._expiry
    
    def get(self) -> Optional[Dict[str, Any]]:
        return self._cache if self.is_valid else None
    
    def set(self, jwks: Dict[str, Any]) -> None:
        self._cache = jwks
        self._expiry = datetime.utcnow() + self._duration
    
    def get_stale(self) -> Optional[Dict[str, Any]]:
        """Return cached data even if expired (fallback)."""
        return self._cache


# Global cache instance
_jwks_cache = JWKSCache()


async def fetch_jwks() -> Dict[str, Any]:
    """Fetch JWKS from Supabase, with caching."""
    
    # Return cached if valid
    cached = _jwks_cache.get()
    if cached:
        return cached
    
    jwks_url = f"{settings.SUPABASE_URL}/auth/v1/jwks"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(jwks_url, timeout=10.0)
            response.raise_for_status()
            jwks = response.json()
            _jwks_cache.set(jwks)
            logger.debug("JWKS cache refreshed")
            return jwks
            
    except Exception as e:
        logger.error(f"Failed to fetch JWKS: {e}")
        
        # Use stale cache as fallback
        stale = _jwks_cache.get_stale()
        if stale:
            logger.warning("Using stale JWKS cache")
            return stale
        
        raise RuntimeError(f"Cannot fetch JWKS: {e}")


def get_public_key_from_jwks(jwks: Dict[str, Any], kid: str):
    """Extract RSA public key from JWKS by key ID."""
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            try:
                return RSAKey(key, algorithm="RS256")
            except Exception as e:
                logger.error(f"Failed to construct RSA key: {e}")
    return None


# ==================================================
#  JWT Token Verification
# ==================================================

async def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify a Supabase JWT token.
    
    Attempts RS256 verification first (using JWKS), then falls back 
    to HS256 using JWT secret.
    
    Args:
        token: JWT access token from Supabase
        
    Returns:
        Decoded token payload containing user info
        
    Raises:
        JWTError: If verification fails
    """
    
    try:
        # Get token header to determine algorithm
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        algorithm = header.get("alg", "HS256")
    except JWTError as e:
        logger.error(f"Invalid token header: {e}")
        raise
    
    # Try RS256 verification first
    if kid and algorithm == "RS256":
        try:
            jwks = await fetch_jwks()
            public_key = get_public_key_from_jwks(jwks, kid)
            
            if public_key:
                payload = jwt.decode(
                    token,
                    public_key,
                    algorithms=["RS256"],
                    audience="authenticated",
                    issuer=f"{settings.SUPABASE_URL}/auth/v1",
                )
                return payload
        except Exception as e:
            logger.warning(f"RS256 verification failed, trying HS256: {e}")
    
    # Fallback to HS256 with JWT secret
    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
        )
        return payload
    except JWTError as e:
        logger.error(f"Token verification failed: {e}")
        raise


def verify_token_sync(token: str) -> Dict[str, Any]:
    """
    Synchronous token verification (HS256 only).
    
    Use this in sync contexts where you can't await.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
        )
        return payload
    except JWTError as e:
        logger.error(f"Token verification failed: {e}")
        raise


# ==================================================
#  Utility Functions
# ==================================================

def extract_user_id(token: str) -> Optional[str]:
    """
    Extract user ID from token WITHOUT verification.
    Only use for logging/debugging, never for auth decisions.
    """
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload.get("sub")
    except JWTError:
        return None


def is_token_expired(token: str) -> bool:
    """Check if token is expired without full verification."""
    try:
        jwt.decode(
            token,
            options={"verify_signature": False, "verify_exp": True}
        )
        return False
    except jwt.ExpiredSignatureError:
        return True
    except JWTError:
        return True


# ==================================================
#  Optional: Password Hashing
#  (Only needed if you're doing custom password handling)
# ==================================================

# Uncomment if you need password hashing:
#
# from passlib.context import CryptContext
#
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#
# def hash_password(password: str) -> str:
#     return pwd_context.hash(password)
#
# def verify_password(plain: str, hashed: str) -> bool:
#     return pwd_context.verify(plain, hashed)