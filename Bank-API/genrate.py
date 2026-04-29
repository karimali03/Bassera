"""
=============================================================================
  Mock Bank Transaction Generator — Cairo, Egypt
  Author  : Senior Fintech Data Engineer
  Purpose : Reads merchant data from `data.json` and produces a realistic,
            chronologically sorted ledger saved to `generated_ledger.json`.
=============================================================================
"""

import json
import random
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path


# =============================================================================
# CONFIGURATION — Edit these values to change global behaviour
# =============================================================================

# Path to your merchant data file
MERCHANTS_FILE = Path("data.json")

# Output ledger file
OUTPUT_FILE = Path("generated_ledger.json")

# Date range for generation (inclusive)
START_DATE = date(2025, 1, 1)
END_DATE   = date(2026, 4, 29)

# Egyptian weekend: Friday=4, Saturday=5  (Monday=0 … Sunday=6)
WEEKEND_DAYS = {4, 5}

# Currency
CURRENCY = "EGP"

# Probability (0–1) that a workday user also buys coffee/lunch
WORKDAY_LUNCH_PROBABILITY = 0.70

# Probability that a holiday outing generates a shopping transaction
HOLIDAY_SHOPPING_PROBABILITY = 0.50

# Salary credit day (day-of-month). Jitter of ±1 applied automatically.
SALARY_DAY = 25


# =============================================================================
# AMOUNT RANGES (EGP) — (min, max) tuples per category
# Adjust to reflect realistic Cairo spend in 2024–2025
# =============================================================================

AMOUNT_RANGES = {
    "Food_and_Dining":       (45,  350),
    "Groceries":             (150, 1_200),
    "Entertainment":         (80,  600),
    "Transportation":        (25,  180),   # Uber/Careem single trip
    "Services_and_Utilities":(25,  800),
    "Shopping":              (200, 3_500),
    "Health_and_Pharmacy":   (50,  900),
    "Salary_and_Income":     (8_000, 35_000),
}

# Hour windows (start_hour, end_hour) per event type — used for realism
HOUR_WINDOWS = {
    "morning_commute":  (7,  9),
    "lunch":            (12, 15),
    "evening_commute":  (17, 21),
    "holiday_outbound": (10, 14),
    "holiday_activity": (13, 20),
    "holiday_return":   (20, 24),  # 24 wraps to next-day 00:00, handled below
    "grocery_run":      (9,  20),
    "random":           (8,  23),
}


# =============================================================================
# SUBSCRIPTION DEFINITIONS
# Each entry: merchant name, category, base_day (day-of-month or None for
# quarterly), frequency, and fixed amount or range.
#
# Frequencies:
#   "monthly"       — once per month on base_day  (±jitter)
#   "twice_monthly" — twice per month: base_day and base_day+14  (±jitter each)
#   "quarterly"     — once every 3 months starting from the month in
#                     base_month, on base_day
# =============================================================================

SUBSCRIPTIONS = [
    {
        "merchant":   "Netflix Egypt",
        "category":   "Services_and_Utilities",
        "frequency":  "monthly",
        "base_day":   3,
        "amount":     120,          # fixed EGP monthly fee
    },
    {
        "merchant":   "Spotify Egypt",
        "category":   "Services_and_Utilities",
        "frequency":  "monthly",
        "base_day":   3,
        "amount":     60,
    },
    {
        "merchant":   "Shahid VIP",
        "category":   "Services_and_Utilities",
        "frequency":  "monthly",
        "base_day":   7,
        "amount":     85,
    },
    {
        "merchant":   "WE Internet Billing",
        "category":   "Services_and_Utilities",
        "frequency":  "monthly",
        "base_day":   10,
        "amount_range": (299, 599),
    },
    {
        "merchant":   "Cairo Electricity Distribution Company",
        "category":   "Services_and_Utilities",
        "frequency":  "twice_monthly",
        "base_day":   5,
        "amount_range": (180, 950),
    },
    {
        "merchant":   "Cairo Water and Sanitation",
        "category":   "Services_and_Utilities",
        "frequency":  "quarterly",
        "base_day":   15,
        "base_month": 1,            # January, April, July, October
        "amount_range": (80, 250),
    },
    {
        "merchant":   "Vodafone Egypt",
        "category":   "Services_and_Utilities",
        "frequency":  "monthly",
        "base_day":   1,
        "amount_range": (99, 349),
    },
    {
        "merchant":   "Seif Pharmacy",          # standing prescription order
        "category":   "Health_and_Pharmacy",
        "frequency":  "monthly",
        "base_day":   20,
        "amount_range": (150, 400),
    },
]


