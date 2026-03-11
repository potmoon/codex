"use client";

import { useState } from "react";
import type { BatchInterpretItem } from "@/lib/types";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";

export function WatchlistTable({ items }: { items: BatchInterpretItem[] }) {
  const [selected, setSelected] = useState<BatchInterpretItem | null>(items[0] ?? null);

  return (
    <div className="grid gap-4 lg:grid-cols-[2fr_1fr]">
      <Card>
        <table className="w-full text-left text-sm">
          <thead className="text-slate-400">
            <tr>
              <th>Ticker</th><th>Score</th><th>Priority</th><th>Action</th><th>Entry</th><th>Setup</th><th>Status</th><th>Reason</th>
            </tr>
          </thead>
          <tbody>
            {items.map((row) => (
              <tr key={row.ticker} className="cursor-pointer border-t border-slate-800 hover:bg-slate-800/40" onClick={() => setSelected(row)}>
                <td>{row.ticker}</td>
                <td>{row.ranking.score}</td>
                <td><Badge>{row.ranking.priority}</Badge></td>
                <td>{row.interpretation.action}</td>
                <td>{row.interpretation.entry_stage}</td>
                <td>{row.interpretation.setup_type}</td>
                <td>{row.status}</td>
                <td className="max-w-[240px] truncate">{row.ranking.reason}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>

      <Card>
        {!selected ? <p>No row selected.</p> : (
          <div className="space-y-3">
            <h3 className="font-semibold">{selected.ticker} details</h3>
            <p className="text-sm">{selected.interpretation.summary}</p>
            <pre className="overflow-x-auto text-xs">{JSON.stringify(selected.facts.mtf_view, null, 2)}</pre>
            <pre className="overflow-x-auto text-xs">{JSON.stringify(selected.facts.levels, null, 2)}</pre>
            <pre className="overflow-x-auto text-xs">{JSON.stringify(selected.facts.reason_flags, null, 2)}</pre>
            <details>
              <summary className="cursor-pointer text-sm">Raw JSON</summary>
              <pre className="overflow-x-auto text-xs">{JSON.stringify(selected, null, 2)}</pre>
            </details>
          </div>
        )}
      </Card>
    </div>
  );
}
