from fastapi import FastAPI
from app.config.database import init_db_indexes
from app.routes import predict, trash_logs, auth 
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Smart Bin AI Backend")

origins = [
    "http://localhost:8080",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:8080",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],   
)

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