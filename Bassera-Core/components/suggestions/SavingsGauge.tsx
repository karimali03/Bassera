"use client";

import React from "react";
import { Card } from "@/components/ui/Card";
import { SavingsPotential } from "@/lib/types";
import { formatEGP } from "@/lib/constants";

interface SavingsGaugeProps {
  savings: SavingsPotential;
}

export function SavingsGauge({ savings }: SavingsGaugeProps) {
  return (
    <Card className="p-6 mb-6">
      <h3 className="text-lg font-bold mb-6">Savings Potential</h3>
      <div className="grid grid-cols-2 gap-6 mb-6">
        <div>
          <p className="text-rev-muted text-sm mb-2">Conservative Estimate</p>
          <p className="text-3xl font-bold text-rev-teal">
            {formatEGP(savings.conservative_egp)}
          </p>
          <p className="text-xs text-rev-muted mt-1">per month</p>
        </div>
        <div>
          <p className="text-rev-muted text-sm mb-2">Moderate Estimate</p>
          <p className="text-3xl font-bold text-rev-blue">
            {formatEGP(savings.moderate_egp)}
          </p>
          <p className="text-xs text-rev-muted mt-1">per month</p>
        </div>
      </div>
      <div className="border-t border-rev-border/20 pt-4">
        <p className="text-white text-sm">{savings.summary}</p>
      </div>
    </Card>
  );
}
