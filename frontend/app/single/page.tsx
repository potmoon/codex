"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { SingleAnalyzeForm } from "@/components/forms/SingleAnalyzeForm";
import { ImageAnalyzeForm } from "@/components/forms/ImageAnalyzeForm";
import { InterpretationCard } from "@/components/cards/InterpretationCard";
import { MtfViewCard } from "@/components/cards/MtfViewCard";
import { LevelsCard } from "@/components/cards/LevelsCard";
import { ReasonFlagsCard } from "@/components/cards/ReasonFlagsCard";
import { InterpreterContextCard } from "@/components/cards/InterpreterContextCard";
import { CompareCard } from "@/components/cards/CompareCard";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { compareSessions, getSession, listSessions, saveSingleSession } from "@/lib/sessions";
import type {
  AnalyzeResponse,
  InterpretWithImagesWrapper,
  InterpretWrapper,
  LlmPayload,
  SessionCompareResponse,
  SessionSummary,
} from "@/lib/types";


type ResultUnion = AnalyzeResponse | InterpretWrapper | InterpretWithImagesWrapper | LlmPayload;

function hasInterpretation(value: ResultUnion): value is InterpretWrapper | InterpretWithImagesWrapper {
  return "interpretation" in value;
}

export default function SinglePage() {
  const [result, setResult] = useState<ResultUnion | null>(null);
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [selectedCompare, setSelectedCompare] = useState<string>("");
  const [compare, setCompare] = useState<SessionCompareResponse | null>(null);

  useEffect(() => {
    void listSessions().then((data) => setSessions(data.filter((s) => s.session_type === "single_ticker_analysis").slice(0, 10)));
  }, []);

  const facts = useMemo(() => {
    if (!result) return null;
    if ("facts" in result) return result.facts;
    if ("decision_context" in result) return result;
    return null;
  }, [result]);

  const llmPayload = useMemo(() => {
    if (!result) return null;
    if ("llm_payload" in result) return result.llm_payload;
    if ("decision_context" in result && "signals" in result) return result;
    return null;
  }, [result]);

  const interpreted = result && hasInterpretation(result) ? result : null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Single Ticker Analyzer</h1>
        <div className="flex gap-3">
          <Link href="/sessions" className="text-blue-400 underline">Sessions</Link>
          <Link href="/" className="text-blue-400 underline">Back home</Link>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <h2 className="mb-3 font-semibold">Analyze / Interpret</h2>
          <SingleAnalyzeForm onResult={(data) => setResult(data)} />
        </Card>
        <Card>
          <h2 className="mb-3 font-semibold">Interpret with Images</h2>
          <ImageAnalyzeForm onResult={(data) => setResult(data)} />
        </Card>
      </div>

      {interpreted ? (
        <Card>
          <div className="flex flex-wrap items-center gap-2">
            <Button onClick={() => void saveSingleSession(interpreted).then(() => listSessions().then((d) => setSessions(d.filter((s) => s.session_type === "single_ticker_analysis").slice(0, 10))))}>Save current result</Button>
            <select className="rounded border border-slate-700 bg-slate-950 p-2 text-sm" value={selectedCompare} onChange={(e) => setSelectedCompare(e.target.value)}>
              <option value="">Compare against saved...</option>
              {sessions.map((s) => <option key={s.id} value={s.id}>{s.ticker || s.label || s.id}</option>)}
            </select>
            <Button disabled={!selectedCompare} onClick={async () => {
              const saved = await getSession(selectedCompare);
              const tempId = await saveSingleSession(interpreted, "current_temp_compare");
              const cmp = await compareSessions(saved.id, tempId.id);
              setCompare(cmp);
            }}>Compare with current</Button>
          </div>
        </Card>
      ) : null}

      <CompareCard compare={compare} />

      {result ? (
        <div className="space-y-4">
          {hasInterpretation(result) ? <InterpretationCard interpretation={result.interpretation} /> : null}
          {facts ? <MtfViewCard mtfView={facts.mtf_view} /> : null}
          {facts ? <LevelsCard levels={facts.levels} /> : null}
          {facts ? <ReasonFlagsCard reasonFlags={facts.reason_flags} /> : null}
          {hasInterpretation(result) && "interpreter_context" in result ? (
            <InterpreterContextCard context={result.interpreter_context} />
          ) : null}

          <Card>
            <details>
              <summary className="cursor-pointer font-medium">Raw facts JSON</summary>
              <pre className="overflow-x-auto text-xs">{JSON.stringify(facts, null, 2)}</pre>
            </details>
            <details>
              <summary className="cursor-pointer font-medium">Raw llm_payload JSON</summary>
              <pre className="overflow-x-auto text-xs">{JSON.stringify(llmPayload, null, 2)}</pre>
            </details>
            <details>
              <summary className="cursor-pointer font-medium">Raw interpretation JSON</summary>
              <pre className="overflow-x-auto text-xs">{JSON.stringify(hasInterpretation(result) ? result.interpretation : null, null, 2)}</pre>
            </details>
          </Card>
        </div>
      ) : null}
    </div>
  );
}
