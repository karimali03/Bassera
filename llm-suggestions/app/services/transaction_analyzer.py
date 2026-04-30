"""
Pure-Python pre-processing layer that runs BEFORE the AI call.
Validates, deduplicates, and summarises the transaction list so the
AI engine receives clean, minimal input.
"""

from collections import defaultdict
from app.models.transaction import Transaction, TransactionType


def deduplicate(transactions: list[Transaction]) -> list[Transaction]:
    """Remove duplicate transaction IDs, keeping the first occurrence."""
    seen: set[str] = set()
    result: list[Transaction] = []
    for t in transactions:
        if t.transaction_id not in seen:
            seen.add(t.transaction_id)
            result.append(t)
    return result


def sort_by_timestamp(transactions: list[Transaction]) -> list[Transaction]:
    return sorted(transactions, key=lambda t: t.timestamp)


def compute_totals(transactions: list[Transaction]) -> dict[str, float]:
    """Return total_debits, total_credits, net_cashflow."""
    total_debits = sum(t.amount for t in transactions if t.type == TransactionType.DEBIT)
    total_credits = sum(t.amount for t in transactions if t.type == TransactionType.CREDIT)
    return {
        "total_debits": round(total_debits, 2),
        "total_credits": round(total_credits, 2),
        "net_cashflow": round(total_credits - total_debits, 2),
    }


def category_summary(transactions: list[Transaction]) -> dict[str, dict[str, float]]:
    """Aggregate debit spending by category."""
    totals: dict[str, float] = defaultdict(float)
    counts: dict[str, int] = defaultdict(int)
    for t in transactions:
        if t.type == TransactionType.DEBIT:
            totals[t.category] += t.amount
            counts[t.category] += 1
    return {cat: {"total": round(totals[cat], 2), "count": counts[cat]} for cat in totals}


def preprocess(transactions: list[Transaction]) -> list[Transaction]:
    """Full preprocessing pipeline: deduplicate → sort."""
    transactions = deduplicate(transactions)
    transactions = sort_by_timestamp(transactions)
    return transactions
