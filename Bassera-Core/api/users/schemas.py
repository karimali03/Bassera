from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime

class AIStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    WORKING = "WORKING"
    FINISHED = "FINISHED"
    FAILED = "FAILED"

class ForecastMetadata(BaseModel):
    forecast_horizon_days: int
    last_transaction_date: str
    forecast_start_date: str
    forecast_end_date: str
    model_mae_egp: Optional[float] = None

class ForecastSummary(BaseModel):
    starting_balance: float
    projected_ending_balance: float
    net_cash_flow: float
    total_income: float
    total_expense: float

class ForecastRule(BaseModel):
    name: str
    day: int
    value: float
    confidence: str

class ForecastRules(BaseModel):
    fixed_incomes: List[ForecastRule]
    fixed_expenses: List[ForecastRule]

class DailyForecastItem(BaseModel):
    date: str
    dynamic_income: float
    fixed_income: float
    total_income: float
    dynamic_expense: float
    fixed_expense: float
    total_expense: float
    net_cash_flow: float
    projected_balance: float

class AIForecastPayload(BaseModel):
    metadata: ForecastMetadata
    summary: ForecastSummary
    warnings: List[str]
    rules: ForecastRules
    daily_forecast: List[DailyForecastItem]

class UserCreate(BaseModel):
    fname: str
    lname: str
    bank_id: str

class UserUpdate(BaseModel):
    fname: Optional[str] = None
    lname: Optional[str] = None
    bank_id: Optional[str] = None

class AIStatusUpdate(BaseModel):
    ai_status: AIStatus

class UserResponse(BaseModel):
    id: str
    fname: str
    lname: str
    bank_id: str
    ai_status: Optional[AIStatus] = None
    ai_last_run: Optional[datetime] = None
    ai_forecast_data: Optional[AIForecastPayload] = None

    class Config:
        from_attributes = True
