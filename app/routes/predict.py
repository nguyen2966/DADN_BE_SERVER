from fastapi import APIRouter, File, Form, BackgroundTasks, HTTPException
from app.services.ai_service import AIService

router = APIRouter()

@router.post("/predict")
async def predict_endpoint(
    background_tasks: BackgroundTasks,
    file: bytes = File(...)
):
    try:
        # Route gọi xuống Service, truyền BackgroundTasks để xử lý side-effects
        result = AIService.handle_trash_detection(file, background_tasks)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))