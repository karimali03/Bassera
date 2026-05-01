import {
  BankResponse,
  UserResponse,
  SuggestionsResponse,
  AIForecastPayload,
} from "./types";

const API_BASE = "/api";
const BANK_BASE = "/bank";

async function fetchJson<T>(url: string): Promise<T> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }
  return response.json();
}

async function postJson<T>(url: string, body: object): Promise<T> {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }
  return response.json();
}

export async function fetchUsers(): Promise<UserResponse[]> {
  return fetchJson(`${API_BASE}/users`);
}

export async function fetchUser(userId: string): Promise<UserResponse> {
  return fetchJson(`${API_BASE}/users/${userId}`);
}

export async function fetchBank(bankId: string): Promise<BankResponse> {
  return fetchJson(`${BANK_BASE}/${bankId}`);
}

export async function fetchBankTransactions(
  bankId: string
): Promise<BankResponse> {
  return fetchJson(`${BANK_BASE}/${bankId}/transactions`);
}

export async function fetchSuggestions(
  userId: string
): Promise<SuggestionsResponse> {
  return fetchJson(`${API_BASE}/suggestions/${userId}`);
}

export async function generateSuggestions(
  userId: string
): Promise<SuggestionsResponse> {
  return postJson(`${API_BASE}/suggestions/${userId}/generate`, {});
}

export async function fetchForecast(
  userId: string
): Promise<AIForecastPayload> {
  return fetchJson(`${API_BASE}/forecast/${userId}`);
}
