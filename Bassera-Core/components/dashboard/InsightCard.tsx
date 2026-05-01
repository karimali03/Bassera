"use client";

import React, { useState, useEffect } from "react";
import { useApp } from "@/components/providers/AppProvider";
import { fetchSuggestions } from "@/lib/api";
import { SuggestionsResponse } from "@/lib/types";
import { Card } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";

export function InsightCard() {
  const { user } = useApp();
  const [insight, setInsight] = useState<SuggestionsResponse | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!user?.id) return;

    const loadInsight = async () => {
      try {
        setLoading(true);
        const data = await fetchSuggestions(user.id);
        setInsight(data);
      } catch (err) {
        // Gracefully handle 404 or other errors
      } finally {
        setLoading(false);
      }
    };

    loadInsight();
  }, [user?.id]);

  if (loading) {
    return (
      <Card className="mb-8 p-6 flex items-center justify-center">
        <Spinner />
      </Card>
    );
  }

  if (!insight?.insight_of_the_day) {
    return null;
  }

  const iconMap: Record<string, string> = {
    lightbulb: "💡",
    trend_up: "📈",
    trend_down: "📉",
    calendar: "📅",
    star: "⭐",
    leaf: "🌿",
  };

  const icon = iconMap[insight.insight_of_the_day.icon_hint] || "💡";

  return (
    <Card className="mb-8 p-6 bg-gradient-to-r from-rev-blue/10 to-rev-teal/10 border-rev-blue/30">
      <div className="flex gap-4 items-start">
        <span className="text-4xl">{icon}</span>
        <div>
          <p className="text-sm text-rev-muted mb-1">Insight of the Day</p>
          <p className="text-white">{insight.insight_of_the_day.text}</p>
        </div>
      </div>
    </Card>
  );
}
