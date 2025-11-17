from enum import Enum

class PlanType(str, Enum):
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    BUSINESS = "business"
    CUSTOM = "custom"

class SessionType(str, Enum):
    USER = "user"
    APP_BOT = "app_bot"

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class OutputType(str, Enum):
    VECTOR = "vector"
    JSONL = "jsonl"
    PARQUET = "parquet"
    RAG_CODE = "rag_code"

class PaymentStatus(str, Enum):
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"

class DiscountType(str, Enum):
    PERCENT = "percent"
    FIXED = "fixed"

class RewardType(str, Enum):
    DISCOUNT = "discount"
    FREE_MONTH = "free_month"
    CREDITS = "credits"
    CASH = "cash"

class RewardStatus(str, Enum):
    PENDING = "pending"
    APPLIED = "applied"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class NotificationType(str, Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    UPGRADE_OFFER = "upgrade_offer"
    FEATURE_ANNOUNCEMENT = "feature_announcement"

class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_RESPONSE = "waiting_response"
    RESOLVED = "resolved"
    CLOSED = "closed"

class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TicketCategory(str, Enum):
    BILLING = "billing"
    TECHNICAL = "technical"
    FEATURE_REQUEST = "feature_request"
    BUG = "bug"
    OTHER = "other"

class EmailStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    BOUNCED = "bounced"

class ChangeType(str, Enum):
    NEW = "new"
    UPGRADE = "upgrade"
    CANCEL = "cancel"

class ProrationOption(str, Enum):
    IMMEDIATE_CHARGE = "immediate_charge"
    NEXT_CYCLE = "next_cycle"

class CancellationType(str, Enum):
    IMMEDIATE = "immediate"
    END_OF_CYCLE = "end_of_cycle"

class RefundEligibility(str, Enum):
    FULL = "full"
    PARTIAL_50 = "partial_50"
    NONE = "none"

class FeatureCategory(str, Enum):
    LIMITS = "limits"
    ACCESS = "access"
    API = "api"
    BOT = "bot"
    ADVANCED = "advanced"

class ValueType(str, Enum):
    NUMBER = "number"
    BOOLEAN = "boolean"
    STRING = "string"
    JSON = "json"