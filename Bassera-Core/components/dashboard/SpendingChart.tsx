"use client";

import React from "react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import { useApp } from "@/components/providers/AppProvider";
import { Card } from "@/components/ui/Card";
import { getCategoryColor } from "@/lib/constants";

export function SpendingChart() {
  const { bank } = useApp();

  if (!bank) return null;

  // Calculate spending by category for current month
  const now = new Date();
  const currentMonth = now.getMonth();
  const currentYear = now.getFullYear();

  const monthTransactions = bank.transactions.filter((tx) => {
    const txDate = new Date(tx.timestamp.replace(" ", "T"));
    return (
      tx.type === "DEBIT" &&
      txDate.getMonth() === currentMonth &&
      txDate.getFullYear() === currentYear
    );
  });

  const categoryTotals: Record<string, number> = {};
  monthTransactions.forEach((tx) => {
    categoryTotals[tx.category] = (categoryTotals[tx.category] || 0) + tx.amount;
  });

  const chartData = Object.entries(categoryTotals).map(([name, value]) => ({
    name,
    value: Math.round(value * 100) / 100,
  }));

  if (chartData.length === 0) {
    return (
      <Card className="p-6 mb-8">
        <h3 className="text-lg font-bold mb-6">Spending by Category</h3>
        <p className="text-rev-muted">No expenses this month</p>
      </Card>
    );
  }

  return (
    <Card className="p-6 mb-8">
      <h3 className="text-lg font-bold mb-6">Spending by Category</h3>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, value }: any) => `${name}: EGP${value}`}
            outerRadius={100}
            fill="#494fdf"
            dataKey="value"
          >
            {chartData.map((entry) => (
              <Cell key={`cell-${entry.name}`} fill={getCategoryColor(entry.name)} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value: any) => `EGP${value}`}
            contentStyle={{
              backgroundColor: "#1e2225",
              border: "1px solid #505a63",
              borderRadius: "8px",
            }}
          />
        </PieChart>
      </ResponsiveContainer>
    </Card>
  );
}
