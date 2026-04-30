from fastapi import APIRouter
from app.api.v1.endpoints import health, suggestions

api_router = APIRouter(prefix="/v1")
api_router.include_router(health.router, tags=["ops"])
api_router.include_router(suggestions.router, tags=["suggestions"])
