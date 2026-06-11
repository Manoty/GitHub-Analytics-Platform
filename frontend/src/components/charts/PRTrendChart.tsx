// frontend/src/components/charts/PRTrendChart.tsx

import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import type { PRTrendPoint } from "@/types";

export function PRTrendChart({ data }: { data: PRTrendPoint[] }) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: -20 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#ffffff08" />
        <XAxis dataKey="week" tick={{ fontSize: 11, fill: "#64748b" }} tickLine={false} axisLine={false} />
        <YAxis tick={{ fontSize: 11, fill: "#64748b" }} tickLine={false} axisLine={false} />
        <Tooltip
          contentStyle={{ background: "#1a1d27", border: "1px solid #ffffff12", borderRadius: 8, fontSize: 12 }}
          labelStyle={{ color: "#94a3b8" }}
        />
        <Legend wrapperStyle={{ fontSize: 11, color: "#64748b" }} />
        <Bar dataKey="opened" name="Opened" fill="#6370f1" radius={[3, 3, 0, 0]} />
        <Bar dataKey="merged" name="Merged" fill="#34d399" radius={[3, 3, 0, 0]} />
        <Bar dataKey="closed" name="Closed" fill="#f87171" radius={[3, 3, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}