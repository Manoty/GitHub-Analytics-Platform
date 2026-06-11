// frontend/src/components/charts/CommitTrendChart.tsx

import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from "recharts";
import type { CommitTrendPoint } from "@/types";

export function CommitTrendChart({ data }: { data: CommitTrendPoint[] }) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <AreaChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: -20 }}>
        <defs>
          <linearGradient id="commitGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%"  stopColor="#6370f1" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#6370f1" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#ffffff08" />
        <XAxis dataKey="date" tick={{ fontSize: 11, fill: "#64748b" }} tickLine={false} axisLine={false} />
        <YAxis tick={{ fontSize: 11, fill: "#64748b" }} tickLine={false} axisLine={false} />
        <Tooltip
          contentStyle={{ background: "#1a1d27", border: "1px solid #ffffff12", borderRadius: 8, fontSize: 12 }}
          labelStyle={{ color: "#94a3b8" }}
          itemStyle={{ color: "#a5b9fc" }}
        />
        <Area
          type="monotone"
          dataKey="commit_count"
          name="Commits"
          stroke="#6370f1"
          strokeWidth={2}
          fill="url(#commitGrad)"
          dot={false}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}