import React from "react";

export function Spinner() {
  return (
    <div className="flex items-center justify-center">
      <div className="w-8 h-8 border-4 border-rev-border border-t-rev-blue rounded-full animate-spin" />
    </div>
  );
}
