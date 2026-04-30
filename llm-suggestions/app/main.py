from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging, logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    configure_logging()
    logger.info("Baseera AI Service starting — env=%s", settings.app_env)
    # Fail fast if upstream API key is not configured — prevents misleading requests
    if not settings.openrouter_api_key:
        logger.error(
            "OPENROUTER_API_KEY is not set. Set it in the environment or .env before starting."
        )
        raise RuntimeError("OPENROUTER_API_KEY is required to start the service")
    yield
    logger.info("Baseera AI Service shutting down.")


app = FastAPI(
    title="Baseera AI Service",
    description="AI-powered financial suggestion engine for the Baseera budget tracker.",
    version="0.1.0",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    lifespan=lifespan,
)

# CORS — tighten allowed_origins before going to production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if not settings.is_production else ["https://baseera-insight-maker.lovable.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
