from app.config.database import trash_logs_collection

class LogService:
    @staticmethod
    async def get_recent_logs(limit: int):
        cursor = trash_logs_collection.find({}, {"_id": 0}).sort("thrownAt", -1).limit(limit)
        return await cursor.to_list(length=limit)