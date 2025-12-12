from enum import Enum


# -------------------------------------------
# ENUMS
# -------------------------------------------
class TicketCategory(str, Enum):
    GENERAL = "general"
    BUG = "bug"
    FEATURE_REQUEST = "feature_request"
    BILLING = "billing"
    ACCOUNT_DELETION = "account_deletion"

class TicketStatus(str, Enum):
    OPEN = "open"             # User created it
    IN_PROGRESS = "in_progress" # Admin replied
    WAITING_ON_USER = "waiting_on_user"
    RESOLVED = "resolved"
    CLOSED = "closed"

class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SenderType(str, Enum):
    USER = "user"
    SUPPORT_AGENT = "support_agent"
    SYSTEM = "system" # e.g. auto-reply