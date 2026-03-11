"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { BatchAnalyzeForm } from "@/components/forms/BatchAnalyzeForm";
import { CsvWatchlistForm } from "@/components/forms/CsvWatchlistForm";
import { WatchlistTable } from "@/components/tables/WatchlistTable";
import { CompareCard } from "@/components/cards/CompareCard";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { compareSessions, getSession, listSessions, saveBatchSession } from "@/lib/sessions";
import type { BatchInterpretResponse, EnrichAndBatchInterpretResponse, SessionCompareResponse, SessionSummary } from "@/lib/types";

export default function WatchlistPage() {
  const [result, setResult] = useState<(BatchInterpretResponse | EnrichAndBatchInterpretResponse) | null>(null);
  const [mode, setMode] = useState<"json" | "csv">("json");
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [left, setLeft] = useState("");
  const [right, setRight] = useState("");
  const [compare, setCompare] = useState<SessionCompareResponse | null>(null);

  useEffect(() => {
    void listSessions().then((data) => setSessions(data.filter((s) => s.session_type === "watchlist_batch_analysis").slice(0, 20)));
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Watchlist Analyzer</h1>
        <div className="flex gap-3">
          <Link href="/sessions" className="text-blue-400 underline">Sessions</Link>
          <Link href="/" className="text-blue-400 underline">Back home</Link>
        </div>
      </div>

      <div className="flex gap-2">
        <Button className={mode === "json" ? "bg-blue-600" : "bg-slate-700 hover:bg-slate-600"} onClick={() => setMode("json")}>Paste JSON</Button>
        <Button className={mode === "csv" ? "bg-blue-600" : "bg-slate-700 hover:bg-slate-600"} onClick={() => setMode("csv")}>Upload CSV</Button>
      </div>

      {mode === "json" ? <BatchAnalyzeForm onResult={setResult} /> : <CsvWatchlistForm onResult={setResult} />}

      {result ? (
        <Card>
          <Button onClick={() => void saveBatchSession(result).then(() => listSessions().then((d) => setSessions(d.filter((s) => s.session_type === "watchlist_batch_analysis").slice(0, 20))))}>Save current batch result</Button>
        </Card>
      ) : null}

      <Card className="space-y-2">
        <h3 className="font-semibold">Compare saved watchlists</h3>
        <div className="grid gap-2 md:grid-cols-2">
          <select className="rounded border border-slate-700 bg-slate-950 p-2 text-sm" value={left} onChange={(e) => setLeft(e.target.value)}>
            <option value="">Left session</option>
            {sessions.map((s) => <option key={`l-${s.id}`} value={s.id}>{s.label || s.created_at}</option>)}
          </select>
          <select className="rounded border border-slate-700 bg-slate-950 p-2 text-sm" value={right} onChange={(e) => setRight(e.target.value)}>
            <option value="">Right session</option>
            {sessions.map((s) => <option key={`r-${s.id}`} value={s.id}>{s.label || s.created_at}</option>)}
          </select>
        </div>
        <div className="flex gap-2">
          <Button disabled={!left || !right} onClick={async () => setCompare(await compareSessions(left, right))}>Compare selected</Button>
          <Button disabled={!left} onClick={async () => {
            const detail = await getSession(left);
            if (detail.metadata?.items) {
              setResult({ count: (detail.metadata.items as unknown[]).length, items: detail.metadata.items as never[], sorted_by: "ranking.score" });
            }
          }}>Open left session</Button>
        </div>
      </Card>

      <CompareCard compare={compare} />

      {result ? <WatchlistTable items={result.items} /> : null}
    </div>
  );
}
