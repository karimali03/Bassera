import React, { ReactNode } from "react";
import { Pill } from "./Pill";

interface EmptyStateProps {
  icon?: string;
  title: string;
  description: string;
  cta?: { label: string; onClick: () => void };
  children?: ReactNode;
}

export function EmptyState({
  icon,
  title,
  description,
  cta,
  children,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-20 px-4">
      {icon && <div className="text-6xl mb-4">{icon}</div>}
      <h2 className="text-heading text-center mb-2">{title}</h2>
      <p className="text-rev-muted text-center mb-6 max-w-md">{description}</p>
      {cta && (
        <Pill onClick={cta.onClick} variant="primary">
          {cta.label}
        </Pill>
      )}
      {children}
    </div>
  );
}
