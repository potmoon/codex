import { Card } from "@/components/ui/Card";
import type { Interpretation } from "@/lib/types";

export function InterpretationCard({ interpretation }: { interpretation: Interpretation }) {
  return (
    <Card>
      <h3 className="mb-2 text-lg font-semibold">Interpretation Summary</h3>
      <p className="mb-3 text-sm text-slate-300">{interpretation.summary}</p>
      <div className="grid grid-cols-2 gap-2 text-sm">
        <div>Action: {interpretation.action}</div>
        <div>Setup: {interpretation.setup_type}</div>
        <div>Entry Stage: {interpretation.entry_stage}</div>
        <div>Confidence: {(interpretation.confidence * 100).toFixed(1)}%</div>
      </div>
    </Card>
  );
}
