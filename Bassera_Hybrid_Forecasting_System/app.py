"""
Baseera REST API Layer.

Exposes the core ML pipeline as a FastAPI service for deployment
to Hugging Face Docker Spaces (or any containerized environment).

Endpoints:
    POST /analyze  — Accepts a transaction ledger, returns both the
                     30-day forecast and the preprocessed historical summary.
    GET  /health   — Simple health check for load balancers / readiness probes.
"""

import logging
import traceback
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.pipeline import generate_forecast, generate_preprocessed_summary

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Baseera Hybrid Forecasting API",
    description=(
        "A hybrid ML service that combines rule-based pattern detection "
        "with a dual-head GRU neural network to forecast personal finances."
    ),
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------
class AnalyzeRequest(BaseModel):
    """
    Incoming payload for the /analyze endpoint.

    Attributes:
        transactions: Raw transaction records from the user's ledger.
        starting_balance: Current account balance (EGP) to anchor the forecast.
        horizon_days: Number of future days to predict (default 30).
    """

    transactions: list[dict[str, Any]] = Field(
        ...,
        description="List of transaction dictionaries from the user's ledger.",
        min_length=1,
    )
    starting_balance: float = Field(
        ...,
        description="Current account balance in EGP. Required for forecast projection.",
    )
    horizon_days: Optional[int] = Field(
        default=30,
        ge=1,
        le=365,
        description="Number of future days to forecast (1–365).",
    )


class AnalyzeResponse(BaseModel):
    """
    Unified response containing both pipeline outputs.

    Attributes:
        forecast: The forward-looking model forecast (30-day projections).
        summary: The backward-looking preprocessed historical summary.
    """

    forecast: dict[str, Any]
    summary: dict[str, Any]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/health", tags=["System"])
async def health_check():
    """Readiness probe for container orchestrators."""
    return {"status": "healthy"}


@app.post(
    "/analyze",
    response_model=AnalyzeResponse,
    tags=["Forecasting"],
    summary="Run the full Baseera analysis pipeline",
    description=(
        "Accepts a list of raw transactions and returns both the "
        "forward-looking forecast and the backward-looking preprocessed "
        "historical summary in a single response."
    ),
)
def analyze(request: AnalyzeRequest):
    """
    Main analysis endpoint.

    1. Runs `generate_preprocessed_summary` to produce the historical
       day → category → merchant audit trail.
    2. Runs `generate_forecast` to produce the 30-day balance trajectory
       with fixed/dynamic breakdowns.
    3. Returns both results under `summary` and `forecast` keys.
    """
    logger.info(
        "Received /analyze request: %d transactions, horizon=%d days",
        len(request.transactions),
        request.horizon_days,
    )

    try:
        # --- Preprocessed historical summary ---
        summary_result = generate_preprocessed_summary(
            transactions=request.transactions,
            source_label="api_input",
        )

        # --- Forward-looking forecast ---
        forecast_result = generate_forecast(
            transactions=request.transactions,
            horizon_days=request.horizon_days,
            starting_balance=request.starting_balance,
        )

    except FileNotFoundError as exc:
        # Missing model artifacts (user hasn't trained yet)
        logger.error("Missing artifacts: %s", exc)
        raise HTTPException(
            status_code=503,
            detail=(
                f"Model artifacts not found: {exc}. "
                "Ensure the model has been trained and artifacts are present."
            ),
        )
    except ValueError as exc:
        # Bad input data (missing columns, empty ledger, etc.)
        logger.error("Validation error: %s", exc)
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        # Catch-all for unexpected pipeline failures
        logger.error("Pipeline error:\n%s", traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Internal pipeline error: {exc}",
        )

    logger.info("Analysis complete. Returning response.")
    return AnalyzeResponse(forecast=forecast_result, summary=summary_result)
