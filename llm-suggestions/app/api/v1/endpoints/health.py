from fastapi import APIRouter
from app.core.config import settings
from app.models.response import HealthResponse

router = APIRouter()

VERSION = "0.1.0"


@router.get("/health", response_model=HealthResponse, summary="Service liveness check")
def health_check() -> HealthResponse:
    return HealthResponse(version=VERSION, environment=settings.app_env)
