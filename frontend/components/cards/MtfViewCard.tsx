import { Card } from "@/components/ui/Card";
import type { MtfView } from "@/lib/types";

export function MtfViewCard({ mtfView }: { mtfView: MtfView }) {
  return (
    <Card>
      <h3 className="mb-2 font-semibold">MTF View</h3>
      <div className="grid grid-cols-3 gap-2 text-sm">
        <div>Daily: {mtfView.daily}</div>
        <div>H4: {mtfView.h4}</div>
        <div>H1: {mtfView.h1}</div>
      </div>
    </Card>
  );
}
