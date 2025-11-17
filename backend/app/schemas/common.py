from datetime import datetime
from typing import Optional, List, Any, TypeVar, Generic
from pydantic import BaseModel, Field

T = TypeVar('T')

# ============================================
# STANDARD RESPONSES
# ============================================
class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[dict] = None

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    code: Optional[str] = None
    details: Optional[dict] = None

class MessageResponse(BaseModel):
    message: str

# ============================================
# PAGINATION
# ============================================
class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool

    @staticmethod
    def create(items: List[T], total: int, params: PaginationParams):
        total_pages = (total + params.page_size - 1) // params.page_size
        return PaginatedResponse(
            items=items,
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=total_pages,
            has_next=params.page < total_pages,
            has_prev=params.page > 1
        )

# ============================================
# HEALTH CHECK
# ============================================
class HealthCheckResponse(BaseModel):
    status: str = "healthy"
    timestamp: datetime
    version: str
    services: dict  # {"supabase": "ok", "r2": "ok"}