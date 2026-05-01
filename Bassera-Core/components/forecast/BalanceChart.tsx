"use client";

import React from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { Card } from "@/components/ui/Card";
import { AIForecastPayload } from "@/lib/types";
import { formatEGP } from "@/lib/constants";

interface BalanceChartProps {
  forecast: AIForecastPayload;
}

export function BalanceChart({ forecast }: BalanceChartProps) {
  const chartData = forecast.daily_forecast.map((day) => ({
    date: day.date.slice(5),
    balance: day.projected_balance,
  }));

  return (
    <Card className="p-6 mb-6">
      <h3 className="text-lg font-bold mb-4">30-Day Balance Projection</h3>
      <ResponsiveContainer width="100%" height={300}>
        {/* @ts-ignore - Recharts has known type issues with React 18+ */}
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="colorBalance" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#494fdf" stopOpacity={0.8} />
              <stop offset="95%" stopColor="#494fdf" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#505a63" />
          <XAxis
            dataKey="date"
            stroke="#8d969e"
            label={{ value: "Day", position: "insideBottomRight", offset: -5 }}
          />
          <YAxis
            stroke="#8d969e"
            tickFormatter={(value: any) => `${(value / 1000).toFixed(0)}k`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#1e2225",
              border: "1px solid #505a63",
              borderRadius: "8px",
            }}
            formatter={(value: any) => formatEGP(value as number)}
          />
          <Area
            type="monotone"
            dataKey="balance"
            stroke="#494fdf"
            fillOpacity={1}
            fill="url(#colorBalance)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </Card>
  );
}
