from typing import List, Optional
from bson import ObjectId
from pymongo.database import Database

class UserRepository:
    def __init__(self, db: Database):
        self.collection = db.get_collection('users')

    def create(self, user_data: dict) -> dict:
        result = self.collection.insert_one(user_data)
        user_data['_id'] = result.inserted_id
        return user_data

    def get_all(self) -> List[dict]:
        return list(self.collection.find({}))

    def get_by_id(self, user_id: str) -> Optional[dict]:
        return self.collection.find_one({"_id": ObjectId(user_id)})

    def update(self, user_id: str, update_data: dict) -> Optional[dict]:
        result = self.collection.update_one(
            {"_id": ObjectId(user_id)}, {"$set": update_data}
        )
        if result.modified_count > 0:
            return self.get_by_id(user_id)
        return self.get_by_id(user_id)

    def update_specific_fields(self, user_id: str, update_data: dict) -> Optional[dict]:
        result = self.collection.update_one(
            {"_id": ObjectId(user_id)}, {"$set": update_data}
        )
        return self.get_by_id(user_id)

    def delete(self, user_id: str) -> bool:
        result = self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0
