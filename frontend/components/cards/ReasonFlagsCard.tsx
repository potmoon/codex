import { Card } from "@/components/ui/Card";
import type { ReasonFlags } from "@/lib/types";

export function ReasonFlagsCard({ reasonFlags }: { reasonFlags: ReasonFlags }) {
  return (
    <Card>
      <h3 className="mb-2 font-semibold">Reason Flags</h3>
      <pre className="overflow-x-auto text-xs">{JSON.stringify(reasonFlags, null, 2)}</pre>
    </Card>
  );
}