# =============================================================================
# HELPER UTILITIES
# =============================================================================

def load_merchants(filepath: Path) -> dict:
    """Load and return the merchant JSON from disk."""
    with open(filepath, "r", encoding="utf-8") as fh:
        return json.load(fh)


def is_weekend(d: date) -> bool:
    """Return True if the given date falls on an Egyptian weekend day."""
    return d.weekday() in WEEKEND_DAYS


def random_amount(category: str) -> float:
    """Return a random spend amount for a given category, rounded to 2 dp."""
    lo, hi = AMOUNT_RANGES.get(category, (50, 500))
    return round(random.uniform(lo, hi), 2)


def pick_merchant(merchants: dict, category: str) -> str:
    """Randomly choose a merchant from the given category list."""
    return random.choice(merchants[category])


def random_hour_in_window(window_key: str) -> int:
    """
    Return a random integer hour within the named time window.
    If the window end is 24, it clamps to 23 (caller handles day overflow).
    """
    start, end = HOUR_WINDOWS[window_key]
    return random.randint(start, min(end, 23))


def make_timestamp(d: date, hour: int, minute: int = None) -> str:
    """
    Build a 'YYYY-MM-DD HH:MM' timestamp string.
    If minute is None a random minute is chosen.
    """
    if minute is None:
        minute = random.randint(0, 59)
    return f"{d.isoformat()} {hour:02d}:{minute:02d}"


def make_transaction(
    merchant: str,
    category: str,
    amount: float,
    timestamp: str,
    transaction_type: str = "DEBIT",
    note: str = "",
) -> dict:
    """
    Assemble a single transaction dict with a UUID reference number.
    """
    return {
        "transaction_id": str(uuid.uuid4()),
        "timestamp":      timestamp,
        "merchant":       merchant,
        "category":       category,
        "amount":         amount,
        "currency":       CURRENCY,
        "type":           transaction_type,
        "note":           note,
    }


def apply_jitter(base_day: int, month: int, year: int, jitter_days: int = 3) -> date:
    """
    Return a date near (year, month, base_day) shifted by a random ±jitter.
    Clamps to valid days within the month.
    """
    base = date(year, month, min(base_day, 28))   # 28 is safe for all months
    delta = random.randint(-jitter_days, jitter_days)
    candidate = base + timedelta(days=delta)
    # Keep within the same calendar month
    if candidate.month != month:
        candidate = base
    return candidate


# =============================================================================
# DAILY ROUTINE GENERATORS
# =============================================================================

