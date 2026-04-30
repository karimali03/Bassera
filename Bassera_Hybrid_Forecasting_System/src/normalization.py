from dataclasses import dataclass
from typing import Dict

import pandas as pd


@dataclass
class Normalizer:
    tx_mean: float = 0.0
    tx_std: float = 1.0

    def fit(self, df_train: pd.DataFrame) -> None:
        tx_values = df_train["log_amount"]
        self.tx_mean = float(tx_values.mean())
        self.tx_std = float(tx_values.std(ddof=0) or 1.0)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["log_amount_normalized"] = (df["log_amount"] - self.tx_mean) / self.tx_std
        return df

    def to_dict(self) -> Dict[str, float]:
        return {
            "tx_mean": self.tx_mean,
            "tx_std": self.tx_std,
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, float]) -> "Normalizer":
        return cls(
            tx_mean=payload.get("tx_mean", 0.0),
            tx_std=payload.get("tx_std", 1.0),
        )
