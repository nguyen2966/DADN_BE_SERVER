# Smart Bin AI Backend (FastAPI)

Đây là hệ thống Backend dành cho dự án Thùng rác thông minh (Smart Bin) tích hợp Trí tuệ Nhân tạo (AI) và Internet vạn vật (IoT). Hệ thống được xây dựng bằng **FastAPI**, chịu trách nhiệm nhận ảnh từ thiết bị vi điều khiển, phân loại rác bằng mô hình học sâu (Deep Learning), lưu trữ dữ liệu lên Cloud và điều khiển phần cứng thông qua giao thức MQTT.

## Tính năng nổi bật

* **Nhận diện AI Tốc độ cao:** Sử dụng TensorFlow/Keras và OpenCV để phân loại rác (Tái chế / Không tái chế) trực tiếp từ luồng ảnh nhị phân.
* **Xử lý Bất đồng bộ (Observer Pattern):** API phản hồi ngay lập tức cho phần cứng, trong khi các tác vụ nặng (lưu MongoDB, upload Cloudinary, gửi lệnh MQTT) được chạy ngầm bằng `BackgroundTasks`.
* **Quản lý thiết bị IoT:** Tích hợp trực tiếp với Adafruit IO (MQTT) để điều khiển động cơ Servo trên bo mạch YOLO:Bit.
* **Xác thực Bảo mật:** Hệ thống tài khoản người dùng với mã hóa mật khẩu (Bcrypt) và xác thực bằng JWT (JSON Web Token).
* **Lưu trữ Đám mây:** Kết nối tự động với MongoDB Atlas và nền tảng lưu trữ ảnh Cloudinary.

---

## Hướng dẫn Cài đặt & Chạy dự án

### 1. Yêu cầu hệ thống (Prerequisites)
* Python 3.9 trở lên.
* Đã có tài khoản: MongoDB Atlas, Cloudinary, và Adafruit IO.

### 2. Thiết lập môi trường
Tạo và kích hoạt môi trường ảo (Virtual Environment) để tránh xung đột thư viện:
```bash
# Tạo môi trường ảo (Windows/macOS/Linux)
python -m venv venv

# Kích hoạt trên Windows:
.\venv\Scripts\activate

# Kích hoạt trên macOS/Linux:
source venv/bin/activate
```

### 3. Cài đặt thư viện
Chạy lệnh sau để cài đặt toàn bộ thư viện cần thiết:

```bash
pip install -r requirements.txt
```

### 4. Cấu hình Biến môi trường (.env)
Tạo một file tên là .env ở thư mục gốc của dự án (ngang hàng với app/) và điền các thông tin của bạn vào:

Code snippet
# MongoDB Atlas
MONGO_URI="mongodb+srv://<username>:<password>@cluster0...mongodb.net/?retryWrites=true&w=majority"

# Cloudinary
CLOUDINARY_CLOUD_NAME=ten_cloud_cua_ban
CLOUDINARY_API_KEY=api_key_cua_ban
CLOUDINARY_API_SECRET=api_secret_cua_ban

# Adafruit IO (MQTT)
ADAFRUIT_IO_USERNAME=username_adafruit_cua_ban
ADAFRUIT_IO_KEY=key_adafruit_cua_ban

# JWT Secret (Tự tạo một chuỗi ngẫu nhiên bất kỳ)
JWT_SECRET=chuoi_ky_tu_bi_mat_cua_ban_123!@#
### 5. Nạp mô hình Trí tuệ Nhân tạo
Hệ thống cần mô hình nhận diện ảnh (TensorFlow/Keras).

Đổi tên file mô hình AI của bạn thành smartbin_model.h5.

Đặt file này vào thư mục gốc của dự án.
(Hoặc bạn có thể đổi đường dẫn trong file app/config/model_loader.py)

### 6. Khởi động Server
Chạy lệnh sau để bật server với chế độ tự động reload (hot-reload):

```Bash
uvicorn app.main:app --reload
```
Nếu terminal hiện dòng chữ "Pinged your deployment. You successfully connected to MongoDB Atlas!" nghĩa là mọi thứ đã hoàn hảo.

Tài liệu API (API Contract)
Hệ thống cung cấp sẵn tài liệu Interactive API (Swagger UI). Sau khi chạy server, bạn truy cập:
http://localhost:8000/docs

# Dưới đây là tóm tắt các API chính:

1. Phân loại & Điều khiển phần cứng (Edge API)
POST /predict

Mô tả: Nhận file ảnh (raw bytes) từ mạch ESP32-CAM.

Xử lý: Chạy AI Inference -> Trả kết quả JSON cho mạch -> Chạy ngầm Upload Cloudinary, Lưu MongoDB và Gửi lệnh MQTT xoay thùng rác.

Input: Form-data (file: Hình ảnh JPEG/PNG).

Auth: Không yêu cầu.

2. Quản lý Tài khoản (Auth)
POST /api/auth/register

Mô tả: Đăng ký tài khoản người dùng mới.

Input: JSON chứa fullName, email, password.

POST /api/auth/login

Mô tả: Đăng nhập và nhận Token.

Input: JSON chứa email, password.

Output: Chuỗi JWT Token.

3. Lịch sử & Thống kê (Dashboard)
GET /api/trash-logs

Mô tả: Lấy danh sách lịch sử các lần vứt rác gần nhất (Kèm nhãn, độ tin cậy AI, URL hình ảnh, thời gian).

Query Params: limit (Mặc định: 10 bản ghi).

Cấu trúc thư mục cốt lõi
Plaintext
.
├── app/
│   ├── config/          # Khởi tạo Singleton (DB, MQTT, Cloudinary, AI Model)
│   ├── core/            # Chứa các hàm Observer chạy ngầm (Background Tasks)
│   ├── models/          # Các schema Pydantic quy định cấu trúc dữ liệu khắt khe
│   ├── routes/          # Các endpoint nhận Request (Controller)
│   ├── services/        # Logic nghiệp vụ (AI, Auth, Database)
│   └── main.py          # File entry-point khởi chạy FastAPI
├── .env                 # File chứa các key bảo mật (Không push lên Git)
├── requirements.txt     # Danh sách thư viện Python
└── smartbin_model.h5    # File mô hình AI (TensorFlow)
