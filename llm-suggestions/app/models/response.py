from pydantic import BaseModel
from app.models.suggestion import (
    AnalysisPeriod,
    InsightOfTheDay,
    SavingsPotential,
    SpendingCategory,
    Suggestion,
)


class SuggestionsResponse(BaseModel):
    """Full response payload returned by POST /v1/suggestions."""

    analysis_period: AnalysisPeriod
    spending_breakdown: list[SpendingCategory]
    suggestions: list[Suggestion]
    savings_potential: SavingsPotential
    insight_of_the_day: InsightOfTheDay


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
    environment: str
