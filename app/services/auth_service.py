import os
import jwt
from datetime import datetime, timedelta, timezone
from app.config.database import users_collection
from app.models.user import UserCreate, verify_password

# Đọc Secret Key từ file .env (Giống như Cloudinary)
SECRET_KEY = os.getenv("JWT_SECRET", "chuoi_khoa_bi_mat_mac_dinh_cho_dev")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # Token có hạn 1 ngày

class AuthService:
    @staticmethod
    def create_access_token(data: dict):
        """Tạo JWT Token"""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    async def register_user(user_data: UserCreate) -> dict:
        """Logic Đăng ký: Kiểm tra email và lưu DB"""
        # 1. Kiểm tra email đã tồn tại chưa
        existing_user = await users_collection.find_one({"email": user_data.email})
        if existing_user:
            raise ValueError("Email already exists")

        # 2. Chuyển Pydantic model thành dictionary
        user_dict = user_data.model_dump()

        print(type(user_data.password), user_data.password)
        print(len(user_data.password.encode('utf-8')))
        
        # 3. Ghi đè password dạng plaintext bằng password đã băm (hash)
        user_dict["password"] = user_data.get_hashed_password()
        user_dict["createdAt"] = datetime.now(timezone.utc)
        
        # 4. Lưu vào MongoDB
        new_user = await users_collection.insert_one(user_dict)
        user_dict["id"] = str(new_user.inserted_id) # Gắn id dạng string để trả về
        
        return user_dict

    @staticmethod
    async def authenticate_user(email: str, password: str) -> dict:
        """Logic Đăng nhập: Tìm user và check password"""
        user = await users_collection.find_one({"email": email})
        if not user:
            return None
        
        # So sánh password nhập vào với mã hash trong DB
        if not verify_password(password, user["password"]):
            return None
            
        user["id"] = str(user["_id"])
        return user