from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime
from enum import Enum
import uuid
from app.database import get_container
from app.messaging import publish_transaction_event

router = APIRouter()

class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"

class TransactionCreate(BaseModel):
    account_id: str
    amount: Decimal
    transaction_type: TransactionType
    description: str = ""
    to_account_id: str = None

class TransactionResponse(BaseModel):
    id: str
    account_id: str
    amount: Decimal
    transaction_type: TransactionType
    description: str
    status: str
    created_at: datetime

@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(data: TransactionCreate, container=Depends(get_container)):
    transaction_id = str(uuid.uuid4())
    transaction = {
        "id": transaction_id,
        "account_id": data.account_id,
        "amount": str(data.amount),
        "transaction_type": data.transaction_type.value,
        "description": data.description,
        "to_account_id": data.to_account_id,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    }
    await container.create_item(body=transaction)
    await publish_transaction_event(transaction)
    return TransactionResponse(
        id=transaction_id,
        account_id=data.account_id,
        amount=data.amount,
        transaction_type=data.transaction_type,
        description=data.description,
        status="pending",
        created_at=datetime.utcnow()
    )

@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: str, container=Depends(get_container)):
    try:
        item = await container.read_item(item=transaction_id, partition_key=transaction_id)
        return TransactionResponse(
            id=item["id"],
            account_id=item["account_id"],
            amount=Decimal(item["amount"]),
            transaction_type=item["transaction_type"],
            description=item["description"],
            status=item["status"],
            created_at=datetime.fromisoformat(item["created_at"])
        )
    except Exception:
        raise HTTPException(status_code=404, detail="Transaction not found")