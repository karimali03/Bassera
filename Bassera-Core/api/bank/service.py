from fastapi import HTTPException, status
from typing import List
import hashlib
import uuid

from .repository import BankRepository
from .schemas import BankCreate, TransactionCreate, BankResponse, TransactionResponse
from .models import BankModel, TransactionModel

class BankService:
    def __init__(self):
        self.repository = BankRepository()

    def _normalize_transaction(self, transaction: dict, bank_id: str, index: int) -> dict:
        normalized_transaction = dict(transaction)
        if not normalized_transaction.get("transaction_id"):
            fingerprint_source = "|".join(
                [
                    bank_id,
                    str(index),
                    str(normalized_transaction.get("timestamp", "")),
                    str(normalized_transaction.get("merchant", "")),
                    str(normalized_transaction.get("amount", "")),
                    str(normalized_transaction.get("category", "")),
                    str(normalized_transaction.get("type", "")),
                ]
            )
            normalized_transaction["transaction_id"] = hashlib.sha1(
                fingerprint_source.encode("utf-8")
            ).hexdigest()[:16]
        return normalized_transaction

    async def create_bank(self, obj_in: BankCreate) -> dict:
        existing_bank = self.repository.get_bank_by_bank_id(obj_in.bank_id)
        if existing_bank:
            raise HTTPException(status_code=400, detail="Bank profile already exists for this user")
        
        bank_model = BankModel(bank_id=obj_in.bank_id, transactions=[])
        bank_data = bank_model.model_dump(by_alias=True)
        # remove generated ObjectId string for Motor to generate cleanly, or keep model's ID
        
        return self.repository.create_bank(bank_data)

    async def get_bank(self, bank_id: str) -> dict:
        bank = self.repository.get_bank_by_bank_id(bank_id)
        if not bank:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bank profile not found")
        bank["transactions"] = [
            self._normalize_transaction(transaction, bank_id, index)
            for index, transaction in enumerate(bank.get("transactions", []))
        ]
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

        success = self.repository.add_transaction(bank_id, new_transaction.model_dump(), amount_diff)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to add transaction")
            
        return transaction_data

    async def get_transactions(self, bank_id: str) -> List[dict]:
        bank = await self.get_bank(bank_id)
        return bank.get("transactions", [])
