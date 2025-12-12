from enum import Enum


class NotificationType(str, Enum):
    EMAIL = "email"
    IN_APP = "in_app"
    PUSH = "push" # Future proofing

class NotificationCategory(str, Enum):
    ACCOUNT = "account"       # Password reset, login
    BILLING = "billing"       # Invoice paid, payment failed
    SYSTEM = "system"         # Maintenance, updates
    PROMOTION = "promotion"   # Offers, coupons

class EmailStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"