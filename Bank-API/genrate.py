"""
=============================================================================
  Mock Bank Transaction Generator — Cairo, Egypt
  Author  : Senior Fintech Data Engineer
  Purpose : Reads merchant data from `data.json` and produces a realistic,
            chronologically sorted ledger saved to `generated_ledger.json`.
=============================================================================
"""

from collections import Counter
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
START_DATE = date(2020, 1, 1)
END_DATE   = date(2026, 4, 29)
# Egyptian weekend: Friday=4, Saturday=5  (Monday=0 … Sunday=6)
WEEKEND_DAYS = {4, 5}
# Currency
CURRENCY = "EGP"
# Income toggles
ENABLE_FIXED_SALARY = True
ENABLE_FREELANCE_INCOME = True
# Probability (0–1) that a workday user also buys coffee/lunch
WORKDAY_LUNCH_PROBABILITY = 0.70
# Probability that a holiday outing generates a shopping transaction
HOLIDAY_SHOPPING_PROBABILITY = 0.50
# Number of vacation trips to generate per year
VACATION_TRIPS_PER_YEAR = (1, 3)
# Salary credit day (day-of-month). Jitter of ±1 applied automatically.
SALARY_DAY = 25
# Freelance income settings
FREELANCE_PROJECTS_PER_MONTH = (0, 5)
# =============================================================================
# INFLATION CONFIGURATION
#
# BASE_YEAR is the reference year — all AMOUNT_RANGES below are expressed in
# BASE_YEAR prices.  For every other year the amount is multiplied by the
# cumulative price index.
#
# ANNUAL_INFLATION_RATES: Egypt CPI-based approximate annual rates.
# Sources: CBE / World Bank / IMF estimates.
#   2020: ~5.7 %   (pre-devaluation, moderate)
#   2021: ~5.2 %
#   2022: ~13.9 %  (post-Ukraine shock, first EGP float)
#   2023: ~35.7 %  (second float + FX liberalisation)
#   2024: ~33.3 %  (continued pass-through)
#   2025: ~16.0 %  (gradual disinflation)
#   2026: ~12.0 %  (forecast)
#
# Any year not in the table falls back to FALLBACK_INFLATION_RATE.
# =============================================================================

BASE_YEAR = 2020

ANNUAL_INFLATION_RATES: dict[int, float] = {
    2020: 0.057,
    2021: 0.052,
    2022: 0.139,
    2023: 0.357,
    2024: 0.333,
    2025: 0.160,
    2026: 0.120,
}

FALLBACK_INFLATION_RATE = 0.10  # 10 % for any unlisted year


def _build_price_index() -> dict[int, float]:
    """
    Pre-compute a cumulative price index for every year from BASE_YEAR to the
    last key in ANNUAL_INFLATION_RATES + a few years of buffer.

    Index[BASE_YEAR] = 1.0 by definition.
    Index[y]         = Index[y-1] * (1 + rate[y])
    """
    all_years = sorted(ANNUAL_INFLATION_RATES) + [max(ANNUAL_INFLATION_RATES) + 5]
    index: dict[int, float] = {BASE_YEAR: 1.0}
    prev_year = BASE_YEAR
    for year in range(BASE_YEAR + 1, all_years[-1] + 1):
        rate = ANNUAL_INFLATION_RATES.get(year, FALLBACK_INFLATION_RATE)
        index[year] = index[prev_year] * (1.0 + rate)
        prev_year = year
    return index


# Computed once at module load time
_PRICE_INDEX: dict[int, float] = _build_price_index()


def inflate(amount: float, year: int) -> float:
    """
    Return `amount` (expressed in BASE_YEAR prices) scaled to `year` prices.
    Result is rounded to 2 decimal places.
    """
    factor = _PRICE_INDEX.get(year, _PRICE_INDEX.get(max(_PRICE_INDEX), 1.0))
    return round(amount * factor, 2)


# =============================================================================
# AMOUNT RANGES (EGP, in BASE_YEAR = 2020 prices)
# Adjust to reflect realistic Cairo spend at the base year; inflation is
# applied automatically at transaction-generation time.
# =============================================================================

