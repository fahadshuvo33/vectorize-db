from datetime import datetime
from typing import Optional
from pydantic import BaseModel, UUID4, Field, condecimal
from .enums import (
    PlanType, PaymentStatus, DiscountType, RewardType, 
    RewardStatus, ChangeType, ProrationOption, 
    CancellationType, RefundEligibility, FeatureCategory, ValueType
)

# ============================================
# PLANS
# ============================================
class PlanBase(BaseModel):
    slug: PlanType
    name: str
    description: Optional[str] = None
    price_monthly: int = Field(ge=0)  # in cents
    price_yearly: int = Field(ge=0)   # in cents
    is_custom: bool = False
    is_visible: bool = True
    sort_order: int = 0

class PlanCreate(PlanBase):
    pass

class PlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price_monthly: Optional[int] = Field(None, ge=0)
    price_yearly: Optional[int] = Field(None, ge=0)
    is_visible: Optional[bool] = None
    sort_order: Optional[int] = None

class PlanInDB(PlanBase):
    id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True

# ============================================
# FEATURES
# ============================================
class FeatureBase(BaseModel):
    key: str = Field(pattern=r'^[a-z_]+$')
    name: str
    description: Optional[str] = None
    category: FeatureCategory
    value_type: ValueType
    default_value: Optional[str] = None
    is_active: bool = True
    sort_order: int = 0

class FeatureCreate(FeatureBase):
    pass

class FeatureUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    default_value: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None

class FeatureInDB(FeatureBase):
    id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True

# ============================================
# PLAN FEATURES
# ============================================
class PlanFeatureBase(BaseModel):
    feature_value: str
    is_included: bool = True

class PlanFeatureCreate(PlanFeatureBase):
    plan_id: UUID4
    feature_id: UUID4

class PlanFeatureInDB(PlanFeatureBase):
    id: UUID4
    plan_id: UUID4
    feature_id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True

# ============================================
# USER FEATURES (Overrides)
# ============================================
class UserFeatureBase(BaseModel):
    feature_value: str
    granted_reason: Optional[str] = None
    expires_at: Optional[datetime] = None

class UserFeatureCreate(UserFeatureBase):
    user_id: UUID4
    feature_id: UUID4
    granted_by: UUID4

class UserFeatureInDB(UserFeatureBase):
    id: UUID4
    user_id: UUID4
    feature_id: UUID4
    is_override: bool = True
    granted_by: UUID4
    created_at: datetime

    class Config:
        from_attributes = True

# ============================================
# PAYMENTS
# ============================================
class PaymentBase(BaseModel):
    plan_slug: PlanType
    amount: int = Field(ge=0)
    discount_applied: int = Field(default=0, ge=0)
    status: PaymentStatus

class PaymentCreate(PaymentBase):
    user_id: UUID4
    stripe_subscription_id: str
    discount_code_id: Optional[UUID4] = None
    current_period_end: datetime

class PaymentUpdate(BaseModel):
    status: Optional[PaymentStatus] = None
    current_period_end: Optional[datetime] = None

class PaymentInDB(PaymentBase):
    id: UUID4
    user_id: UUID4
    stripe_subscription_id: str
    discount_code_id: Optional[UUID4] = None
    current_period_end: datetime
    created_at: datetime

    class Config:
        from_attributes = True

# ============================================
# DISCOUNT CODES
# ============================================
class DiscountCodeBase(BaseModel):
    code: str = Field(min_length=3, max_length=50)
    type: DiscountType
    value: int = Field(ge=0)
    plan_slug: Optional[PlanType] = None
    max_uses: int = -1  # -1 = unlimited
    valid_from: datetime
    valid_until: datetime
    is_active: bool = True

class DiscountCodeCreate(DiscountCodeBase):
    created_by: UUID4

class DiscountCodeUpdate(BaseModel):
    is_active: Optional[bool] = None
    valid_until: Optional[datetime] = None

class DiscountCodeInDB(DiscountCodeBase):
    id: UUID4
    created_by: UUID4
    used_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True

# ============================================
# USER DISCOUNT USAGE
# ============================================
class UserDiscountUsageCreate(BaseModel):
    user_id: UUID4
    discount_code_id: UUID4

class UserDiscountUsageInDB(BaseModel):
    id: UUID4
    user_id: UUID4
    discount_code_id: UUID4
    applied_at: datetime

    class Config:
        from_attributes = True

# ============================================
# REFERRAL REWARDS
# ============================================
class ReferralRewardBase(BaseModel):
    reward_type: RewardType
    reward_value: int = Field(ge=0)
    status: RewardStatus = RewardStatus.PENDING
    expires_at: Optional[datetime] = None

class ReferralRewardCreate(ReferralRewardBase):
    referrer_id: UUID4
    referred_id: UUID4

class ReferralRewardUpdate(BaseModel):
    status: Optional[RewardStatus] = None
    applied_at: Optional[datetime] = None

class ReferralRewardInDB(ReferralRewardBase):
    id: UUID4
    referrer_id: UUID4
    referred_id: UUID4
    applied_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

# ============================================
# SUBSCRIPTION CHANGES
# ============================================
class SubscriptionChangeBase(BaseModel):
    from_plan: Optional[PlanType] = None
    to_plan: PlanType
    change_type: ChangeType
    proration_option: ProrationOption
    old_price: int = Field(default=0, ge=0)
    new_price: int = Field(ge=0)
    days_remaining: int = Field(default=0, ge=0)
    proration_credit: int = Field(default=0, ge=0)
    proration_charge: int = Field(default=0, ge=0)
    total_charge: int = Field(ge=0)
    effective_date: datetime

class SubscriptionChangeCreate(SubscriptionChangeBase):
    user_id: UUID4
    stripe_invoice_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None

class SubscriptionChangeInDB(SubscriptionChangeBase):
    id: UUID4
    user_id: UUID4
    stripe_invoice_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# ============================================
# CANCELLATION REQUESTS
# ============================================
class CancellationRequestBase(BaseModel):
    cancellation_type: CancellationType
    refund_eligibility: RefundEligibility
    refund_amount: int = Field(default=0, ge=0)
    refund_reason: Optional[str] = None
    days_used: int = Field(ge=0)
    cancels_at: datetime

class CancellationRequestCreate(CancellationRequestBase):
    user_id: UUID4
    subscription_id: UUID4

class CancellationRequestUpdate(BaseModel):
    status: str
    stripe_refund_id: Optional[str] = None

class CancellationRequestInDB(CancellationRequestBase):
    id: UUID4
    user_id: UUID4
    subscription_id: UUID4
    requested_at: datetime
    stripe_refund_id: Optional[str] = None
    status: str = "pending"
    created_at: datetime

    class Config:
        from_attributes = True