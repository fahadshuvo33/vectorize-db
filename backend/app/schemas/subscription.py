from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, UUID4, Field, validator
from app.models.enums import (
    PlanType, PaymentStatus, DiscountType, 
    RewardType, RewardStatus
)

# ============================================
# SUBSCRIPTION REQUESTS
# ============================================
class UpgradePlanRequest(BaseModel):
    plan_slug: PlanType
    billing_cycle: str = Field(default="monthly", pattern="^(monthly|yearly)$")
    discount_code: Optional[str] = None

class CancelSubscriptionRequest(BaseModel):
    reason: Optional[str] = Field(None, max_length=500)
    feedback: Optional[str] = Field(None, max_length=1000)

class ApplyDiscountRequest(BaseModel):
    discount_code: str = Field(min_length=3, max_length=50)

# ============================================
# SUBSCRIPTION RESPONSES
# ============================================
class FeatureResponse(BaseModel):
    key: str
    name: str
    description: Optional[str] = None
    category: str
    value: str  # Formatted (e.g., "Unlimited", "5,000 rows")
    is_included: bool

class PlanResponse(BaseModel):
    id: UUID4
    slug: PlanType
    name: str
    description: Optional[str] = None
    price_monthly: int  # cents
    price_yearly: int
    features: List[FeatureResponse]
    is_current: bool = False
    is_recommended: bool = False
    savings_percent: Optional[int] = None  # For yearly

class SubscriptionResponse(BaseModel):
    plan: PlanType
    status: PaymentStatus
    current_period_end: datetime
    cancel_at_period_end: bool
    stripe_subscription_id: Optional[str] = None

class UpgradeQuoteResponse(BaseModel):
    """Preview before upgrade"""
    from_plan: PlanType
    to_plan: PlanType
    new_price_monthly: int
    proration_credit: int
    proration_charge: int
    total_charge_today: int
    new_billing_date: datetime

class DiscountValidationResponse(BaseModel):
    valid: bool
    discount_code: Optional[str] = None
    discount_type: Optional[str] = None
    discount_value: Optional[int] = None
    final_price: Optional[int] = None
    savings: Optional[int] = None
    error: Optional[str] = None

class ReferralStatsResponse(BaseModel):
    referral_code: str
    referral_url: str
    total_referrals: int
    pending_rewards: int
    total_rewards_earned: int
    rewards: List["RewardResponse"]

class RewardResponse(BaseModel):
    id: UUID4
    reward_type: RewardType
    reward_value: int
    status: RewardStatus
    referred_user_email: Optional[str] = None
    applied_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime

# ============================================
# ADMIN REQUESTS (Discount Codes)
# ============================================
class CreateDiscountCodeRequest(BaseModel):
    code: str = Field(min_length=3, max_length=50, pattern="^[A-Z0-9_]+$")
    type: DiscountType
    value: int = Field(ge=0)
    plan_slug: Optional[PlanType] = None
    max_uses: int = -1
    valid_from: datetime
    valid_until: datetime

class DiscountCodeResponse(BaseModel):
    id: UUID4
    code: str
    type: DiscountType
    value: int
    plan_slug: Optional[PlanType] = None
    max_uses: int
    used_count: int
    valid_from: datetime
    valid_until: datetime
    is_active: bool
    created_at: datetime