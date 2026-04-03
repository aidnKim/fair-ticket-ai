from contextlib import asynccontextmanager
from fastapi import FastAPI
from kafka_consumer import run_in_background, blocked_users
from detector import feature_extractor

@asynccontextmanager
async def lifespan(app: FastAPI):
    run_in_background()
    print("🚀 AI Fraud Detector started")
    yield

app = FastAPI(title="Fair-Ticket AI Fraud Detector", lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/reset")
def reset():
    """새 티켓팅 세션 시작 시 상태 초기화"""
    blocked_users.clear()
    feature_extractor.user_history.clear()
    return {"status": "reset", "message": "blocked_users and user_history cleared"}
