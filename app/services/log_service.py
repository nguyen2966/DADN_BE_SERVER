from app.config.database import trash_logs_collection
import httpx

class LogService:
    @staticmethod
    async def get_recent_logs(limit: int):
        cursor = trash_logs_collection.find({}, {"_id": 0}).sort("thrownAt", -1).limit(limit)
        return await cursor.to_list(length=limit)
    
    @staticmethod
    async def get_health_advice(limit: int = 100) -> dict:
        logs = await LogService.get_recent_logs(limit)

        recyclable = sum(1 for log in logs if log.get("label") == "recycle")

        non_recyclable = sum(1 for log in logs if log.get("label") == "non-recycle")

        total = recyclable + non_recyclable

        if total == 0:
            return {
                "recyclable_count": 0,
                "non_recyclable_count": 0,
                "ratio": None,
                "level": "unknown",
                "advice": (
                    "Chưa có dữ liệu rác thải nào. "
                    "Hãy bắt đầu ghi nhận để nhận lời khuyên phù hợp."
                ),
            }

        ratio = (
            non_recyclable / recyclable
            if recyclable > 0
            else float("inf")
        )

        # ===== LEVEL =====
        if ratio == float("inf"):
            level = "nguy cấp"
        elif ratio >= 3:
            level = "kém"
        elif ratio >= 1.5:
            level = "trung bình"
        elif ratio >= 0.8:
            level = "tốt"
        else:
            level = "rất tốt"

        # ===== PROMPT =====
        prompt = f"""
            Bạn là AI coach về lối sống xanh.

            Dữ liệu:
            - Rác tái chế: {recyclable}
            - Rác không tái chế: {non_recyclable}
            - Mức đánh giá: {level}

            Yêu cầu:
            - Trả lời hoàn toàn bằng tiếng Việt.
            - Dùng markdown để hiển thị đẹp hơn.
            - Không bịa số liệu mới.
            - Không đưa tuyên bố y khoa mạnh.
            - Giọng văn thân thiện và tích cực.
            - Độ dài khoảng 100 từ.

            Hãy:
            1. Đánh giá ngắn gọn thói quen sống xanh.
            2. Đưa ra 1 lời khuyên thực tế.
            """

        # ===== CALL OLLAMA =====
        try:
            print("CALLING OLLAMA")
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": "qwen2.5:3b",
                        "prompt": prompt,
                        "stream": False
                    },
                )

            data = response.json()

            ai_advice = data.get("response", "").strip()

        except Exception as e:
            print(e)
            ai_advice = (
                "Không thể tạo lời khuyên từ AI tại thời điểm hiện tại."
            )

        return {
            "recyclable_count": recyclable,
            "non_recyclable_count": non_recyclable,
            "ratio": round(ratio, 2)
                if ratio != float("inf")
                else None,
            "level": level,
            "advice": ai_advice,
        }