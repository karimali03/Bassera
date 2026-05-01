"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  TrendingUp,
  Wallet,
  BarChart3,
  Lightbulb,
  Menu,
  X,
} from "lucide-react";

export function Sidebar() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  const navItems = [
    { href: "/", icon: Wallet, label: "Dashboard" },
    { href: "/transactions", icon: BarChart3, label: "Transactions" },
    { href: "/forecast", icon: TrendingUp, label: "Forecast" },
    { href: "/suggestions", icon: Lightbulb, label: "Suggestions" },
  ];

  return (
    <>
      {/* Mobile hamburger */}
      <button
        onClick={() => setOpen(!open)}
        className="fixed top-5 left-4 z-50 lg:hidden p-2 rounded-sm bg-card border border-rev-border/20"
      >
        {open ? <X size={20} /> : <Menu size={20} />}
      </button>

      {/* Overlay */}
      {open && (
        <div
          className="fixed inset-0 bg-black/50 z-30 lg:hidden"
          onClick={() => setOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={`fixed left-0 top-0 h-screen w-60 bg-rev-dark border-r border-rev-border/20 flex flex-col p-6 z-40
          transition-transform lg:translate-x-0 ${open ? "translate-x-0" : "-translate-x-full"}`}
      >
        <div className="mb-12">
          <h1 className="text-2xl font-bold text-rev-blue">Baseera</h1>
          <p className="text-rev-muted text-sm">Financial Advisor</p>
        </div>

        <nav className="flex-1 space-y-2">
          {navItems.map(({ href, icon: Icon, label }) => {
            const isActive = pathname === href;
            return (
              <Link key={href} href={href} onClick={() => setOpen(false)}>
                <div
                  className={`flex items-center gap-3 px-4 py-3 rounded-sm transition-colors ${
                    isActive
                      ? "bg-rev-blue text-white"
                      : "text-rev-muted hover:text-white hover:bg-white/5"
                  }`}
                >
                  <Icon size={20} />
                  <span className="text-sm font-medium">{label}</span>
                </div>
              </Link>
            );
          })}
        </nav>

        <div className="border-t border-rev-border/20 pt-4">
          <p className="text-xs text-rev-muted">Baseera &copy; 2026</p>
        </div>
      </div>
    </>
  );
}
