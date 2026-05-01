"use client";

import React from "react";
import { useApp } from "@/components/providers/AppProvider";
import { EmptyState } from "@/components/ui/EmptyState";
import { BalanceChart } from "@/components/forecast/BalanceChart";
import { ForecastSummary } from "@/components/forecast/ForecastSummary";
import { RulesDisplay } from "@/components/forecast/RulesDisplay";
import { WarningsList } from "@/components/forecast/WarningsList";

export default function ForecastPage() {
  const { user } = useApp();

  if (!user?.ai_forecast_data) {
    return (
      <div className="max-w-6xl mx-auto">
        <h1 className="text-heading font-bold mb-8">30-Day Forecast</h1>
        <EmptyState
          icon="📊"
          title="Forecast Not Generated"
          description="AI forecast data will appear here once the forecasting model processes your transactions."
        />
      </div>
    );
  }

  const forecast = user.ai_forecast_data;

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-heading font-bold mb-8">30-Day Forecast</h1>
      <ForecastSummary forecast={forecast} />
      <BalanceChart forecast={forecast} />
      <WarningsList warnings={forecast.warnings} />
      <RulesDisplay
        fixedIncomes={forecast.rules.fixed_incomes}
        fixedExpenses={forecast.rules.fixed_expenses}
      />
    </div>
  );
}
