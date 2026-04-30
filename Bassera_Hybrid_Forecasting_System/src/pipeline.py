import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader, TensorDataset

from .config import (
    ARTIFACT_DIR,
    DATA_CUTOFF_MONTHS,
    FEATURE_COLS,
    FUTURE_FEATURE_COLS,
    MAX_SEQ_LEN,
    OUTPUT_DIR,
    PLOTS_DIR,
    PREDICT_DAYS,
    STEP_DAYS,
    WINDOW_DAYS,
)
from .data_loading import load_and_clean_transactions
from .features import add_calendar_features, add_hijri_features, add_rolling_features, encode_categories
from .inference import forecast_trajectory
from .model import FinanceForecaster
from .normalization import Normalizer
from .plots import (
    plot_balance_forecast,
    plot_actual_vs_predicted,
    plot_daily_cashflow,
    plot_detected_patterns_summary,
    plot_training_curves,
)
from .rule_detector import detect_recurring_patterns, format_patterns_summary
from .train import predict_on_loader, train_model
from .utils import ensure_dir, save_json, set_seed
from .windows import build_windows, chronological_split, make_target_dates, windows_to_arrays


def _build_dataloaders(
    x_seq: np.ndarray,
    x_future: np.ndarray,
    y: np.ndarray,
    batch_size: int,
) -> DataLoader:
    """
    Constructs PyTorch DataLoaders for the model.

    Args:
        x_seq: Historical sequence features (shape: [batch_size, seq_len, num_features]).
        x_future: Future anchor features (shape: [batch_size, future_dim]).
        y: Target daily expense values (shape: [batch_size]).
        batch_size: The batch size for the DataLoader.

    Returns:
        A DataLoader instance configured with the given tensors.
    """
    dataset = TensorDataset(
        torch.tensor(x_seq, dtype=torch.float32),
        torch.tensor(x_future, dtype=torch.float32),
        torch.tensor(y, dtype=torch.float32),
    )
    return DataLoader(dataset, batch_size=batch_size, shuffle=False)


def _apply_cutoff(df_full: pd.DataFrame) -> tuple[pd.DataFrame, pd.Timestamp]:
    """
    Filters the dataset to retain only recent transactions, helping the model 
    avoid training on outdated inflation contexts.

    Args:
        df_full: The complete, raw transaction DataFrame.

    Returns:
        A tuple containing the recent DataFrame and the cutoff timestamp.
    """
    cutoff_date = df_full["timestamp"].max() - pd.DateOffset(months=DATA_CUTOFF_MONTHS)
    df_recent = df_full[df_full["timestamp"] >= cutoff_date].copy()
    return df_recent, cutoff_date


def _filter_stochastic_transactions(df: pd.DataFrame, patterns: list[dict]) -> pd.DataFrame:
    """
    Strips out transactions that match our highly-confident, deterministic 
    rules (like salary, subscriptions). The remaining dataset represents the 
    chaotic, stochastic cashflow ideal for GRU processing.

    Args:
        df: The DataFrame of transactions.
        patterns: A list of detected rule-based patterns.

    Returns:
        A filtered DataFrame containing only non-pattern stochastic transactions.
    """
    pattern_pairs = {
        (p["category"], p["merchant"])
        for p in patterns if p.get("confidence") in {"high", "medium"}
    }
    
    # Create a mask for rows that match any (category, merchant) in the patterns set
    is_pattern = df.apply(lambda row: (row["category"], row["merchant"]) in pattern_pairs, axis=1)
    df_stochastic = df[~is_pattern].copy()
    
    if df_stochastic.empty:
        raise ValueError("No non-pattern transactions found after filtering.")
    return df_stochastic


def _prepare_features(
    df_expense: pd.DataFrame,
    history_start_date: pd.Timestamp,
    normalizer: Normalizer,
    label_classes: np.ndarray | None = None,
) -> tuple[pd.DataFrame, Normalizer, np.ndarray]:
    """
    Injects critical temporal context into the dataset:
    - Gregorian Calendar bounds (weekend, month-end).
    - Hijri Calendar bounds (Ramadan, Eid spikes).
    - Rolling window statistics.
    
    Normalizes numeric features and encodes categories.

    Args:
        df_expense: The filtered expenses DataFrame.
        history_start_date: Reference start date for calculating temporal elapsed limits.
        normalizer: An initialized or fitted normalizer to scale features.
        label_classes: Array of pre-fitted label classes for categories (if inferring).

    Returns:
        The fully processed feature DataFrame, the Normalizer, and label classes.
    """
    df_expense = add_calendar_features(df_expense, history_start_date)
    df_expense = add_hijri_features(df_expense)
    df_expense = add_rolling_features(df_expense)

    df_expense = normalizer.transform(df_expense)
    df_expense, label_encoder = encode_categories(df_expense, classes=label_classes)
    return df_expense, normalizer, label_encoder.classes_


