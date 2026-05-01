"use client";

import React, { useEffect, useState, useCallback } from "react";
import { useApp } from "@/components/providers/AppProvider";
import { fetchSuggestions } from "@/lib/api";
import { SuggestionsResponse } from "@/lib/types";
import { GenerateButton } from "@/components/suggestions/GenerateButton";
import { SpendingBreakdown } from "@/components/suggestions/SpendingBreakdown";
import { SavingsGauge } from "@/components/suggestions/SavingsGauge";
import { SuggestionCard } from "@/components/suggestions/SuggestionCard";
import { Spinner } from "@/components/ui/Spinner";

export default function SuggestionsPage() {
  const { user } = useApp();
  const [suggestions, setSuggestions] = useState<SuggestionsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const loadSuggestions = useCallback(async () => {
    if (!user?.id) return;
    try {
      setLoading(true);
      const data = await fetchSuggestions(user.id);
      setSuggestions(data);
    } catch (err) {
      setSuggestions(null);
    } finally {
      setLoading(false);
    }
  }, [user?.id]);

  useEffect(() => {
    loadSuggestions();
  }, [loadSuggestions]);

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto">
        <h1 className="text-heading font-bold mb-8">AI Suggestions</h1>
        <div className="flex items-center justify-center py-12">
          <Spinner />
        </div>
      </div>
    );
  }

  if (!suggestions || suggestions.suggestions.length === 0) {
    return (
      <div className="max-w-6xl mx-auto">
        <h1 className="text-heading font-bold mb-8">AI Suggestions</h1>
        {user?.id && (
          <GenerateButton userId={user.id} onGenerate={loadSuggestions} />
        )}
      </div>
    );
  }

  const sortedSuggestions = [...suggestions.suggestions].sort((a, b) => {
    const priorityOrder = { HIGH: 0, MEDIUM: 1, LOW: 2 };
    return priorityOrder[a.priority] - priorityOrder[b.priority];
  });

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-heading font-bold mb-8">AI Suggestions</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2">
          <SpendingBreakdown categories={suggestions.spending_breakdown} />
        </div>
        <div>
          <SavingsGauge savings={suggestions.savings_potential} />
        </div>
      </div>

      <div>
        <h2 className="text-heading font-bold mb-6">
          Your Suggestions ({suggestions.suggestions.length})
        </h2>
        {sortedSuggestions.map((suggestion) => (
          <SuggestionCard key={suggestion.id} suggestion={suggestion} />
        ))}
      </div>
    </div>
  );
}
