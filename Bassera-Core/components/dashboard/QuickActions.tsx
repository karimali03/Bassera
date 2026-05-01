"use client";

import React from "react";
import Link from "next/link";
import { Pill } from "@/components/ui/Pill";

export function QuickActions() {
  return (
    <div className="mt-8 grid grid-cols-2 gap-4">
      <Link href="/transactions">
        <Pill variant="secondary" className="w-full text-center">
          View All Transactions
        </Pill>
      </Link>
      <Link href="/forecast">
        <Pill variant="secondary" className="w-full text-center">
          Check Forecast
        </Pill>
      </Link>
      <Link href="/suggestions" className="col-span-2">
        <Pill variant="primary" className="w-full text-center">
          Get AI Suggestions
        </Pill>
      </Link>
    </div>
  );
}
