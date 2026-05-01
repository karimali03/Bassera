from datetime import datetime, timezone
from lib.db import get_collection


class SuggestionsRepository:
    def __init__(self):
        self.col = get_collection('suggestions')

    def save(self, user_id: str, data: dict) -> dict:
        doc = {"user_id": user_id, "created_at": datetime.now(timezone.utc), **data}
        result = self.col.insert_one(doc)
        doc["id"] = str(result.inserted_id)
        return doc

    def get_latest(self, user_id: str) -> dict | None:
        doc = self.col.find_one({"user_id": user_id}, sort=[("created_at", -1)])
        if doc:
            doc["id"] = str(doc.pop("_id"))
        return doc
