import asyncio

import pytest

import app.services.log_service as log_module
from app.services.log_service import LogService


class FakeCursor:
    def __init__(self, logs):
        self.logs = logs
        self.sort_args = None
        self.limit_value = None

    def sort(self, *args):
        self.sort_args = args
        return self

    def limit(self, limit):
        self.limit_value = limit
        return self

    async def to_list(self, length):
        return self.logs[:length]


class FakeTrashLogsCollection:
    def __init__(self, logs):
        self.logs = logs
        self.find_args = None
        self.cursor = FakeCursor(logs)

    def find(self, *args):
        self.find_args = args
        return self.cursor


class FakeOllamaResponse:
    def json(self):
        return {"response": "Lời khuyên AI mock."}


class FakeAsyncClient:
    def __init__(self, *args, **kwargs):
        self.timeout = kwargs.get("timeout")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False

    async def post(self, url, json):
        assert url == "http://localhost:11434/api/generate"
        assert json["model"] == "qwen2.5:3b"
        assert json["stream"] is False
        assert "prompt" in json
        return FakeOllamaResponse()


class FailingAsyncClient(FakeAsyncClient):
    async def post(self, url, json):
        raise RuntimeError("Ollama is down")


def test_get_recent_logs_returns_logs_sorted_by_thrown_at_desc(monkeypatch):
    logs = [
        {"label": "recycle", "thrownAt": "2026-01-02"},
        {"label": "non-recycle", "thrownAt": "2026-01-01"},
    ]
    fake_collection = FakeTrashLogsCollection(logs)

    monkeypatch.setattr(log_module, "trash_logs_collection", fake_collection)

    result = asyncio.run(LogService.get_recent_logs(limit=10))

    assert result == logs
    assert fake_collection.find_args == ({}, {"_id": 0})
    assert fake_collection.cursor.sort_args == ("thrownAt", -1)
    assert fake_collection.cursor.limit_value == 10


def test_get_health_advice_no_logs_returns_unknown(monkeypatch):
    async def fake_get_recent_logs(limit):
        return []

    monkeypatch.setattr(
        log_module.LogService,
        "get_recent_logs",
        staticmethod(fake_get_recent_logs),
    )

    result = asyncio.run(LogService.get_health_advice())

    assert result["recyclable_count"] == 0
    assert result["non_recyclable_count"] == 0
    assert result["ratio"] is None
    assert result["level"] == "unknown"
    assert "Chưa có dữ liệu" in result["advice"]


@pytest.mark.parametrize(
    "recycle_count, non_recycle_count, expected_ratio, expected_level",
    [
        (0, 2, None, "nguy cấp"),
        (1, 3, 3.0, "kém"),
        (2, 3, 1.5, "trung bình"),
        (10, 8, 0.8, "tốt"),
        (10, 7, 0.7, "rất tốt"),
    ],
)
def test_get_health_advice_level_by_ratio(
    monkeypatch,
    recycle_count,
    non_recycle_count,
    expected_ratio,
    expected_level,
):
    logs = [{"label": "recycle"} for _ in range(recycle_count)] + [
        {"label": "non-recycle"} for _ in range(non_recycle_count)
    ]

    async def fake_get_recent_logs(limit):
        return logs

    monkeypatch.setattr(
        log_module.LogService,
        "get_recent_logs",
        staticmethod(fake_get_recent_logs),
    )
    monkeypatch.setattr(log_module.httpx, "AsyncClient", FakeAsyncClient)

    result = asyncio.run(LogService.get_health_advice(limit=100))

    assert result["recyclable_count"] == recycle_count
    assert result["non_recyclable_count"] == non_recycle_count
    assert result["ratio"] == expected_ratio
    assert result["level"] == expected_level
    assert result["advice"] == "Lời khuyên AI mock."


def test_get_health_advice_ollama_error_returns_fallback_advice(monkeypatch):
    logs = [
        {"label": "recycle"},
        {"label": "non-recycle"},
    ]

    async def fake_get_recent_logs(limit):
        return logs

    monkeypatch.setattr(
        log_module.LogService,
        "get_recent_logs",
        staticmethod(fake_get_recent_logs),
    )
    monkeypatch.setattr(log_module.httpx, "AsyncClient", FailingAsyncClient)

    result = asyncio.run(LogService.get_health_advice(limit=100))

    assert result["level"] == "tốt"
    assert result["advice"] == "Không thể tạo lời khuyên từ AI tại thời điểm hiện tại."
