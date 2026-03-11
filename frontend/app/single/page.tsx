"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { SingleAnalyzeForm } from "@/components/forms/SingleAnalyzeForm";
import { ImageAnalyzeForm } from "@/components/forms/ImageAnalyzeForm";
import { InterpretationCard } from "@/components/cards/InterpretationCard";
import { MtfViewCard } from "@/components/cards/MtfViewCard";
import { LevelsCard } from "@/components/cards/LevelsCard";
import { ReasonFlagsCard } from "@/components/cards/ReasonFlagsCard";
import { InterpreterContextCard } from "@/components/cards/InterpreterContextCard";
import { Card } from "@/components/ui/Card";
import type { AnalyzeResponse, InterpretWithImagesWrapper, InterpretWrapper, LlmPayload } from "@/lib/types";


type ResultUnion = AnalyzeResponse | InterpretWrapper | InterpretWithImagesWrapper | LlmPayload;

function hasInterpretation(value: ResultUnion): value is InterpretWrapper | InterpretWithImagesWrapper {
  return "interpretation" in value;
}

export default function SinglePage() {
  const [result, setResult] = useState<ResultUnion | null>(null);

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

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Single Ticker Analyzer</h1>
        <Link href="/" className="text-blue-400 underline">Back home</Link>
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
