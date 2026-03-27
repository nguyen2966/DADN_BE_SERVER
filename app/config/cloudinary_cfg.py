import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
from dotenv import load_dotenv

# Tải các biến môi trường từ file .env vào hệ thống
load_dotenv()

# Lấy thông tin cấu hình từ biến môi trường
CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
API_KEY = os.getenv("CLOUDINARY_API_KEY")
API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

# Hàm khởi tạo cấu hình (chỉ chạy 1 lần khi file này được import - Singleton Pattern)
def init_cloudinary():
    if not CLOUD_NAME or CLOUD_NAME == "YOUR_CLOUD_NAME":
        print("Cảnh báo: Chưa cấu hình Cloudinary credentials trong file .env!")
        
    cloudinary.config(
        cloud_name=CLOUD_NAME,
        api_key=API_KEY,
        api_secret=API_SECRET,
        secure=True # Đảm bảo URL trả về luôn sử dụng HTTPS
    )
    print("Cloudinary đã được cấu hình thành công.")

# Tự động gọi hàm cấu hình khi module này được import lần đầu tiên
init_cloudinary()