AMOUNT_RANGES = {
    "Food_and_Dining":        (45,   350),
    "Groceries":              (150,  1_200),
    "Entertainment":          (80,   600),
    "Transportation":         (25,   180),   # Uber/Careem single trip
    "Travel":                 (60,   650),
    "Services_and_Utilities": (25,   800),
    "Shopping":               (200,  3_500),
    "Health_and_Pharmacy":    (50,   900),
    "Salary_and_Income":      (8_000, 35_000),
    "Freelance_Work":         (500,  12_000),
}

# Hour windows (start_hour, end_hour) per event type — used for realism
HOUR_WINDOWS = {
    "morning_commute":  (7,  9),
    "lunch":            (12, 15),
    "evening_commute":  (17, 21),
    "holiday_outbound": (10, 14),
    "holiday_activity": (13, 20),
    "holiday_return":   (20, 23),
    "grocery_run":      (9,  20),
    "random":           (8,  23),
}


# =============================================================================
# SUBSCRIPTION DEFINITIONS
# Each entry: merchant name, category, base_day (day-of-month or None for
# quarterly),
# Frequencies:
#   "monthly"       — once per month on base_day  (±jitter)
#   "twice_monthly" — twice per month: base_day and base_day+14  (±jitter each)
#   "quarterly"     — once every 3 months starting from the month in
#                     base_month, on base_day
# =============================================================================

SERVICE_SUBSCRIPTION_TEMPLATES = {
    "Netflix Egypt": {
        "merchant":   "Netflix Egypt",
        "category":   "Services_and_Utilities",
        "frequency":  "monthly",
        "base_day":   3,
        "amount":     120,        
    },
    "Spotify Egypt": {
        "merchant":   "Spotify Egypt",
        "category":   "Services_and_Utilities",
        "frequency":  "monthly",
        "base_day":   3,
        "amount":     60,
    },
    "Shahid VIP": {
        "merchant":   "Shahid VIP",
        "category":   "Services_and_Utilities",
        "frequency":  "monthly",
        "base_day":   7,
        "amount":     85,
    },
    "WE Internet Billing": {
        "merchant":     "WE Internet Billing",
        "category":     "Services_and_Utilities",
        "frequency":    "monthly",
        "base_day":     10,
        "amount_range": (299, 599),   # BASE_YEAR prices
    },
    "Cairo Electricity Distribution Company": {
        "merchant":     "Cairo Electricity Distribution Company",
        "category":     "Services_and_Utilities",
        "frequency":    "twice_monthly",
        "base_day":     5,
        "amount_range": (180, 950),
    },
    "Cairo Water and Sanitation": {
        "merchant":     "Cairo Water and Sanitation",
        "category":     "Services_and_Utilities",
        "frequency":    "quarterly",
        "base_day":     15,
        "base_month":   1,            # January, April, July, October
        "amount_range": (80, 250),
    },
    "Vodafone Egypt": {
        "merchant":     "Vodafone Egypt",
        "category":     "Services_and_Utilities",
        "frequency":    "monthly",
        "base_day":     1,
        "amount_range": (99, 349),
    },
    "Seif Pharmacy": {          # standing prescription order
        "merchant":     "Seif Pharmacy",
        "category":     "Health_and_Pharmacy",
        "frequency":    "monthly",
        "base_day":     20,
        "amount_range": (150, 400),
    },
}


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


def random_amount(category: str, year: int) -> float:
    """
    Return a random spend amount for a given category, rounded to 2 dp.
    The base range is expressed in BASE_YEAR prices; the result is inflated
    to `year` prices automatically.
    """
    lo, hi = AMOUNT_RANGES.get(category, (50, 500))
    base_amount = random.uniform(lo, hi)
    return inflate(base_amount, year)


def random_amount_from_range(lo: float, hi: float, year: int) -> float:
    """
    Like random_amount but uses an explicit (lo, hi) range instead of a
    category lookup.  Used for per-subscription amount_range values.
    """
    return inflate(random.uniform(lo, hi), year)


def pick_merchant(merchants: dict, category: str) -> str:
    """Randomly choose a merchant from the given category list."""
    return random.choice(merchants[category])


