from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal
from datetime import datetime, timezone

# Schema gốc
class TrashLogBase(BaseModel):
    # Ràng buộc enum y hệt Mongoose
    label: Literal['recycle', 'non-recycle'] = Field(..., description="Label must be 'recycle' or 'non-recycle'")
    # Ràng buộc min=0, max=1
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    imageUrl: Optional[str] = Field(default=None)

# Schema dùng khi AI Server gọi POST /api/trash-logs
class TrashLogCreate(TrashLogBase):
    thrownAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Schema dùng để lưu vào Database
class TrashLogInDB(TrashLogBase):
    thrownAt: datetime
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Schema dùng để trả về API cho Frontend
class TrashLogResponse(TrashLogBase):
    id: str
    thrownAt: datetime
    createdAt: datetime
    
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)