def _print_forecast_summary(trajectory_df: pd.DataFrame, patterns: list[dict]) -> None:
    """
    Generates an easy-to-read, 30-day CLI summary of the projected balance
    by aggregating both deterministic rules and predicted GRU variances.

    Args:
        trajectory_df: A DataFrame containing day-by-day projected states.
        patterns: The detected rule patterns applied to the forecast.
    """
    gru_income_total = trajectory_df["gru_income"].sum() if "gru_income" in trajectory_df.columns else 0.0
    rule_income_total = trajectory_df["rule_income"].sum()
    total_income = trajectory_df["total_income"].sum()
    total_expense = trajectory_df["total_expense"].sum()
    starting_balance = trajectory_df["projected_balance"].iloc[0] - trajectory_df["net"].iloc[0]
    final_balance = trajectory_df["projected_balance"].iloc[-1]

    salary_patterns = [
        p
        for p in patterns
        if p.get("confidence") in {"high", "medium"}
        and p.get("active")
        and p.get("type") == "income"
        and "salary" in str(p.get("category", "")).lower()
    ]
    installment_patterns = [
        p
        for p in patterns
        if p.get("confidence") in {"high", "medium"}
        and p.get("active")
        and p.get("type") == "expense"
        and (
            "installment" in str(p.get("category", "")).lower()
            or "services" in str(p.get("category", "")).lower()
            or "health" in str(p.get("category", "")).lower()
        )
    ]

    if not salary_patterns:
        salary_lines = [" Salaries          : none detected"]
    else:
        salary_lines = [
            f" Salary            : day {p['day_of_month']} ({p['merchant']}) +{abs(float(p['amount'])):,.0f} EGP [{p['confidence'].upper()}]"
            for p in salary_patterns
        ]

    if not installment_patterns:
        installment_lines = [" Installments      : none detected"]
    else:
        installment_lines = [
            f" Installment       : day {p['day_of_month']} ({p['merchant']}) -{abs(float(p['amount'])):,.0f} EGP [{p['confidence'].upper()}]"
            for p in installment_patterns
        ]

    print("\n" + "=" * 46)
    print(" 30-DAY FORECAST SUMMARY")
    print("=" * 46)
    print(f" Starting Balance   : {starting_balance:,.0f} EGP")
    print(f" Expected Income    : {total_income:,.0f} EGP")
    print(f"   ↳ Deterministic  : {rule_income_total:,.0f} EGP (salaries)")
    print(f"   ↳ GRU Predicted  : {gru_income_total:,.0f} EGP (freelance/irregular)")
    print(f" Expected Expenses  : {total_expense:,.0f} EGP")
    print(f" Projected Balance  : {final_balance:,.0f} EGP")
    print("-" * 46)
    for line in salary_lines:
        print(line)
    print("-" * 46)
    for line in installment_lines:
        print(line)
    print("=" * 46 + "\n")


