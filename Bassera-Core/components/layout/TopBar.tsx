"use client";

import React from "react";
import { useApp } from "@/components/providers/AppProvider";
import { formatEGP } from "@/lib/constants";
import { Badge } from "@/components/ui/Badge";

export function TopBar() {
  const { user, bank } = useApp();

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return "Good morning";
    if (hour < 18) return "Good afternoon";
    return "Good evening";
  };

  return (
    <div className="fixed top-0 left-0 lg:left-60 right-0 h-20 bg-rev-dark border-b border-rev-border/20 flex items-center justify-between px-8 z-20">
      <div className="ml-12 lg:ml-0">
        <p className="text-rev-muted text-sm">{getGreeting()},</p>
        <h1 className="text-xl font-bold">
          {user?.fname} {user?.lname}
        </h1>
      </div>

      {bank && (
        <div className="flex items-center gap-4">
          <Badge variant="success">
            Balance: {formatEGP(bank.balance)}
          </Badge>
        </div>
      )}
    </div>
  );
}
