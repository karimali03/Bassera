"use client";

import React, { useState } from "react";
import { TxFilters } from "@/components/transactions/TxFilters";
import { TxTable } from "@/components/transactions/TxTable";

export default function TransactionsPage() {
  const [filters, setFilters] = useState({
    category: "",
    type: "",
    search: "",
  });
  const [page, setPage] = useState(0);

  const handleFilterChange = (newFilters: typeof filters) => {
    setFilters(newFilters);
    setPage(0);
  };

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-heading font-bold mb-8">Transactions</h1>
      <TxFilters onFilterChange={handleFilterChange} />
      <TxTable filters={filters} page={page} onPageChange={setPage} />
    </div>
  );
}
