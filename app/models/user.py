from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime, timezone
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserBase(BaseModel):
    fullName: str = Field(..., description="Họ và tên đầy đủ")
    email: EmailStr = Field(..., description="Unique, dùng để đăng nhập")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="bcrypt hash, không lưu plaintext")
    
    def get_hashed_password(self) -> str:
        return pwd_context.hash(self.password)

class UserInDB(UserBase):
    password: str
    createdAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), 
        description="Auto-generated"
    )

class UserResponse(UserBase):
    id: str # Tương đương _id (ObjectId)
    createdAt: datetime
    
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)