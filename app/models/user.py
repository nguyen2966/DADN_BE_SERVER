from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime, timezone
from passlib.context import CryptContext

# Khởi tạo context mã hóa mật khẩu bằng bcrypt (Tương đương bcryptjs trong Node)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Schema gốc chứa các field chung
class UserBase(BaseModel):
    fullName: str = Field(..., min_length=1, description="Full name is required")
    email: EmailStr = Field(..., description="Valid email is required")

# Schema dùng khi nhận request đăng ký từ client
class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")
    
    # Hàm băm mật khẩu trước khi lưu
    def get_hashed_password(self) -> str:
        return pwd_context.hash(self.password)

# Schema dùng để map với dữ liệu lưu trong MongoDB
class UserInDB(UserBase):
    password: str # Lưu password đã được mã hóa
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Schema dùng để trả về API (Loại bỏ password, tương tự transform toJSON của Mongoose)
class UserResponse(UserBase):
    id: str # FastAPI thường dùng 'id' kiểu string thay cho '_id' kiểu ObjectId để dễ parse JSON
    createdAt: datetime
    
    # Cho phép Pydantic tự động map '_id' từ MongoDB sang 'id'
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

# Hàm tiện ích để so sánh mật khẩu khi đăng nhập
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)