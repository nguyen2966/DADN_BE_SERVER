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

## 1. Phân loại & Điều khiển phần cứng (Edge API)
POST /predict

Mô tả: Nhận file ảnh (raw bytes) từ mạch ESP32-CAM.

Xử lý: Chạy AI Inference -> Trả kết quả JSON cho mạch -> Chạy ngầm Upload Cloudinary, Lưu MongoDB và Gửi lệnh MQTT xoay thùng rác.

Input: Form-data (file: Hình ảnh JPEG/PNG).

Auth: Không yêu cầu.

## 2. Quản lý Tài khoản (Auth)
POST /api/auth/register

Mô tả: Đăng ký tài khoản người dùng mới.

Input: JSON chứa fullName, email, password.

POST /api/auth/login

Mô tả: Đăng nhập và nhận Token.

Input: JSON chứa email, password.

Output: Chuỗi JWT Token.

## 3. Lịch sử & Thống kê (Dashboard)
GET /api/trash-logs

Mô tả: Lấy danh sách lịch sử các lần vứt rác gần nhất (Kèm nhãn, độ tin cậy AI, URL hình ảnh, thời gian).

Query Params: limit (Mặc định: 10 bản ghi).

## 4. Lời khuyên sức khỏe / sống xanh

**GET** `/api/trash-logs/health-advice`

**Mô tả:**
Phân tích lịch sử phân loại rác gần nhất để tính tỷ lệ giữa rác tái chế và rác không tái chế. Dựa trên tỷ lệ này, hệ thống đánh giá mức độ thói quen sống xanh của người dùng và gọi AI thông qua Ollama để tạo lời khuyên phù hợp.

**Query Params:**

| Tham số | Kiểu dữ liệu | Bắt buộc | Mặc định | Mô tả                                            |
| ------- | ------------ | -------: | -------: | ------------------------------------------------ |
| `limit` | `number`     |    Không |    `100` | Số lượng bản ghi gần nhất được dùng để phân tích |

**Response trả về gồm:**

| Trường                 | Kiểu dữ liệu     | Mô tả                                                                                              |
| ---------------------- | ---------------- | -------------------------------------------------------------------------------------------------- |
| `recyclable_count`     | `number`         | Số lượng rác tái chế                                                                               |
| `non_recyclable_count` | `number`         | Số lượng rác không tái chế                                                                         |
| `ratio`                | `number \| null` | Tỷ lệ rác không tái chế trên rác tái chế                                                           |
| `level`                | `string`         | Mức đánh giá thói quen sống xanh, gồm `unknown`, `nguy cấp`, `kém`, `trung bình`, `tốt`, `rất tốt` |
| `advice`               | `string`         | Lời khuyên được tạo bởi AI dựa trên dữ liệu thống kê                                               |

**Ví dụ response:**

```json
{
  "recyclable_count": 8,
  "non_recyclable_count": 12,
  "ratio": 1.5,
  "level": "trung bình",
  "advice": "Bạn đang có thói quen phân loại rác ở mức trung bình. Hãy cố gắng giảm lượng rác không tái chế bằng cách ưu tiên sử dụng sản phẩm có thể tái chế hoặc tái sử dụng."
}
```


# Cấu trúc thư mục cốt lõi
```Plaintext
.
├── venv/                # Chứa các package cần thiết
├── app/
│   ├── config/          # Khởi tạo Singleton (DB, MQTT, Cloudinary, AI Model)
│   ├── core/            # Chứa các hàm Observer chạy ngầm (Background Tasks)
│   ├── models/          # Các schema Pydantic quy định cấu trúc dữ liệu khắt khe
│   ├── routes/          # Các endpoint nhận Request (Controller)
│   ├── services/        # Logic nghiệp vụ (AI, Auth, Database)
│   └── main.py          # File entry-point khởi chạy FastAPI
├── .env                 # File chứa các key bảo mật (Không push lên Git)
├── requirements.txt     # Danh sách thư viện Python
```

# Unit tests for Smart Bin Backend

## Mô tả tổng quan về 19 unit test

Hệ thống được xây dựng với tổng cộng **19 unit test**, tập trung vào ba service chính: **AI Service**, **Authentication Service** và **Log Service**. Trong đó, AI Service có 5 test case, Authentication Service có 6 test case và Log Service có 8 test case.

Các unit test này được thiết kế để kiểm tra những chức năng cốt lõi của từng service. Với AI Service, các test tập trung vào xử lý ảnh hợp lệ, ảnh không hợp lệ, bước tiền xử lý ảnh, upload ảnh và luồng phân loại hoàn chỉnh. Với Authentication Service, các test kiểm tra đăng ký tài khoản, xử lý email trùng, đăng nhập đúng/sai thông tin và tạo JWT token. Với Log Service, các test kiểm tra truy vấn lịch sử, xử lý trường hợp không có dữ liệu, phân loại mức độ dựa trên tỷ lệ recycle/non-recycle và xử lý lỗi khi Ollama không phản hồi.

Các test này là hợp lý vì chúng bao phủ cả **luồng thành công** và **luồng lỗi** của hệ thống. Những thành phần bên ngoài như mô hình AI, Cloudinary, MongoDB và Ollama đều được mock, giúp bài kiểm thử chỉ tập trung vào logic nội bộ của service. Nhờ đó, kết quả test ổn định, chạy nhanh và không phụ thuộc vào môi trường bên ngoài.


## Chạy test
Đứng ở thư mục gốc `smart-bin-backend` rồi chạy:

```bash
python -m pytest app/test -q
```

## Ghi chú

- `test_ai_service.py` mock `app.config.model_loader` trước khi import `AIService`, nên pytest sẽ không load file `clean_model.keras` thật.
- Các async test dùng `asyncio.run(...)`, nên không cần cài thêm `pytest-asyncio`.
## Kết quả mong đợi
```
...................                                                                                                               
19 passed in 0.62s
```