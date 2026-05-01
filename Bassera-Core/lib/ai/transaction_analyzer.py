from collections import defaultdict
from lib.ai.transaction import Transaction, TransactionType


def deduplicate(transactions: list[Transaction]) -> list[Transaction]:
    seen: set[str] = set()
    result: list[Transaction] = []
    for t in transactions:
        if t.transaction_id not in seen:
            seen.add(t.transaction_id)
            result.append(t)
    return result


def preprocess(transactions: list[Transaction]) -> list[Transaction]:
    transactions = deduplicate(transactions)
    return sorted(transactions, key=lambda t: t.timestamp)
