"""Lightweight validation helpers used across the service."""

import re
from app.models.transaction import Transaction

SUPPORTED_CURRENCIES = {"EGP", "USD", "EUR", "AED", "SAR"}


def validate_currency(transactions: list[Transaction]) -> list[str]:
    """Return a list of warnings for any unsupported currency codes."""
    warnings = []
    for t in transactions:
        if t.currency.upper() not in SUPPORTED_CURRENCIES:
            warnings.append(
                f"Transaction {t.transaction_id}: unsupported currency '{t.currency}'"
            )
    return warnings


def is_valid_uuid(value: str) -> bool:
    uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
    )
    return bool(uuid_pattern.match(value))
