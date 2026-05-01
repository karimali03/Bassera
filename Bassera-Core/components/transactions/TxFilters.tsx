"use client";

import React, { useState } from "react";
import { useApp } from "@/components/providers/AppProvider";
import { formatCategory } from "@/lib/constants";

export function TxFilters({
  onFilterChange,
}: {
  onFilterChange: (filters: {
    category: string;
    type: string;
    search: string;
  }) => void;
}) {
  const { bank } = useApp();
  const [category, setCategory] = useState("");
  const [type, setType] = useState("");
  const [search, setSearch] = useState("");

  const categories = Array.from(
    new Set(bank?.transactions.map((tx) => tx.category) || [])
  ).sort();

  return (
    <div className="card p-6 mb-6">
      <h3 className="text-lg font-bold mb-4">Filters</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm text-rev-muted mb-2">Category</label>
          <select
            value={category}
            onChange={(e) => {
              const v = e.target.value;
              setCategory(v);
              onFilterChange({ category: v, type, search });
            }}
            className="w-full bg-white/5 border border-rev-border/30 rounded-sm px-3 py-2 text-white"
          >
            <option value="">All Categories</option>
            {categories.map((cat) => (
              <option key={cat} value={cat}>
                {formatCategory(cat)}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm text-rev-muted mb-2">Type</label>
          <select
            value={type}
            onChange={(e) => {
              const v = e.target.value;
              setType(v);
              onFilterChange({ category, type: v, search });
            }}
            className="w-full bg-white/5 border border-rev-border/30 rounded-sm px-3 py-2 text-white"
          >
            <option value="">All Types</option>
            <option value="CREDIT">Income</option>
            <option value="DEBIT">Expense</option>
          </select>
        </div>

        <div>
          <label className="block text-sm text-rev-muted mb-2">Search</label>
          <input
            type="text"
            placeholder="Merchant or note..."
            value={search}
            onChange={(e) => {
              const v = e.target.value;
              setSearch(v);
              onFilterChange({ category, type, search: v });
            }}
            className="w-full bg-white/5 border border-rev-border/30 rounded-sm px-3 py-2 text-white placeholder-rev-muted"
          />
        </div>
      </div>
    </div>
  );
}
