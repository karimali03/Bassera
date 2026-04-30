from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings
from app.core.exceptions import AIEngineError, AIResponseParseError, raise_422, raise_502
from app.core.logging import logger
from app.models.request import SuggestionsRequest
from app.models.response import SuggestionsResponse
from app.services import ai_engine, transaction_analyzer

router = APIRouter()
bearer = HTTPBearer(auto_error=False)


def verify_api_key(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer),
) -> None:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing Authorization header.",
        )

    incoming = credentials.credentials

    # Exact match to the configured service API key always allowed
    if incoming == settings.service_api_key:
        return

    # Optionally allow the OpenRouter API key to be used as the local bearer
    # Key sharing is permitted when explicitly enabled or in non-production
    if (
        incoming == settings.openrouter_api_key
        and (
            settings.allow_shared_api_key
            or settings.app_env != "production"
        )
    ):
        return

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API key.",
    )


@router.post(
    "/suggestions",
    response_model=SuggestionsResponse,
    summary="Generate AI saving suggestions from transaction data",
    responses={
        403: {"description": "Forbidden — missing Authorization header"},
        401: {"description": "Unauthorized — invalid API key"},
        422: {"description": "Unprocessable transaction payload"},
        502: {"description": "AI engine unavailable"},
    },
)
def create_suggestions(
    body: SuggestionsRequest,
    _: None = Depends(verify_api_key),
) -> SuggestionsResponse:
    """
    Accepts a list of pre-tagged bank transactions and returns Baseera's
    AI-generated financial insights and saving suggestions.
    """
    logger.info("POST /suggestions — %d transactions received", len(body.transactions))

    clean_transactions = transaction_analyzer.preprocess(body.transactions)
    if not clean_transactions:
        raise_422("No valid transactions remain after pre-processing.")

    try:
        response = ai_engine.generate_suggestions(clean_transactions)
    except AIResponseParseError as exc:
        logger.error("Parse error: %s", exc)
        raise_502("AI engine returned an unexpected response format.")
    except AIEngineError as exc:
        logger.error("Engine error: %s", exc)
        raise_502()

    return response
