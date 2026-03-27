from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from app.models.user import UserCreate, UserResponse
from app.services.auth_service import AuthService

router = APIRouter()

# Model phụ dùng để nhận body của request Login
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
async def register_endpoint(user: UserCreate):
    try:
        # Gọi service xử lý logic
        created_user = await AuthService.register_user(user)
        
        # Ép kiểu dữ liệu trả về qua UserResponse để tự động ẩn field 'password'
        user_response = UserResponse(**created_user)
        
        return {
            "message": "Đăng ký thành công",
            "user": user_response
        }
    except ValueError as e:
        # Bắt lỗi "Email already exists" từ service
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/auth/login")
async def login_endpoint(credentials: LoginRequest):
    # Xác thực người dùng
    user = await AuthService.authenticate_user(credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Tạo Token chứa ID và Email
    access_token = AuthService.create_access_token(
        data={"sub": user["email"], "id": str(user["id"])}
    )
    
    # Loại bỏ password trước khi trả về
    user_response = UserResponse(**user)
    
    return {
        "token": access_token,
        "user": user_response
    }