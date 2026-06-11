// frontend/src/pages/HealthPage.tsx

import { useState } from "react";
import { useRepositories } from "@/hooks/useRepositories";
import { useOverview } from "@/hooks/useAnalytics";
import { Header } from "@/components/layout/Header";
import { HealthScoreCard } from "@/components/health/HealthScoreCard";
import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { PageSpinner } from "@/components/ui/Spinner";
import { formatHours } from "@/lib/utils";

function ScoreBar({ label, score }: { label: string; score: number }) {
  const color =
    score >= 80 ? "bg-emerald-500" :
    score >= 60 ? "bg-blue-500" :
    score >= 40 ? "bg-amber-500" : "bg-red-500";

  return (
    <div className="space-y-1.5">
      <div className="flex justify-between text-xs">
        <span className="text-slate-400">{label}</span>
        <span className="text-slate-300 font-medium">{score.toFixed(0)}</span>
      </div>
      <div className="h-2 rounded-full bg-white/5 overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ${color}`}
          style={{ width: `${score}%` }}
        />
      </div>
    </div>
  );
}

export default function HealthPage() {
  const { data: reposData } = useRepositories();
  const repos = reposData?.items ?? [];
  const [selectedId, setSelectedId] = useState<string>("");
  const repoId = selectedId || repos[0]?.id || "";

  const { data: overview, isLoading } = useOverview(repoId);

  return (
    <div className="animate-fade-in">
      <Header
        title="Repository Health"
        subtitle="Health scores and component breakdowns"
        action={
          repos.length > 0 ? (
            <select
              className="rounded-lg border border-white/10 bg-surface-100 px-3 py-2 text-sm text-slate-300 focus:outline-none"
              value={repoId}
              onChange={(e) => setSelectedId(e.target.value)}
            >
              {repos.map((r) => (
                <option key={r.id} value={r.id}>{r.full_name}</option>
              ))}
            </select>
          ) : null
        }
      />
      <div className="px-8 py-6 grid gap-6 lg:grid-cols-2">
        {isLoading && <PageSpinner />}
        {overview && (
          <>
            <HealthScoreCard overview={overview} />
            <Card>
              <CardHeader><CardTitle>Component Scores</CardTitle></CardHeader>
              <div className="space-y-5 mt-2">
                <ScoreBar label="Commit Frequency (30%)" score={0} />
                <ScoreBar label="Issue Resolution (25%)" score={0} />
                <ScoreBar label="PR Merge Speed (25%)" score={0} />
                <ScoreBar label="Contributor Diversity (20%)" score={0} />
              </div>
              <div className="mt-6 grid grid-cols-2 gap-4 pt-5 border-t border-white/8 text-sm">
                <div>
                  <span className="text-slate-500">Avg PR Merge Time</span>
                  <p className="text-white font-semibold mt-0.5">{formatHours(overview.avg_pr_merge_hours)}</p>
                </div>
                <div>
                  <span className="text-slate-500">Avg Issue Close Time</span>
                  <p className="text-white font-semibold mt-0.5">{formatHours(overview.avg_issue_close_hours)}</p>
                </div>
                <div>
                  <span className="text-slate-500">Total Contributors</span>
                  <p className="text-white font-semibold mt-0.5">{overview.total_contributors}</p>
                </div>
                <div>
                  <span className="text-slate-500">Merged PRs</span>
                  <p className="text-white font-semibold mt-0.5">{overview.merged_pull_requests}</p>
                </div>
              </div>
            </Card>
          </>
        )}
      </div>
    </div>
  );
}