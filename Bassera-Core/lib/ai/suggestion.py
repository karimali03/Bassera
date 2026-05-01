from enum import StrEnum
from pydantic import BaseModel, Field


class Priority(StrEnum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class SuggestionType(StrEnum):
    REDUCE = "REDUCE"
    REPLACE = "REPLACE"
    CONSOLIDATE = "CONSOLIDATE"
    SCHEDULE = "SCHEDULE"
    SAVE = "SAVE"


class IconHint(StrEnum):
    LIGHTBULB = "lightbulb"
    TREND_UP = "trend_up"
    TREND_DOWN = "trend_down"
    CALENDAR = "calendar"
    STAR = "star"
    LEAF = "leaf"


class Suggestion(BaseModel):
    id: str
    priority: Priority
    type: SuggestionType
    title: str = Field(..., max_length=80)
    body: str
    estimated_monthly_saving_egp: float = Field(..., ge=0)
    affected_categories: list[str]
    action_label: str = Field(..., max_length=40)


class AnalysisPeriod(BaseModel):
    from_date: str = Field(..., alias="from")
    to_date: str = Field(..., alias="to")
    total_debits: float
    total_credits: float
    net_cashflow: float
    currency: str = "EGP"

    model_config = {"populate_by_name": True}


class SpendingCategory(BaseModel):
    category: str
    total: float
    percentage_of_debits: float
    transaction_count: int


class SavingsPotential(BaseModel):
    conservative_egp: float
    moderate_egp: float
    summary: str


class InsightOfTheDay(BaseModel):
    text: str
    icon_hint: IconHint
