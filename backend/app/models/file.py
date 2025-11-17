from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, UUID4, Field
from .enums import OutputType

# ============================================
# FILES ORIGINAL
# ============================================
class FileOriginalBase(BaseModel):
    filename: str
    original_name: str
    size_bytes: int = Field(ge=0)
    mime_type: str

class FileOriginalCreate(FileOriginalBase):
    user_id: UUID4
    storage_path: str

class FileOriginalInDB(FileOriginalBase):
    id: UUID4
    user_id: UUID4
    storage_path: str
    uploaded_at: datetime

    class Config:
        from_attributes = True

# ============================================
# FILES CONVERTED
# ============================================
class FileConvertedBase(BaseModel):
    filename: str
    output_type: OutputType
    embedding_model: Optional[str] = None
    row_count: Optional[int] = Field(None, ge=0)
    config_snapshot: Optional[dict] = None

class FileConvertedCreate(FileConvertedBase):
    user_id: UUID4
    original_file_id: UUID4
    storage_path: str

class FileConvertedInDB(FileConvertedBase):
    id: UUID4
    user_id: UUID4
    original_file_id: UUID4
    storage_path: str
    created_at: datetime

    class Config:
        from_attributes = True

# ============================================
# CONVERSION STEPS
# ============================================
class ConversionStepBase(BaseModel):
    step_order: int = Field(ge=1)
    action: str
    details: Optional[dict] = None

class ConversionStepCreate(ConversionStepBase):
    converted_file_id: UUID4

class ConversionStepInDB(ConversionStepBase):
    id: UUID4
    converted_file_id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True