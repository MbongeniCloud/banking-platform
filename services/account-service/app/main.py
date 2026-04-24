from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import init_db
from app.routes import accounts, auth
from app.telemetry import setup_telemetry

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="Account Service", version="1.0.0", lifespan=lifespan)

setup_telemetry(app)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(accounts.router, prefix="/accounts", tags=["accounts"])

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "account-service"}