def generate_workday_transactions(d: date, merchants: dict) -> list:
    """
    Simulate a typical Cairo workday:
      1. Morning commute (Transportation)
      2. Optional lunch / coffee (Food_and_Dining)  — 70 % chance
      3. Evening commute home (Transportation, similar fare)
    """
    txns = []

    # --- Morning commute -------------------------------------------------------
    morning_hour   = random_hour_in_window("morning_commute")
    commute_amount = round(random.uniform(*AMOUNT_RANGES["Transportation"]), 2)

    txns.append(make_transaction(
        merchant  = pick_merchant(merchants, "Transportation"),
        category  = "Transportation",
        amount    = commute_amount,
        timestamp = make_timestamp(d, morning_hour),
        note      = "Morning commute",
    ))

    # --- Optional lunch / coffee -----------------------------------------------
    if random.random() < WORKDAY_LUNCH_PROBABILITY:
        lunch_hour = random_hour_in_window("lunch")
        txns.append(make_transaction(
            merchant  = pick_merchant(merchants, "Food_and_Dining"),
            category  = "Food_and_Dining",
            amount    = random_amount("Food_and_Dining"),
            timestamp = make_timestamp(d, lunch_hour),
            note      = "Workday lunch / coffee",
        ))

    # --- Evening commute -------------------------------------------------------
    # Fare is ±20 % of the morning fare to keep the pair believable
    evening_hour   = random_hour_in_window("evening_commute")
    variance_pct   = random.uniform(-0.20, 0.20)
    return_amount  = round(commute_amount * (1 + variance_pct), 2)
    return_amount  = max(AMOUNT_RANGES["Transportation"][0], return_amount)

    txns.append(make_transaction(
        merchant  = pick_merchant(merchants, "Transportation"),
        category  = "Transportation",
        amount    = return_amount,
        timestamp = make_timestamp(d, evening_hour),
        note      = "Evening commute home",
    ))

    return txns


def generate_holiday_transactions(d: date, merchants: dict) -> list:
    """
    Simulate a Cairo weekend / holiday outing:
      1. Outbound ride (Transportation)
      2. Entertainment or Food_and_Dining activity
      3. Optional Shopping   — 50 % chance
      4. Return ride home    (Transportation, similar fare to outbound)
    """
    txns = []

    # --- Outbound ride ---------------------------------------------------------
    outbound_hour   = random_hour_in_window("holiday_outbound")
    outbound_amount = round(random.uniform(*AMOUNT_RANGES["Transportation"]), 2)

    txns.append(make_transaction(
        merchant  = pick_merchant(merchants, "Transportation"),
        category  = "Transportation",
        amount    = outbound_amount,
        timestamp = make_timestamp(d, outbound_hour),
        note      = "Holiday outing — ride there",
    ))

    # --- Main activity: Entertainment or Food_and_Dining -----------------------
    activity_category = random.choice(["Entertainment", "Food_and_Dining"])
    activity_hour     = random_hour_in_window("holiday_activity")

    txns.append(make_transaction(
        merchant  = pick_merchant(merchants, activity_category),
        category  = activity_category,
        amount    = random_amount(activity_category),
        timestamp = make_timestamp(d, activity_hour),
        note      = "Holiday outing activity",
    ))

    # --- Optional shopping -----------------------------------------------------
    if random.random() < HOLIDAY_SHOPPING_PROBABILITY:
        shop_hour = activity_hour + random.randint(1, 2)   # after the activity
        shop_hour = min(shop_hour, 22)                      # cap at 22:00

        txns.append(make_transaction(
            merchant  = pick_merchant(merchants, "Shopping"),
            category  = "Shopping",
            amount    = random_amount("Shopping"),
            timestamp = make_timestamp(d, shop_hour),
            note      = "Holiday shopping",
        ))

    # --- Return ride -----------------------------------------------------------
    return_hour   = random_hour_in_window("holiday_return")
    variance_pct  = random.uniform(-0.20, 0.20)
    return_amount = round(outbound_amount * (1 + variance_pct), 2)
    return_amount = max(AMOUNT_RANGES["Transportation"][0], return_amount)

    txns.append(make_transaction(
        merchant  = pick_merchant(merchants, "Transportation"),
        category  = "Transportation",
        amount    = return_amount,
        timestamp = make_timestamp(d, return_hour),
        note      = "Holiday outing — ride home",
    ))

    return txns


