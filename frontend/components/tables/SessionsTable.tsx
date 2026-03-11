"use client";

import type { SessionSummary } from "@/lib/types";
import { Button } from "@/components/ui/Button";

export function SessionsTable({
  sessions,
  onOpen,
  onToggleCompare,
  selected,
}: {
  sessions: SessionSummary[];
  onOpen: (id: string) => void;
  onToggleCompare: (id: string) => void;
  selected: string[];
}) {
  return (
    <table className="w-full text-left text-sm">
      <thead className="text-slate-400">
        <tr>
          <th>Created</th><th>Type</th><th>Ticker/Label</th><th>Open</th><th>Compare</th>
        </tr>
      </thead>
      <tbody>
        {sessions.map((s) => (
          <tr key={s.id} className="border-t border-slate-800">
            <td>{new Date(s.created_at).toLocaleString()}</td>
            <td>{s.session_type}</td>
            <td>{s.ticker || s.label || "-"}</td>
            <td><Button onClick={() => onOpen(s.id)}>Open</Button></td>
            <td>
              <input
                type="checkbox"
                checked={selected.includes(s.id)}
                onChange={() => onToggleCompare(s.id)}
              />
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
