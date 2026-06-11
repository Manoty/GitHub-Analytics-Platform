// frontend/src/components/charts/LanguageChart.tsx

import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts";
import type { LanguagePoint } from "@/types";

const COLORS = ["#6370f1","#34d399","#f59e0b","#f87171","#a78bfa","#38bdf8","#fb923c","#e879f9"];

export function LanguageChart({ data }: { data: LanguagePoint[] }) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <PieChart>
        <Pie
          data={data}
          dataKey="percentage"
          nameKey="language"
          cx="50%"
          cy="50%"
          outerRadius={80}
          strokeWidth={0}
        >
          {data.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{ background: "#1a1d27", border: "1px solid #ffffff12", borderRadius: 8, fontSize: 12 }}
          formatter={(val: number) => `${val.toFixed(1)}%`}
        />
        <Legend wrapperStyle={{ fontSize: 11, color: "#64748b" }} />
      </PieChart>
    </ResponsiveContainer>
  );
}