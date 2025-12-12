# app/models/base.py
import uuid
from datetime import datetime
from sqlmodel import SQLModel, Field

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
        max_length=50
    )
    
    created_at: datetime = Field(default_factory=datetime.now())
    
    updated_at: datetime = Field(
        default_factory=datetime.now(), 
        sa_column_kwargs={"onupdate": datetime.now()}
    )