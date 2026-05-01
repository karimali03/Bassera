"use client";

import React from "react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { ForecastRule } from "@/lib/types";
import { formatEGP } from "@/lib/constants";

interface RulesTableProps {
  title: string;
  rules: ForecastRule[];
}

function RulesTable({ title, rules }: RulesTableProps) {
  return (
    <Card className="p-6 mb-6">
      <h3 className="text-lg font-bold mb-4">{title}</h3>
      {rules.length === 0 ? (
        <p className="text-rev-muted">No {title.toLowerCase()}</p>
      ) : (
        <div className="space-y-2">
          {rules.map((rule, idx) => (
            <div
              key={idx}
              className="flex items-center justify-between p-3 bg-white/5 rounded-sm"
            >
              <div className="flex-1">
                <p className="text-white font-medium">{rule.name}</p>
                <p className="text-xs text-rev-muted">Day {rule.day}</p>
              </div>
              <div className="flex items-center gap-3">
                <p className="font-bold text-white">{formatEGP(rule.value)}</p>
                <Badge variant="info">{rule.confidence}</Badge>
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}

interface IncomeExpenseProps {
  fixedIncomes: ForecastRule[];
  fixedExpenses: ForecastRule[];
}

export function RulesDisplay({ fixedIncomes, fixedExpenses }: IncomeExpenseProps) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <RulesTable title="Fixed Income" rules={fixedIncomes} />
      <RulesTable title="Fixed Expenses" rules={fixedExpenses} />
    </div>
  );
}
