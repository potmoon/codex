"use client";

import { useState } from "react";
import { analyzeTicker, buildLlmPayload, interpretTicker } from "@/lib/api";
import type { AnalyzeRequest, AnalyzeResponse, InterpretWrapper, LlmPayload } from "@/lib/types";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Textarea } from "@/components/ui/Textarea";
import { Spinner } from "@/components/ui/Spinner";

type Props = {
  onResult: (data: AnalyzeResponse | InterpretWrapper | LlmPayload) => void;
};

const SAMPLE = '[{"timestamp":"1","open":10,"high":11,"low":9.5,"close":10.4}]';

export function SingleAnalyzeForm({ onResult }: Props) {
  const [ticker, setTicker] = useState("WIMI");
  const [daily, setDaily] = useState(SAMPLE);
  const [h4, setH4] = useState(SAMPLE);
  const [h1, setH1] = useState(SAMPLE);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const parsePayload = (): AnalyzeRequest => ({
    ticker,
    candles: {
      daily: JSON.parse(daily),
      h4: JSON.parse(h4),
      h1: JSON.parse(h1),
    },
  });

  const run = async (kind: "analyze" | "interpret" | "llm") => {
    setLoading(true);
    setError(null);
    try {
      const payload = parsePayload();
      const data =
        kind === "analyze"
          ? await analyzeTicker(payload)
          : kind === "llm"
            ? await buildLlmPayload(payload)
            : await interpretTicker(payload);
      onResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="space-y-3">
      <Input value={ticker} onChange={(e) => setTicker(e.target.value)} placeholder="Ticker" />
      <Textarea rows={6} value={daily} onChange={(e) => setDaily(e.target.value)} placeholder="Daily candles JSON" />
      <Textarea rows={6} value={h4} onChange={(e) => setH4(e.target.value)} placeholder="H4 candles JSON" />
      <Textarea rows={6} value={h1} onChange={(e) => setH1(e.target.value)} placeholder="H1 candles JSON" />
      <div className="flex gap-2">
        <Button onClick={() => run("analyze")} disabled={loading}>Analyze</Button>
        <Button onClick={() => run("interpret")} disabled={loading}>Interpret</Button>
        <Button onClick={() => run("llm")} disabled={loading}>LLM Payload</Button>
        {loading ? <Spinner /> : null}
      </div>
      {error ? <p className="text-sm text-red-400">{error}</p> : null}
    </section>
  );
}
