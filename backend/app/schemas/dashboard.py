from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from .user import UserResponse, UsageResponse
from .subscription import SubscriptionResponse
from .file import FileListResponse
from .chat import ChatSessionResponse
from .support import NotificationResponse

# ============================================
# DASHBOARD RESPONSES
# ============================================
class UpgradeBannerResponse(BaseModel):
    show: bool
    reason: str  # "limit_reached", "feature_locked", etc.
    message: str
    cta_text: str
    cta_url: str

class DashboardStatsResponse(BaseModel):
    total_files: int
    total_conversions: int
    total_chats: int
    total_api_requests: int

class DashboardResponse(BaseModel):
    user: UserResponse
    usage: UsageResponse
    subscription: Optional[SubscriptionResponse] = None
    stats: DashboardStatsResponse
    recent_files: List[FileListResponse]
    recent_chats: List[ChatSessionResponse]
    notifications: List[NotificationResponse]
    upgrade_banner: Optional[UpgradeBannerResponse] = None

class QuickStatsResponse(BaseModel):
    """Quick stats for header/navbar"""
    conversions_remaining: int
    chats_remaining: int
    plan_name: str
    plan_ends_at: Optional[datetime] = None
    unread_notifications: int