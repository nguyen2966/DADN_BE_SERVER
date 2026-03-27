import os
import pymongo
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

# Load biến môi trường từ .env
load_dotenv()

# Lấy URI từ .env, nếu không có thì fallback về localhost để dev offline
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

# Khởi tạo Motor Client với cấu hình ServerApi cho Atlas
client = AsyncIOMotorClient(MONGO_URI, server_api=ServerApi('1'))

# MongoDB sẽ tự tạo db và collections khi có dữ liệu chèn vào
db = client.smartbin_db
trash_logs_collection = db.trash_logs
users_collection = db.users

async def init_db_indexes():
    """Hàm chạy lúc khởi động server để test kết nối và tạo index"""
    try:
        # Gửi 1 lệnh ping để test kết nối (Giống code mẫu của Atlas)
        await client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB Atlas!")
        
        # Tạo index cho TrashLog
        await trash_logs_collection.create_index([("thrownAt", pymongo.DESCENDING)])
        await trash_logs_collection.create_index([
            ("label", pymongo.ASCENDING), 
            ("thrownAt", pymongo.DESCENDING)
        ])
        
        # Tạo index cho User
        await users_collection.create_index("email", unique=True)
        
        print("MongoDB Indexes ensured.")
    except Exception as e:
        print(f"Lỗi kết nối MongoDB Atlas: {e}")