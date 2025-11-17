from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, UUID4, Field, validator
from app.models.enums import OutputType

# ============================================
# FILE REQUESTS
# ============================================
class FileUploadRequest(BaseModel):
    """Metadata sent with file upload"""
    clean_data: bool = True
    remove_duplicates: bool = True
    fill_blanks: bool = False

class MeltRequest(BaseModel):
    """Convert file to AI-ready format"""
    file_id: str  # UUID as string
    output_types: List[OutputType] = [OutputType.VECTOR, OutputType.JSONL]
    embedding_model: Optional[str] = "all-MiniLM-L6-v2"
    text_columns: Optional[List[str]] = None

    @validator('output_types')
    def validate_output_types(cls, v):
        if not v:
            raise ValueError("At least one output type required")
        return v

class DownloadFileRequest(BaseModel):
    converted_file_id: str  # UUID as string
    output_type: Optional[OutputType] = None

# ============================================
# FILE RESPONSES
# ============================================
class FileUploadResponse(BaseModel):
    file_id: UUID4
    filename: str
    original_name: str
    size_bytes: int
    mime_type: str
    row_count: Optional[int] = None
    preview: Optional[List[dict]] = None  # First 5 rows
    detected_columns: Optional[List[str]] = None
    text_columns: Optional[List[str]] = None
    uploaded_at: datetime

class MeltResponse(BaseModel):
    """Immediate response when melt starts"""
    job_id: UUID4
    status: str = "processing"
    estimated_time_seconds: int

class MeltStatusResponse(BaseModel):
    """Poll this for progress"""
    job_id: UUID4
    status: str  # processing, completed, failed
    progress_percent: int = Field(ge=0, le=100)
    current_step: Optional[str] = None
    result: Optional["MeltResultResponse"] = None
    error: Optional[str] = None

class MeltResultResponse(BaseModel):
    """Final result after completion"""
    converted_file_id: UUID4
    output_type: OutputType
    filename: str
    row_count: int
    embedding_model: Optional[str] = None
    download_url: str
    expires_at: datetime
    chat_session_id: Optional[UUID4] = None

class ConversionStepResponse(BaseModel):
    step_order: int
    action: str
    details: dict
    created_at: datetime

class FileResponse(BaseModel):
    """Single file detail"""
    id: UUID4
    filename: str
    original_name: str
    size_bytes: int
    mime_type: str
    row_count: Optional[int] = None
    uploaded_at: datetime

class FileListResponse(BaseModel):
    """File with conversions"""
    file: FileResponse
    conversions: List["ConversionSummaryResponse"]

class ConversionSummaryResponse(BaseModel):
    id: UUID4
    output_type: OutputType
    filename: str
    row_count: int
    embedding_model: Optional[str] = None
    created_at: datetime