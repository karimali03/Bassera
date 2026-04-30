from pathlib import Path
from typing import List, Sequence

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .utils import ensure_dir


def plot_balance_forecast(
    trajectory_df: pd.DataFrame, patterns: List[dict], output_dir: Path
) -> None:
    ensure_dir(output_dir)

    dates = trajectory_df["date"]
    balance = trajectory_df["projected_balance"]

    salary_days = {
        int(p["day_of_month"])
        for p in patterns
        if p.get("confidence") in {"high", "medium"}
        and p.get("active")
        and p.get("type") == "income"
        and "salary" in str(p.get("category", "")).lower()
    }
    installment_days = {
        int(p["day_of_month"])
        for p in patterns
        if p.get("confidence") in {"high", "medium"}
        and p.get("active")
        and p.get("type") == "expense"
        and "installment" in str(p.get("category", "")).lower()
    }

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(dates, balance, color="#2c7fb8", linewidth=2, label="Projected balance")

    if salary_days:
        salary_idx = [i for i, d in enumerate(dates) if d.day in salary_days]
        ax.scatter(
            dates.iloc[salary_idx],
            balance.iloc[salary_idx],
            color="#27ae60",
            s=40,
            label="Salary day",
            zorder=3,
        )

    if installment_days:
        inst_idx = [i for i, d in enumerate(dates) if d.day in installment_days]
        ax.scatter(
            dates.iloc[inst_idx],
            balance.iloc[inst_idx],
            color="#e74c3c",
            s=40,
            label="Installment day",
            zorder=3,
        )

    ax.set_title("30-Day Balance Forecast")
    ax.set_xlabel("Date")
    ax.set_ylabel("Balance (EGP)")
    ax.grid(alpha=0.3)
    ax.legend()
    plt.tight_layout()

    out_path = output_dir / "balance_forecast.png"
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_daily_cashflow(trajectory_df: pd.DataFrame, output_dir: Path) -> None:
    ensure_dir(output_dir)

    dates = trajectory_df["date"]
    x = np.arange(len(dates))

    rule_income = trajectory_df["rule_income"].to_numpy()
    rule_expense = trajectory_df["rule_expense"].to_numpy()
    gru_expense = trajectory_df["gru_expense"].to_numpy()

    fig, ax = plt.subplots(figsize=(13, 5))
    ax.bar(x, rule_income, color="#27ae60", label="Rule income")
    ax.bar(x, -rule_expense, color="#e74c3c", label="Rule expense")
    ax.bar(
        x,
        -gru_expense,
        bottom=-rule_expense,
        color="#f39c12",
        label="GRU expense",
    )

    ax.set_xticks(x)
    ax.set_xticklabels([d.strftime("%b %d") for d in dates], rotation=45, ha="right")
    ax.set_title("Daily Cashflow (Rule vs GRU)")
    ax.set_ylabel("Amount (EGP)")
    ax.grid(axis="y", alpha=0.3)
    ax.legend()
    plt.tight_layout()

    out_path = output_dir / "daily_cashflow.png"
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_training_curves(
    train_losses: Sequence[float], val_losses: Sequence[float], output_dir: Path
) -> None:
    ensure_dir(output_dir)

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(train_losses, label="Train loss", color="#2c7fb8", linewidth=2)
    ax.plot(val_losses, label="Val loss", color="#e74c3c", linewidth=2, linestyle="--")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Loss")
    ax.set_title("Training and Validation Loss")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()

    out_path = output_dir / "training_curves.png"
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_actual_vs_predicted(
    dates_test: Sequence[pd.Timestamp],
    y_true: Sequence[float],
    y_pred: Sequence[float],
    output_dir: Path,
) -> None:
    ensure_dir(output_dir)

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(dates_test, y_true, label="Actual", color="#e74c3c", linewidth=1.6)
    ax.plot(
        dates_test,
        y_pred,
        label="Predicted",
        color="#2c7fb8",
        linewidth=1.6,
        linestyle="--",
    )
    ax.fill_between(dates_test, y_true, y_pred, alpha=0.1, color="#e74c3c")
    ax.set_title("Actual vs Predicted Daily Expense (Test Set)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Expense (EGP)")
    ax.grid(alpha=0.3)
    ax.legend()
    plt.tight_layout()

    out_path = output_dir / "actual_vs_predicted.png"
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_detected_patterns_summary(patterns: List[dict], output_dir: Path) -> None:
    ensure_dir(output_dir)

    if not patterns:
        patterns = [
            {
                "category": "none",
                "type": "expense",
                "day_of_month": "-",
                "amount": 0,
                "confidence": "low",
                "active": False,
                "occurrences": 0,
            }
        ]

    table_rows = []
    for p in patterns:
        amount = float(p.get("amount", 0.0))
        sign = "+" if amount >= 0 else "-"
        table_rows.append(
            [
                str(p.get("category", "")),
                str(p.get("type", "")),
                str(p.get("day_of_month", "")),
                f"{sign}{abs(amount):,.0f}",
                str(p.get("confidence", "")).upper(),
                "yes" if p.get("active") else "no",
                str(p.get("occurrences", "")),
            ]
        )

    fig, ax = plt.subplots(figsize=(12, 0.6 + 0.35 * len(table_rows)))
    ax.axis("off")

    table = ax.table(
        cellText=table_rows,
        colLabels=[
            "Category",
            "Type",
            "Day",
            "Amount",
            "Confidence",
            "Active",
            "Occurrences",
        ],
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.2)

    plt.tight_layout()
    out_path = output_dir / "detected_patterns_summary.png"
    plt.savefig(out_path, dpi=150)
    plt.close()
