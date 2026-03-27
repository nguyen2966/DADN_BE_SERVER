from fastapi import FastAPI
from app.config.database import init_db_indexes
from app.routes import predict, trash_logs, auth 

app = FastAPI(title="Smart Bin AI Backend")

@app.on_event("startup")
async def startup_db_client():
    await init_db_indexes()

# Mount các Router
app.include_router(auth.router, tags=["Authentication"]) 
app.include_router(predict.router, tags=["AI Prediction"])
app.include_router(trash_logs.router, tags=["Trash Logs"])

@app.get("/")
def health_check():
    return {"status": "System is running smoothly"}