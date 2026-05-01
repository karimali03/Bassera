"use client";

import React from "react";
import { TransactionResponse } from "@/lib/types";
import { Badge } from "@/components/ui/Badge";
import { formatEGP, formatDate, formatTime, formatCategory } from "@/lib/constants";

export function TxRow({ tx }: { tx: TransactionResponse }) {
  return (
    <div className="flex items-center justify-between p-4 bg-white/5 rounded-sm hover:bg-white/10 transition-colors border-b border-rev-border/10 last:border-b-0">
      <div className="flex-1">
        <p className="text-white font-medium">{tx.merchant}</p>
        <div className="flex items-center gap-2 mt-1">
          <Badge variant="info" className="text-xs">
            {formatCategory(tx.category)}
          </Badge>
          <p className="text-xs text-rev-muted">{formatDate(tx.timestamp)}</p>
          <p className="text-xs text-rev-muted">{formatTime(tx.timestamp)}</p>
        </div>
        {tx.note && <p className="text-xs text-rev-muted mt-1 italic">&quot;{tx.note}&quot;</p>}
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
      </div>
    </div>
  );
}
