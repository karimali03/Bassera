import React, { ReactNode } from "react";

interface BadgeProps {
  children: ReactNode;
  variant?: "primary" | "danger" | "warning" | "success" | "info";
  className?: string;
}

export function Badge({ children, variant = "primary", className = "" }: BadgeProps) {
  const variantClass = {
    primary: "bg-rev-blue text-white",
    danger: "bg-rev-danger text-white",
    warning: "bg-rev-warning text-rev-dark",
    success: "bg-rev-teal text-white",
    info: "bg-rev-slate text-white",
  }[variant];

  return (
    <span className={`inline-block rounded-pill px-3 py-1 text-xs font-semibold ${variantClass} ${className}`}>
      {children}
    </span>
  );
}
