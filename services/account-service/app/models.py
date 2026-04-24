from pydantic import BaseModel, EmailStr
from decimal import Decimal
from datetime import datetime
from enum import Enum

class AccountType(str, Enum):
    SAVINGS = "savings"
    CHEQUE = "cheque"
    BUSINESS = "business"

class AccountCreate(BaseModel):
    owner_name: str
    email: EmailStr
    account_type: AccountType
    initial_deposit: Decimal = Decimal("0.00")

class AccountResponse(BaseModel):
    id: str
    owner_name: str
    email: str
    account_type: AccountType
    balance: Decimal
    created_at: datetime
    is_active: bool

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
