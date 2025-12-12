
from datetime import datetime, date
from typing import Optional, List,TYPE_CHECKING

# SQLModel imports
from sqlmodel import Field, Relationship, UniqueConstraint, Index
# SQLAlchemy specific imports for complex types
from sqlalchemy import Column, Enum , Numeric
from app.models.base import BaseModel 
from decimal import Decimal
# -------------------------------------------
# UTILITIES & ENUMS
# -------------------------------------------
from app.models.enums.subscription import (
    PlanStatus,
    SubscriptionType,
    BillingCycle,
    SubStatus,
    UpgradeType,
    Urgency,
    RequestStatus,
    OfferType,
    OfferStatus,
    TransactionType,
    TransactionStatus
)
if TYPE_CHECKING:
    from app.models.user import Profile
# -------------------------------------------
# MODELS
# -------------------------------------------

class Plan(BaseModel, table=True):
    __tablename__ = "plans"
    
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    
    monthly_price: Decimal = Field(sa_column=Column(Numeric(10, 2)))
    annual_price: Optional[float] = None
    
    file_limit: int
    row_limit: int
    daily_convert: int
    api_access: bool = Field(default=False)
    priority_support: bool = Field(default=False)
    
    display_order: Optional[int] = None
    is_active: bool = Field(default=True)
    icon_color: Optional[str] = Field(default=None, max_length=50)
    
    
    # Relationships
    subscriptions: List["Subscription"] = Relationship(back_populates="plan")
    
    # Complex relationships require sa_relationship_kwargs in SQLModel when dealing with multiple FKs
    upgrade_requests_from: List["UpgradeRequest"] = Relationship(
        back_populates="from_plan",
        sa_relationship_kwargs={"foreign_keys": "UpgradeRequest.from_plan_id"}
    )
    upgrade_requests_to: List["UpgradeRequest"] = Relationship(
        back_populates="to_plan",
        sa_relationship_kwargs={"foreign_keys": "UpgradeRequest.to_plan_id"}
    )


class CustomPlan(BaseModel, table=True):
    __tablename__ = "custom_plans"
    
    user_id: str = Field(foreign_key="profiles.id", max_length=50)
    
    plan_name: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=500)
    
    file_limit: int
    row_limit: int
    daily_convert: int
    api_access: bool = Field(default=False)
    priority_support: bool = Field(default=False)
    
    requested_price: float
    approved_price: Optional[float] = None
    annual_price: Optional[float] = None
    
    # Using sa_column for Enum to ensure database level constraints
    status: PlanStatus = Field(
        sa_column=Column(Enum(PlanStatus), default=PlanStatus.DRAFT)
    )
    
    admin_notes: Optional[str] = Field(default=None, max_length=500)
    reviewed_by: Optional[str] = Field(default=None, max_length=50)
    reviewed_at: Optional[datetime] = None
    
    is_active: bool = Field(default=False)

    
    # Relationships
    user: Optional["Profile"] = Relationship(back_populates="custom_plans")
    subscriptions: List["Subscription"] = Relationship(back_populates="custom_plan")
    
    upgrade_requests_from: List["UpgradeRequest"] = Relationship(
        back_populates="from_custom_plan",
        sa_relationship_kwargs={"foreign_keys": "UpgradeRequest.from_custom_plan_id"}
    )
    upgrade_requests_to: List["UpgradeRequest"] = Relationship(
        back_populates="to_custom_plan",
        sa_relationship_kwargs={"foreign_keys": "UpgradeRequest.to_custom_plan_id"}
    )


