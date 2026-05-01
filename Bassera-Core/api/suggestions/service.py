from fastapi import HTTPException
from bson import ObjectId
from lib.db import get_collection
from lib.ai.transaction import Transaction
from lib.ai import transaction_analyzer, ai_engine
from lib.ai.exceptions import AIEngineError, AIResponseParseError
from .repository import SuggestionsRepository


class SuggestionsService:
    def __init__(self):
        self.repo = SuggestionsRepository()
        self.users = get_collection('users')
        self.banks = get_collection('banks')

    def generate(self, user_id: str) -> dict:
        user = self.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(404, "User not found")
        bank = self.banks.find_one({"bank_id": user["bank_id"]})
        if not bank or not bank.get("transactions"):
            raise HTTPException(404, "No transactions found")
        txns = transaction_analyzer.preprocess([Transaction(**t) for t in bank["transactions"]])
        try:
            result = ai_engine.generate_suggestions(txns)
        except (AIEngineError, AIResponseParseError) as e:
            raise HTTPException(502, str(e))
        return self.repo.save(user_id, result.model_dump(by_alias=True))

    def get_latest(self, user_id: str) -> dict:
        doc = self.repo.get_latest(user_id)
        if not doc:
            raise HTTPException(404, "No suggestions found")
        return doc
