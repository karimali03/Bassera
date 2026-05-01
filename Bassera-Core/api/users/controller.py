from fastapi import HTTPException
from typing import List
from .service import UserService
from .schemas import UserCreate, UserUpdate, UserResponse, AIStatusUpdate, AIForecastPayload

class UserController:
    def __init__(self, service: UserService):
        self.service = service

    def create_user(self, user_data: UserCreate) -> dict:
        return self.service.create_user(user_data)

    def get_all_users(self) -> List[dict]:
        return self.service.get_all_users()

    def get_user_by_id(self, user_id: str) -> dict:
        user = self.service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def update_user(self, user_id: str, update_data: UserUpdate) -> dict:
        updated_user = self.service.update_user(user_id, update_data)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found or unable to update")
        return updated_user

    def update_ai_status(self, user_id: str, status_data: AIStatusUpdate) -> dict:
        updated_user = self.service.update_ai_status(user_id, status_data.ai_status)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found or unable to update")
        return updated_user

    def update_ai_forecast(self, user_id: str, payload: AIForecastPayload) -> dict:
        updated_user = self.service.update_ai_forecast(user_id, payload)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found or unable to update")
        return updated_user

    def delete_user(self, user_id: str) -> dict:
        success = self.service.delete_user(user_id)
        if not success:
            raise HTTPException(status_code=404, detail="User not found or unable to delete")
        return {"message": "User deleted successfully"}