def generate_incidental_transactions(d: date, merchants: dict) -> list:
    """
    Small random chance of additional organic transactions any day:
      • Grocery run (weekends more likely)
      • Pharmacy visit
    These model the non-routine but frequent micro-purchases in Egyptian life.
    """
    txns = []

    # Grocery probability: 30 % on weekdays, 55 % on weekends
    grocery_prob = 0.55 if is_weekend(d) else 0.30
    if random.random() < grocery_prob:
        hour = random_hour_in_window("grocery_run")
        txns.append(make_transaction(
            merchant  = pick_merchant(merchants, "Groceries"),
            category  = "Groceries",
            amount    = random_amount("Groceries"),
            timestamp = make_timestamp(d, hour),
            note      = "Grocery run",
        ))

    # Pharmacy probability: 15 % any day
    if random.random() < 0.15:
        hour = random_hour_in_window("random")
        txns.append(make_transaction(
            merchant  = pick_merchant(merchants, "Health_and_Pharmacy"),
            category  = "Health_and_Pharmacy",
            amount    = random_amount("Health_and_Pharmacy"),
            timestamp = make_timestamp(d, hour),
            note      = "Pharmacy purchase",
        ))

    return txns


# =============================================================================
# SUBSCRIPTION GENERATOR
# =============================================================================

def generate_subscriptions(merchants: dict, start: date, end: date) -> list:
    """
    Iterate over the SUBSCRIPTIONS config and emit a transaction for every
    billing cycle that falls within [start, end].
    """
    txns = []

    # Build a quick lookup: category → list of merchant names
    # (so we can validate the merchant exists in data.json)

    for sub in SUBSCRIPTIONS:
        merchant  = sub["merchant"]
        category  = sub["category"]
        frequency = sub["frequency"]
        base_day  = sub["base_day"]

        # Resolve amount
        if "amount" in sub:
            fixed_amount = sub["amount"]
            use_range    = False
        else:
            use_range    = True

        # ── monthly ────────────────────────────────────────────────────────
        if frequency == "monthly":
            current = date(start.year, start.month, 1)
            while current <= end:
                billing_date = apply_jitter(base_day, current.month, current.year)
                if start <= billing_date <= end:
                    amount = random_amount(category) if use_range else fixed_amount
                    txns.append(make_transaction(
                        merchant  = merchant,
                        category  = category,
                        amount    = amount,
                        timestamp = make_timestamp(billing_date, random.randint(0, 23)),
                        note      = f"Subscription — {frequency}",
                    ))
                # Advance one month
                if current.month == 12:
                    current = date(current.year + 1, 1, 1)
                else:
                    current = date(current.year, current.month + 1, 1)

        # ── twice_monthly ──────────────────────────────────────────────────
        elif frequency == "twice_monthly":
            current = date(start.year, start.month, 1)
            while current <= end:
                for offset in (0, 14):          # e.g., day 5 and day 19
                    billing_date = apply_jitter(
                        base_day + offset, current.month, current.year
                    )
                    if start <= billing_date <= end:
                        amount = random_amount(category) if use_range else fixed_amount
                        txns.append(make_transaction(
                            merchant  = merchant,
                            category  = category,
                            amount    = amount,
                            timestamp = make_timestamp(billing_date, random.randint(0, 23)),
                            note      = f"Subscription — {frequency}",
                        ))
                if current.month == 12:
                    current = date(current.year + 1, 1, 1)
                else:
                    current = date(current.year, current.month + 1, 1)

        # ── quarterly ──────────────────────────────────────────────────────
        elif frequency == "quarterly":
            base_month = sub.get("base_month", start.month)
            # Generate the four possible anchor months in a year
            anchor_months = [base_month, base_month + 3, base_month + 6, base_month + 9]
            for year in range(start.year, end.year + 1):
                for month in anchor_months:
                    if month > 12:
                        continue                 # skip invalid months
                    billing_date = apply_jitter(base_day, month, year)
                    if start <= billing_date <= end:
                        amount = random_amount(category) if use_range else fixed_amount
                        txns.append(make_transaction(
                            merchant  = merchant,
                            category  = category,
                            amount    = amount,
                            timestamp = make_timestamp(billing_date, random.randint(0, 23)),
                            note      = f"Subscription — {frequency}",
                        ))

    return txns


# =============================================================================
# SALARY GENERATOR
# =============================================================================

