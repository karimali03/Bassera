"""Unit tests for prompt construction logic."""

import json
from datetime import datetime
from app.models.transaction import Transaction, TransactionType
from app.services.prompt_builder import build_user_message, SYSTEM_PROMPT


def make_txn(txn_id: str = "abc-123") -> Transaction:
    return Transaction(
        transaction_id=txn_id,
        timestamp=datetime(2025, 1, 15, 9, 30),
        merchant="Cairo Café",
        category="Food_and_Dining",
        amount=85.50,
        currency="EGP",
        type=TransactionType.DEBIT,
        note="Breakfast",
    )


class TestBuildUserMessage:
    def test_returns_valid_json(self) -> None:
        msg = build_user_message([make_txn()])
        parsed = json.loads(msg)
        assert isinstance(parsed, list)
        assert len(parsed) == 1

    def test_transaction_fields_present(self) -> None:
        msg = build_user_message([make_txn("test-id-001")])
        data = json.loads(msg)
        txn = data[0]
        assert txn["transaction_id"] == "test-id-001"
        assert txn["merchant"] == "Cairo Café"
        assert txn["amount"] == 85.50
        assert txn["currency"] == "EGP"
        assert txn["type"] == "DEBIT"

    def test_timestamp_format(self) -> None:
        msg = build_user_message([make_txn()])
        data = json.loads(msg)
        assert data[0]["timestamp"] == "2025-01-15 09:30"

    def test_multiple_transactions(self) -> None:
        txns = [make_txn(f"id-{i}") for i in range(5)]
        msg = build_user_message(txns)
        data = json.loads(msg)
        assert len(data) == 5

    def test_null_note_preserved(self) -> None:
        txn = make_txn()
        txn = txn.model_copy(update={"note": None})
        msg = build_user_message([txn])
        data = json.loads(msg)
        assert data[0]["note"] is None


class TestSystemPrompt:
    def test_prompt_contains_sharia_instructions(self) -> None:
        assert "Musharaka" in SYSTEM_PROMPT
        assert "Mudarabah" in SYSTEM_PROMPT
        assert "Riba" in SYSTEM_PROMPT

    def test_prompt_instructs_json_only_output(self) -> None:
        assert "ONLY a valid JSON object" in SYSTEM_PROMPT
        assert "No preamble" in SYSTEM_PROMPT

    def test_prompt_references_baseera_identity(self) -> None:
        assert "Baseera" in SYSTEM_PROMPT
        assert "بصيرة" in SYSTEM_PROMPT

    def test_prompt_contains_output_schema(self) -> None:
        assert "analysis_period" in SYSTEM_PROMPT
        assert "suggestions" in SYSTEM_PROMPT
        assert "savings_potential" in SYSTEM_PROMPT
        assert "insight_of_the_day" in SYSTEM_PROMPT
