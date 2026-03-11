"use client";

import { useState } from "react";
import { interpretTickerWithImages } from "@/lib/api";
import type { InterpretWithImagesWrapper } from "@/lib/types";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Textarea } from "@/components/ui/Textarea";
import { Spinner } from "@/components/ui/Spinner";

type Props = {
  onResult: (data: InterpretWithImagesWrapper) => void;
};

const SAMPLE = '[{"timestamp":"1","open":10,"high":11,"low":9.5,"close":10.4}]';

export function ImageAnalyzeForm({ onResult }: Props) {
  const [ticker, setTicker] = useState("WIMI");
  const [daily, setDaily] = useState(SAMPLE);
  const [h4, setH4] = useState(SAMPLE);
  const [h1, setH1] = useState(SAMPLE);
  const [files, setFiles] = useState<FileList | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async () => {
    setLoading(true);
    setError(null);
    try {
      const form = new FormData();
      form.append("ticker", ticker);
      form.append("daily", daily);
      form.append("h4", h4);
      form.append("h1", h1);
      if (!files || files.length === 0) {
        throw new Error("Please upload at least one image");
      }
      Array.from(files).forEach((file) => form.append("images", file));
      const data = await interpretTickerWithImages(form);
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
      <Textarea rows={4} value={daily} onChange={(e) => setDaily(e.target.value)} placeholder="Daily candles JSON" />
      <Textarea rows={4} value={h4} onChange={(e) => setH4(e.target.value)} placeholder="H4 candles JSON" />
      <Textarea rows={4} value={h1} onChange={(e) => setH1(e.target.value)} placeholder="H1 candles JSON" />
      <input type="file" multiple accept=".png,.jpg,.jpeg,image/png,image/jpeg" onChange={(e) => setFiles(e.target.files)} />
      <div className="flex gap-2">
        <Button onClick={submit} disabled={loading}>Interpret with Images</Button>
        {loading ? <Spinner /> : null}
      </div>
      {error ? <p className="text-sm text-red-400">{error}</p> : null}
    </section>
  );
}
