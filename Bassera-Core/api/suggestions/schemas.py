from pydantic import BaseModel
from datetime import datetime
from lib.ai.suggestion import AnalysisPeriod, SpendingCategory, Suggestion, SavingsPotential, InsightOfTheDay


class SuggestionsRecord(BaseModel):
    id: str
    user_id: str
    created_at: datetime
    analysis_period: AnalysisPeriod
    spending_breakdown: list[SpendingCategory]
    suggestions: list[Suggestion]
    savings_potential: SavingsPotential
    insight_of_the_day: InsightOfTheDay
