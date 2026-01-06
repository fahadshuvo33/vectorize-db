"""
Schemas for VectorizeDB API
Organized by domain (mirrors models structure)
"""


from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    SetPasswordRequest,
    ChangePasswordRequest,
    RefreshTokenRequest,
    ResendVerificationRequest,
    TokensResponse,
    AuthResponse,
    OAuthURLResponse,
)
from app.schemas.user import (
    UserResponse,
    UserProfileResponse,
    UpdateProfileRequest,
    LinkedAccountsResponse,
    SocialAccountResponse,
    ChangeEmailRequest,
    DeleteAccountRequest,
)


# Notification
from .notification import (
    TemplateBase,
    TemplateCreate,
    TemplateUpdate,
    TemplateRead,
    InAppNotificationRead,
    InAppNotificationUpdate,
    EmailLogRead,
)

# Subscription
from .subscription import (
    PlanBase,
    PlanCreate,
    PlanUpdate,
    PlanRead,
    CustomPlanBase,
    CustomPlanCreate,
    CustomPlanUpdateAdmin,
    CustomPlanRead,
    SubscriptionRead,
    SubUsageRead,
    UpgradeRequestCreate,
    UpgradeRequestRead,
    UpgradeOfferCreate,
    UpgradeOfferRead,
    UpgradeOfferResponse,
    BillingHistoryRead,
)

# Support
from .support import (
    TicketMessageBase,
    TicketMessageCreate,
    TicketMessageRead,
    SupportTicketBase,
    SupportTicketCreate,
    SupportTicketUpdate,
    SupportTicketRead,
    SupportTicketChatRead,
    AppReviewCreate,
    AppReviewRead
)

"""
All Pydantic schemas (request/response models).
"""

__all__ = [
    # Common
    "MessageResponse",
    "PaginatedResponse",
    # Auth
    "RegisterRequest",
    "LoginRequest",
    "ForgotPasswordRequest",
    "ResetPasswordRequest",
    "SetPasswordRequest",
    "ChangePasswordRequest",
    "RefreshTokenRequest",
    "ResendVerificationRequest",
    "TokensResponse",
    "AuthResponse",
    "OAuthURLResponse",
    # User
    "UserResponse",
    "UserProfileResponse",
    "UpdateProfileRequest",
    "LinkedAccountsResponse",
    "SocialAccountResponse",
]