def generate_salary_credits(merchants: dict, start: date, end: date) -> list:
    """
    Emit one salary CREDIT per month on approximately SALARY_DAY (±1 jitter).
    The merchant is drawn from Salary_and_Income and the amount is in the
    defined range for that category.
    """
    txns    = []
    current = date(start.year, start.month, 1)

    while current <= end:
        salary_date = apply_jitter(SALARY_DAY, current.month, current.year, jitter_days=1)
        if start <= salary_date <= end:
            txns.append(make_transaction(
                merchant         = pick_merchant(merchants, "Salary_and_Income"),
                category         = "Salary_and_Income",
                amount           = random_amount("Salary_and_Income"),
                timestamp        = make_timestamp(salary_date, random.randint(7, 12)),
                transaction_type = "CREDIT",
                note             = "Monthly salary credit",
            ))
        # Advance one month
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)

    return txns


# =============================================================================
# MAIN ORCHESTRATOR
# =============================================================================

def generate_ledger(
    merchants: dict,
    start: date,
    end: date,
) -> list:
    """
    Walk every calendar day in [start, end] and accumulate transactions.
    Then merge with subscriptions and salary credits, and sort chronologically.
    """
    all_transactions = []

    # ── Daily spending loop ────────────────────────────────────────────────────
    current_day = start
    while current_day <= end:

        if is_weekend(current_day):
            daily_txns = generate_holiday_transactions(current_day, merchants)
        else:
            daily_txns = generate_workday_transactions(current_day, merchants)

        # Incidental purchases happen any day
        daily_txns += generate_incidental_transactions(current_day, merchants)
        all_transactions.extend(daily_txns)

        current_day += timedelta(days=1)

    # ── Subscriptions ──────────────────────────────────────────────────────────
    all_transactions.extend(generate_subscriptions(merchants, start, end))

    # ── Salary credits ─────────────────────────────────────────────────────────
    all_transactions.extend(generate_salary_credits(merchants, start, end))

    # ── Sort chronologically ───────────────────────────────────────────────────
    all_transactions.sort(key=lambda tx: tx["timestamp"])

    return all_transactions


# =============================================================================
# ENTRY POINT
# =============================================================================

def main():
    # 1. Load merchant data
    if not MERCHANTS_FILE.exists():
        raise FileNotFoundError(
            f"Could not find '{MERCHANTS_FILE}'. "
            "Make sure data.json is in the same directory as this script."
        )

    merchants = load_merchants(MERCHANTS_FILE)
    print(f"[✓] Loaded merchant data from '{MERCHANTS_FILE}'")
    print(f"    Categories found: {list(merchants.keys())}")

    # 2. Generate ledger
    print(f"\n[→] Generating transactions from {START_DATE} to {END_DATE} …")
    ledger = generate_ledger(merchants, START_DATE, END_DATE)
    print(f"[✓] Generated {len(ledger):,} transactions")

    # 3. Write output
    with open(OUTPUT_FILE, "w", encoding="utf-8") as fh:
        json.dump(ledger, fh, ensure_ascii=False, indent=2)

    print(f"[✓] Ledger written to '{OUTPUT_FILE}'")

    # 4. Quick summary stats
    from collections import Counter
    cat_counts = Counter(tx["category"] for tx in ledger)
    type_totals = {
        t: round(sum(tx["amount"] for tx in ledger if tx["type"] == t), 2)
        for t in ("DEBIT", "CREDIT")
    }
    print("\n── Category breakdown ───────────────────────────────────────")
    for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
        print(f"   {cat:<30} {count:>4} txns")
    print("\n── Financial summary ────────────────────────────────────────")
    print(f"   Total debits  : EGP {type_totals.get('DEBIT',  0):>12,.2f}")
    print(f"   Total credits : EGP {type_totals.get('CREDIT', 0):>12,.2f}")
    net = type_totals.get("CREDIT", 0) - type_totals.get("DEBIT", 0)
    print(f"   Net balance   : EGP {net:>12,.2f}")
    print("─────────────────────────────────────────────────────────────\n")


if __name__ == "__main__":
    main()