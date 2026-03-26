import cv2
import numpy as np
import cloudinary.uploader
from datetime import datetime, timezone
from app.config.model_loader import model, LABELS
from app.core.observers import save_to_mongodb_observer, publish_mqtt_observer
from fastapi import BackgroundTasks

class AIService:
    @staticmethod
    def process_and_predict(file_bytes: bytes) -> tuple:
        """Decode ảnh, tiền xử lý và chạy AI Inference"""
        np_arr = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Invalid image format")

        img_resized = cv2.resize(img, (150, 150))
        img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
        img_normalized = img_rgb / 255.0
        img_batch = np.expand_dims(img_normalized, axis=0)

        predictions = model.predict(img_batch)
        predicted_idx = np.argmax(predictions[0])
        
        return LABELS[predicted_idx], float(predictions[0][predicted_idx])

    @staticmethod
    def handle_trash_detection(file_bytes: bytes, device_id: str, background_tasks: BackgroundTasks) -> dict:
        """Luồng chính: Nhận ảnh -> Phân loại -> Upload -> Kích hoạt Observers"""
        # 1. AI Phân loại
        label, confidence = AIService.process_and_predict(file_bytes)

        # 2. Upload Cloudinary (Chạy đồng bộ để lấy URL ngay)
        upload_result = cloudinary.uploader.upload(file_bytes, folder="smart_bin")
        image_url = upload_result.get("secure_url")

        # 3. Chuẩn bị dữ liệu lưu DB
        log_document = {
            "label": label,
            "confidence": confidence,
            "imageUrl": image_url,
            "device_id": device_id,
            "thrownAt": datetime.now(timezone.utc)
        }

        # 4. Kích hoạt Observers (Background Tasks)
        background_tasks.add_task(save_to_mongodb_observer, log_document)
        background_tasks.add_task(publish_mqtt_observer, label)

        return {
            "label": label,
            "confidence": confidence,
            "imageUrl": image_url
        }