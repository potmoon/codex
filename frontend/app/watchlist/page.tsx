"use client";

import Link from "next/link";
import { useState } from "react";
import { BatchAnalyzeForm } from "@/components/forms/BatchAnalyzeForm";
import { CsvWatchlistForm } from "@/components/forms/CsvWatchlistForm";
import { WatchlistTable } from "@/components/tables/WatchlistTable";
import { Button } from "@/components/ui/Button";
import type { BatchInterpretResponse, EnrichAndBatchInterpretResponse } from "@/lib/types";

export default function WatchlistPage() {
  const [result, setResult] = useState<(BatchInterpretResponse | EnrichAndBatchInterpretResponse) | null>(null);
  const [mode, setMode] = useState<"json" | "csv">("json");

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Watchlist Analyzer</h1>
        <Link href="/" className="text-blue-400 underline">Back home</Link>
      </div>

      <div className="flex gap-2">
        <Button className={mode === "json" ? "bg-blue-600" : "bg-slate-700 hover:bg-slate-600"} onClick={() => setMode("json")}>Paste JSON</Button>
        <Button className={mode === "csv" ? "bg-blue-600" : "bg-slate-700 hover:bg-slate-600"} onClick={() => setMode("csv")}>Upload CSV</Button>
      </div>

      {mode === "json" ? <BatchAnalyzeForm onResult={setResult} /> : <CsvWatchlistForm onResult={setResult} />}

      {result ? <WatchlistTable items={result.items} /> : null}
    </div>
  );
}
