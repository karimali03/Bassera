from typing import Dict, List, Sequence, Tuple

import numpy as np
import pandas as pd

from .inference import extract_future_features


def make_target_dates(
    df: pd.DataFrame, window_days: int, step_days: int
) -> pd.DatetimeIndex:
    min_ts = df["timestamp"].min().normalize()
    max_ts = df["timestamp"].max().normalize()
    start = min_ts + pd.Timedelta(days=window_days)
    return pd.date_range(start=start, end=max_ts, freq=f"{step_days}D")


def build_daily_targets(df: pd.DataFrame) -> Dict[pd.Timestamp, Tuple[float, float]]:
    """
    Compute per-day expense and income totals, then apply log1p to compress
    the target range and stabilize training.
    """
    df = df.copy()
    df["date"] = df["timestamp"].dt.normalize()
    df["expense_amount"] = np.where(df["amount"] < 0, df["amount"].abs(), 0.0)
    df["income_amount"]  = np.where(df["amount"] > 0, df["amount"],        0.0)

    grouped = df.groupby(["date"], sort=True)[["expense_amount", "income_amount"]].sum().reset_index()
    target_map: Dict[pd.Timestamp, Tuple[float, float]] = {}
    for _, row in grouped.iterrows():
        # log1p compresses e.g. 5000 EGP → ~8.5  and 0 EGP → 0
        # This dramatically reduces the loss scale and gradient variance.
        target_map[row["date"]] = (
            float(np.log1p(row["expense_amount"])),
            float(np.log1p(row["income_amount"])),
        )
    return target_map


def build_windows(
    df: pd.DataFrame,
    feature_cols: Sequence[str],
    history_start_date: pd.Timestamp,
    window_days: int,
    max_seq_len: int,
    step_days: int,
) -> List[Tuple[np.ndarray, np.ndarray, float, pd.Timestamp]]:
    df = df.sort_values("timestamp").copy()
    target_dates = make_target_dates(df, window_days, step_days)
    target_map = build_daily_targets(df)

    windows: List[Tuple[np.ndarray, np.ndarray, np.ndarray, pd.Timestamp]] = []
    for target_date in target_dates:
        window_start = target_date - pd.Timedelta(days=window_days)
        hist = df[(df["timestamp"] >= window_start) & (df["timestamp"] < target_date)]
        seq = np.nan_to_num(hist[feature_cols].to_numpy(dtype=np.float32), nan=0.0)

        if len(seq) > max_seq_len:
            seq = seq[-max_seq_len:]
        elif len(seq) < max_seq_len:
            pad = np.zeros((max_seq_len - len(seq), seq.shape[1]), dtype=np.float32)
            seq = np.vstack([pad, seq])

        future_feats = extract_future_features(target_date, history_start_date)
        expense, income = target_map.get(target_date, (0.0, 0.0))
        windows.append((seq, future_feats, np.array([expense, income], dtype=np.float32), target_date))

    return windows


def windows_to_arrays(
    windows: Sequence[Tuple[np.ndarray, np.ndarray, np.ndarray, pd.Timestamp]]
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    x_seq = np.stack([w[0] for w in windows])
    x_future = np.stack([w[1] for w in windows])
    y = np.array([w[2] for w in windows], dtype=np.float32)
    dates = np.array([w[3] for w in windows])
    return x_seq, x_future, y, dates


def chronological_split(
    arrays: Sequence[Sequence],
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
) -> List[Tuple[Sequence, Sequence, Sequence]]:
    n = len(arrays[0])
    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))
    splits: List[Tuple[Sequence, Sequence, Sequence]] = []

    for arr in arrays:
        splits.append((arr[:train_end], arr[train_end:val_end], arr[val_end:]))

    return splits
