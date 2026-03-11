import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

export function Badge({ children, className }: { children: ReactNode; className?: string }) {
  return <span className={cn("rounded bg-slate-700 px-2 py-1 text-xs", className)}>{children}</span>;
}
