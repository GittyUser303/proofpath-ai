import type { CaseDetail, CaseSummary } from "../types";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with status ${response.status}`);
  }

  const contentType = response.headers.get("content-type") ?? "";
  if (contentType.includes("application/json")) {
    return response.json() as Promise<T>;
  }
  return response.text() as Promise<T>;
}

export async function investigate(userId: string, input: string) {
  return request<{ case_id: string; status: string }>("/api/investigate", {
    method: "POST",
    body: JSON.stringify({ user_id: userId, input, mode: "standard" }),
  });
}

export async function getCase(caseId: string) {
  return request<CaseDetail>(`/api/cases/${encodeURIComponent(caseId)}`);
}

export async function listCases(userId: string) {
  return request<CaseSummary[]>(`/api/cases?user_id=${encodeURIComponent(userId)}`);
}

export async function getReport(caseId: string) {
  return request<string>(`/api/report/${encodeURIComponent(caseId)}`);
}
