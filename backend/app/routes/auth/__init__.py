"""
Auth Router - Combines all auth-related routes.
"""

from fastapi import APIRouter

from app.routes.auth.register import router as register_router
from app.routes.auth.login import router as login_router
from app.routes.auth.oauth import router as oauth_router
from app.routes.auth.password import router as password_router
from app.routes.auth.verification import router as verification_router

router = APIRouter()

# Include all auth sub-routers
router.include_router(register_router)
router.include_router(login_router)
router.include_router(oauth_router)
router.include_router(password_router)
router.include_router(verification_router)

__all__ = ["router"]