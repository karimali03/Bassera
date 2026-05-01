"""
Example client script for the Baseera forecasting service.

Usage:
    python forecast_client.py --starting-balance 250000
    python forecast_client.py --input data/generated_ledger.json --horizon 30 --output my_forecast.json --starting-balance 250000
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

# Add project root to path so we can import src
sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline import generate_forecast, generate_preprocessed_summary


def _rule_day_value(rule: dict) -> Optional[int]:
    if "day" in rule:
        return rule["day"]
    if "day_of_month" in rule:
        return rule["day_of_month"]
    date_str = rule.get("next_occurrence_date")
    if date_str:
        try:
            return int(str(date_str).split("-")[-1])
        except (ValueError, TypeError):
            return None
    return None


def _rule_amount(rule: dict) -> Optional[float]:
    if "value" in rule:
        return rule["value"]
    if "amount" in rule:
        return rule["amount"]
    return None


def main():
    parser = argparse.ArgumentParser(description="Baseera Forecast Client")
    parser.add_argument(
        "--input",
        type=str,
        default="data/generated_ledger.json",
        help="Path to the transactions JSON file.",
    )
    parser.add_argument(
        "--horizon",
        type=int,
        default=30,
        help="Number of future days to forecast.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="outputs/forecast_result.json",
        help="Path to write the forecast output JSON.",
    )
    parser.add_argument(
        "--starting-balance",
        type=float,
        default=None,
        help="Current account balance to start the forecast (EGP).",
    )
    args = parser.parse_args()

    # --- Load transactions ---
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"[ERROR] Input file not found: {input_path}")
        sys.exit(1)

    print(f"[INFO] Loading transactions from: {input_path}")
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    starting_balance = args.starting_balance
    json_starting_balance = None
    if isinstance(data, dict):
        if "transactions" in data:
            if not isinstance(data["transactions"], list):
                print("[ERROR] 'transactions' must be a list in the input JSON.")
                sys.exit(1)
            transactions = data["transactions"]
            json_starting_balance = (
                data.get("starting_balance")
                or data.get("current_balance")
                or data.get("balance")
            )
        else:
            transactions = [data]
    elif isinstance(data, list):
        transactions = data
    else:
        print("[ERROR] Input JSON must be a list of transactions or an object with 'transactions'.")
        sys.exit(1)

    if starting_balance is None:
        starting_balance = json_starting_balance
    if starting_balance is None:
        print("[ERROR] starting_balance is required (CLI --starting-balance or input JSON 'starting_balance').")
        sys.exit(1)

    print(f"[INFO] Loaded {len(transactions)} transactions.")

    # --- Call the forecasting service ---
    print(f"[INFO] Running forecast for {args.horizon} days...")
    result = generate_forecast(
        transactions=transactions,
        horizon_days=args.horizon,
        starting_balance=float(starting_balance),
    )

    # --- Write output to JSON file ---
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"[INFO] Forecast written to: {output_path}")

    # --- Generate preprocessed summary ---
    print("[INFO] Generating preprocessed summary...")
    preprocess_result = generate_preprocessed_summary(
        transactions=transactions,
        source_label=input_path.name,
    )
    preprocess_path = output_path.parent / "preprocessed_summary.json"
    preprocess_path.parent.mkdir(parents=True, exist_ok=True)
    with open(preprocess_path, "w", encoding="utf-8") as f:
        json.dump(preprocess_result, f, indent=2, ensure_ascii=False)
    print(f"[INFO] Preprocessed summary written to: {preprocess_path}")

    # --- Print a quick summary to console ---
    meta = result["metadata"]
    summary = result["summary"]
    rules = result["rules"]
    warnings = result["warnings"]

    print("\n" + "=" * 50)
    print("  FORECAST SUMMARY")
    print("=" * 50)
    print(f"  Forecast window : {meta['forecast_start_date']} → {meta['forecast_end_date']}")
    print(f"  Horizon         : {meta['forecast_horizon_days']} days")
    print(f"  Starting balance: {summary['starting_balance']:,.0f} EGP")
    print(f"  Ending balance  : {summary['projected_ending_balance']:,.0f} EGP")
    print(f"  Net cash flow   : {summary['net_cash_flow']:+,.0f} EGP")
    print(f"  Total income    : {summary['total_income']:,.0f} EGP")
    print(f"  Total expenses  : {summary['total_expense']:,.0f} EGP")
    print("-" * 50)
    print(f"  Fixed incomes   : {len(rules['fixed_incomes'])} detected")
    for r in rules["fixed_incomes"]:
        day_val = _rule_day_value(r)
        day_label = f"{day_val:2d}" if isinstance(day_val, int) else "--"
        amount = _rule_amount(r)
        amount_label = f"{float(amount):,.0f}" if amount is not None else "0"
        name = r.get("name", "(unknown)")
        confidence = str(r.get("confidence", "UNKNOWN")).upper()
        print(f"    → Day {day_label}  {name}  +{amount_label} EGP  [{confidence}]")
    print(f"  Fixed expenses  : {len(rules['fixed_expenses'])} detected")
    for r in rules["fixed_expenses"]:
        day_val = _rule_day_value(r)
        day_label = f"{day_val:2d}" if isinstance(day_val, int) else "--"
        amount = _rule_amount(r)
        amount_label = f"{float(amount):,.0f}" if amount is not None else "0"
        name = r.get("name", "(unknown)")
        confidence = str(r.get("confidence", "UNKNOWN")).upper()
        print(f"    → Day {day_label}  {name}  -{amount_label} EGP  [{confidence}]")
    print("-" * 50)
    if warnings:
        print(f"  ⚠️  Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"    [{w['date']}] {w['type']}: {w['message']}")
    else:
        print("  ✅ No balance warnings.")
    print("=" * 50)


if __name__ == "__main__":
    main()
