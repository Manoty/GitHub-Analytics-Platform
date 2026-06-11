// frontend/src/pages/RepositoryDetailPage.tsx

import { useParams } from "react-router-dom";
import { RefreshCw, GitCommit, GitPullRequest, AlertCircle, Users } from "lucide-react";
import { Header } from "@/components/layout/Header";
import { Button } from "@/components/ui/Button";
import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { StatCard } from "@/components/ui/StatCard";
import { PageSpinner } from "@/components/ui/Spinner";
import { ErrorState } from "@/components/ui/ErrorState";
import { CommitTrendChart } from "@/components/charts/CommitTrendChart";
import { PRTrendChart } from "@/components/charts/PRTrendChart";
import { IssueTrendChart } from "@/components/charts/IssueTrendChart";
import { LanguageChart } from "@/components/charts/LanguageChart";
import { ContributionHeatmap } from "@/components/charts/ContributionHeatmap";
import { HealthScoreCard } from "@/components/health/HealthScoreCard";
import { useRepository, useSyncRepo } from "@/hooks/useRepositories";
import { useOverview, useCommitTrends, usePRTrends, useIssueTrends, useHeatmap, useLanguages, useTrendSignals } from "@/hooks/useAnalytics";
import { formatHours, directionColor } from "@/lib/utils";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

function TrendArrow({ direction }: { direction: string }) {
  if (direction === "increasing") return <TrendingUp className="h-4 w-4 text-emerald-400" />;
  if (direction === "declining")  return <TrendingDown className="h-4 w-4 text-red-400" />;
  return <Minus className="h-4 w-4 text-slate-500" />;
}

export default function RepositoryDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: repo, isLoading: repoLoading } = useRepository(id!);
  const { data: overview, isLoading: overviewLoading } = useOverview(id!);
  const { data: commitTrends } = useCommitTrends(id!);
  const { data: prTrends } = usePRTrends(id!);
  const { data: issueTrends } = useIssueTrends(id!);
  const { data: heatmap } = useHeatmap(id!);
  const { data: languages } = useLanguages(id!);
  const { data: trends } = useTrendSignals(id!);
  const sync = useSyncRepo();

  if (repoLoading || overviewLoading) return <PageSpinner />;
  if (!repo || !overview) return <ErrorState />;

  return (
    <div className="animate-fade-in">
      <Header
        title={repo.name}
        subtitle={repo.full_name}
        action={
          <Button
            size="sm"
            variant="secondary"
            onClick={() => sync.mutate(repo.id)}
            loading={sync.isPending}
          >
            <RefreshCw className="h-3.5 w-3.5" /> Sync
          </Button>
        }
      />

      <div className="px-8 py-6 space-y-6">
        {/* Stats row */}
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <StatCard
            label="Commits"
            value={overview.total_commits}
            icon={GitCommit}
            trend={trends ? { value: trends.commits.pct_change ?? 0, direction: trends.commits.direction } : undefined}
          />
          <StatCard
            label="Pull Requests"
            value={overview.total_pull_requests}
            icon={GitPullRequest}
            trend={trends ? { value: trends.pull_requests.pct_change ?? 0, direction: trends.pull_requests.direction } : undefined}
          />
          <StatCard label="Issues" value={overview.total_issues} icon={AlertCircle} iconColor="text-amber-400" />
          <StatCard label="Contributors" value={overview.total_contributors} icon={Users} iconColor="text-emerald-400" />
        </div>

        {/* Health + trend signals */}
        <div className="grid gap-4 lg:grid-cols-3">
          <HealthScoreCard overview={overview} />

          <Card className="lg:col-span-2">
            <CardHeader><CardTitle>Trend Signals — last 30 days vs prior 30</CardTitle></CardHeader>
            {trends && (
              <div className="grid grid-cols-2 gap-6 mt-2">
                {(["commits", "pull_requests"] as const).map((key) => {
                  const t = trends[key];
                  return (
                    <div key={key} className="flex flex-col gap-1">
                      <span className="text-xs text-slate-500 capitalize">{key.replace("_", " ")}</span>
                      <div className="flex items-center gap-2">
                        <TrendArrow direction={t.direction} />
                        <span className={`text-lg font-semibold ${directionColor(t.direction)}`}>
                          {t.pct_change !== null ? `${t.pct_change > 0 ? "+" : ""}${t.pct_change}%` : "—"}
                        </span>
                      </div>
                      <span className="text-xs text-slate-600">{t.current_30d} this period · {t.previous_30d} prior</span>
                    </div>
                  );
                })}
              </div>
            )}

            <div className="mt-6 grid grid-cols-2 gap-4 pt-4 border-t border-white/8">
              <div>
                <span className="text-xs text-slate-500">Avg PR Merge Time</span>
                <p className="text-xl font-semibold text-white mt-1">{formatHours(overview.avg_pr_merge_hours)}</p>
              </div>
              <div>
                <span className="text-xs text-slate-500">Avg Issue Close Time</span>
                <p className="text-xl font-semibold text-white mt-1">{formatHours(overview.avg_issue_close_hours)}</p>
              </div>
            </div>
          </Card>
        </div>

        {/* Charts */}
        <div className="grid gap-4 lg:grid-cols-2">
          <Card>
            <CardHeader><CardTitle>Commit Activity — last 90 days</CardTitle></CardHeader>
            {commitTrends && <CommitTrendChart data={commitTrends} />}
          </Card>
          <Card>
            <CardHeader><CardTitle>Pull Request Trends</CardTitle></CardHeader>
            {prTrends && <PRTrendChart data={prTrends} />}
          </Card>
          <Card>
            <CardHeader><CardTitle>Issue Trends</CardTitle></CardHeader>
            {issueTrends && <IssueTrendChart data={issueTrends} />}
          </Card>
          <Card>
            <CardHeader><CardTitle>Language Distribution</CardTitle></CardHeader>
            {languages && languages.length > 0 ? <LanguageChart data={languages} /> : (
              <p className="text-sm text-slate-600 py-8 text-center">No language data</p>
            )}
          </Card>
        </div>

        {/* Heatmap */}
        <Card>
          <CardHeader><CardTitle>Contribution Heatmap — last 365 days</CardTitle></CardHeader>
          {heatmap && <ContributionHeatmap data={heatmap} />}
        </Card>
      </div>
    </div>
  );
}