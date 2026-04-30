from typing import Iterable, Tuple, Optional

import numpy as np
import pandas as pd
from hijri_converter import convert
from sklearn.preprocessing import LabelEncoder

# Egyptian weekend days: Friday (4) and Saturday (5)
WEEKEND_DAYS = {4, 5}


def add_calendar_features(df: pd.DataFrame, start_date: pd.Timestamp) -> pd.DataFrame:
    """
    Extracts standard Gregorian calendar features from the transaction timestamp.
    
    These temporal anchors help the GRU learn cyclic spending behaviors (e.g., 
    higher spending on weekends or end-of-month salary stretches).
    
    Args:
        df (pd.DataFrame): DataFrame containing a 'timestamp' column.
        start_date (pd.Timestamp): The earliest date in the training context, 
                                   used to calculate a normalized 'months_since_start'.
                                   
    Returns:
        pd.DataFrame: DataFrame augmented with standard calendar features.
    """
    df = df.copy()
    ts = df["timestamp"]
    
    # Granular time features
    df["hour"] = ts.dt.hour.astype(int)
    df["hour_slot"] = (ts.dt.hour // 6).astype(int)
    
    # Weekly features
    df["day_of_week"] = ts.dt.dayofweek.astype(int)
    df["is_weekend"] = ts.dt.dayofweek.isin(WEEKEND_DAYS).astype(int)
    df["week_of_year"] = ts.dt.isocalendar().week.astype(int)
    
    # Monthly/Quarterly features
    df["day_of_month"] = ts.dt.day.astype(int)
    df["month"] = ts.dt.month.astype(int)
    df["quarter"] = ts.dt.quarter.astype(int)
    df["is_month_start"] = (ts.dt.day <= 5).astype(int)
    df["is_month_end"] = (ts.dt.day >= 25).astype(int)

    # Time remaining in the month often dictates financial conservatism
    month_end = ts + pd.offsets.MonthEnd(0)
    df["days_to_month_end"] = (month_end - ts).dt.days.astype(int)

    # Macro trend tracking
    start = pd.Timestamp(start_date).normalize()
    month_index = (ts.dt.year - start.year) * 12 + (ts.dt.month - start.month)
    df["months_since_start"] = month_index.astype(int)
    
    return df


def add_hijri_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts Islamic (Hijri) calendar features.
    
    In the Middle East, spending patterns shift drastically based on the 
    lunar calendar (e.g., increased food spending in Ramadan, shopping in Eid). 
    Since the Hijri calendar shifts by ~11 days annually against the Gregorian 
    calendar, these features are essential to prevent the model from falsely 
    correlating Eid spikes with fixed Gregorian months.
    
    Args:
        df (pd.DataFrame): DataFrame containing a 'timestamp' column.
        
    Returns:
        pd.DataFrame: DataFrame augmented with Hijri features.
    """
    df = df.copy()
    
    hijri = df["timestamp"].apply(
        lambda ts: convert.Gregorian(ts.year, ts.month, ts.day).to_hijri()
    )
    
    df["hijri_month"] = hijri.apply(lambda h: h.month)
    df["hijri_day"] = hijri.apply(lambda h: h.day)
    
    df["is_ramadan"] = (df["hijri_month"] == 9).astype(int)
    df["is_eid_al_fitr"] = (
        (df["hijri_month"] == 10) & (df["hijri_day"] <= 3)
    ).astype(int)
    df["is_eid_al_adha"] = (
        (df["hijri_month"] == 12) & (df["hijri_day"] <= 3)
    ).astype(int)
    
    return df


def add_rolling_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates retrospective rolling sum features.
    
    These act as 'budget exhaustion' signals for the GRU. If the 30-day rolling 
    expense is extremely high, the model learns that the user is likely to reduce 
    spending in the immediate future.
    
    Args:
        df (pd.DataFrame): The transaction DataFrame.
        
    Returns:
        pd.DataFrame: DataFrame augmented with rolling expense features.
    """
    df = df.copy()
    if "timestamp" in df.index.names:
        df = df.reset_index(drop=True)
    
    df = df.sort_values("timestamp")
    df = df.set_index("timestamp", drop=False)

    expense = df["amount"].abs()
    
    # We use closed="left" to ensure we don't leak the current day's amount 
    # into the feature used to predict it.
    for window in [7, 14, 30]:
        df[f"rolling_expense_{window}d"] = (
            expense.rolling(f"{window}D", closed="left").sum().fillna(0.0)
        )

    df["tx_count_7d"] = (
        pd.Series(1, index=df.index).rolling("7D", closed="left").sum().fillna(0.0)
    )

    df = df.reset_index(drop=True)
    return df


def encode_categories(
    df: pd.DataFrame, classes: Optional[Iterable[str]] = None
) -> Tuple[pd.DataFrame, LabelEncoder]:
    """
    Encodes categorical transaction types into integers for PyTorch embedding.
    
    Args:
        df (pd.DataFrame): The transaction DataFrame.
        classes (Optional[Iterable[str]]): Pre-fitted classes to enforce consistency 
                                           during inference.
                                           
    Returns:
        Tuple[pd.DataFrame, LabelEncoder]: The mutated DataFrame and the fitted encoder.
    """
    encoder = LabelEncoder()
    df = df.copy()

    if classes is None:
        categories = list(pd.unique(df["category"].astype(str)))
        if "unknown" not in categories:
            categories.append("unknown")
        encoder.fit(categories)
    else:
        encoder.classes_ = np.array(list(classes))

    # Protect against unseen categories during inference
    safe_category = df["category"].where(
        df["category"].isin(encoder.classes_), "unknown"
    )
    df["category_encoded"] = encoder.transform(safe_category)
    
    return df, encoder
