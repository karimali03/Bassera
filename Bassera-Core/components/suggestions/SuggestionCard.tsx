"use client";

import React from "react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { SuggestionData } from "@/lib/types";
import { formatEGP } from "@/lib/constants";

const iconMap: Record<string, string> = {
  lightbulb: "💡",
  trend_up: "📈",
  trend_down: "📉",
  calendar: "📅",
  star: "⭐",
  leaf: "🌿",
};

interface SuggestionCardProps {
  suggestion: SuggestionData;
}

export function SuggestionCard({ suggestion }: SuggestionCardProps) {
  const priorityColor = {
    HIGH: "danger",
    MEDIUM: "warning",
    LOW: "info",
  } as const;

  const icon = iconMap[suggestion.icon_hint || "lightbulb"] || "💡";

  return (
    <Card className="p-6 mb-4">
      <div className="flex gap-4">
        <div className="text-4xl flex-shrink-0">{icon}</div>
        <div className="flex-1">
          <div className="flex items-start justify-between mb-2">
            <div>
              <h4 className="text-lg font-bold text-white mb-1">
                {suggestion.title}
              </h4>
              <div className="flex gap-2 mb-3">
                <Badge variant={priorityColor[suggestion.priority]}>
                  {suggestion.priority}
                </Badge>
                <Badge variant="info">{suggestion.type}</Badge>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-rev-muted">Monthly Saving</p>
              <p className="text-2xl font-bold text-rev-teal">
                {formatEGP(suggestion.estimated_monthly_saving_egp)}
              </p>
            </div>
          </div>

          <p className="text-white mb-4">{suggestion.body}</p>

          {suggestion.affected_categories.length > 0 && (
            <div className="mb-4">
              <p className="text-xs text-rev-muted mb-2">Affected Categories:</p>
              <div className="flex flex-wrap gap-2">
                {suggestion.affected_categories.map((cat) => (
                  <Badge key={cat} variant="info" className="text-xs">
                    {cat}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          <button className="text-rev-blue hover:text-rev-blue/80 font-medium text-sm">
            {suggestion.action_label} →
          </button>
        </div>
      </div>
    </Card>
  );
}
