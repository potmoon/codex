import { Card } from "@/components/ui/Card";
import type { InterpreterContext } from "@/lib/types";

export function InterpreterContextCard({ context }: { context: InterpreterContext }) {
  return (
    <Card>
      <h3 className="mb-2 font-semibold">Interpreter Context</h3>
      <div className="grid grid-cols-3 gap-2 text-sm">
        <div>Mode: {context.mode}</div>
        <div>Used Images: {String(context.used_images)}</div>
        <div>Image Count: {context.image_count}</div>
      </div>
    </Card>
  );
}
