from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, HttpUrl, UUID4, Field, validator

# ============================================
# API KEY REQUESTS
# ============================================
class CreateAPIKeyRequest(BaseModel):
    name: str = Field(min_length=3, max_length=100)

class UpdateAPIKeyRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    is_active: Optional[bool] = None

# ============================================
# API KEY RESPONSES
# ============================================
class APIKeyCreateResponse(BaseModel):
    """Only time the plain key is shown"""
    id: UUID4
    name: str
    key: str  # dbm_xxxxxxxxxxxxxxxxx (plain text)
    key_prefix: str
    created_at: datetime
    warning: str = "⚠️ Save this key! It won't be shown again."

class APIKeyResponse(BaseModel):
    """List view (no plain key)"""
    id: UUID4
    name: str
    key_prefix: str  # dbm_xxxxxxxx****
    is_active: bool
    created_at: datetime
    last_used: Optional[datetime] = None

class APIUsageResponse(BaseModel):
    api_key_id: UUID4
    requests_today: int
    requests_this_month: int
    rate_limit_per_minute: int
    remaining_this_minute: int
    resets_at: datetime

# ============================================
# WEBHOOK REQUESTS
# ============================================
class CreateWebhookRequest(BaseModel):
    url: HttpUrl
    event_types: List[str] = Field(min_items=1, max_items=10)

    @validator('event_types')
    def validate_event_types(cls, v):
        allowed = {
            "file.uploaded", "file.converted", "chat.started",
            "chat.message", "subscription.created", "subscription.updated",
            "subscription.canceled", "payment.succeeded", "payment.failed"
        }
        invalid = set(v) - allowed
        if invalid:
            raise ValueError(f"Invalid event types: {invalid}")
        return v

class UpdateWebhookRequest(BaseModel):
    url: Optional[HttpUrl] = None
    event_types: Optional[List[str]] = None
    is_active: Optional[bool] = None

class TestWebhookRequest(BaseModel):
    webhook_id: str  # UUID as string
    event_type: str

# ============================================
# WEBHOOK RESPONSES
# ============================================
class WebhookResponse(BaseModel):
    id: UUID4
    url: HttpUrl
    event_types: List[str]
    is_active: bool
    retry_count: int
    last_triggered: Optional[datetime] = None
    last_success: Optional[datetime] = None
    last_error: Optional[str] = None
    created_at: datetime

class WebhookEventResponse(BaseModel):
    """Payload sent to webhook URL"""
    event_id: UUID4
    event_type: str
    timestamp: datetime
    data: dict
    signature: str  # HMAC-SHA256 for verification

class WebhookTestResponse(BaseModel):
    success: bool
    status_code: Optional[int] = None
    response_time_ms: Optional[int] = None
    error: Optional[str] = None

# ============================================
# API DB SUPPORT RESPONSES
# ============================================
class APIDBSupportResponse(BaseModel):
    db_type: str
    api_version: str
    is_supported: bool
    read_support: bool
    write_support: bool
    min_plan_required: Optional[str] = None
    features: Optional[dict] = None
    connection_example: Optional[dict] = None