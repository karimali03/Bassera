"""Unit tests for utility validators."""

from app.utils.validators import validate_currency, is_valid_uuid
from app.models.transaction import Transaction, TransactionType
from datetime import datetime


def make_txn(currency: str = "EGP", txn_id: str = "abc-123") -> Transaction:
    return Transaction(
        transaction_id=txn_id,
        timestamp=datetime(2025, 1, 1, 10, 0),
        merchant="Test Merchant",
        category="Shopping",
        amount=100.0,
        currency=currency,
        type=TransactionType.DEBIT,
        note=None,
    )


class TestValidateCurrency:
    def test_supported_currencies_no_warnings(self) -> None:
        for currency in ["EGP", "USD", "EUR", "AED", "SAR"]:
            txn = make_txn(currency=currency)
            assert validate_currency([txn]) == []

    def test_unsupported_currency_returns_warning(self) -> None:
        txn = make_txn(currency="XYZ")
        warnings = validate_currency([txn])
        assert len(warnings) == 1
        assert "XYZ" in warnings[0]

    def test_multiple_transactions_mixed(self) -> None:
        txns = [make_txn("EGP", "id-1"), make_txn("XYZ", "id-2"), make_txn("USD", "id-3")]
        warnings = validate_currency(txns)
        assert len(warnings) == 1


class TestIsValidUuid:
    def test_valid_uuid(self) -> None:
        assert is_valid_uuid("ebf90783-868a-4980-97d3-9893231589b8") is True

    def test_invalid_uuid_short(self) -> None:
        assert is_valid_uuid("not-a-uuid") is False

    def test_invalid_uuid_empty(self) -> None:
        assert is_valid_uuid("") is False

    def test_uppercase_uuid_valid(self) -> None:
        assert is_valid_uuid("EBF90783-868A-4980-97D3-9893231589B8") is True
