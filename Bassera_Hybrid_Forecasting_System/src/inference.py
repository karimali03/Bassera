from typing import Iterable, List, Tuple

import numpy as np
import pandas as pd
import torch
from hijri_converter import convert

from .config import FUTURE_FEATURE_COLS


def _months_since_start(target_date: pd.Timestamp, start_date: pd.Timestamp) -> int:
    start = pd.Timestamp(start_date).normalize()
    return (target_date.year - start.year) * 12 + (target_date.month - start.month)


def extract_future_features(
    target_date: pd.Timestamp, history_start_date: pd.Timestamp
) -> np.ndarray:
    hijri = convert.Gregorian(
        target_date.year, target_date.month, target_date.day
    ).to_hijri()

    date_only = target_date.normalize()
    month_end = date_only + pd.offsets.MonthEnd(0)
    days_to_month_end = (month_end - date_only).days

    features = {
        "hour_slot": 0,
        "day_of_week": int(target_date.dayofweek),
        "day_of_month": int(target_date.day),
        "week_of_year": int(target_date.isocalendar()[1]),
        "month": int(target_date.month),
        "quarter": int(target_date.quarter),
        "is_weekend": int(target_date.dayofweek in [4, 5]),
        "is_month_start": int(target_date.day <= 5),
        "is_month_end": int(target_date.day >= 25),
        "days_to_month_end": int(days_to_month_end),
        "months_since_start": int(_months_since_start(target_date, history_start_date)),
        "hijri_month": int(hijri.month),
        "hijri_day": int(hijri.day),
        "is_ramadan": int(hijri.month == 9),
        "is_eid_al_fitr": int(hijri.month == 10 and hijri.day <= 3),
        "is_eid_al_adha": int(hijri.month == 12 and hijri.day <= 3),
    }

    return np.array([features[col] for col in FUTURE_FEATURE_COLS], dtype=np.float32)


def build_future_features(
    future_dates: Iterable[pd.Timestamp], history_start_date: pd.Timestamp
) -> np.ndarray:
    feats = [extract_future_features(d, history_start_date) for d in future_dates]
    return np.stack(feats)


def build_history_sequence(
    df_expense: pd.DataFrame,
    feature_cols: List[str],
    window_days: int,
    max_seq_len: int,
) -> np.ndarray:
    max_ts = df_expense["timestamp"].max()
    window_start = max_ts - pd.Timedelta(days=window_days)
    hist = df_expense[df_expense["timestamp"] >= window_start]
    seq = np.nan_to_num(hist[feature_cols].to_numpy(dtype=np.float32), nan=0.0)

    if len(seq) > max_seq_len:
        seq = seq[-max_seq_len:]
    elif len(seq) < max_seq_len:
        pad = np.zeros((max_seq_len - len(seq), seq.shape[1]), dtype=np.float32)
        seq = np.vstack([pad, seq])

    return seq


def _rule_contributions(
    future_dates: Iterable[pd.Timestamp], patterns: List[dict]
) -> Tuple[np.ndarray, np.ndarray]:
    rule_income = np.zeros(len(future_dates), dtype=np.float64)
    rule_expense = np.zeros(len(future_dates), dtype=np.float64)

    usable = [
        p
        for p in patterns
        if p.get("confidence") in {"high", "medium"} and p.get("active")
    ]

    for i, date in enumerate(future_dates):
        for pattern in usable:
            if int(pattern["day_of_month"]) != int(date.day):
                continue
            if pattern["type"] == "income":
                rule_income[i] += abs(float(pattern["amount"]))
            else:
                rule_expense[i] += abs(float(pattern["amount"]))

    return rule_income, rule_expense


def forecast_trajectory(
    model: torch.nn.Module,
    df_expense: pd.DataFrame,
    patterns: List[dict],
    history_start_date: pd.Timestamp,
    starting_balance: float,
    horizon_days: int,
    feature_cols: List[str],
    window_days: int,
    max_seq_len: int,
    device: torch.device,
) -> pd.DataFrame:
    model.eval()

    last_date = df_expense["timestamp"].max().normalize()
    future_dates = pd.date_range(
        start=last_date + pd.Timedelta(days=1), periods=horizon_days, freq="D"
    )

    seq = build_history_sequence(df_expense, feature_cols, window_days, max_seq_len)
    x_seq = torch.tensor(seq, dtype=torch.float32).unsqueeze(0).to(device)

    with torch.no_grad():
        h = model.encode(x_seq)

    x_future = build_future_features(future_dates, history_start_date)
    x_future_t = torch.tensor(x_future, dtype=torch.float32).to(device)

    with torch.no_grad():
        h_expanded = h.expand(x_future_t.shape[0], -1)
        combined = torch.cat([h_expanded, x_future_t], dim=-1)
        # Shape: [horizon_days, 2] — column 0 = expense, column 1 = income
        preds = model.decoder(combined).cpu().numpy()

    rule_income, rule_expense = _rule_contributions(future_dates, patterns)
    # Inverse the log1p transform to convert back to raw EGP
    gru_expense = np.expm1(preds[:, 0])
    gru_income  = np.expm1(preds[:, 1])

    total_income  = rule_income + gru_income
    total_expense = rule_expense + gru_expense
    net = total_income - total_expense
    projected_balance = starting_balance + np.cumsum(net)

    return pd.DataFrame(
        {
            "date": future_dates,
            "rule_income": rule_income,
            "rule_expense": rule_expense,
            "gru_expense": gru_expense,
            "gru_income": gru_income,
            "total_income": total_income,
            "total_expense": total_expense,
            "net": net,
            "projected_balance": projected_balance,
        }
    )
