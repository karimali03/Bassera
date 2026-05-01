export type AIStatus = "NOT_STARTED" | "WORKING" | "FINISHED" | "FAILED";

export interface TransactionResponse {
  transaction_id: string;
  timestamp: string;
  type: "CREDIT" | "DEBIT";
  amount: number;
  merchant: string;
  category: string;
  note: string;
}

export interface BankResponse {
  _id: string;
  bank_id: string;
  balance: number;
  transactions: TransactionResponse[];
}

export interface UserResponse {
  id: string;
  fname: string;
  lname: string;
  bank_id: string;
  ai_status: AIStatus;
  ai_last_run: string | null;
  ai_forecast_data: AIForecastPayload | null;
}

export interface ForecastRule {
  name: string;
  day: number;
  value: number;
  confidence: string;
}

export interface DailyForecast {
  date: string;
  dynamic_income: number;
  fixed_income: number;
  total_income: number;
  dynamic_expense: number;
  fixed_expense: number;
  total_expense: number;
  net_cash_flow: number;
  projected_balance: number;
}

export interface AIForecastPayload {
  metadata: {
    forecast_horizon_days: number;
    last_transaction_date: string;
    forecast_start_date: string;
    forecast_end_date: string;
    model_mae_egp: number | null;
  };
  summary: {
    starting_balance: number;
    projected_ending_balance: number;
    net_cash_flow: number;
    total_income: number;
    total_expense: number;
  };
  warnings: string[];
  rules: {
    fixed_incomes: ForecastRule[];
    fixed_expenses: ForecastRule[];
  };
  daily_forecast: DailyForecast[];
}

export interface SpendingCategory {
  category: string;
  total: number;
  percentage_of_debits: number;
  transaction_count: number;
}

export interface AnalysisPeriod {
  from: string;
  to: string;
  total_debits: number;
  total_credits: number;
  net_cashflow: number;
  currency: string;
}

export interface SavingsPotential {
  conservative_egp: number;
  moderate_egp: number;
  summary: string;
}

export interface SuggestionData {
  id: string;
  priority: "HIGH" | "MEDIUM" | "LOW";
  type: "REDUCE" | "REPLACE" | "CONSOLIDATE" | "SCHEDULE" | "SAVE";
  title: string;
  body: string;
  estimated_monthly_saving_egp: number;
  affected_categories: string[];
  action_label: string;
  icon_hint?: "lightbulb" | "trend_up" | "trend_down" | "calendar" | "star" | "leaf";
}

export interface InsightOfTheDay {
  text: string;
  icon_hint: "lightbulb" | "trend_up" | "trend_down" | "calendar" | "star" | "leaf";
}

export interface SuggestionsResponse {
  id: string;
  user_id: string;
  created_at: string;
  analysis_period: AnalysisPeriod;
  spending_breakdown: SpendingCategory[];
  suggestions: SuggestionData[];
  savings_potential: SavingsPotential;
  insight_of_the_day: InsightOfTheDay;
}
