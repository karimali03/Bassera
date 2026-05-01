"use client";

import React, { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { fetchUsers, fetchBank } from "@/lib/api";
import { UserResponse, BankResponse } from "@/lib/types";
import { BANK_ID } from "@/lib/constants";
import { Spinner } from "@/components/ui/Spinner";

interface AppContextType {
  user: UserResponse | null;
  bank: BankResponse | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [bank, setBank] = useState<BankResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch users to get the user ID
      const users = await fetchUsers();
      if (!users || users.length === 0) {
        throw new Error("No users found");
      }
      const currentUser = users[0];
      setUser(currentUser);

      // Fetch bank data
      const bankData = await fetchBank(BANK_ID);
      setBank(bankData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Spinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h1 className="text-heading mb-2">Connection Error</h1>
          <p className="text-rev-muted mb-6">{error}</p>
          <button
            onClick={loadData}
            className="pill-primary"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <AppContext.Provider value={{ user, bank, loading, error, refresh: loadData }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error("useApp must be used within AppProvider");
  }
  return context;
}
