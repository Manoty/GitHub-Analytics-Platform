// frontend/src/components/ui/StatCard.tsx

import { cn, formatNumber } from "@/lib/utils";
import { Card } from "./Card";
import type { LucideIcon } from "lucide-react";

interface StatCardProps {
  label: string;
  value: number | string;
  icon: LucideIcon;
  trend?: { value: number; direction: string };
  className?: string;
  iconColor?: string;
}

export function StatCard({ label, value, icon: Icon, trend, className, iconColor = "text-brand-400" }: StatCardProps) {
  return (
    <Card className={cn("flex flex-col gap-3", className)}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium uppercase tracking-wider text-slate-500">{label}</span>
        <Icon className={cn("h-4 w-4", iconColor)} />
      </div>
      <div className="text-3xl font-bold text-white">
        {typeof value === "number" ? formatNumber(value) : value}
      </div>
      {trend && (
        <div className={cn(
          "text-xs font-medium",
          trend.direction === "increasing" ? "text-emerald-400" :
          trend.direction === "declining"  ? "text-red-400" : "text-slate-500"
        )}>
          {trend.value > 0 ? "+" : ""}{trend.value}% vs prior 30d
        </div>
      )}
    </Card>
  );
}