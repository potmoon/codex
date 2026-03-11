"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { SessionsTable } from "@/components/tables/SessionsTable";
import { CompareCard } from "@/components/cards/CompareCard";
import { compareSessions, getSession, listSessions } from "@/lib/sessions";
import type { SessionCompareResponse, SessionDetail, SessionSummary } from "@/lib/types";

export default function SessionsPage() {
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [detail, setDetail] = useState<SessionDetail | null>(null);
  const [compare, setCompare] = useState<SessionCompareResponse | null>(null);

  useEffect(() => {
    void listSessions().then(setSessions).catch(() => setSessions([]));
  }, []);

  const toggleCompare = (id: string) => {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : prev.length < 2 ? [...prev, id] : [prev[1], id],
    );
  };

  const runCompare = async () => {
    if (selected.length !== 2) return;
    setCompare(await compareSessions(selected[0], selected[1]));
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Saved Sessions</h1>
        <Link href="/" className="text-blue-400 underline">Back home</Link>
      </div>
      <Card>
        <SessionsTable
          sessions={sessions}
          selected={selected}
          onToggleCompare={toggleCompare}
          onOpen={(id) => void getSession(id).then(setDetail)}
        />
        <div className="mt-3">
          <Button onClick={runCompare} disabled={selected.length !== 2}>Compare selected</Button>
        </div>
      </Card>
      <CompareCard compare={compare} />
      {detail ? (
        <Card>
          <h3 className="mb-2 font-semibold">Session detail</h3>
          <pre className="overflow-x-auto text-xs">{JSON.stringify(detail, null, 2)}</pre>
        </Card>
      ) : null}
    </div>
  );
}
