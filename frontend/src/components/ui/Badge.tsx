// frontend/src/components/ui/Badge.tsx

import { cn, gradeBg } from "@/lib/utils";

interface BadgeProps {
  label: string;
  grade?: boolean;
  className?: string;
}

export function Badge({ label, grade = false, className }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium",
        grade ? gradeBg(label) : "bg-white/5 text-slate-400 border-white/10",
        className
      )}
    >
      {label}
    </span>
  );
}