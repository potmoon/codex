import Link from "next/link";
import { Card } from "@/components/ui/Card";

export default function HomePage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-semibold">Chart Analyzer Dashboard</h1>
      <p className="text-slate-300">Internal operator console for deterministic analysis and interpretation workflows.</p>
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <h2 className="mb-2 text-lg font-semibold">Single Ticker Analyzer</h2>
          <p className="mb-3 text-sm text-slate-300">Run Analyze, Interpret, and Interpret with Images for one ticker.</p>
          <Link className="text-blue-400 underline" href="/single">Open single analyzer</Link>
        </Card>
        <Card>
          <h2 className="mb-2 text-lg font-semibold">Watchlist Analyzer</h2>
          <p className="mb-3 text-sm text-slate-300">Submit batch payload and review ranked watchlist output.</p>
          <Link className="text-blue-400 underline" href="/watchlist">Open watchlist analyzer</Link>
        </Card>
        <Card>
          <h2 className="mb-2 text-lg font-semibold">Sessions</h2>
          <p className="mb-3 text-sm text-slate-300">Browse, reopen, and compare saved runs.</p>
          <Link className="text-blue-400 underline" href="/sessions">Open sessions</Link>
        </Card>
      </div>
    </div>
  );
}
