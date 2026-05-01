"use client";

import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { Card } from "@/components/ui/Card";
import { SpendingCategory } from "@/lib/types";
import { getCategoryColor } from "@/lib/constants";

interface SpendingBreakdownProps {
  categories?: SpendingCategory[];
}

export function SpendingBreakdown({ categories }: SpendingBreakdownProps) {
  if (!categories || categories.length === 0) {
    return (
      <Card className="p-6 mb-6">
        <h3 className="text-lg font-bold mb-4">Spending Breakdown</h3>
        <p className="text-rev-muted">No spending data available</p>
      </Card>
    );
  }

  const chartData = categories.map((cat) => ({
    name: cat.category.replace(/_/g, " "),
    category: cat.category,
    percentage: Math.round(cat.percentage_of_debits * 100),
  }));

  return (
    <Card className="p-6 mb-6">
      <h3 className="text-lg font-bold mb-4">Spending Breakdown</h3>
      <ResponsiveContainer width="100%" height={300}>
        {/* @ts-ignore - Recharts has known type issues with React 18+ */}
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#505a63" />
          <XAxis type="number" stroke="#8d969e" />
          <YAxis dataKey="name" type="category" stroke="#8d969e" width={100} />
          <Tooltip
            contentStyle={{
              backgroundColor: "#1e2225",
              border: "1px solid #505a63",
              borderRadius: "8px",
            }}
            formatter={(value: any) => `${value}%`}
          />
          <Bar dataKey="percentage" radius={[0, 8, 8, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getCategoryColor(entry.category)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
}
