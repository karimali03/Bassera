import json
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd

REQUIRED_COLS = {
    "transaction_id",
    "timestamp",
    "amount",
    "category",
    "transaction_type",
}


def _read_json_records(path: Path) -> List[dict]:
    """
    Reads transaction records from a JSON file.
    
    Supports both standard JSON arrays and JSON Lines format. If the JSON
    is nested within a 'transactions' key, it will extract the list.
    
    Args:
        path (Path): Path to the JSON ledger file.
        
    Returns:
        List[dict]: A list of raw transaction dictionaries.
    """
    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            df = pd.read_json(path, lines=True)
            return df.to_dict(orient="records")

    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        if "transactions" in data and isinstance(data["transactions"], list):
            return data["transactions"]
        return [data]
    return []


def load_and_clean_transactions(
    user_file: "Path | List[dict]", cap_outliers: bool = True
) -> pd.DataFrame:
    """
    Loads raw transaction JSON data into a cleaned, normalized pandas DataFrame.
    
    This function handles column renaming, dropping duplicates, coercing timestamps,
    normalizing category strings, and ensuring that 'debit' and 'credit' amounts 
    carry the correct mathematical signs.
    
    Args:
        user_file: Path to the input JSON ledger, OR a pre-loaded list of
                   transaction dictionaries (used by the API to skip disk I/O).
        cap_outliers (bool): Whether to cap extreme values (99th percentile) to 
                             prevent gradient explosion during GRU training.
                             
    Returns:
        pd.DataFrame: A cleaned DataFrame indexed by timestamp.
    """
    if isinstance(user_file, list):
        records = user_file
    else:
        user_file = Path(user_file)
        if not user_file.exists():
            raise FileNotFoundError(f"User file not found: {user_file}")
        records = _read_json_records(user_file)

    df = pd.DataFrame.from_records(records)

    rename_map = {}
    if "transaction_type" not in df.columns and "type" in df.columns:
        rename_map["type"] = "transaction_type"
    if "description" not in df.columns and "note" in df.columns:
        rename_map["note"] = "description"
    if rename_map:
        df = df.rename(columns=rename_map)

    missing = REQUIRED_COLS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df = df.drop_duplicates(subset=["transaction_id"]).copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])
    if df["timestamp"].dt.tz is not None:
        df["timestamp"] = df["timestamp"].dt.tz_convert(None)

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
    
    # Normalize categories: lowercase and replace spaces/slashes with underscores
    df["category"] = (
        df["category"]
        .fillna("unknown")
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace("/", "_", regex=False)
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
    )

    df["transaction_type"] = (
        df["transaction_type"].fillna("").astype(str).str.strip().str.lower()
    )
    
    # Infer missing transaction types based on the sign of the amount
    missing_type = df["transaction_type"].isin(["", "unknown", "nan"])
    df.loc[missing_type & (df["amount"] < 0), "transaction_type"] = "debit"
    df.loc[missing_type & (df["amount"] >= 0), "transaction_type"] = "credit"

    # Enforce correct mathematical signs
    debit_mask = df["transaction_type"] == "debit"
    credit_mask = df["transaction_type"] == "credit"
    df.loc[debit_mask, "amount"] = -df.loc[debit_mask, "amount"].abs()
    df.loc[credit_mask, "amount"] = df.loc[credit_mask, "amount"].abs()

    df = df.sort_values("timestamp").reset_index(drop=True)
    df = df.set_index("timestamp", drop=False)

    if cap_outliers:
        df = _cap_outliers(df)
        
    # Log scale the amount to handle wide variance in spending (e.g. 5 EGP vs 5000 EGP)
    df["log_amount"] = np.sign(df["amount"]) * np.log1p(np.abs(df["amount"]))
    return df


def _cap_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Caps extreme transaction amounts at the 99th percentile per category.
    
    Neural networks are highly sensitive to massive outlier variances.
    By capping the 99th percentile, we preserve the overall distribution 
    without allowing a single random 50,000 EGP purchase to ruin the weights.
    
    Args:
        df (pd.DataFrame): The dataframe to cap.
        
    Returns:
        pd.DataFrame: A dataframe with an added 'is_capped' flag and adjusted amounts.
    """
    q99 = (
        df.groupby("category")["amount"]
        .apply(lambda s: s.abs().quantile(0.99))
        .to_dict()
    )
    cap_values = df["category"].map(q99).fillna(0.0)
    abs_amount = df["amount"].abs()
    
    # Mark which transactions were capped
    df["is_capped"] = (abs_amount > cap_values).astype(int)
    
    # Preserve the original sign while capping the absolute value
    df["amount"] = np.sign(df["amount"]) * np.minimum(abs_amount, cap_values)
    return df
