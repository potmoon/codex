import { Card } from "@/components/ui/Card";
import type { SessionCompareResponse } from "@/lib/types";

export function CompareCard({ compare }: { compare: SessionCompareResponse | null }) {
  if (!compare) return null;
  return (
    <Card>
      <h3 className="mb-2 font-semibold">Comparison</h3>
      <pre className="overflow-x-auto text-xs">{JSON.stringify(compare, null, 2)}</pre>
    </Card>
  );
}
