from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

class TransactionBase(BaseModel):
    merchant: str
    category: str
    amount: float
    currency: str = "EGP"
    type: str  # e.g., "DEBIT", "CREDIT"
    note: Optional[str] = None
    timestamp: datetime

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    transaction_id: str

class BankCreate(BaseModel):
    bank_id: str

class BankResponse(BaseModel):
    id: str = Field(alias="_id")
    bank_id: str
    balance: float = 0.0
    transactions: List[TransactionResponse] = []

    class Config:
        populate_by_name = True
