import sys
import types

import cv2
import numpy as np
import pytest


class DummyModel:
    def __init__(self, predictions):
        self.predictions = np.array(predictions, dtype=float)
        self.last_input = None

    def predict(self, img_batch):
        self.last_input = img_batch
        return self.predictions

fake_model_loader = types.ModuleType("app.config.model_loader")
fake_model_loader.model = DummyModel([[0.2, 0.8]])
fake_model_loader.LABELS = ["non-recycle", "recycle"]
sys.modules["app.config.model_loader"] = fake_model_loader

# Avoid Cloudinary config side effects during import.
fake_cloudinary_cfg = types.ModuleType("app.config.cloudinary_cfg")
sys.modules["app.config.cloudinary_cfg"] = fake_cloudinary_cfg

# Avoid observer side effects during import.
fake_observers = types.ModuleType("app.core.observers")

def fake_save_to_mongodb_observer(log_document):
    return None


def fake_publish_mqtt_observer(label):
    return None

fake_observers.save_to_mongodb_observer = fake_save_to_mongodb_observer
fake_observers.publish_mqtt_observer = fake_publish_mqtt_observer
sys.modules["app.core.observers"] = fake_observers

# Avoid depending on real cloudinary package/config in unit tests.
fake_cloudinary = types.ModuleType("cloudinary")
fake_uploader = types.ModuleType("cloudinary.uploader")

def fake_upload(*args, **kwargs):
    return {"secure_url": "https://example.com/default.png"}

fake_uploader.upload = fake_upload
fake_cloudinary.uploader = fake_uploader
sys.modules["cloudinary"] = fake_cloudinary
sys.modules["cloudinary.uploader"] = fake_uploader

import app.services.ai_service as ai_module
from app.services.ai_service import AIService


def make_image_bytes(ext: str = ".jpg") -> bytes:
    """Create a valid test image as bytes."""
    image = np.zeros((60, 80, 3), dtype=np.uint8)
    image[:, :] = (10, 120, 240)

    ok, buffer = cv2.imencode(ext, image)
    assert ok is True

    return buffer.tobytes()


def test_process_and_predict_valid_image_returns_label_and_confidence(monkeypatch):
    dummy_model = DummyModel([[0.25, 0.75]])

    monkeypatch.setattr(ai_module, "model", dummy_model)
    monkeypatch.setattr(ai_module, "LABELS", ["recycle", "non-recycle"])

    label, confidence = AIService.process_and_predict(make_image_bytes(".png"))

    assert label == "non-recycle"
    assert confidence == pytest.approx(0.75)


def test_process_and_predict_invalid_image_raises_error():
    with pytest.raises(ValueError, match="Invalid image format"):
        AIService.process_and_predict(b"this-is-not-an-image")


def test_process_and_predict_preprocesses_image_to_expected_shape_and_range(monkeypatch):
    dummy_model = DummyModel([[0.90, 0.10]])

    monkeypatch.setattr(ai_module, "model", dummy_model)
    monkeypatch.setattr(ai_module, "LABELS", ["recycle", "non-recycle"])

    AIService.process_and_predict(make_image_bytes(".jpg"))

    assert dummy_model.last_input is not None
    assert dummy_model.last_input.shape == (1, 150, 150, 3)
    assert dummy_model.last_input.min() >= 0.0
    assert dummy_model.last_input.max() <= 1.0


class FakeBackgroundTasks:
    def __init__(self):
        self.tasks = []

    def add_task(self, func, *args, **kwargs):
        self.tasks.append((func, args, kwargs))


def test_handle_trash_detection_returns_result_and_adds_background_tasks(monkeypatch):
    file_bytes = make_image_bytes(".jpg")
    background_tasks = FakeBackgroundTasks()

    def fake_process_and_predict(received_bytes):
        assert received_bytes == file_bytes
        return "recycle", 0.88

    def fake_cloudinary_upload(received_bytes, folder):
        assert received_bytes == file_bytes
        assert folder == "smart_bin"
        return {"secure_url": "https://res.cloudinary.com/demo/image.jpg"}

    def fake_save_observer(log_document):
        return None

    def fake_mqtt_observer(label):
        return None

    monkeypatch.setattr(
        ai_module.AIService,
        "process_and_predict",
        staticmethod(fake_process_and_predict),
    )
    monkeypatch.setattr(ai_module.cloudinary.uploader, "upload", fake_cloudinary_upload)
    monkeypatch.setattr(ai_module, "save_to_mongodb_observer", fake_save_observer)
    monkeypatch.setattr(ai_module, "publish_mqtt_observer", fake_mqtt_observer)

    result = AIService.handle_trash_detection(file_bytes, background_tasks)

    assert result == {
        "label": "recycle",
        "confidence": 0.88,
        "imageUrl": "https://res.cloudinary.com/demo/image.jpg",
    }

    assert len(background_tasks.tasks) == 2

    save_task_func, save_task_args, _ = background_tasks.tasks[0]
    mqtt_task_func, mqtt_task_args, _ = background_tasks.tasks[1]

    assert save_task_func is fake_save_observer
    assert save_task_args[0]["label"] == "recycle"
    assert save_task_args[0]["confidence"] == 0.88
    assert save_task_args[0]["imageUrl"] == "https://res.cloudinary.com/demo/image.jpg"
    assert "thrownAt" in save_task_args[0]

    assert mqtt_task_func is fake_mqtt_observer
    assert mqtt_task_args == ("recycle",)


def test_handle_trash_detection_returns_image_url_when_cloudinary_upload_success(monkeypatch):
    file_bytes = make_image_bytes(".jpg")
    background_tasks = FakeBackgroundTasks()

    monkeypatch.setattr(
        ai_module.AIService,
        "process_and_predict",
        staticmethod(lambda _: ("non-recycle", 0.91)),
    )
    monkeypatch.setattr(
        ai_module.cloudinary.uploader,
        "upload",
        lambda *_args, **_kwargs: {"secure_url": "https://example.com/uploaded.png"},
    )

    result = AIService.handle_trash_detection(file_bytes, background_tasks)

    assert result["imageUrl"] == "https://example.com/uploaded.png"
