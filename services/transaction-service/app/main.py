from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import init_db
from app.routes import transactions
from app.telemetry import setup_telemetry

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="Transaction Service", version="1.0.0", lifespan=lifespan)

setup_telemetry(app)

app.include_router(transactions.router, prefix="/transactions", tags=["transactions"])

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "transaction-service"}