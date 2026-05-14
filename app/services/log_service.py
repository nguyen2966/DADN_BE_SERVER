from app.config.database import trash_logs_collection

class LogService:
    @staticmethod
    async def get_recent_logs(limit: int):
        cursor = trash_logs_collection.find({}, {"_id": 0}).sort("thrownAt", -1).limit(limit)
        return await cursor.to_list(length=limit)
    
    @staticmethod
    async def get_health_advice(limit: int = 100) -> dict:
        """
        Fetch recent logs, compute the non-recyclable / recyclable ratio,
        and return a structured health-advice payload.
        """
        logs = await LogService.get_recent_logs(limit)
 
        recyclable     = sum(1 for log in logs if log.get("label") == "recycle")
        non_recyclable = sum(1 for log in logs if not log.get("label") == "recycle")
        total          = recyclable + non_recyclable
 
        # Avoid division-by-zero when there are no logs yet
        if total == 0:
            return {
                "recyclable_count":     0,
                "non_recyclable_count": 0,
                "ratio":                None,
                "level":                "unknown",
                "advice":               "Chưa có dữ liệu rác thải nào. Hãy bắt đầu ghi nhận để nhận lời khuyên phù hợp.",
            }
 
        ratio = non_recyclable / recyclable if recyclable > 0 else float("inf")
 
        # ── Advice tiers ──────────────────────────────────────────────────────
        if ratio == float("inf"):
            level  = "critical"
            advice = (
                "Toàn bộ rác thải của bạn đều là rác không thể tái chế. "
                "Hãy thử thay thế đồ nhựa dùng một lần và bao bì thực phẩm "
                "bằng các sản phẩm có thể tái sử dụng hoặc phân hủy sinh học."
            )
        elif ratio >= 3:
            level  = "poor"
            advice = (
                f"Lượng rác không thể tái chế của bạn gấp {ratio:.1f} lần rác có thể tái chế — "
                "tỉ lệ này khá cao. Hãy xem xét lại các loại rác phổ biến nhất của bạn "
                "và chuyển sang sử dụng sản phẩm có bao bì thân thiện với môi trường."
            )
        elif ratio >= 1.5:
            level  = "moderate"
            advice = (
                f"Tỉ lệ rác không thể tái chế của bạn là {ratio:.1f} lần. Bạn đang có những nỗ lực nhất định, "
                "nhưng vẫn còn nhiều điều có thể cải thiện. Hãy tìm kiếm các sản phẩm thay thế "
                "có thể tái chế cho những loại rác không tái chế phổ biến nhất của bạn."
            )
        elif ratio >= 0.8:
            level  = "good"
            advice = (
                f"Tỉ lệ khá tốt! Lượng rác không thể tái chế của bạn gấp {ratio:.1f} lần rác tái chế. "
                "Hãy duy trì thói quen này và cố gắng giảm thêm tổng lượng rác thải."
            )
        else:
            level  = "excellent"
            advice = (
                f"Xuất sắc! Lượng rác tái chế của bạn vượt trội hơn hẳn rác không tái chế (tỉ lệ {ratio:.1f} lần). "
                "Hãy chia sẻ thói quen tốt này với mọi người xung quanh và hướng tới mục tiêu không rác thải."
            )
 
        return {
            "recyclable_count":     recyclable,
            "non_recyclable_count": non_recyclable,
            "ratio":                round(ratio, 2) if ratio != float("inf") else None,
            "level":                level,
            "advice":               advice,
        }