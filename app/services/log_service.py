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
 
        recyclable     = sum(1 for log in logs if log.get("is_recyclable") is True)
        non_recyclable = sum(1 for log in logs if log.get("is_recyclable") is False)
        total          = recyclable + non_recyclable
 
        # Avoid division-by-zero when there are no logs yet
        if total == 0:
            return {
                "recyclable_count":     0,
                "non_recyclable_count": 0,
                "ratio":                None,
                "level":                "unknown",
                "advice":               "No waste data available yet. Start logging to receive personalised advice.",
            }
 
        ratio = non_recyclable / recyclable if recyclable > 0 else float("inf")
 
        # ── Advice tiers ──────────────────────────────────────────────────────
        if ratio == float("inf"):
            level  = "critical"
            advice = (
                "All of your logged waste is non-recyclable. "
                "Try to replace single-use plastics and food packaging with "
                "reusable or compostable alternatives."
            )
        elif ratio >= 3:
            level  = "poor"
            advice = (
                f"Your non-recyclable waste is {ratio:.1f}× your recyclable waste — "
                "this is quite high. Consider auditing your most common waste types "
                "and switching to products with eco-friendly packaging."
            )
        elif ratio >= 1.5:
            level  = "moderate"
            advice = (
                f"Your non-recyclable ratio is {ratio:.1f}×. You're making some effort, "
                "but there's room to improve. Look for recyclable substitutes for your "
                "top non-recyclable items."
            )
        elif ratio >= 0.8:
            level  = "good"
            advice = (
                f"Good balance! Your non-recyclable ratio is {ratio:.1f}×. "
                "Keep it up and try to reduce overall waste volume."
            )
        else:
            level  = "excellent"
            advice = (
                f"Excellent! Your recyclable waste far outweighs non-recyclable ({ratio:.1f}×). "
                "Share your habits with others and aim for zero-waste milestones."
            )
 
        return {
            "recyclable_count":     recyclable,
            "non_recyclable_count": non_recyclable,
            "ratio":                round(ratio, 2) if ratio != float("inf") else None,
            "level":                level,
            "advice":               advice,
        }