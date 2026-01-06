# app/models/base.py
import uuid
from datetime import datetime
from sqlmodel import SQLModel, Field
from app.utils import utc_now

# UUID Generator
def generate_uuid():
    return str(uuid.uuid4())

class BaseModel(SQLModel):
    """
    Base model that includes UUID primary key and timestamp fields.
    Inherit from this instead of SQLModel for your tables.
    """
    
    id: str = Field(
        default_factory=generate_uuid, 
        primary_key=True, 
        index=True,
        nullable=False
    )

    created_at: datetime = Field(default_factory=utc_now)

    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_column_kwargs={
            "onupdate": utc_now
        }
    )