from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt # Thư viện PyJWT hoặc python-jose
import os

# Khai báo scheme, URL này để Swagger UI biết nơi lấy token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

SECRET_KEY = os.getenv("JWT_SECRET", "chuoi_khoa_bi_mat_mac_dinh_cho_dev") # Nên lấy từ biến môi trường (.env)
ALGORITHM = "HS256"

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Dependency này tự động lấy token từ header 'Authorization: Bearer <token>',
    giải mã và xác thực. Nếu hợp lệ, trả về thông tin user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Giải mã token đã tạo ở hàm login_endpoint
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_id: str = payload.get("id")
        
        if email is None or user_id is None:
            raise credentials_exception
            
        # Tùy chọn: Bạn có thể query DB ở đây để check xem user còn tồn tại/bị khóa không
        # user = await db.get_user(user_id)
        
        return {"email": email, "id": user_id}
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise credentials_exception