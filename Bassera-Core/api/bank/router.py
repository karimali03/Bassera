from fastapi import APIRouter, status
from typing import List

from .controller import BankController
from .schemas import BankCreate, BankResponse, TransactionCreate, TransactionResponse

router = APIRouter(prefix="/bank", tags=["Bank"])
controller = BankController()

@router.post("/", response_model=BankResponse, status_code=status.HTTP_201_CREATED)
async def create_bank_profile(bank_in: BankCreate):
    return await controller.create_bank(bank_in)

@router.get("/{bank_id}", response_model=BankResponse)
async def get_bank_profile(bank_id: str):
    return await controller.get_bank(bank_id)

@router.post("/{bank_id}/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def add_transaction(bank_id: str, transaction_in: TransactionCreate):
    return await controller.add_transaction(bank_id, transaction_in)

@router.get("/{bank_id}/transactions", response_model=List[TransactionResponse])
async def get_transactions(bank_id: str):
    return await controller.get_transactions(bank_id)
