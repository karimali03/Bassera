from lib.db import get_collection
from typing import Optional, Dict, Any

class BankRepository:
    def __init__(self):
        # We assume motor/pymongo based db connection from lib.db
        self.collection = get_collection('banks')

    def create_bank(self, bank_data: dict) -> dict:
        result = self.collection.insert_one(bank_data)
        bank_data["_id"] = str(result.inserted_id)
        return bank_data

    def get_bank_by_bank_id(self, bank_id: str) -> Optional[dict]:
        bank = self.collection.find_one({"bank_id": bank_id})
        if bank:
            bank["_id"] = str(bank["_id"])
        return bank

    def add_transaction(self, bank_id: str, transaction_data: dict, amount_diff: float = 0.0) -> bool:
        # Crucial requirement: Using $push operator to efficiently append the transaction
        # And $inc operator to update the balance
        result = self.collection.update_one(
            {"bank_id": bank_id},
            {
                "$push": {"transactions": transaction_data},
                "$inc": {"balance": amount_diff}
            }
        )
        return result.modified_count > 0
