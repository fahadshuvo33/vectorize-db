"""
Router Manager - Register all route modules.
"""

from fastapi import APIRouter

from app.routes.auth import router as auth_router
from app.routes.users import router as users_router

router = APIRouter()

# Register routes
router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(users_router, prefix="/users", tags=["Users"])

__all__ = ["router"]