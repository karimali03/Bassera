"""Unit tests for the transaction pre-processing pipeline."""

import pytest
from datetime import datetime
from app.models.transaction import Transaction, TransactionType
from app.services.transaction_analyzer import (
    deduplicate,
    sort_by_timestamp,
    compute_totals,
    category_summary,
    preprocess,
)


def make_txn(
    txn_id: str,
    merchant: str,
    amount: float,
    type_: TransactionType = TransactionType.DEBIT,
    category: str = "Food_and_Dining",
    timestamp: str = "2025-01-01 10:00",
) -> Transaction:
    return Transaction(
        transaction_id=txn_id,
        timestamp=datetime.strptime(timestamp, "%Y-%m-%d %H:%M"),
        merchant=merchant,
        category=category,
        amount=amount,
        currency="EGP",
        type=type_,
        note=None,
    )


class TestDeduplicate:
    def test_removes_duplicate_ids(self) -> None:
        txns = [
            make_txn("id-1", "Merchant A", 100),
            make_txn("id-1", "Merchant A", 100),  # duplicate
            make_txn("id-2", "Merchant B", 200),
        ]
        result = deduplicate(txns)
        assert len(result) == 2
        assert result[0].transaction_id == "id-1"
        assert result[1].transaction_id == "id-2"

    def test_no_duplicates_unchanged(self) -> None:
        txns = [make_txn("id-1", "A", 50), make_txn("id-2", "B", 75)]
        assert deduplicate(txns) == txns

    def test_empty_list(self) -> None:
        assert deduplicate([]) == []


class TestSortByTimestamp:
    def test_sorts_ascending(self) -> None:
        txns = [
            make_txn("id-3", "C", 100, timestamp="2025-01-03 08:00"),
            make_txn("id-1", "A", 100, timestamp="2025-01-01 06:00"),
            make_txn("id-2", "B", 100, timestamp="2025-01-02 12:00"),
        ]
        result = sort_by_timestamp(txns)
        assert [t.transaction_id for t in result] == ["id-1", "id-2", "id-3"]

    def test_already_sorted_unchanged(self) -> None:
        txns = [
            make_txn("id-1", "A", 100, timestamp="2025-01-01 06:00"),
            make_txn("id-2", "B", 100, timestamp="2025-01-02 06:00"),
        ]
        assert sort_by_timestamp(txns) == txns


class TestComputeTotals:
    def test_basic_totals(self) -> None:
        txns = [
            make_txn("id-1", "A", 500, type_=TransactionType.DEBIT),
            make_txn("id-2", "B", 300, type_=TransactionType.DEBIT),
            make_txn("id-3", "Salary", 2000, type_=TransactionType.CREDIT),
        ]
        totals = compute_totals(txns)
        assert totals["total_debits"] == 800.0
        assert totals["total_credits"] == 2000.0
        assert totals["net_cashflow"] == 1200.0

    def test_all_debits_negative_cashflow(self) -> None:
        txns = [make_txn("id-1", "A", 1000, type_=TransactionType.DEBIT)]
        totals = compute_totals(txns)
        assert totals["net_cashflow"] == -1000.0

    def test_empty_list(self) -> None:
        totals = compute_totals([])
        assert totals == {"total_debits": 0.0, "total_credits": 0.0, "net_cashflow": 0.0}


class TestCategorySummary:
    def test_aggregates_by_category(self) -> None:
        txns = [
            make_txn("id-1", "A", 100, category="Food_and_Dining"),
            make_txn("id-2", "B", 200, category="Food_and_Dining"),
            make_txn("id-3", "C", 150, category="Transportation"),
        ]
        summary = category_summary(txns)
        assert summary["Food_and_Dining"]["total"] == 300.0
        assert summary["Food_and_Dining"]["count"] == 2
        assert summary["Transportation"]["total"] == 150.0

    def test_credits_excluded(self) -> None:
        txns = [
            make_txn("id-1", "A", 500, type_=TransactionType.CREDIT, category="Salary"),
            make_txn("id-2", "B", 100, type_=TransactionType.DEBIT, category="Food_and_Dining"),
        ]
        summary = category_summary(txns)
        assert "Salary" not in summary
        assert "Food_and_Dining" in summary


class TestPreprocess:
    def test_deduplicates_and_sorts(self) -> None:
        txns = [
            make_txn("id-2", "B", 100, timestamp="2025-01-03 08:00"),
            make_txn("id-1", "A", 100, timestamp="2025-01-01 06:00"),
            make_txn("id-1", "A", 100, timestamp="2025-01-01 06:00"),  # duplicate
        ]
        result = preprocess(txns)
        assert len(result) == 2
        assert result[0].transaction_id == "id-1"
        assert result[1].transaction_id == "id-2"