def build_subscriptions(merchants: dict) -> list:
    """
    Build the subscription plan from data.json so every services merchant is
    represented, while preserving the custom billing patterns for known bills.
    """
    subscriptions = []
    service_merchants = merchants.get("Services_and_Utilities", [])
    recurring_frequencies = ("monthly", "twice_monthly", "quarterly")

    for index, merchant in enumerate(service_merchants):
        template = SERVICE_SUBSCRIPTION_TEMPLATES.get(merchant)
        if template is not None:
            subscriptions.append(template)
            continue

        frequency = recurring_frequencies[index % len(recurring_frequencies)]
        if frequency == "monthly":
            base_day    = 1 + (index % 28)
            extra_fields = {}
        elif frequency == "twice_monthly":
            base_day    = 1 + (index % 14)
            extra_fields = {}
        else:
            base_day    = 1 + (index % 28)
            extra_fields = {"base_month": 1 + (index % 3)}

        subscriptions.append({
            "merchant":     merchant,
            "category":     "Services_and_Utilities",
            "frequency":    frequency,
            "base_day":     base_day,
            "amount_range": (25, 800),
            **extra_fields,
        })

    # Seif Pharmacy lives in Health_and_Pharmacy, not Services_and_Utilities,
    # so it is not picked up by the loop above — append it explicitly.
    subscriptions.append(SERVICE_SUBSCRIPTION_TEMPLATES["Seif Pharmacy"])
    return subscriptions


def random_hour_in_window(window_key: str) -> int:
    """Return a random integer hour within the named time window."""
    start, end = HOUR_WINDOWS[window_key]
    return random.randint(start, end)


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
    """Assemble a single transaction dict with a UUID reference number."""
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
    base      = date(year, month, min(base_day, 28))   # 28 is safe for all months
    delta     = random.randint(-jitter_days, jitter_days)
    candidate = base + timedelta(days=delta)
    # Keep within the same calendar month
    if candidate.month != month:
        candidate = base
    return candidate


