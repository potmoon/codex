import type {
  AnalyzeRequest,
  AnalyzeResponse,
  BatchInterpretRequest,
  BatchInterpretResponse,
  EnrichAndBatchInterpretRequest,
  EnrichAndBatchInterpretResponse,
  InterpretWithImagesWrapper,
  InterpretWrapper,
  LlmPayload,
} from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

async function apiFetch<T>(path: string, init: RequestInit): Promise<T> {
  if (!API_BASE_URL) {
    throw new Error("NEXT_PUBLIC_API_BASE_URL is not set");
  }
  const response = await fetch(`${API_BASE_URL}${path}`, init);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${response.status}`);
  }
  return (await response.json()) as T;
}

export function analyzeTicker(payload: AnalyzeRequest): Promise<AnalyzeResponse> {
  return apiFetch("/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function interpretTicker(payload: AnalyzeRequest): Promise<InterpretWrapper> {
  return apiFetch("/analyze/interpret", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function interpretTickerWithImages(formData: FormData): Promise<InterpretWithImagesWrapper> {
  return apiFetch("/analyze/interpret-with-images", {
    method: "POST",
    body: formData,
  });
}

export function batchInterpret(payload: BatchInterpretRequest): Promise<BatchInterpretResponse> {
  return apiFetch("/analyze/batch-interpret", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function buildLlmPayload(payload: AnalyzeRequest): Promise<LlmPayload> {
  return apiFetch("/analyze/llm-payload", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}


export function enrichAndBatchInterpret(payload: EnrichAndBatchInterpretRequest): Promise<EnrichAndBatchInterpretResponse> {
  return apiFetch("/watchlist/enrich-and-batch-interpret", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}
