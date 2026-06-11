// frontend/src/components/charts/IssueTrendChart.tsx

import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import type { IssueTrendPoint } from "@/types";

export function IssueTrendChart({ data }: { data: IssueTrendPoint[] }) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <LineChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: -20 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#ffffff08" />
        <XAxis dataKey="week" tick={{ fontSize: 11, fill: "#64748b" }} tickLine={false} axisLine={false} />
        <YAxis tick={{ fontSize: 11, fill: "#64748b" }} tickLine={false} axisLine={false} />
        <Tooltip
          contentStyle={{ background: "#1a1d27", border: "1px solid #ffffff12", borderRadius: 8, fontSize: 12 }}
          labelStyle={{ color: "#94a3b8" }}
        />
        <Legend wrapperStyle={{ fontSize: 11, color: "#64748b" }} />
        <Line type="monotone" dataKey="opened" name="Opened" stroke="#f59e0b" strokeWidth={2} dot={false} />
        <Line type="monotone" dataKey="closed" name="Closed" stroke="#34d399" strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}