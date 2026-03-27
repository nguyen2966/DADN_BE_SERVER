from app.config.database import trash_logs_collection
from app.config.mqtt import aio_client

async def save_to_mongodb_observer(document: dict):
    """Nhiệm vụ: Lưu log vào MongoDB (Async)"""
    await trash_logs_collection.insert_one(document)
    print("Đã insert record trashlog vào DB")

def publish_mqtt_observer(label: str):
    """Nhiệm vụ: Publish lệnh điều khiển Servo lên Adafruit MQTT"""
    try:
        aio_client.send_data('smartbin-dot-command', label)
    except Exception as e:
        print(f"MQTT Publish Error: {e}")