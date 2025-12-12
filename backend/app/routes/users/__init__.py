"""
Users Router - Combines all user-related routes.
"""

from fastapi import APIRouter

from app.routes.users.profile import router as profile_router
from app.routes.users.accounts import router as accounts_router

router = APIRouter()

# Include all user sub-routers
router.include_router(profile_router)
router.include_router(accounts_router)

__all__ = ["router"]