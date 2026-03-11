"use client";

import { useMemo, useState } from "react";
import { batchInterpret } from "@/lib/api";
import { csvRowsToBatchRequest, parseTickerCsv } from "@/lib/csv";
import type { BatchInterpretResponse, CsvTickerRow } from "@/lib/types";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Spinner } from "@/components/ui/Spinner";
import { Textarea } from "@/components/ui/Textarea";

const SAMPLE_CSV = "ticker\nWIMI\nFSCO\nBATL";

export function CsvWatchlistForm({ onResult }: { onResult: (data: BatchInterpretResponse) => void }) {
  const [rawCsv, setRawCsv] = useState(SAMPLE_CSV);
  const [rows, setRows] = useState<CsvTickerRow[]>([]);
  const [errors, setErrors] = useState<string[]>([]);
  const [basePrice, setBasePrice] = useState("10");
  const [step, setStep] = useState("0.5");
  const [loading, setLoading] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const generatedPayload = useMemo(() => {
    const parsedBase = Number(basePrice);
    const parsedStep = Number(step);
    if (!Number.isFinite(parsedBase) || !Number.isFinite(parsedStep)) {
      return null;
    }
    return csvRowsToBatchRequest(rows, parsedBase, parsedStep);
  }, [rows, basePrice, step]);

  const handleFile = async (file: File) => {
    const text = await file.text();
    setRawCsv(text);
    const result = parseTickerCsv(text);
    setRows(result.rows);
    setErrors(result.errors);
  };

  const parseNow = () => {
    const result = parseTickerCsv(rawCsv);
    setRows(result.rows);
    setErrors(result.errors);
  };

  const submit = async () => {
    setSubmitError(null);
    if (!generatedPayload) {
      setSubmitError("Unable to build batch payload from CSV. Check base/step values.");
      return;
    }
    if (rows.length === 0) {
      setSubmitError("No valid ticker rows to submit.");
      return;
    }

    setLoading(true);
    try {
      const data = await batchInterpret(generatedPayload);
      onResult(data);
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : "Unexpected error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="space-y-4">
      <div className="space-y-2">
        <label className="text-sm text-slate-300">Upload CSV</label>
        <input
          type="file"
          accept=".csv,text/csv"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) {
              void handleFile(file);
            }
          }}
        />
      </div>

      <Textarea rows={8} value={rawCsv} onChange={(e) => setRawCsv(e.target.value)} />
      <Button onClick={parseNow}>Parse CSV</Button>

      <Card>
        <h3 className="mb-2 font-semibold">CSV Mapping (temporary mock candles)</h3>
        <p className="mb-2 text-xs text-slate-400">
          Real market-data enrichment is not automated yet. For now, CSV rows are converted into placeholder candles for development/testing.
        </p>
        <div className="grid gap-2 md:grid-cols-2">
          <Input value={basePrice} onChange={(e) => setBasePrice(e.target.value)} placeholder="Base price" />
          <Input value={step} onChange={(e) => setStep(e.target.value)} placeholder="Price step per row" />
        </div>
      </Card>

      {errors.length > 0 ? (
        <Card>
          <h4 className="mb-1 text-sm font-semibold text-red-300">CSV validation errors</h4>
          <ul className="list-disc pl-5 text-sm text-red-300">
            {errors.map((err) => (
              <li key={err}>{err}</li>
            ))}
          </ul>
        </Card>
      ) : null}

      <Card>
        <h4 className="mb-2 font-semibold">Parsed rows preview</h4>
        {rows.length === 0 ? (
          <p className="text-sm text-slate-400">No parsed rows yet.</p>
        ) : (
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="text-slate-400">
                <th>#</th>
                <th>Ticker</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row, idx) => (
                <tr key={`${row.ticker}-${idx}`} className="border-t border-slate-800">
                  <td>{idx + 1}</td>
                  <td>{row.ticker}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>

      <Card>
        <details>
          <summary className="cursor-pointer text-sm font-medium">Generated batch JSON preview</summary>
          <pre className="overflow-x-auto text-xs">{JSON.stringify(generatedPayload, null, 2)}</pre>
        </details>
      </Card>

      <div className="flex items-center gap-2">
        <Button onClick={submit} disabled={loading || rows.length === 0}>Run Watchlist Ranking from CSV</Button>
        {loading ? <Spinner /> : null}
      </div>
      {submitError ? <p className="text-sm text-red-400">{submitError}</p> : null}
    </section>
  );
}
