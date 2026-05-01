"use client";

import React from "react";
import { Card } from "@/components/ui/Card";
import { AIForecastPayload } from "@/lib/types";

interface WarningsListProps {
  warnings: string[];
}

export function WarningsList({ warnings }: WarningsListProps) {
  if (!warnings || warnings.length === 0) {
    return null;
  }

  return (
    <Card className="p-6 mb-6 border-rev-warning/50 bg-rev-warning/5">
      <h3 className="text-lg font-bold mb-4 text-rev-warning">Warnings</h3>
      <ul className="space-y-2">
        {warnings.map((warning, idx) => (
          <li key={idx} className="flex gap-3 text-white">
            <span className="text-rev-warning mt-0.5">⚠️</span>
            <p>{warning}</p>
          </li>
        ))}
      </ul>
    </Card>
  );
}
