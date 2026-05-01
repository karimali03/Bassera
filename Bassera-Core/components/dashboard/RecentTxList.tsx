"use client";

import React, { useState } from "react";
import { useApp } from "@/components/providers/AppProvider";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { formatEGP, formatDate, formatTime, formatCategory } from "@/lib/constants";

export function RecentTxList() {
  const { bank } = useApp();
  const [visibleCount, setVisibleCount] = useState(10);

  if (!bank || bank.transactions.length === 0) return null;

  // Sort by timestamp descending and take first N
  const sortedTxs = [...bank.transactions]
    .sort((a, b) => new Date(b.timestamp.replace(" ", "T")).getTime() - new Date(a.timestamp.replace(" ", "T")).getTime())
    .slice(0, visibleCount);

  return (
    <Card className="p-6">
      <h3 className="text-lg font-bold mb-4">Recent Transactions</h3>
      <div className="space-y-3">
        {sortedTxs.map((tx) => (
          <div
            key={tx.transaction_id}
            className="flex items-center justify-between p-3 bg-white/5 rounded-sm hover:bg-white/10 transition-colors"
          >
            <div className="flex-1">
              <p className="text-white font-medium">{tx.merchant}</p>
              <div className="flex items-center gap-2 mt-1">
                <p className="text-xs text-rev-muted">{formatCategory(tx.category)}</p>
                <Badge variant="info" className="text-xs">
                  {formatDate(tx.timestamp)}
                </Badge>
              </div>
            </div>
            <div className="text-right">
              <p
                className={`font-bold text-lg ${
                  tx.type === "CREDIT" ? "text-rev-teal" : "text-rev-danger"
                }`}
              >
                {tx.type === "CREDIT" ? "+" : "-"}
                {formatEGP(tx.amount)}
              </p>
              <p className="text-xs text-rev-muted">{formatTime(tx.timestamp)}</p>
            </div>
          </div>
        ))}
      </div>

      {bank.transactions.length > visibleCount && (
        <button
          onClick={() => setVisibleCount(visibleCount + 10)}
          className="mt-4 text-rev-blue hover:text-rev-blue/80 text-sm font-medium"
        >
          Load more
        </button>
      )}
    </Card>
  );
}
