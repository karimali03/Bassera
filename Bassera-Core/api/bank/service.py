from fastapi import HTTPException, status
from typing import List
import uuid

from .repository import BankRepository
from .schemas import BankCreate, TransactionCreate, BankResponse, TransactionResponse
from .models import BankModel, TransactionModel

class BankService:
    def __init__(self):
        self.repository = BankRepository()

    async def create_bank(self, obj_in: BankCreate) -> dict:
        existing_bank = await self.repository.get_bank_by_bank_id(obj_in.bank_id)
        if existing_bank:
            raise HTTPException(status_code=400, detail="Bank profile already exists for this user")
        
        bank_model = BankModel(bank_id=obj_in.bank_id, transactions=[])
        bank_data = bank_model.model_dump(by_alias=True)
        # remove generated ObjectId string for Motor to generate cleanly, or keep model's ID
        
        return await self.repository.create_bank(bank_data)

    async def get_bank(self, bank_id: str) -> dict:
        bank = await self.repository.get_bank_by_bank_id(bank_id)
        if not bank:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bank profile not found")
        return bank

    async def add_transaction(self, bank_id: str, obj_in: TransactionCreate) -> dict:
        # Check if bank exists
        await self.get_bank(bank_id)
        
        # Add generated id to transaction object
        transaction_id = str(uuid.uuid4())
        transaction_data = obj_in.model_dump()
        transaction_data["transaction_id"] = transaction_id
        
        # Validating with model safely
        new_transaction = TransactionModel(**transaction_data)
        
        amount_diff = new_transaction.amount if new_transaction.type == "CREDIT" else -new_transaction.amount

        success = await self.repository.add_transaction(bank_id, new_transaction.model_dump(), amount_diff)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to add transaction")
            
        return transaction_data

    async def get_transactions(self, bank_id: str) -> List[dict]:
        bank = await self.get_bank(bank_id)
        return bank.get("transactions", [])
