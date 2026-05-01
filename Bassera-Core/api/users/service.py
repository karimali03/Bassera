from typing import List, Optional
from datetime import datetime, timezone
from .repository import UserRepository
from .schemas import UserCreate, UserUpdate, AIForecastPayload, AIStatus

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def _map_to_schema(self, user_dict: dict) -> dict:
        if not user_dict:
            return None
        user_dict['id'] = str(user_dict.pop('_id'))
        return user_dict

    def create_user(self, user_data: UserCreate) -> dict:
        user_dict = user_data.dict()
        user_dict['ai_status'] = AIStatus.NOT_STARTED.value
        created_user = self.repository.create(user_dict)
        return self._map_to_schema(created_user)

    def get_all_users(self) -> List[dict]:
        users = self.repository.get_all()
        return [self._map_to_schema(u) for u in users]

    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        user = self.repository.get_by_id(user_id)
        return self._map_to_schema(user) if user else None

    def update_user(self, user_id: str, update_data: UserUpdate) -> Optional[dict]:
        update_dict = update_data.dict(exclude_unset=True)
        if not update_dict:
            return self.get_user_by_id(user_id) # Return existing if no fields provided
        
        updated_user = self.repository.update(user_id, update_dict)
        return self._map_to_schema(updated_user) if updated_user else None

    def update_ai_status(self, user_id: str, ai_status: AIStatus) -> Optional[dict]:
        update_dict = {"ai_status": ai_status.value}
        updated_user = self.repository.update_specific_fields(user_id, update_dict)
        return self._map_to_schema(updated_user) if updated_user else None

    def update_ai_forecast(self, user_id: str, payload: AIForecastPayload) -> Optional[dict]:
        update_dict = {
            "ai_forecast_data": payload.model_dump(),
            "ai_status": AIStatus.FINISHED.value,
            "ai_last_run": datetime.now(timezone.utc)
        }
        updated_user = self.repository.update_specific_fields(user_id, update_dict)
        return self._map_to_schema(updated_user) if updated_user else None

    def delete_user(self, user_id: str) -> bool:
        return self.repository.delete(user_id)
