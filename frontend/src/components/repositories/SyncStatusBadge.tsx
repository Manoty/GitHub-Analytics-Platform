// frontend/src/components/repositories/SyncStatusBadge.tsx

import { cn } from "@/lib/utils";
import type { SyncStatus } from "@/types";

const config: Record<SyncStatus, { label: string; className: string }> = {
  pending:   { label: "Pending",   className: "bg-slate-400/10 text-slate-400 border-slate-400/20" },
  syncing:   { label: "Syncing…",  className: "bg-blue-400/10 text-blue-400 border-blue-400/20 animate-pulse" },
  completed: { label: "Synced",    className: "bg-emerald-400/10 text-emerald-400 border-emerald-400/20" },
  failed:    { label: "Failed",    className: "bg-red-400/10 text-red-400 border-red-400/20" },
};

export function SyncStatusBadge({ status }: { status: SyncStatus }) {
  const { label, className } = config[status];
  return (
    <span className={cn("inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium", className)}>
      {label}
    </span>
  );
}