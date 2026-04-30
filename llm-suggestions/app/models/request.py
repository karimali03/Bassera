from pydantic import BaseModel, Field, model_validator
from app.models.transaction import Transaction


class SuggestionsRequest(BaseModel):
    """Inbound payload for POST /v1/suggestions."""

    transactions: list[Transaction] = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Array of pre-tagged bank transactions from the Open Banking API",
    )

    @model_validator(mode="after")
    def must_have_at_least_one_debit(self) -> "SuggestionsRequest":
        from app.models.transaction import TransactionType
        debits = [t for t in self.transactions if t.type == TransactionType.DEBIT]
        if not debits:
            raise ValueError("At least one DEBIT transaction is required to generate suggestions.")
        return self
