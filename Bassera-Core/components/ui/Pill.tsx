import React, { ReactNode } from "react";

interface PillProps {
  children: ReactNode;
  onClick?: () => void;
  variant?: "primary" | "secondary" | "outline" | "ghost";
  className?: string;
  disabled?: boolean;
  type?: "button" | "submit";
}

export function Pill({
  children,
  onClick,
  variant = "primary",
  className = "",
  disabled = false,
  type = "button",
}: PillProps) {
  const variantClass = {
    primary: "pill-primary",
    secondary: "pill-secondary",
    outline: "pill-outline",
    ghost: "pill-ghost",
  }[variant];

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${variantClass} disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
    >
      {children}
    </button>
  );
}
