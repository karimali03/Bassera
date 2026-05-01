import json
from openai import OpenAI, OpenAIError
from lib.ai import config
from lib.ai.exceptions import AIEngineError, AIResponseParseError
from lib.ai.response import SuggestionsResponse
from lib.ai.transaction import Transaction
from lib.ai.prompt_builder import SYSTEM_PROMPT, build_user_message


def _build_client() -> OpenAI:
    return OpenAI(
        api_key=config.OPENROUTER_API_KEY,
        base_url=config.OPENROUTER_BASE_URL,
        default_headers={
            "HTTP-Referer": config.OPENROUTER_SITE_URL,
            "X-Title": config.OPENROUTER_APP_NAME,
        },
    )


def generate_suggestions(transactions: list[Transaction]) -> SuggestionsResponse:
    user_message = build_user_message(transactions)
    client = _build_client()

    try:
        message = client.chat.completions.create(
            model=config.OPENROUTER_MODEL,
            max_tokens=config.OPENROUTER_MAX_TOKENS,
            temperature=0,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )
    except OpenAIError as exc:
        raise AIEngineError(f"OpenRouter API call failed: {exc}") from exc

    raw_text = message.choices[0].message.content if message.choices else ""
    if not isinstance(raw_text, str):
        raw_text = "" if raw_text is None else str(raw_text)

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise AIResponseParseError(f"Model returned non-JSON output: {exc}") from exc

    try:
        return SuggestionsResponse.model_validate(data)
    except Exception as exc:
        raise AIResponseParseError(f"Response does not match expected schema: {exc}") from exc
