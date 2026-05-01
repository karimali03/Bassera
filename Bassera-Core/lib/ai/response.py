from pydantic import BaseModel
from lib.ai.suggestion import (
    AnalysisPeriod, InsightOfTheDay, SavingsPotential, SpendingCategory, Suggestion,
)


class SuggestionsResponse(BaseModel):
    analysis_period: AnalysisPeriod
    spending_breakdown: list[SpendingCategory]
    suggestions: list[Suggestion]
    savings_potential: SavingsPotential
    insight_of_the_day: InsightOfTheDay
