from fastapi import APIRouter
from app.services.log_service import LogService

router = APIRouter()

@router.get("/api/trash-logs")
async def get_logs_endpoint(limit: int = 10):
    logs = await LogService.get_recent_logs(limit)
    return {"data": logs}