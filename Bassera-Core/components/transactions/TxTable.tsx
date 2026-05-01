"use client";

import React, { useMemo } from "react";
import { useApp } from "@/components/providers/AppProvider";
import { Card } from "@/components/ui/Card";
import { TxRow } from "./TxRow";
import { TransactionResponse } from "@/lib/types";

interface TxTableProps {
  filters: { category: string; type: string; search: string };
  page: number;
  onPageChange: (page: number) => void;
}

const ITEMS_PER_PAGE = 50;

export function TxTable({ filters, page, onPageChange }: TxTableProps) {
  const { bank } = useApp();

  const filteredTxs = useMemo(() => {
    if (!bank) return [];

    let result = [...bank.transactions];

    if (filters.category) {
      result = result.filter((tx) => tx.category === filters.category);
    }
    if (filters.type) {
      result = result.filter((tx) => tx.type === filters.type);
    }
    if (filters.search) {
      const search = filters.search.toLowerCase();
      result = result.filter(
        (tx) =>
          tx.merchant.toLowerCase().includes(search) ||
          tx.note.toLowerCase().includes(search)
      );
    }

    return result.sort(
      (a, b) =>
        new Date(b.timestamp.replace(" ", "T")).getTime() -
        new Date(a.timestamp.replace(" ", "T")).getTime()
    );
  }, [bank, filters]);

  const paginatedTxs = filteredTxs.slice(
    page * ITEMS_PER_PAGE,
    (page + 1) * ITEMS_PER_PAGE
  );

  const totalPages = Math.ceil(filteredTxs.length / ITEMS_PER_PAGE);

  return (
    <Card className="p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-bold">
          Transactions ({filteredTxs.length})
        </h3>
        <p className="text-sm text-rev-muted">
          Page {page + 1} of {Math.max(1, totalPages)}
        </p>
      </div>

      {paginatedTxs.length === 0 ? (
        <p className="text-rev-muted py-8 text-center">No transactions found</p>
      ) : (
        <>
          <div className="space-y-1 mb-6">
            {paginatedTxs.map((tx) => (
              <TxRow key={tx.transaction_id} tx={tx} />
            ))}
          </div>

          {totalPages > 1 && (
            <div className="flex justify-between items-center pt-4 border-t border-rev-border/20">
              <button
                onClick={() => onPageChange(Math.max(0, page - 1))}
                disabled={page === 0}
                className="px-4 py-2 rounded-sm bg-white/5 text-white disabled:opacity-50 disabled:cursor-not-allowed hover:bg-white/10"
              >
                Previous
              </button>
              <p className="text-sm text-rev-muted">
                {page * ITEMS_PER_PAGE + 1} to{" "}
                {Math.min((page + 1) * ITEMS_PER_PAGE, filteredTxs.length)} of{" "}
                {filteredTxs.length}
              </p>
              <button
                onClick={() => onPageChange(Math.min(totalPages - 1, page + 1))}
                disabled={page >= totalPages - 1}
                className="px-4 py-2 rounded-sm bg-white/5 text-white disabled:opacity-50 disabled:cursor-not-allowed hover:bg-white/10"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </Card>
  );
}
