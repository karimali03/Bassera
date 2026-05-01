"use client";

import React, { useState } from "react";
import { generateSuggestions } from "@/lib/api";
import { Pill } from "@/components/ui/Pill";
import { Spinner } from "@/components/ui/Spinner";

interface GenerateButtonProps {
  userId: string;
  onGenerate: () => void;
}

export function GenerateButton({ userId, onGenerate }: GenerateButtonProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    try {
      setLoading(true);
      setError(null);
      await generateSuggestions(userId);
      onGenerate();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate suggestions");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="text-center py-12">
      {loading && (
        <div className="mb-6">
          <Spinner />
          <p className="text-rev-muted mt-4">Generating AI suggestions...</p>
          <p className="text-sm text-rev-muted">(This may take 10-30 seconds)</p>
        </div>
      )}
      {error && (
        <div className="mb-6 p-4 bg-rev-danger/10 border border-rev-danger/30 rounded-sm">
          <p className="text-rev-danger">{error}</p>
        </div>
      )}
      {!loading && (
        <>
          <h2 className="text-heading mb-4">No Suggestions Yet</h2>
          <p className="text-rev-muted mb-8">
            Click below to generate personalized AI-powered spending suggestions.
          </p>
          <Pill onClick={handleGenerate} variant="primary">
            Generate Suggestions
          </Pill>
        </>
      )}
    </div>
  );
}
