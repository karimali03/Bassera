from typing import List, Dict, Any

import pandas as pd

# ---------------------------------------------------------------------------
# HEURISTIC THRESHOLDS
# 
# DAY_STD_THRESHOLD: 
# Maximum allowed Standard Deviation (in days) for a pattern to be considered fixed.
# A value of 2.5 allows a transaction to jitter slightly across weekends/holidays
# without being disqualified.
DAY_STD_THRESHOLD = 2.5

# AMOUNT_CV_THRESHOLD:
# Coefficient of Variation (CV) = Standard Deviation / Mean.
# A CV of 0.15 means the transaction amount can vary by up to 15% from its average.
# This accommodates bills (like electricity or water) that fluctuate slightly
# each month but still represent deterministic obligations.
AMOUNT_CV_THRESHOLD = 0.25

# Stricter thresholds required to classify a pattern as "HIGH" confidence.
HIGH_DAY_STD = 1.5
HIGH_AMOUNT_CV = 0.20
# ---------------------------------------------------------------------------


def detect_recurring_patterns(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Sweeps the transaction history to identify recurring deterministic patterns.
    
    A pattern is considered deterministic if it happens around the same time 
    of the month (low day_of_month standard deviation) and for roughly the same 
    amount (low coefficient of variation).
    
    Args:
        df (pd.DataFrame): The raw, uncapped transaction ledger.
        
    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each representing a detected rule.
    """
    patterns: List[Dict[str, Any]] = []
    if df.empty:
        return patterns

    max_ts = df["timestamp"].max()
    df = df.copy()
    df["day_of_month"] = df["timestamp"].dt.day

    for (category, merchant), group in df.groupby(["category", "merchant"]):
        occurrences = len(group)
        if occurrences < 3:
            continue

        # 1. Timing Consistency Check
        day_std = float(group["day_of_month"].std(ddof=0) or 0.0)
        
        # 2. Amount Consistency Check
        abs_amount = group["amount"].abs()
        amount_mean = float(abs_amount.mean())
        amount_std = float(abs_amount.std(ddof=0) or 0.0)
        amount_cv = float(amount_std / amount_mean) if amount_mean > 0 else float("inf")

        day_fixed = day_std <= DAY_STD_THRESHOLD
        amount_fixed = amount_cv <= AMOUNT_CV_THRESHOLD

        if day_fixed and amount_fixed:
            if occurrences >= 6 and day_std <= HIGH_DAY_STD and amount_cv <= HIGH_AMOUNT_CV:
                confidence = "high"
            else:
                confidence = "medium"
        else:
            confidence = "low"

        # 3. Activation Check
        # If the pattern hasn't been seen in the last 2 months, it might be a cancelled 
        # subscription or finished installment. Mark as inactive.
        median_day = int(group["day_of_month"].median())
        median_amount = float(group["amount"].median())
        last_seen = group["timestamp"].max().normalize()
        active = last_seen >= (max_ts.normalize() - pd.DateOffset(months=2))

        patterns.append(
            {
                "category": category,
                "merchant": merchant,
                "type": "income" if median_amount >= 0 else "expense",
                "day_of_month": median_day,
                "amount": median_amount,
                "amount_std": float(group["amount"].std(ddof=0) or 0.0),
                "occurrences": occurrences,
                "last_seen": last_seen.date().isoformat(),
                "confidence": confidence,
                "active": bool(active),
            }
        )

    return patterns


def format_patterns_summary(patterns: List[Dict[str, Any]]) -> str:
    """
    Formats the detected patterns into a human-readable CLI summary block.
    
    Args:
        patterns (List[Dict[str, Any]]): The list of detected pattern rules.
        
    Returns:
        str: A formatted string block ready for console printing.
    """
    lines = [
        "DETECTED PATTERNS FOR USER",
        "---------------------------------------------",
    ]

    if not patterns:
        lines.append("No recurring patterns detected.")
        return "\n".join(lines)

    for pattern in patterns:
        amount = float(pattern.get("amount", 0.0))
        sign = "+" if amount >= 0 else "-"
        amount_text = f"{sign}{abs(amount):,.0f} EGP"
        conf = str(pattern.get("confidence", "")).upper()
        occ = int(pattern.get("occurrences", 0))
        day = int(pattern.get("day_of_month", 0))
        category = str(pattern.get("category", ""))
        merchant = str(pattern.get("merchant", ""))
        lines.append(
            f"[{category}] ({merchant}) {amount_text}  every day {day}   confidence: {conf}   ({occ} occurrences)"
        )

    return "\n".join(lines)
