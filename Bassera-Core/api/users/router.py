from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pymongo.database import Database
from lib.db import get_mongo_client

from .schemas import UserCreate, UserUpdate, UserResponse, AIStatusUpdate, AIForecastPayload
from .repository import UserRepository
from .service import UserService
from .controller import UserController

router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)

# Dependency Injection
def get_db_session() -> Database:
    client = get_mongo_client()
    # The client returned from db.py's get_mongo_client() is already the default DB instance
    return client

def get_repository(db: Database = Depends(get_db_session)) -> UserRepository:
    return UserRepository(db)

def get_service(repository: UserRepository = Depends(get_repository)) -> UserService:
    return UserService(repository)

def get_controller(service: UserService = Depends(get_service)) -> UserController:
    return UserController(service)


@router.post("/", response_model=UserResponse)
def create_user(user_data: UserCreate, controller: UserController = Depends(get_controller)):
    return controller.create_user(user_data)

@router.get("/", response_model=List[UserResponse])
def get_all_users(controller: UserController = Depends(get_controller)):
    return controller.get_all_users()

@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: str, controller: UserController = Depends(get_controller)):
    return controller.get_user_by_id(user_id)

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: str, update_data: UserUpdate, controller: UserController = Depends(get_controller)):
    return controller.update_user(user_id, update_data)

@router.patch("/{user_id}/ai-status", response_model=UserResponse)
def update_ai_status(user_id: str, status_data: AIStatusUpdate, controller: UserController = Depends(get_controller)):
    return controller.update_ai_status(user_id, status_data)

@router.put("/{user_id}/ai-forecast", response_model=UserResponse)
def update_ai_forecast(user_id: str, payload: AIForecastPayload, controller: UserController = Depends(get_controller)):
    return controller.update_ai_forecast(user_id, payload)

@router.delete("/{user_id}")
def delete_user(user_id: str, controller: UserController = Depends(get_controller)):
    return controller.delete_user(user_id)