#!/usr/bin/env python3
"""
Quick script to hit the local /v1/suggestions endpoint with realistic
mock transaction data — useful for manual testing during the hackathon.

Usage:
    python scripts/seed_mock_data.py [--url http://localhost:8000] [--api-key your-key]
"""

import argparse
import json
import sys
import os
from pathlib import Path

import httpx

MOCK_TRANSACTIONS = [
    {"transaction_id": "ebf90783-868a-4980-97d3-9893231589b8", "timestamp": "2025-01-01 06:08",
     "merchant": "Orange Egypt", "category": "Services_and_Utilities",
     "amount": 676.10, "currency": "EGP", "type": "DEBIT", "note": "Subscription — twice_monthly"},
    {"transaction_id": "dfc2f190-8140-43e4-88e4-8935e0512007", "timestamp": "2025-01-01 07:11",
     "merchant": "Nile Taxi", "category": "Transportation",
     "amount": 40.63, "currency": "EGP", "type": "DEBIT", "note": "Morning commute"},
    {"transaction_id": "a1b2c3d4-0000-0000-0000-000000000001", "timestamp": "2025-01-01 09:00",
     "merchant": "Carrefour Egypt", "category": "Groceries",
     "amount": 850.00, "currency": "EGP", "type": "DEBIT", "note": "Weekly groceries"},
    {"transaction_id": "b2c3d4e5-0000-0000-0000-000000000002", "timestamp": "2025-01-02 12:30",
     "merchant": "Talabat", "category": "Food_and_Dining",
     "amount": 185.00, "currency": "EGP", "type": "DEBIT", "note": "Lunch delivery"},
    {"transaction_id": "c3d4e5f6-0000-0000-0000-000000000003", "timestamp": "2025-01-02 14:00",
     "merchant": "Talabat", "category": "Food_and_Dining",
     "amount": 210.00, "currency": "EGP", "type": "DEBIT", "note": "Dinner delivery"},
    {"transaction_id": "d4e5f6a7-0000-0000-0000-000000000004", "timestamp": "2025-01-03 08:00",
     "merchant": "Nile Taxi", "category": "Transportation",
     "amount": 38.50, "currency": "EGP", "type": "DEBIT", "note": "Morning commute"},
    {"transaction_id": "e5f6a7b8-0000-0000-0000-000000000005", "timestamp": "2025-01-05 09:00",
     "merchant": "Employer Co.", "category": "Salary",
     "amount": 15000.00, "currency": "EGP", "type": "CREDIT", "note": "Monthly salary"},
    {"transaction_id": "f6a7b8c9-0000-0000-0000-000000000006", "timestamp": "2025-01-06 19:00",
     "merchant": "Netflix", "category": "Entertainment",
     "amount": 200.00, "currency": "EGP", "type": "DEBIT", "note": "Monthly subscription"},
    {"transaction_id": "a7b8c9d0-0000-0000-0000-000000000007", "timestamp": "2025-01-07 20:00",
     "merchant": "Shahid", "category": "Entertainment",
     "amount": 99.00, "currency": "EGP", "type": "DEBIT", "note": "Monthly subscription"},
    {"transaction_id": "b8c9d0e1-0000-0000-0000-000000000008", "timestamp": "2025-01-08 11:00",
     "merchant": "Talabat", "category": "Food_and_Dining",
     "amount": 170.00, "currency": "EGP", "type": "DEBIT", "note": "Weekend brunch"},
]


def load_env_file(env_path: Path = Path(".env")) -> dict[str, str]:
    """Load simple KEY=VALUE pairs from a local .env file."""
    values: dict[str, str] = {}
    if not env_path.exists():
        return values

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")

    return values


def resolve_api_key(explicit_api_key: str | None) -> str:
    if explicit_api_key and explicit_api_key != "change-me-before-deploy":
        return explicit_api_key

    env_values = load_env_file()
    return (
        os.environ.get("SERVICE_API_KEY")
        or env_values.get("SERVICE_API_KEY")
        or os.environ.get("OPENROUTER_API_KEY")
        or env_values.get("OPENROUTER_API_KEY")
        or "change-me-before-deploy"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Baseera AI with mock transactions")
    parser.add_argument("--url", default="http://localhost:8000", help="Service base URL")
    parser.add_argument(
        "--api-key",
        default=os.environ.get("SERVICE_API_KEY", "change-me-before-deploy"),
        help="Bearer API key (defaults to SERVICE_API_KEY env var)"
    )
    args = parser.parse_args()

    api_key = resolve_api_key(args.api_key)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    print(f"POSTing {len(MOCK_TRANSACTIONS)} transactions to {args.url}/v1/suggestions ...")

    try:
        response = httpx.post(
            f"{args.url}/v1/suggestions",
            json={"transactions": MOCK_TRANSACTIONS},
            headers=headers,
            timeout=180.0,
        )
        response.raise_for_status()
        print("\n✅ Success! Response:\n")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except httpx.HTTPStatusError as e:
        print(f"\n❌ HTTP {e.response.status_code}: {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except httpx.RequestError as e:
        print(f"\n❌ Connection error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
