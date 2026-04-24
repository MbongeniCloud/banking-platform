from fastapi import APIRouter, Depends, HTTPException, status
from app.models import AccountCreate, AccountResponse
from app.database import get_connection
from passlib.context import CryptContext
from datetime import datetime
import uuid

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(data: AccountCreate, conn=Depends(get_connection)):
    account_id = str(uuid.uuid4())
    password_hash = pwd_context.hash("changeme123")
    cursor = await conn.cursor()
    await cursor.execute(
        "INSERT INTO accounts (id, owner_name, email, password_hash, account_type, balance) VALUES (?, ?, ?, ?, ?, ?)",
        account_id, data.owner_name, data.email,
        password_hash, data.account_type.value, float(data.initial_deposit)
    )
    await conn.commit()
    return AccountResponse(
        id=account_id,
        owner_name=data.owner_name,
        email=data.email,
        account_type=data.account_type,
        balance=data.initial_deposit,
        created_at=datetime.utcnow(),
        is_active=True
    )

@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(account_id: str, conn=Depends(get_connection)):
    cursor = await conn.cursor()
    await cursor.execute("SELECT * FROM accounts WHERE id = ?", account_id)
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Account not found")
    return AccountResponse(
        id=row[0],
        owner_name=row[1],
        email=row[2],
        account_type=row[4],
        balance=row[5],
        created_at=row[7],
        is_active=bool(row[6])
    )