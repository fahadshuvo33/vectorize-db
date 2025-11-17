"""
Schemas for DBMelt API
Organized by domain (mirrors models structure)
"""

# Common
from .common import (
    SuccessResponse,
    ErrorResponse,
    MessageResponse,
    PaginationParams,
    PaginatedResponse,
    HealthCheckResponse
)

# User
from .user import (
    # Requests
    SignupRequest,
    LoginRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
    UpdateProfileRequest,
    # Responses
    UserResponse,
    AuthResponse,
    ProfileResponse,
    UsageResponse,
    UsageStatsResponse
)

# File
from .file import (
    # Requests
    FileUploadRequest,
    MeltRequest,
    DownloadFileRequest,
    # Responses
    FileUploadResponse,
    MeltResponse,
    MeltStatusResponse,
    MeltResultResponse,
    ConversionStepResponse,
    FileResponse,
    FileListResponse,
    ConversionSummaryResponse
)

# Chat
from .chat import (
    # Requests
    StartChatRequest,
    SendMessageRequest,
    UpdateChatTitleRequest,
    # Responses
    ChatSessionResponse,
    ChatMessageResponse,
    SendMessageResponse,
    ChatHistoryResponse,
    ChatListResponse
)

# Subscription
from .subscription import (
    # Requests
    UpgradePlanRequest,
    CancelSubscriptionRequest,
    ApplyDiscountRequest,
    CreateDiscountCodeRequest,
    # Responses
    FeatureResponse,
    PlanResponse,
    SubscriptionResponse,
    UpgradeQuoteResponse,
    DiscountValidationResponse,
    DiscountCodeResponse,
    ReferralStatsResponse,
    RewardResponse
)

# Support
from .support import (
    # Requests
    CreateTicketRequest,
    ReplyTicketRequest,
    UpdateTicketRequest,
    MarkNotificationReadRequest,
    # Responses
    TicketResponse,
    TicketMessageResponse,
    TicketDetailResponse,
    TicketListResponse,
    NotificationResponse,
    NotificationCountResponse,
    EmailTemplateResponse,
    EmailLogResponse
)

# API
from .api import (
    # Requests
    CreateAPIKeyRequest,
    UpdateAPIKeyRequest,
    CreateWebhookRequest,
    UpdateWebhookRequest,
    TestWebhookRequest,
    # Responses
    APIKeyCreateResponse,
    APIKeyResponse,
    APIUsageResponse,
    WebhookResponse,
    WebhookEventResponse,
    WebhookTestResponse,
    APIDBSupportResponse
)

# Dashboard
from .dashboard import (
    UpgradeBannerResponse,
    DashboardStatsResponse,
    DashboardResponse,
    QuickStatsResponse
)

# Admin
from .admin import (
    # Requests
    GrantFeatureRequest,
    AdminUserSearchRequest,
    AdminUpdateUserRequest,
    # Responses
    AdminStatsResponse,
    RevenueStatsResponse,
    UserDetailResponse,
    UserStatsResponse,
    ActivityLogResponse,
    AdminUserListResponse
)

__all__ = [
    # Common
    "SuccessResponse",
    "ErrorResponse",
    "MessageResponse",
    "PaginationParams",
    "PaginatedResponse",
    "HealthCheckResponse",
    # User
    "SignupRequest",
    "LoginRequest",
    "ResetPasswordRequest",
    "ChangePasswordRequest",
    "UpdateProfileRequest",
    "UserResponse",
    "AuthResponse",
    "ProfileResponse",
    "UsageResponse",
    "UsageStatsResponse",
    # File
    "FileUploadRequest",
    "MeltRequest",
    "DownloadFileRequest",
    "FileUploadResponse",
    "MeltResponse",
    "MeltStatusResponse",
    "MeltResultResponse",
    "ConversionStepResponse",
    "FileResponse",
    "FileListResponse",
    "ConversionSummaryResponse",
    # Chat
    "StartChatRequest",
    "SendMessageRequest",
    "UpdateChatTitleRequest",
    "ChatSessionResponse",
    "ChatMessageResponse",
    "SendMessageResponse",
    "ChatHistoryResponse",
    "ChatListResponse",
    # Subscription
    "UpgradePlanRequest",
    "CancelSubscriptionRequest",
    "ApplyDiscountRequest",
    "CreateDiscountCodeRequest",
    "FeatureResponse",
    "PlanResponse",
    "SubscriptionResponse",
    "UpgradeQuoteResponse",
    "DiscountValidationResponse",
    "DiscountCodeResponse",
    "ReferralStatsResponse",
    "RewardResponse",
    # Support
    "CreateTicketRequest",
    "ReplyTicketRequest",
    "UpdateTicketRequest",
    "MarkNotificationReadRequest",
    "TicketResponse",
    "TicketMessageResponse",
    "TicketDetailResponse",
    "TicketListResponse",
    "NotificationResponse",
    "NotificationCountResponse",
    "EmailTemplateResponse",
    "EmailLogResponse",
    # API
    "CreateAPIKeyRequest",
    "UpdateAPIKeyRequest",
    "CreateWebhookRequest",
    "UpdateWebhookRequest",
    "TestWebhookRequest",
    "APIKeyCreateResponse",
    "APIKeyResponse",
    "APIUsageResponse",
    "WebhookResponse",
    "WebhookEventResponse",
    "WebhookTestResponse",
    "APIDBSupportResponse",
    # Dashboard
    "UpgradeBannerResponse",
    "DashboardStatsResponse",
    "DashboardResponse",
    "QuickStatsResponse",
    # Admin
    "GrantFeatureRequest",
    "AdminUserSearchRequest",
    "AdminUpdateUserRequest",
    "AdminStatsResponse",
    "RevenueStatsResponse",
    "UserDetailResponse",
    "UserStatsResponse",
    "ActivityLogResponse",
    "AdminUserListResponse",
]