class Subscription(BaseModel, table=True):
    __tablename__ = "subscriptions"
    # Table Args for Constraints
    __table_args__ = (
        Index(
            "idx_unique_active_subscription",
            "user_id",
            unique=True,
            postgresql_where=text("status = 'ACTIVE'")
        ),
    )
    
    user_id: str = Field(foreign_key="profiles.id", max_length=50)
    
    plan_id: Optional[str] = Field(default=None, foreign_key="plans.id", max_length=50)
    custom_plan_id: Optional[str] = Field(default=None, foreign_key="custom_plans.id", max_length=50)
    
    subscription_type: SubscriptionType = Field(sa_column=Column(Enum(SubscriptionType), nullable=False))
    
    monthly_price: Decimal = Field(sa_column=Column(Numeric(10, 2)))
    annual_price: Optional[float] = None
    
    billing_start_date: date
    billing_end_date: date
    billing_cycle: BillingCycle = Field(sa_column=Column(Enum(BillingCycle), default=BillingCycle.MONTHLY))
    auto_renew: bool = Field(default=True)
    
    status: SubStatus = Field(sa_column=Column(Enum(SubStatus), default=SubStatus.ACTIVE))
    
    last_upgrade_request_id: Optional[str] = Field(default=None, max_length=50)
    last_upgrade_at: Optional[datetime] = None
    
    
    # Relationships
    user: Optional["Profile"] = Relationship(back_populates="subscriptions")
    plan: Optional["Plan"] = Relationship(back_populates="subscriptions")
    custom_plan: Optional["CustomPlan"] = Relationship(back_populates="subscriptions")
    usage: List["SubscriptionUsage"] = Relationship(back_populates="subscription")
    upgrade_requests: List["UpgradeRequest"] = Relationship(back_populates="subscription")
    billing_history: List["BillingHistory"] = Relationship(back_populates="subscription")


class SubscriptionUsage(BaseModel, table=True):
    __tablename__ = "subscription_usage"
    __table_args__ = (
        UniqueConstraint("subscription_id", "usage_date", name="unique_sub_date"),
        Index("idx_user_date", "user_id", "usage_date"),
    )
    
    subscription_id: str = Field(foreign_key="subscriptions.id", max_length=50)
    user_id: str = Field(foreign_key="profiles.id", max_length=50)
    
    files_used: int = Field(default=0)
    rows_used: int = Field(default=0)
    daily_converts_used: int = Field(default=0)
    api_calls_used: int = Field(default=0)
    
    files_remaining: Optional[int] = None
    rows_remaining: Optional[int] = None
    daily_convert_remaining: Optional[int] = None
    
    usage_date: date
    last_daily_reset: Optional[datetime] = None
    last_monthly_reset: Optional[datetime] = None

    
    # Relationships
    subscription: Optional["Subscription"] = Relationship(back_populates="usage")
    user: Optional["Profile"] = Relationship(back_populates="subscription_usage")


class UpgradeRequest(BaseModel, table=True):
    __tablename__ = "upgrade_requests"
    __table_args__ = (
        Index("idx_req_status", "status"),
        Index("idx_req_user_id", "user_id"),
        Index("idx_req_created_at", "created_at"),
    )
    
    user_id: str = Field(foreign_key="profiles.id", max_length=50)
    subscription_id: str = Field(foreign_key="subscriptions.id", max_length=50)
    
    from_plan_id: Optional[str] = Field(default=None, foreign_key="plans.id", max_length=50)
    from_custom_plan_id: Optional[str] = Field(default=None, foreign_key="custom_plans.id", max_length=50)
    
    to_plan_id: Optional[str] = Field(default=None, foreign_key="plans.id", max_length=50)
    to_custom_plan_id: Optional[str] = Field(default=None, foreign_key="custom_plans.id", max_length=50)
    
    upgrade_type: UpgradeType = Field(sa_column=Column(Enum(UpgradeType), nullable=False))
    
    reason: Optional[str] = Field(default=None, max_length=255)
    urgency: Urgency = Field(sa_column=Column(Enum(Urgency), default=Urgency.FLEXIBLE))
    status: RequestStatus = Field(sa_column=Column(Enum(RequestStatus), default=RequestStatus.PENDING))
    
    admin_reviewed_at: Optional[datetime] = None
    offer_sent_at: Optional[datetime] = None
    user_responded_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Relationships
    user: Optional["Profile"] = Relationship(back_populates="upgrade_requests")
    subscription: Optional["Subscription"] = Relationship(back_populates="upgrade_requests")
    
    # Explicit Relationship definitions for multiple FKs
    from_plan: Optional[Plan] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[UpgradeRequest.from_plan_id]"},
        back_populates="upgrade_requests_from"
    )
    to_plan: Optional[Plan] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[UpgradeRequest.to_plan_id]"},
        back_populates="upgrade_requests_to"
    )
    from_custom_plan: Optional[CustomPlan] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[UpgradeRequest.from_custom_plan_id]"},
        back_populates="upgrade_requests_from"
    )
    to_custom_plan: Optional[CustomPlan] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[UpgradeRequest.to_custom_plan_id]"},
        back_populates="upgrade_requests_to"
    )
    
    offers: List["UpgradeOffer"] = Relationship(back_populates="upgrade_request")


