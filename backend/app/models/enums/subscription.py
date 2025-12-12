from enum import Enum

class PlanStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"

class SubscriptionType(str, Enum):
    STANDARD = "standard"
    CUSTOM = "custom"

class BillingCycle(str, Enum):
    MONTHLY = "monthly"
    ANNUAL = "annual"

class SubStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELED = "canceled"

class UpgradeType(str, Enum):
    STD_TO_STD = "standard_to_standard"
    STD_TO_CUSTOM = "standard_to_custom"
    CUSTOM_TO_CUSTOM = "custom_to_custom"

class Urgency(str, Enum):
    IMMEDIATE = "immediate"
    NEXT_CYCLE = "next_cycle"
    FLEXIBLE = "flexible"

class RequestStatus(str, Enum):
    PENDING = "pending"
    OFFER_SENT = "offer_sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    COMPLETED = "completed"

class OfferType(str, Enum):
    PRORATED = "prorated"
    CUSTOM_PRICE = "custom_price"
    DISCOUNT = "discount"
    FREE_DAYS = "free_days"

class OfferStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"

class TransactionType(str, Enum):
    SUBSCRIPTION = "subscription"
    UPGRADE = "upgrade"
    CREDIT = "credit"
    REFUND = "refund"

class TransactionStatus(str, Enum):
    SUCCEEDED = "succeeded"
    PENDING = "pending"
    FAILED = "failed"
