from contextlib import asynccontextmanager
from fastapi import FastAPI
from kafka_consumer import run_in_background

@asynccontextmanager
async def lifespan(app: FastAPI):
    run_in_background()
    print("🚀 AI Fraud Detector started")
    yield

app = FastAPI(title="Fair-Ticket AI Fraud Detector", lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "ok"}