from typing import Optional, List
from datetime import datetime, date
from sqlmodel import SQLModel

# Import Enums to ensure validation matches DB
from app.models.enums.subscription import (
    PlanStatus, SubscriptionType, BillingCycle, SubStatus, 
    UpgradeType, Urgency, RequestStatus, OfferType, 
    OfferStatus, TransactionType, TransactionStatus
)

# ==========================================
# 1. PLANS (Standard)
# ==========================================
class PlanBase(SQLModel):
    name: str
    description: Optional[str] = None
    monthly_price: float
    annual_price: Optional[float] = None
    file_limit: int
    row_limit: int
    daily_convert: int
    api_access: bool = False
    priority_support: bool = False
    icon_color: Optional[str] = None

class PlanCreate(PlanBase):
    display_order: Optional[int] = None
    is_active: bool = True

class PlanUpdate(SQLModel):
    name: Optional[str] = None
    monthly_price: Optional[float] = None
    # ... add other fields as optional if needed

class PlanRead(PlanBase):
    id: str
    is_active: bool
    display_order: Optional[int]
    created_at: datetime

# ==========================================
# 2. CUSTOM PLANS
# ==========================================
class CustomPlanBase(SQLModel):
    plan_name: str
    description: Optional[str] = None
    file_limit: int
    row_limit: int
    daily_convert: int
    api_access: bool = False
    priority_support: bool = False
    
class CustomPlanCreate(CustomPlanBase):
    requested_price: float

class CustomPlanUpdateAdmin(SQLModel):
    approved_price: Optional[float] = None
    annual_price: Optional[float] = None
    status: Optional[PlanStatus] = None
    admin_notes: Optional[str] = None

class CustomPlanRead(CustomPlanBase):
    id: str
    user_id: str
    requested_price: float
    approved_price: Optional[float]
    status: PlanStatus
    admin_notes: Optional[str] = None # Might want to hide this from user?
    created_at: datetime

# ==========================================
# 3. SUBSCRIPTIONS
# ==========================================
class SubscriptionRead(SQLModel):
    id: str
    plan_id: Optional[str]
    custom_plan_id: Optional[str]
    subscription_type: SubscriptionType
    status: SubStatus
    billing_start_date: date
    billing_end_date: date
    billing_cycle: BillingCycle
    auto_renew: bool
    created_at: datetime

    # We can include the Plan details nested if we want, 
    # but usually frontend matches ID to Plan list

# ==========================================
# 4. SUBSCRIPTION USAGE
# ==========================================
class SubUsageRead(SQLModel):
    files_used: int
    rows_used: int
    daily_converts_used: int
    files_remaining: Optional[int]
    rows_remaining: Optional[int]
    usage_date: date

# ==========================================
# 5. UPGRADE REQUESTS & OFFERS
# ==========================================

# Request
class UpgradeRequestCreate(SQLModel):
    subscription_id: str
    to_plan_id: Optional[str] = None
    to_custom_plan_id: Optional[str] = None
    upgrade_type: UpgradeType
    reason: Optional[str] = None
    urgency: Urgency = Urgency.FLEXIBLE

class UpgradeRequestRead(SQLModel):
    id: str
    status: RequestStatus
    created_at: datetime
    user_responded_at: Optional[datetime]

# Offer
class UpgradeOfferCreate(SQLModel):
    # Admin creates this
    upgrade_request_id: str
    offer_type: OfferType
    new_plan_price: float
    credit_applied: float
    charge_amount: float
    valid_until: Optional[datetime]

class UpgradeOfferRead(SQLModel):
    id: str
    offer_type: OfferType
    charge_amount: Optional[float]
    credit_applied: Optional[float]
    bonus_free_days: int
    status: OfferStatus
    valid_until: Optional[datetime]

class UpgradeOfferResponse(SQLModel):
    # User responds to offer
    user_decision: str # "accept" or "reject"
    user_notes: Optional[str] = None

# ==========================================
# 6. BILLING HISTORY
# ==========================================
class BillingHistoryRead(SQLModel):
    id: str
    amount: float
    transaction_type: TransactionType
    status: TransactionStatus
    paid_at: Optional[datetime]
    invoice_number: Optional[str]
    created_at: datetime