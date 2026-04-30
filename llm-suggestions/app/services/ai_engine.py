"""
Thin wrapper around the OpenRouter client.
Responsible for: sending the prompt, receiving raw JSON text, and parsing it
into a SuggestionsResponse — nothing more.
"""

import json

from openai import OpenAI, OpenAIError

from app.core.config import settings
from app.core.exceptions import AIEngineError, AIResponseParseError
from app.core.logging import logger
from app.models.response import SuggestionsResponse
from app.models.transaction import Transaction
from app.services.prompt_builder import SYSTEM_PROMPT, build_user_message


def _build_client() -> OpenAI:
    return OpenAI(
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
        default_headers={
            "HTTP-Referer": settings.openrouter_site_url,
            "X-Title": settings.openrouter_app_name,
        },
    )


def generate_suggestions(transactions: list[Transaction]) -> SuggestionsResponse:
    """
    Send transactions to OpenRouter and return a validated SuggestionsResponse.
    Raises AIEngineError on API failure, AIResponseParseError on bad JSON.
    """
    user_message = build_user_message(transactions)
    client = _build_client()
    logger.info(
        "Sending %d transactions to OpenRouter (%s)",
        len(transactions),
        settings.openrouter_model,
    )

    try:
        message = client.chat.completions.create(
            model=settings.openrouter_model,
            max_tokens=settings.openrouter_max_tokens,
            temperature=0,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )
    except OpenAIError as exc:
        logger.error("OpenRouter API error: %s", exc)
        raise AIEngineError(f"OpenRouter API call failed: {exc}") from exc

    raw_text = message.choices[0].message.content if message.choices else ""
    if not isinstance(raw_text, str):
        raw_text = "" if raw_text is None else str(raw_text)
    logger.debug("Raw AI response: %.200s...", raw_text)

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse AI response as JSON: %s", exc)
        raise AIResponseParseError(f"Model returned non-JSON output: {exc}") from exc

    try:
        return SuggestionsResponse.model_validate(data)
    except Exception as exc:
        logger.error("Response schema validation failed: %s", exc)
        raise AIResponseParseError(f"Response does not match expected schema: {exc}") from exc
