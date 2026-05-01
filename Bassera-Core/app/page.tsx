"use client";

import { BalanceHero } from "@/components/dashboard/BalanceHero";
import { InsightCard } from "@/components/dashboard/InsightCard";
import { SpendingChart } from "@/components/dashboard/SpendingChart";
import { RecentTxList } from "@/components/dashboard/RecentTxList";
import { QuickActions } from "@/components/dashboard/QuickActions";

export default function Home() {
  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-heading font-bold mb-8">Dashboard</h1>
      <BalanceHero />
      <InsightCard />
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <SpendingChart />
          <RecentTxList />
        </div>
        <div>
          <QuickActions />
        </div>
      </div>
    </div>
  );
}
