import type {
  BatchInterpretResponse,
  InterpretWrapper,
  SessionCompareResponse,
  SessionDetail,
  SessionSummary,
} from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

async function fetchSessions<T>(path: string, init?: RequestInit): Promise<T> {
  if (!API_BASE_URL) throw new Error("NEXT_PUBLIC_API_BASE_URL is not set");
  const res = await fetch(`${API_BASE_URL}${path}`, init);
  if (!res.ok) throw new Error(await res.text());
  return (await res.json()) as T;
}

export function saveSingleSession(payload: InterpretWrapper, label?: string): Promise<{ id: string }> {
  return fetchSessions("/sessions/save-single", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ label, payload }),
  });
}

export function saveBatchSession(payload: BatchInterpretResponse, label?: string): Promise<{ id: string }> {
  return fetchSessions("/sessions/save-batch", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ label, payload }),
  });
}

export async function listSessions(): Promise<SessionSummary[]> {
  const data = await fetchSessions<{ items: SessionSummary[] }>("/sessions");
  return data.items;
}

export function getSession(sessionId: string): Promise<SessionDetail> {
  return fetchSessions(`/sessions/${sessionId}`);
}

export function compareSessions(leftId: string, rightId: string): Promise<SessionCompareResponse> {
  return fetchSessions(`/sessions/compare?left_id=${encodeURIComponent(leftId)}&right_id=${encodeURIComponent(rightId)}`);
}
