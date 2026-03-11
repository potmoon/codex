"use client";

import { useState } from "react";
import { batchInterpret } from "@/lib/api";
import type { BatchInterpretRequest, BatchInterpretResponse } from "@/lib/types";
import { Button } from "@/components/ui/Button";
import { Textarea } from "@/components/ui/Textarea";
import { Spinner } from "@/components/ui/Spinner";

const SAMPLE = '{"items":[{"ticker":"WIMI","daily":[{"timestamp":"1","open":10,"high":11,"low":9.5,"close":10.4}],"h4":[{"timestamp":"1","open":10,"high":11,"low":9.5,"close":10.4}],"h1":[{"timestamp":"1","open":10,"high":11,"low":9.5,"close":10.4}]}]}';

export function BatchAnalyzeForm({ onResult }: { onResult: (data: BatchInterpretResponse) => void }) {
  const [raw, setRaw] = useState(SAMPLE);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async () => {
    setLoading(true);
    setError(null);
    try {
      const payload = JSON.parse(raw) as BatchInterpretRequest;
      const data = await batchInterpret(payload);
      onResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="space-y-3">
      <Textarea rows={14} value={raw} onChange={(e) => setRaw(e.target.value)} />
      <div className="flex gap-2">
        <Button onClick={submit} disabled={loading}>Run Watchlist Ranking</Button>
        {loading ? <Spinner /> : null}
      </div>
      {error ? <p className="text-sm text-red-400">{error}</p> : null}
    </section>
  );
}
