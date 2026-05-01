"use client";

import React from "react";
import { useApp } from "@/components/providers/AppProvider";
import { formatEGP, getMonthYear } from "@/lib/constants";

export function BalanceHero() {
  const { bank } = useApp();

  if (!bank) return null;

  // Calculate current month income and expenses
  const now = new Date();
  const currentMonth = now.getMonth();
  const currentYear = now.getFullYear();

  const monthTransactions = bank.transactions.filter((tx) => {
    const txDate = new Date(tx.timestamp.replace(" ", "T"));
    return txDate.getMonth() === currentMonth && txDate.getFullYear() === currentYear;
  });

  const income = monthTransactions
    .filter((tx) => tx.type === "CREDIT")
    .reduce((sum, tx) => sum + tx.amount, 0);

  const expenses = monthTransactions
    .filter((tx) => tx.type === "DEBIT")
    .reduce((sum, tx) => sum + tx.amount, 0);

  return (
    <div className="card bg-gradient-to-br from-rev-blue/20 to-rev-blue/5 border-rev-blue/30 p-8 mb-8">
      <p className="text-rev-muted text-sm mb-2">Current Balance</p>
      <h1 className="text-display text-rev-white mb-8">{formatEGP(bank.balance)}</h1>

      <div className="grid grid-cols-2 gap-6">
        <div>
          <p className="text-rev-muted text-sm mb-1">This Month Income</p>
          <p className="text-2xl font-bold text-rev-teal">{formatEGP(income)}</p>
        </div>
        <div>
          <p className="text-rev-muted text-sm mb-1">This Month Expenses</p>
          <p className="text-2xl font-bold text-rev-danger">{formatEGP(expenses)}</p>
        </div>
      </div>
    </div>
  );
}
