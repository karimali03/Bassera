# Baseera: Advanced Personal Finance Forecaster

**Baseera** is a hybrid Machine Learning pipeline designed to forecast a user's 30-day financial balance trajectory with high accuracy. 

Unlike traditional time-series forecasting models (like ARIMA or pure LSTMs) that struggle with the chaotic, dual-nature of personal finance, Baseera splits the problem into two distinct domains:
1. **Deterministic Rule Detection:** Identifies fixed, recurring financial patterns (e.g., salaries, monthly subscriptions, bank installments) using statistical heuristics.
2. **Stochastic Deep Learning (GRU):** Models the highly variable, random daily cash flows (both expenses and irregular income like freelancing) using a dual-head GRU neural network with attention mechanisms.

By isolating the predictable income/expenses from the chaotic daily spend, Baseera achieves superior forecasting stability without the problem of "exploding gradients" or catastrophic drifting often seen in auto-regressive models.

---

## 🚀 Getting Started

### Prerequisites

Ensure you have Python 3.10+ installed. It is highly recommended to use a virtual environment.

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
```

---

## 📊 1. The Synthetic Data Generator (`genrate.py`)

If you do not have your own financial ledger, you can generate a highly realistic, synthetic dataset modeled after a typical Cairo (Egypt) professional.

```bash
python genrate.py
```

### Why is this generator special?
This is not a random number generator. It is a sophisticated simulator that respects real-world macroeconomic and behavioral constraints:
- **Historical Inflation Modeling:** Base prices are set to 2020. The script applies true Egyptian historical inflation rates (e.g., 35.7% in 2023, 33.3% in 2024) to ensure the generated prices realistically scale over the 5-year ledger.
- **Behavioral Jitter:** Models routines such as morning/evening commutes and workday lunches, applying "stable jitter" (±8% variation) to mimic natural variations in Uber fares or coffee prices.
- **Weekend/Holiday Logistics:** Detects Egyptian weekends (Fridays/Saturdays) and dynamically shifts spending probabilities from commutes to entertainment, dining, and shopping.
- **Hardcoded Billing Cycles:** Accurately models real-world subscriptions (Netflix, Vodafone, WE Internet, Electricity) with their respective monthly, bi-monthly, or quarterly billing frequencies.

Running the script produces `generated_ledger.json`, serving as the primary input for Baseera.

---

## 🧠 2. The Hybrid ML Pipeline

### Training the Model

To train the GRU network and extract the deterministic rules, run:

```bash
python -m src.main --mode train --user_file generated_ledger.json
```

**What happens during training?**
1. **Data Cutoff:** The pipeline isolates the last 18 months of data. *Why?* Because personal spending habits and inflation rapidly drift. Training on 5-year-old prices for a neural network predicting next month's coffee will severely under-predict the cost.
2. **Rule Extraction:** The `Rule Detector` sweeps the ledger for any transactions showing low standard deviation in date (±2.5 days) and low variance in amount (CV ≤ 0.25). These are siphoned off and saved as deterministic rules — covering salaries, subscriptions, installments, and any other fixed recurring transaction.
3. **Feature Engineering:** The remaining "chaotic" transactions are enriched with calendar features (day of week, month end proximity), Hijri calendar features (Ramadan, Eid), and rolling 7/14/30-day averages.
4. **Dual-Head GRU Training:** A 2-layer GRU with attention learns to predict both daily expenses and irregular income (e.g., freelance work) from the last 35 days of context. Training produces separate performance metrics for each head.

### Generating a Forecast (CLI)

To generate your 30-day balance forecast via the command line:

```bash
python -m src.main --mode infer --user_file generated_ledger.json
```

**The Inference Process:**
The inference engine aggregates the deterministic rules (adding your salary, subtracting your subscriptions on exact days) and superimposes the GRU's stochastic daily predictions on top. The result is a highly accurate, day-by-day trajectory of your projected bank balance.

### Programmatic Usage (`generate_forecast`)

Baseera is designed to be imported directly by a backend service — no API server required:

```python
from src.pipeline import generate_forecast

# Pass a list of transaction dicts + forecast horizon
result = generate_forecast(transactions=list_of_dicts, horizon_days=30)
```

The function accepts either a file `Path` or a `List[dict]` of raw transactions and returns a structured dictionary:

```json
{
  "metadata": {
    "forecast_horizon_days": 30,
    "last_transaction_date": "2026-04-29",
    "forecast_start_date": "2026-04-30",
    "forecast_end_date": "2026-05-29",
    "model_mae_egp": null
  },
  "summary": {
    "starting_balance": 2775173.87,
    "projected_ending_balance": 2788639.96,
    "net_cash_flow": 13466.09,
    "total_income": 100574.30,
    "total_expense": 87108.21
  },
  "warnings": [],
  "rules": {
    "fixed_incomes": [
      {"name": "Primary Employer", "day": 25, "value": 50284.88, "confidence": "HIGH"}
    ],
    "fixed_expenses": [
      {"name": "Netflix Egypt", "day": 3, "value": 301.71, "confidence": "MEDIUM"}
    ]
  },
  "daily_forecast": [
    {
      "date": "2026-04-30",
      "dynamic_income": 0.18,
      "fixed_income": 0.0,
      "total_income": 0.18,
      "dynamic_expense": 1473.40,
      "fixed_expense": 0.0,
      "total_expense": 1473.40,
      "net_cash_flow": -1473.22,
      "projected_balance": 2773700.65
    }
  ]
}
```

---

## 📁 Outputs & Artifacts

After running an inference pipeline, check the following directories:

- **Forecast Data (`outputs/forecast.csv`):** A day-by-day breakdown of projected rule-based income, rule-based expenses, GRU-predicted random expenses, and net balance.
- **Visualizations (`outputs/plots/`):**
  - `balance_forecast.png`: A 30-day line chart of your projected bank balance, with scatter points indicating salary days and fixed expense days.
  - `daily_cashflow.png`: A bar chart separating deterministic expenses vs. GRU expenses.
  - `actual_vs_predicted_expense.png`: Actual vs predicted daily expense on the test set.
  - `actual_vs_predicted_income.png`: Actual vs predicted daily income on the test set.
  - `training_curves.png`: Train and validation loss over epochs.
  - `detected_patterns_summary.png`: A table of all detected recurring rules.
- **Model Artifacts (`artifacts/`):** Contains the saved PyTorch model weights (`best_model.pt`), the extracted deterministic patterns (`detected_patterns.json`), and normalization scales.

---

For a deeper, theoretical dive into *why* this architecture was chosen, please read [ARCHITECTURE.md](ARCHITECTURE.md).
