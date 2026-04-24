from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.subscriber import start_subscriber
from app.telemetry import setup_telemetry
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(start_subscriber())
    yield
    task.cancel()

app = FastAPI(title="Fraud Detection Service", version="1.0.0", lifespan=lifespan)

setup_telemetry(app)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "fraud-service"}