def _resolve_sub_amount(sub: dict, year: int) -> float:
    """
    FIX 1: Resolve the transaction amount for a subscription entry.

    Priority:
      1. "amount"       — fixed EGP value (from BASE_YEAR), inflated to year.
      2. "amount_range" — (lo, hi) tuple (BASE_YEAR prices), inflated to year.
      3. Fallback       — general AMOUNT_RANGES for the subscription's category.

    Previously the code only checked for "amount" and fell back directly to
    random_amount(category), silently ignoring any "amount_range" on the sub.
    """
    if "amount" in sub:
        return inflate(sub["amount"], year)
    if "amount_range" in sub:
        lo, hi = sub["amount_range"]
        return random_amount_from_range(lo, hi, year)
    return random_amount(sub["category"], year)


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
    year = d.year

    # --- Morning commute -------------------------------------------------------
    morning_hour   = random_hour_in_window("morning_commute")
    commute_amount = random_amount("Transportation", year)

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
            amount    = random_amount("Food_and_Dining", year),
            timestamp = make_timestamp(d, lunch_hour),
            note      = "Workday lunch / coffee",
        ))

    # --- Evening commute -------------------------------------------------------
    # Fare is ±20 % of the morning fare to keep the pair believable
    evening_hour  = random_hour_in_window("evening_commute")
    variance_pct  = random.uniform(-0.20, 0.20)
    return_amount = round(commute_amount * (1 + variance_pct), 2)
    return_amount = max(inflate(AMOUNT_RANGES["Transportation"][0], year), return_amount)

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
      1. Outbound ride (Transportation or Travel)
      2. Entertainment or Food_and_Dining activity
      3. Optional Shopping   — 50 % chance
      4. Return ride home    (Transportation or Travel, similar fare to outbound)
    """
    txns = []
    year = d.year

    # --- Outbound ride ---------------------------------------------------------
    outbound_hour   = random_hour_in_window("holiday_outbound")
    travel_category = random.choice(["Transportation", "Travel"])
    outbound_amount = random_amount(travel_category, year)

    txns.append(make_transaction(
        merchant  = pick_merchant(merchants, travel_category),
        category  = travel_category,
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
        amount    = random_amount(activity_category, year),
        timestamp = make_timestamp(d, activity_hour),
        note      = "Holiday outing activity",
    ))

    # --- Optional shopping -----------------------------------------------------
    if random.random() < HOLIDAY_SHOPPING_PROBABILITY:
        shop_hour = min(activity_hour + random.randint(1, 2), 22)
        txns.append(make_transaction(
            merchant  = pick_merchant(merchants, "Shopping"),
            category  = "Shopping",
            amount    = random_amount("Shopping", year),
            timestamp = make_timestamp(d, shop_hour),
            note      = "Holiday shopping",
        ))

    # --- Return ride -----------------------------------------------------------
    return_hour   = random_hour_in_window("holiday_return")
    variance_pct  = random.uniform(-0.20, 0.20)
    return_amount = round(outbound_amount * (1 + variance_pct), 2)
    return_amount = max(inflate(AMOUNT_RANGES[travel_category][0], year), return_amount)

    txns.append(make_transaction(
        merchant  = pick_merchant(merchants, travel_category),
        category  = travel_category,
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
    year = d.year

    # Grocery probability: 30 % on weekdays, 55 % on weekends
    grocery_prob = 0.55 if is_weekend(d) else 0.30
    if random.random() < grocery_prob:
        hour = random_hour_in_window("grocery_run")
        txns.append(make_transaction(
            merchant  = pick_merchant(merchants, "Groceries"),
            category  = "Groceries",
            amount    = random_amount("Groceries", year),
            timestamp = make_timestamp(d, hour),
            note      = "Grocery run",
        ))

    # Pharmacy probability: 15 % any day
    if random.random() < 0.15:
        hour = random_hour_in_window("random")
        txns.append(make_transaction(
            merchant  = pick_merchant(merchants, "Health_and_Pharmacy"),
            category  = "Health_and_Pharmacy",
            amount    = random_amount("Health_and_Pharmacy", year),
            timestamp = make_timestamp(d, hour),
            note      = "Pharmacy purchase",
        ))

    return txns


# =============================================================================
# VACATION GENERATOR
# =============================================================================

def generate_vacation_transactions(
    merchants: dict,
    start: date,
    end: date,
) -> tuple[list, set]:
    """
    Generate 1–3 vacation trips per year. Each trip includes travel legs plus
    a few discretionary expenses during the stay.

    Returns
    -------
    txns        : list of transaction dicts
    vacation_days : set of date objects that are part of a vacation trip
                   (used by generate_ledger to suppress the daily loop on
                   those days — FIX 2).
    """
    txns: list         = []
    vacation_days: set = set()

    for year in range(start.year, end.year + 1):
        year_start = max(start, date(year, 1, 1))
        year_end   = min(end,   date(year, 12, 31))
        if year_start > year_end:
            continue

        trip_count = random.randint(*VACATION_TRIPS_PER_YEAR)
        for _ in range(trip_count):
            trip_length  = random.randint(3, 7)
            latest_start = year_end - timedelta(days=trip_length - 1)
            if latest_start < year_start:
                continue

            trip_start = year_start + timedelta(
                days=random.randint(0, (latest_start - year_start).days)
            )
            trip_days  = [trip_start + timedelta(days=i) for i in range(trip_length)]

            # Register every day of this trip so the daily loop skips them
            vacation_days.update(trip_days)

            outbound_day    = trip_days[0]
            return_day      = trip_days[-1]
            outbound_hour   = random_hour_in_window("holiday_outbound")
            outbound_amount = random_amount("Travel", year)

            txns.append(make_transaction(
                merchant  = pick_merchant(merchants, "Travel"),
                category  = "Travel",
                amount    = outbound_amount,
                timestamp = make_timestamp(outbound_day, outbound_hour),
                note      = f"Vacation outbound trip ({trip_length} days)",
            ))

            if trip_length > 2:
                midpoint_day      = trip_days[trip_length // 2]
                activity_category = random.choice(["Entertainment", "Food_and_Dining", "Shopping"])
                txns.append(make_transaction(
                    merchant  = pick_merchant(merchants, activity_category),
                    category  = activity_category,
                    amount    = random_amount(activity_category, year),
                    timestamp = make_timestamp(midpoint_day, random_hour_in_window("holiday_activity")),
                    note      = "Vacation activity",
                ))

            if random.random() < 0.60 and trip_length > 3:
                txns.append(make_transaction(
                    merchant  = pick_merchant(merchants, "Food_and_Dining"),
                    category  = "Food_and_Dining",
                    amount    = random_amount("Food_and_Dining", year),
                    timestamp = make_timestamp(trip_days[1], random_hour_in_window("lunch")),
                    note      = "Vacation meal",
                ))

            return_amount = round(outbound_amount * random.uniform(0.85, 1.15), 2)
            return_amount = max(inflate(AMOUNT_RANGES["Travel"][0], year), return_amount)

            txns.append(make_transaction(
                merchant  = pick_merchant(merchants, "Travel"),
                category  = "Travel",
                amount    = return_amount,
                timestamp = make_timestamp(return_day, random_hour_in_window("holiday_return")),
                note      = "Vacation return trip",
            ))

    return txns, vacation_days


# =============================================================================
# SUBSCRIPTION GENERATOR
# =============================================================================

def generate_subscriptions(merchants: dict, start: date, end: date) -> list:
    """
    Iterate over the subscription plan built from data.json and emit a
    transaction for every billing cycle that falls within [start, end].
    """
    txns = []

    for sub in build_subscriptions(merchants):
        merchant  = sub["merchant"]
        category  = sub["category"]
        frequency = sub["frequency"]
        base_day  = sub["base_day"]

        # ── monthly ────────────────────────────────────────────────────────
        if frequency == "monthly":
            current = date(start.year, start.month, 1)
            while current <= end:
                billing_date = apply_jitter(base_day, current.month, current.year)
                if start <= billing_date <= end:
                    txns.append(make_transaction(
                        merchant  = merchant,
                        category  = category,
                        # FIX 1: use _resolve_sub_amount so per-template
                        # amount_range values are honoured.
                        amount    = _resolve_sub_amount(sub, billing_date.year),
                        timestamp = make_timestamp(billing_date, random.randint(0, 23)),
                        note      = f"Subscription — {frequency}",
                    ))
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
                        txns.append(make_transaction(
                            merchant  = merchant,
                            category  = category,
                            amount    = _resolve_sub_amount(sub, billing_date.year),
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
            for year in range(start.year, end.year + 1):
                for quarter_offset in (0, 3, 6, 9):
                    raw_month = base_month + quarter_offset
                    # FIX 3: wrap months >12 into the correct calendar year
                    # instead of skipping them with `continue`.
                    actual_year  = year + (raw_month - 1) // 12
                    actual_month = ((raw_month - 1) % 12) + 1
                    if actual_year > end.year:
                        continue
                    billing_date = apply_jitter(base_day, actual_month, actual_year)
                    if start <= billing_date <= end:
                        txns.append(make_transaction(
                            merchant  = merchant,
                            category  = category,
                            amount    = _resolve_sub_amount(sub, billing_date.year),
                            timestamp = make_timestamp(billing_date, random.randint(0, 23)),
                            note      = f"Subscription — {frequency}",
                        ))

    return txns


# =============================================================================
# SALARY GENERATOR
# =============================================================================

def generate_salary_credits(merchants: dict, start: date, end: date) -> list:
    """
    Emit one salary CREDIT per month on approximately SALARY_DAY (±1 jitter)
    when fixed salary generation is enabled.
    """
    if not ENABLE_FIXED_SALARY:
        return []

    txns    = []
    current = date(start.year, start.month, 1)

    while current <= end:
        salary_date = apply_jitter(SALARY_DAY, current.month, current.year, jitter_days=1)
        if start <= salary_date <= end:
            txns.append(make_transaction(
                merchant         = pick_merchant(merchants, "Salary_and_Income"),
                category         = "Salary_and_Income",
                amount           = random_amount("Salary_and_Income", salary_date.year),
                timestamp        = make_timestamp(salary_date, random.randint(7, 12)),
                transaction_type = "CREDIT",
                note             = "Monthly salary credit",
            ))
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)

    return txns


def generate_freelance_credits(merchants: dict, start: date, end: date) -> list:
    """
    Emit 0–5 freelance CREDIT transactions per month when enabled.
    Each month chooses a random project count and a variable amount per project.
    """
    if not ENABLE_FREELANCE_INCOME:
        return []

    txns = []
    current = date(start.year, start.month, 1)

    while current <= end:
        project_count = random.randint(*FREELANCE_PROJECTS_PER_MONTH)
        month_start = current
        if current.month == 12:
            next_month = date(current.year + 1, 1, 1)
        else:
            next_month = date(current.year, current.month + 1, 1)
        month_end = min(end, next_month - timedelta(days=1))

        for _ in range(project_count):
            project_day = month_start + timedelta(days=random.randint(0, (month_end - month_start).days))
            txns.append(make_transaction(
                merchant         = pick_merchant(merchants, "Freelance_Work"),
                category         = "Freelance_Work",
                amount           = random_amount("Freelance_Work", project_day.year),
                timestamp        = make_timestamp(project_day, random.randint(9, 19)),
                transaction_type = "CREDIT",
                note             = "Freelance project payment",
            ))

        current = next_month

    return txns


# =============================================================================
# MAIN ORCHESTRATOR
# =============================================================================

def generate_ledger(merchants: dict, start: date, end: date) -> list:
    """
    Walk every calendar day in [start, end] and accumulate transactions.
    Then merge with subscriptions and salary credits, and sort chronologically.
    """
    all_transactions: list = []

    # ── Vacations first so we know which days to skip in the daily loop ────────
    # FIX 2: vacation_days is now returned and used to suppress the normal
    # daily commute/outing loop on days the person is away on a trip.
    vacation_txns, vacation_days = generate_vacation_transactions(merchants, start, end)
    all_transactions.extend(vacation_txns)

    # ── Daily spending loop ────────────────────────────────────────────────────
    current_day = start
    while current_day <= end:

        if current_day in vacation_days:
            current_day += timedelta(days=1)
            continue

        if is_weekend(current_day):
            daily_txns = generate_holiday_transactions(current_day, merchants)
        else:
            daily_txns = generate_workday_transactions(current_day, merchants)

        # Incidental purchases happen any non-vacation day
        daily_txns += generate_incidental_transactions(current_day, merchants)
        all_transactions.extend(daily_txns)

        current_day += timedelta(days=1)

    # ── Subscriptions ──────────────────────────────────────────────────────────
    all_transactions.extend(generate_subscriptions(merchants, start, end))

    # ── Income credits ─────────────────────────────────────────────────────────
    all_transactions.extend(generate_salary_credits(merchants, start, end))
    all_transactions.extend(generate_freelance_credits(merchants, start, end))

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

    # 2. Show inflation index for transparency
    print("\n── Inflation price index (relative to BASE_YEAR) ────────────")
    for yr in sorted(yr for yr in _PRICE_INDEX if START_DATE.year <= yr <= END_DATE.year):
        print(f"   {yr}: ×{_PRICE_INDEX[yr]:.4f}")

    # 3. Generate ledger
    print(f"\n[→] Generating transactions from {START_DATE} to {END_DATE} …")
    ledger = generate_ledger(merchants, START_DATE, END_DATE)
    print(f"[✓] Generated {len(ledger):,} transactions")

    # 4. Write output
    with open(OUTPUT_FILE, "w", encoding="utf-8") as fh:
        json.dump(ledger, fh, ensure_ascii=False, indent=2)
    print(f"[✓] Ledger written to '{OUTPUT_FILE}'")

    # 5. Quick summary stats
    cat_counts = Counter(tx["category"] for tx in ledger)
    type_totals = {
        t: round(sum(tx["amount"] for tx in ledger if tx["type"] == t), 2)
        for t in ("DEBIT", "CREDIT")
    }
    print("\n── Category breakdown ───────────────────────────────────────")
    for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
        print(f"   {cat:<38} {count:>4} txns")
    print("\n── Financial summary ────────────────────────────────────────")
    print(f"   Total debits  : EGP {type_totals.get('DEBIT',  0):>14,.2f}")
    print(f"   Total credits : EGP {type_totals.get('CREDIT', 0):>14,.2f}")
    net = type_totals.get("CREDIT", 0) - type_totals.get("DEBIT", 0)
    print(f"   Net balance   : EGP {net:>14,.2f}")
    print("─────────────────────────────────────────────────────────────\n")


if __name__ == "__main__":
    main()