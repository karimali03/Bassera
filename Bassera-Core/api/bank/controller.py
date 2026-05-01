from fastapi import APIRouter
from typing import List

from .service import BankService
from .schemas import BankCreate, BankResponse, TransactionCreate, TransactionResponse

class BankController:
    def __init__(self):
        self.service = BankService()

    async def create_bank(self, bank_in: BankCreate) -> BankResponse:
        bank_data = await self.service.create_bank(bank_in)
        return BankResponse(**bank_data)

    async def get_bank(self, bank_id: str) -> BankResponse:
        bank_data = await self.service.get_bank(bank_id)
        return BankResponse(**bank_data)

    async def add_transaction(self, bank_id: str, transaction_in: TransactionCreate) -> TransactionResponse:
        transaction_data = await self.service.add_transaction(bank_id, transaction_in)
        return TransactionResponse(**transaction_data)

    async def get_transactions(self, bank_id: str) -> List[TransactionResponse]:
        transactions_data = await self.service.get_transactions(bank_id)
        return [TransactionResponse(**txn) for txn in transactions_data]
