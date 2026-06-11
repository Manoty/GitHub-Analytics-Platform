// frontend/src/components/charts/ContributionHeatmap.tsx

import { useMemo } from "react";
import type { HeatmapPoint } from "@/types";
import { cn } from "@/lib/utils";

interface Props { data: HeatmapPoint[] }

function intensityClass(count: number): string {
  if (count === 0) return "bg-white/5";
  if (count <= 2)  return "bg-brand-900";
  if (count <= 5)  return "bg-brand-700";
  if (count <= 10) return "bg-brand-500";
  return "bg-brand-300";
}

export function ContributionHeatmap({ data }: Props) {
  const byDate = useMemo(() => {
    const map: Record<string, number> = {};
    data.forEach((d) => { map[d.date] = d.count; });
    return map;
  }, [data]);

  // Build last 52 weeks grid
  const weeks = useMemo(() => {
    const grid: { date: string; count: number }[][] = [];
    const today = new Date();
    const start = new Date(today);
    start.setDate(start.getDate() - 364);

    let current = new Date(start);
    // Align to Sunday
    current.setDate(current.getDate() - current.getDay());

    while (current <= today) {
      const week: { date: string; count: number }[] = [];
      for (let d = 0; d < 7; d++) {
        const iso = current.toISOString().slice(0, 10);
        week.push({ date: iso, count: byDate[iso] ?? 0 });
        current.setDate(current.getDate() + 1);
      }
      grid.push(week);
    }
    return grid;
  }, [byDate]);

  return (
    <div className="overflow-x-auto">
      <div className="flex gap-1">
        {weeks.map((week, wi) => (
          <div key={wi} className="flex flex-col gap-1">
            {week.map((day) => (
              <div
                key={day.date}
                title={`${day.date}: ${day.count} commits`}
                className={cn("h-3 w-3 rounded-sm transition-colors", intensityClass(day.count))}
              />
            ))}
          </div>
        ))}
      </div>
      <div className="mt-2 flex items-center gap-1 text-xs text-slate-600">
        <span>Less</span>
        {[0, 2, 5, 10, 15].map((n) => (
          <div key={n} className={cn("h-3 w-3 rounded-sm", intensityClass(n))} />
        ))}
        <span>More</span>
      </div>
    </div>
  );
}