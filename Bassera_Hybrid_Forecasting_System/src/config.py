from pathlib import Path

WINDOW_DAYS = 35
MAX_SEQ_LEN = 150
PREDICT_DAYS = 30
STEP_DAYS = 1
DATA_CUTOFF_MONTHS = 18

ARTIFACT_DIR = Path("artifacts")
OUTPUT_DIR = Path("outputs")
PLOTS_DIR = OUTPUT_DIR / "plots"

FEATURE_COLS = [
    "hour",
    "hour_slot",
    "day_of_week",
    "day_of_month",
    "week_of_year",
    "month",
    "quarter",
    "is_weekend",
    "is_month_start",
    "is_month_end",
    "days_to_month_end",
    "months_since_start",
    "hijri_month",
    "hijri_day",
    "is_ramadan",
    "is_eid_al_fitr",
    "is_eid_al_adha",
    "rolling_expense_7d",
    "rolling_expense_14d",
    "rolling_expense_30d",
    "tx_count_7d",
    "category_encoded",
    "log_amount_normalized",
]

FUTURE_FEATURE_COLS = [
    "hour_slot",
    "day_of_week",
    "day_of_month",
    "week_of_year",
    "month",
    "quarter",
    "is_weekend",
    "is_month_start",
    "is_month_end",
    "days_to_month_end",
    "months_since_start",
    "hijri_month",
    "hijri_day",
    "is_ramadan",
    "is_eid_al_fitr",
    "is_eid_al_adha",
]