class UpgradeOffer(BaseModel, table=True):
    __tablename__ = "upgrade_offers"
    __table_args__ = (
        Index("idx_offer_status", "status"),
        Index("idx_request_id", "upgrade_request_id"),
    )
    
    upgrade_request_id: str = Field(foreign_key="upgrade_requests.id", max_length=50)
    
    offer_type: OfferType = Field(sa_column=Column(Enum(OfferType), nullable=False))
    
    current_plan_price: Optional[float] = None
    new_plan_price: Optional[float] = None
    
    # Added back days_remaining which was missing in your last snippet
    days_remaining: Optional[int] = None
    days_in_cycle: Optional[int] = None
    
    credit_balance: Optional[float] = None
    credit_applied: Optional[float] = None
    charge_amount: Optional[float] = None
    
    discount_percentage: int = Field(default=0)
    discount_reason: Optional[str] = Field(default=None, max_length=255)
    bonus_free_days: int = Field(default=0)
    
    admin_notes: Optional[str] = Field(default=None, max_length=500)
    calculated_by: Optional[str] = Field(default=None, max_length=50)
    
    valid_until: Optional[datetime] = None
    status: OfferStatus = Field(sa_column=Column(Enum(OfferStatus), default=OfferStatus.PENDING))
    
    user_decision: Optional[str] = Field(default=None, max_length=50)
    user_response_at: Optional[datetime] = None
    user_notes: Optional[str] = Field(default=None, max_length=500)
    
    # Relationships
    upgrade_request: Optional["UpgradeRequest"] = Relationship(back_populates="offers")
    billing_history: List["BillingHistory"] = Relationship(back_populates="upgrade_offer")


class BillingHistory(BaseModel, table=True):
    __tablename__ = "billing_history"
    __table_args__ = (
        Index("idx_bill_user_date", "user_id", "created_at"),
        Index("idx_bill_status", "status"),
        Index("idx_bill_subscription_id", "subscription_id"),
    )
    
    user_id: str = Field(foreign_key="profiles.id", max_length=50)
    subscription_id: Optional[str] = Field(default=None, foreign_key="subscriptions.id", max_length=50)
    
    upgrade_request_id: Optional[str] = Field(default=None, foreign_key="upgrade_requests.id", max_length=50)
    upgrade_offer_id: Optional[str] = Field(default=None, foreign_key="upgrade_offers.id", max_length=50)
    
    amount: Decimal = Field(sa_column=Column(Numeric(10, 2)))
    
    transaction_type: TransactionType = Field(sa_column=Column(Enum(TransactionType), nullable=False))
    
    payment_processor: Optional[str] = Field(default=None, max_length=50)
    processor_transaction_id: Optional[str] = Field(default=None, max_length=255)
    invoice_number: Optional[str] = Field(default=None, max_length=50)
    
    status: TransactionStatus = Field(sa_column=Column(Enum(TransactionStatus), default=TransactionStatus.PENDING))
    
    paid_at: Optional[datetime] = None
    
    # Relationships
    user: Optional["Profile"] = Relationship(back_populates="billing_history")
    subscription: Optional["Subscription"] = Relationship(back_populates="billing_history")
    upgrade_offer: Optional["UpgradeOffer"] = Relationship(back_populates="billing_history")

