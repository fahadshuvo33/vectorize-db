from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, HttpUrl, UUID4, Field

# ============================================
# API KEYS
# ============================================
class APIKeyBase(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    is_active: bool = True

class APIKeyCreate(APIKeyBase):
    user_id: UUID4

class APIKeyUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None

class APIKeyInDB(APIKeyBase):
    id: UUID4
    user_id: UUID4
    key_hash: str  # bcrypt hash
    key_prefix: str  # first 8 chars for display
    last_rate_limit_reset: datetime
    requests_this_minute: int = 0
    created_at: datetime
    last_used: Optional[datetime] = None

    class Config:
        from_attributes = True

class APIKeyResponse(BaseModel):
    """Return this ONCE when key is created (includes plain key)"""
    id: UUID4
    name: str
    key: str  # Plain text (only shown once)
    key_prefix: str
    created_at: datetime

# ============================================
# WEBHOOKS
# ============================================
class WebhookBase(BaseModel):
    url: HttpUrl
    event_types: List[str] = Field(min_items=1)
    is_active: bool = True

class WebhookCreate(WebhookBase):
    user_id: UUID4

class WebhookUpdate(BaseModel):
    url: Optional[HttpUrl] = None
    event_types: Optional[List[str]] = None
    is_active: Optional[bool] = None

class WebhookInDB(WebhookBase):
    id: UUID4
    user_id: UUID4
    secret: str  # For webhook signature verification
    retry_count: int = 0
    last_triggered: Optional[datetime] = None
    last_success: Optional[datetime] = None
    last_error: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# ============================================
# API DB SUPPORT
# ============================================
class APIDBSupportBase(BaseModel):
    db_type: str
    api_version: str = "v1"
    is_supported: bool = True
    read_support: bool = True
    write_support: bool = False
    min_plan_required: Optional[str] = None
    features: Optional[dict] = None
    connection_info: Optional[dict] = None

class APIDBSupportCreate(APIDBSupportBase):
    pass

class APIDBSupportUpdate(BaseModel):
    is_supported: Optional[bool] = None
    read_support: Optional[bool] = None
    write_support: Optional[bool] = None
    min_plan_required: Optional[str] = None

class APIDBSupportInDB(APIDBSupportBase):
    id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True