// frontend/src/components/health/HealthScoreCard.tsx

import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { HealthGauge } from "./HealthGauge";
import type { RepositoryOverview } from "@/types";

export function HealthScoreCard({ overview }: { overview: RepositoryOverview }) {
  const score = overview.health_score ?? 0;
  const grade = overview.health_grade ?? "—";

  return (
    <Card>
      <CardHeader>
        <CardTitle>Health Score</CardTitle>
        <Badge label={grade} grade />
      </CardHeader>
      <div className="flex flex-col items-center gap-6">
        <HealthGauge score={score} />
        {overview.health_insights.length > 0 && (
          <ul className="w-full space-y-2">
            {overview.health_insights.map((insight, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-slate-400">
                <span className="mt-1.5 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-brand-400" />
                {insight}
              </li>
            ))}
          </ul>
        )}
      </div>
    </Card>
  );
}