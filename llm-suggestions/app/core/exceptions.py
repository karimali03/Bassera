from fastapi import HTTPException, status


class BaseeraException(Exception):
    """Base exception for all service-level errors."""


class InvalidTransactionDataError(BaseeraException):
    """Raised when the incoming transaction payload fails validation."""


class AIEngineError(BaseeraException):
    """Raised when the LMM API call fails or returns unparsable output."""


class AIResponseParseError(AIEngineError):
    """Raised when the model's JSON response cannot be parsed."""


def raise_422(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


def raise_502(detail: str = "AI engine is temporarily unavailable.") -> None:
    raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)
