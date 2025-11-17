from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, UUID4, Field
from app.models.enums import PlanType
from .user import UserResponse, UsageResponse
from .subscription import SubscriptionResponse

# ============================================
# ADMIN REQUESTS
# ============================================
class GrantFeatureRequest(BaseModel):
    user_id: str  # UUID as string
    feature_key: str
    feature_value: str
    reason: str = Field(min_length=5, max_length=500)
    expires_at: Optional[datetime] = None

class AdminUserSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=100)
    search_by: str = Field(default="email", pattern="^(email|id|name)$")

class AdminUpdateUserRequest(BaseModel):
    current_plan: Optional[PlanType] = None
    plan_ends_at: Optional[datetime] = None
    is_banned: Optional[bool] = None

# ============================================
# ADMIN RESPONSES
# ============================================
class AdminStatsResponse(BaseModel):
    total_users: int
    active_users_today: int
    active_users_month: int
    total_conversions: int
    conversions_today: int
    total_chats: int
    chats_today: int
    total_revenue: int  # cents
    mrr: int  # Monthly Recurring Revenue
    churn_rate: float
    avg_conversions_per_user: float

class RevenueStatsResponse(BaseModel):
    today: int
    yesterday: int
    this_week: int
    this_month: int
    last_month: int
    total: int

class UserDetailResponse(BaseModel):
    user: UserResponse
    usage: UsageResponse
    subscription: Optional[SubscriptionResponse]
    stats: "UserStatsResponse"
    recent_activity: List["ActivityLogResponse"]

class UserStatsResponse(BaseModel):
    total_files: int
    total_conversions: int
    total_chats: int
    total_api_requests: int
    lifetime_value: int  # cents
    account_age_days: int
    last_login: Optional[datetime] = None

class ActivityLogResponse(BaseModel):
    id: UUID4
    action: str
    details: dict
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime

class AdminUserListResponse(BaseModel):
    id: UUID4
    email: EmailStr
    full_name: Optional[str] = None
    current_plan: PlanType
    total_conversions: int
    lifetime_value: int
    created_at: datetime
    last_login: Optional[datetime] = None