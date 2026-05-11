from fastapi import APIRouter, Depends
from app.services.log_service import LogService

from app.core.security import get_current_user
router = APIRouter()

@router.get("/api/trash-logs")
async def get_logs_endpoint(limit: int = 10, current_user: dict = Depends(get_current_user)):
    print(current_user['id'] + " is demanding trash logs!")
    logs = await LogService.get_recent_logs(limit)
    return {"data": logs}


@router.get("/api/trash-logs/health-advice")
async def get_health_advice_endpoint(
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze recent trash logs and return health advice based on the
    ratio of non-recyclable to recyclable waste.
    """
    advice = await LogService.get_health_advice(limit)
    return {"data": advice}