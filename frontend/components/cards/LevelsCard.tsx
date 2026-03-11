import { Card } from "@/components/ui/Card";
import type { Levels } from "@/lib/types";

export function LevelsCard({ levels }: { levels: Levels }) {
  return (
    <Card>
      <h3 className="mb-2 font-semibold">Levels</h3>
      <pre className="overflow-x-auto text-xs">{JSON.stringify(levels, null, 2)}</pre>
    </Card>
  );
}
