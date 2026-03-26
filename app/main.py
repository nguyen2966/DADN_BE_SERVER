from fastapi import FastAPI
from app.routes import predict, trash_logs

# Init app
app = FastAPI(title="Smart Bin AI Backend")

# Mount các Router
app.include_router(predict.router, tags=["AI Prediction"])
app.include_router(trash_logs.router, tags=["Trash Logs"])

@app.get("/")
def health_check():
    return {"status": "System is running smoothly"}