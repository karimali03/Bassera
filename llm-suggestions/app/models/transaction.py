from datetime import datetime
from enum import StrEnum
from pydantic import BaseModel, Field, field_validator


class TransactionType(StrEnum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


class Transaction(BaseModel):
    """Single bank transaction as provided by the Open Banking mock API."""

    transaction_id: str = Field(..., description="Unique UUID for the transaction")
    timestamp: datetime = Field(..., description="Transaction datetime (YYYY-MM-DD HH:mm)")
    merchant: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1, description="Pre-tagged category from bank API")
    amount: float = Field(..., gt=0)
    currency: str = Field("EGP", min_length=3, max_length=3)
    type: TransactionType
    note: str | None = Field(None, description="Optional context note")

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, v: object) -> object:
        if isinstance(v, str):
            # Accept both "YYYY-MM-DD HH:mm" and ISO 8601
            for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"):
                try:
                    return datetime.strptime(v, fmt)
                except ValueError:
                    continue
            raise ValueError(f"Cannot parse timestamp: {v!r}")
        return v

    model_config = {"str_strip_whitespace": True}