def train_pipeline(args: argparse.Namespace) -> None:
    """
    The main execution flow for training the Baseera forecaster.
    
    Process:
    1. Extracts the last N months of data to avoid extreme inflation drift.
    2. Runs the heuristic Rule Detector to siphon off predictable cash flows.
    3. Engineers features out of the remaining random expenses.
    4. Slices history into robust chronological 35-day windows.
    5. Trains the Sequence-to-Sequence GRU architecture.
    6. Saves normalizers, features, weights, and rules.

    Args:
        args: Argparse namespace containing config parameters.
    """
    ensure_dir(ARTIFACT_DIR)
    ensure_dir(OUTPUT_DIR)
    ensure_dir(PLOTS_DIR)

    user_file = Path(args.user_file).expanduser()
    df_full_capped = load_and_clean_transactions(user_file, cap_outliers=True)
    df_recent, cutoff_date = _apply_cutoff(df_full_capped)
    print(
        f"Data cutoff: using last {DATA_CUTOFF_MONTHS} months "
        f"({len(df_recent)} of {len(df_full_capped)} transactions, "
        f"from {df_recent['timestamp'].min().date()})"
    )

    df_full_uncapped = load_and_clean_transactions(user_file, cap_outliers=False)
    df_recent_uncapped = df_full_uncapped[df_full_uncapped["timestamp"] >= cutoff_date].copy()

    patterns = detect_recurring_patterns(df_recent_uncapped)
    print(format_patterns_summary(patterns))
    save_json(patterns, ARTIFACT_DIR / "detected_patterns.json")
    plot_detected_patterns_summary(patterns, PLOTS_DIR)

    df_expense = _filter_stochastic_transactions(df_recent, patterns)
    history_start_date = df_expense["timestamp"].min().normalize()

    target_dates = make_target_dates(df_expense, WINDOW_DAYS, STEP_DAYS)
    if len(target_dates) == 0:
        raise ValueError("Not enough data to build training windows")
    train_index = max(int(len(target_dates) * 0.7) - 1, 0)
    train_cutoff = target_dates[train_index]

    df_train = df_expense[df_expense["timestamp"] < train_cutoff]
    normalizer = Normalizer()
    normalizer.fit(df_train)

    df_expense, normalizer, label_classes = _prepare_features(
        df_expense, history_start_date, normalizer
    )

    windows = build_windows(
        df_expense,
        FEATURE_COLS,
        history_start_date,
        WINDOW_DAYS,
        MAX_SEQ_LEN,
        STEP_DAYS,
    )
    x_seq, x_future, y_raw, dates = windows_to_arrays(windows)

    splits = chronological_split([x_seq, x_future, y_raw, dates])
    x_seq_train, x_seq_val, x_seq_test = splits[0]
    x_future_train, x_future_val, x_future_test = splits[1]
    y_train, y_val, y_test = splits[2]
    _, _, dates_test = splits[3]

    train_loader = _build_dataloaders(
        x_seq_train, x_future_train, y_train, args.batch_size
    )
    val_loader = _build_dataloaders(
        x_seq_val, x_future_val, y_val, args.batch_size
    )
    test_loader = _build_dataloaders(
        x_seq_test, x_future_test, y_test, args.batch_size
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = FinanceForecaster(
        input_size=len(FEATURE_COLS),
        future_size=len(FUTURE_FEATURE_COLS),
        hidden_size=128,
        num_layers=2,
        dropout=0.2,
    ).to(device)

    checkpoint_path = ARTIFACT_DIR / "best_model.pt"
    model, train_losses, val_losses = train_model(
        model,
        train_loader,
        val_loader,
        device,
        epochs=args.epochs,
        lr=args.lr,
        checkpoint_path=checkpoint_path,
    )

    plot_training_curves(train_losses, val_losses, PLOTS_DIR)

    preds, targets = predict_on_loader(model, test_loader, device)
    # Inverse the log1p transform to get back to raw EGP for interpretable metrics
    preds_exp   = np.expm1(preds[:, 0])
    targets_exp = np.expm1(targets[:, 0])
    preds_inc   = np.expm1(preds[:, 1])
    targets_inc = np.expm1(targets[:, 1])

    def _calc_metrics(t: np.ndarray, p: np.ndarray):
        mae = float(np.mean(np.abs(t - p)))
        rmse = float(np.sqrt(np.mean((t - p) ** 2)))
        mask = t != 0
        mape = float(np.mean(np.abs((t[mask] - p[mask]) / t[mask])) * 100) if mask.sum() > 0 else float("nan")
        denom = np.abs(t) + np.abs(p)
        smask = denom > 0
        smape = float(np.mean(2 * np.abs(t[smask] - p[smask]) / denom[smask]) * 100) if smask.sum() > 0 else float("nan")
        ss_res = np.sum((t - p) ** 2)
        ss_tot = np.sum((t - np.mean(t)) ** 2)
        r2 = float(1.0 - ss_res / ss_tot) if ss_tot > 0 else float("nan")
        return mae, rmse, mape, smape, r2

    mae_e, rmse_e, mape_e, smape_e, r2_e = _calc_metrics(targets_exp, preds_exp)
    mae_i, rmse_i, mape_i, smape_i, r2_i = _calc_metrics(targets_inc, preds_inc)

    print("\n======== Test Set (GRU Expense) ========")
    print(
        f"MAE: {mae_e:.2f} EGP | RMSE: {rmse_e:.2f} "
        f"| MAPE: {mape_e:.1f}% | sMAPE: {smape_e:.1f}% | R2: {r2_e:.4f}"
    )
    print("\n======== Test Set (GRU Income) ========")
    print(
        f"MAE: {mae_i:.2f} EGP | RMSE: {rmse_i:.2f} "
        f"| MAPE: {mape_i:.1f}% | sMAPE: {smape_i:.1f}% | R2: {r2_i:.4f}"
    )

    # Plot just the expense curve for backwards compatibility with the plotting function
    plot_actual_vs_predicted(dates_test, targets_exp, preds_exp, PLOTS_DIR)

    save_json(FEATURE_COLS, ARTIFACT_DIR / "feature_cols.json")
    save_json(FUTURE_FEATURE_COLS, ARTIFACT_DIR / "future_feature_cols.json")
    save_json(
        {
            **normalizer.to_dict(),
            "history_start_date": history_start_date.date().isoformat(),
        },
        ARTIFACT_DIR / "user_stats.json",
    )

    np.save(ARTIFACT_DIR / "category_label_encoder.npy", label_classes)
    torch.save(model.state_dict(), checkpoint_path)

    print("\nTraining completed. Artifacts saved.")


def infer_pipeline(args: argparse.Namespace) -> None:
    """
    Executes the trained model to generate the next 30 days of cash flow predictions.
    
    Aggregates deterministic rules directly onto the timeline and overlays the GRU's
    stochastic daily expense predictions to derive the absolute Net Balance.

    Args:
        args: Argparse namespace containing config parameters.
    """
    ensure_dir(ARTIFACT_DIR)
    ensure_dir(OUTPUT_DIR)
    ensure_dir(PLOTS_DIR)

    user_file = Path(args.user_file).expanduser()
    df_full_capped = load_and_clean_transactions(user_file, cap_outliers=True)
    df_recent, cutoff_date = _apply_cutoff(df_full_capped)
    print(
        f"Data cutoff: using last {DATA_CUTOFF_MONTHS} months "
        f"({len(df_recent)} of {len(df_full_capped)} transactions, "
        f"from {df_recent['timestamp'].min().date()})"
    )

    df_full_uncapped = load_and_clean_transactions(user_file, cap_outliers=False)
    df_recent_uncapped = df_full_uncapped[df_full_uncapped["timestamp"] >= cutoff_date].copy()

    patterns = detect_recurring_patterns(df_recent_uncapped)
    print(format_patterns_summary(patterns))
    save_json(patterns, ARTIFACT_DIR / "detected_patterns.json")
    plot_detected_patterns_summary(patterns, PLOTS_DIR)

    df_expense = _filter_stochastic_transactions(df_recent, patterns)

    user_stats_path = ARTIFACT_DIR / "user_stats.json"
    if not user_stats_path.exists():
        raise FileNotFoundError("Missing artifacts/user_stats.json. Run train mode first.")

    with open(user_stats_path, "r", encoding="utf-8") as fh:
        user_stats = json.load(fh)

    history_start_date = pd.Timestamp(user_stats.get("history_start_date"))

    normalizer = Normalizer.from_dict(user_stats)
    label_classes = np.load(ARTIFACT_DIR / "category_label_encoder.npy", allow_pickle=True)

    df_expense, _, _ = _prepare_features(
        df_expense, history_start_date, normalizer, label_classes
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = FinanceForecaster(
        input_size=len(FEATURE_COLS),
        future_size=len(FUTURE_FEATURE_COLS),
        hidden_size=128,
        num_layers=2,
        dropout=0.2,
    ).to(device)

    checkpoint_path = ARTIFACT_DIR / "best_model.pt"
    if not checkpoint_path.exists():
        raise FileNotFoundError("Missing artifacts/best_model.pt. Run train mode first.")

    model.load_state_dict(torch.load(checkpoint_path, map_location=device))

    starting_balance = float(df_full_uncapped["amount"].sum())
    trajectory = forecast_trajectory(
        model,
        df_expense,
        patterns,
        history_start_date,
        starting_balance,
        PREDICT_DAYS,
        FEATURE_COLS,
        WINDOW_DAYS,
        MAX_SEQ_LEN,
        device,
    )

    forecast_path = OUTPUT_DIR / "forecast.csv"
    trajectory.to_csv(forecast_path, index=False)

    plot_balance_forecast(trajectory, patterns, PLOTS_DIR)
    plot_daily_cashflow(trajectory, PLOTS_DIR)

    _print_forecast_summary(trajectory, patterns)
    print("Done. Forecast and plots saved.")
