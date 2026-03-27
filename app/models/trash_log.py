from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal
from datetime import datetime, timezone

class TrashLogBase(BaseModel):
    label: Literal['recycle', 'non-recycle'] = Field(
        ..., 
        description='"recycle" hoặc "non-recycle"'
    )
    confidence: Optional[float] = Field(
        default=None, 
        ge=0.0, le=1.0, 
        description="Độ tin cậy AI, giá trị 0.0 – 1.0"
    )
    imageUrl: Optional[str] = Field(
        default=None, 
        description="URL ảnh trên Cloudinary"
    )

class TrashLogCreate(TrashLogBase):
    thrownAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), 
        description="Thời điểm bỏ rác (từ sensor trigger)"
    )

class TrashLogInDB(TrashLogBase):
    thrownAt: datetime

class TrashLogResponse(TrashLogBase):
    id: str # Tương đương _id (ObjectId)
    thrownAt: datetime
    
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)