"use client";

import React from "react";
import { Card } from "@/components/ui/Card";
import { formatEGP } from "@/lib/constants";
import { AIForecastPayload } from "@/lib/types";

interface ForecastSummaryProps {
  forecast: AIForecastPayload;
}

export function ForecastSummary({ forecast }: ForecastSummaryProps) {
  const { summary } = forecast;
  const stats = [
    {
      label: "Starting Balance",
      value: formatEGP(summary.starting_balance),
      color: "text-rev-blue",
    },
    {
      label: "Projected Ending",
      value: formatEGP(summary.projected_ending_balance),
      color:
        summary.projected_ending_balance >= summary.starting_balance
          ? "text-rev-teal"
          : "text-rev-danger",
    },
    {
      label: "Total Income",
      value: formatEGP(summary.total_income),
      color: "text-rev-teal",
    },
    {
      label: "Total Expense",
      value: formatEGP(summary.total_expense),
      color: "text-rev-danger",
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {stats.map((stat) => (
        <Card key={stat.label} className="p-6 text-center">
          <p className="text-rev-muted text-sm mb-2">{stat.label}</p>
          <p className={`text-2xl font-bold ${stat.color}`}>{stat.value}</p>
        </Card>
      ))}
    </div>
  );
}
