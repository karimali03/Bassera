export const BANK_ID = "BANK-KARIM-001";

export const CATEGORY_COLORS: Record<string, string> = {
  Groceries: "#00a87e",
  Food_and_Dining: "#ec7e00",
  Transportation: "#494fdf",
  Shopping: "#e61e49",
  Services_and_Utilities: "#505a63",
  Entertainment: "#b09000",
  Health_and_Pharmacy: "#e23b4a",
  Installment: "#8d969e",
  Salary_and_Income: "#00a87e",
  Travel: "#007bc2",
  Other: "#c9c9cd",
};

export const CATEGORY_DISPLAY_NAMES: Record<string, string> = {
  Groceries: "🛒 Groceries",
  Food_and_Dining: "🍽️ Food & Dining",
  Transportation: "🚗 Transportation",
  Shopping: "🛍️ Shopping",
  Services_and_Utilities: "💡 Utilities",
  Entertainment: "🎬 Entertainment",
  Health_and_Pharmacy: "🏥 Health & Pharmacy",
  Installment: "💳 Installment",
  Salary_and_Income: "💰 Salary",
  Travel: "✈️ Travel",
  Other: "📦 Other",
};

export function formatEGP(amount: number): string {
  return new Intl.NumberFormat("ar-EG", {
    style: "currency",
    currency: "EGP",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
}

export function formatDate(dateStr: string): string {
  // Handle "2026-04-29 17:28" format
  const normalized = dateStr.replace(" ", "T");
  const date = new Date(normalized);
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(date);
}

export function formatTime(dateStr: string): string {
  const normalized = dateStr.replace(" ", "T");
  const date = new Date(normalized);
  return new Intl.DateTimeFormat("en-US", {
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

export function formatCategory(category: string): string {
  return CATEGORY_DISPLAY_NAMES[category] || category;
}

export function getCategoryColor(category: string): string {
  return CATEGORY_COLORS[category] || "#c9c9cd";
}

export function getMonthYear(dateStr: string): string {
  const normalized = dateStr.replace(" ", "T");
  const date = new Date(normalized);
  return new Intl.DateTimeFormat("en-US", {
    month: "long",
    year: "numeric",
  }).format(date);
}
