from fastapi import APIRouter, Depends, HTTPException, status
from app.models import LoginRequest, TokenResponse
from app.database import get_connection
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 60))

def create_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=EXPIRE_MINUTES)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, conn=Depends(get_connection)):
    cursor = await conn.cursor()
    await cursor.execute(
        "SELECT id, password_hash FROM accounts WHERE email = ?",
        request.email
    )
    row = await cursor.fetchone()
    if not row or not pwd_context.verify(request.password, row[1]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    token = create_token({"sub": row[0], "email": request.email})
    return TokenResponse(access_token=token)