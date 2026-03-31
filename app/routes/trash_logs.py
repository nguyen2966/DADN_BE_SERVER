from fastapi import APIRouter, Depends
from app.services.log_service import LogService

from app.core.security import get_current_user
router = APIRouter()

@router.get("/api/trash-logs")
async def get_logs_endpoint(limit: int = 10, current_user: dict = Depends(get_current_user)):
    print(current_user['id'] + " is demanding trash logs!")
    logs = await LogService.get_recent_logs(limit)
    return {"data": logs}