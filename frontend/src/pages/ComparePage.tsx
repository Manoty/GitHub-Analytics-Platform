// frontend/src/pages/ComparePage.tsx

import { useState } from "react";
import { ArrowLeftRight } from "lucide-react";
import { useRepositories } from "@/hooks/useRepositories";
import { useComparison } from "@/hooks/useAnalytics";
import { Header } from "@/components/layout/Header";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { PageSpinner } from "@/components/ui/Spinner";
import { formatNumber, formatHours } from "@/lib/utils";
import type { RepoComparisonSide } from "@/types";

function CompareCol({ repo }: { repo: RepoComparisonSide }) {
  return (
    <div className="space-y-3">
      <h3 className="font-semibold text-white truncate">{repo.full_name ?? "—"}</h3>
      {[
        { label: "Health Score", value: repo.health_score !== null ? `${repo.health_score}` : "—" },
        { label: "Health Grade", value: repo.health_grade ? <Badge label={repo.health_grade} grade /> : "—" },
        { label: "Commits",      value: formatNumber(repo.total_commits) },
        { label: "Pull Requests", value: formatNumber(repo.total_pull_requests) },
        { label: "Merged PRs",   value: formatNumber(repo.merged_pull_requests) },
        { label: "Issues",       value: formatNumber(repo.total_issues) },
        { label: "Contributors", value: formatNumber(repo.total_contributors) },
        { label: "Stars",        value: formatNumber(repo.stars) },
        { label: "Forks",        value: formatNumber(repo.forks) },
        { label: "Avg PR Merge", value: formatHours(repo.avg_pr_merge_hours) },
        { label: "Avg Issue Close", value: formatHours(repo.avg_issue_close_hours) },
      ].map(({ label, value }) => (
        <div key={label} className="flex flex-col gap-0.5 rounded-lg bg-white/3 px-4 py-3">
          <span className="text-xs text-slate-500">{label}</span>
          <span className="text-sm font-semibold text-slate-200">{value}</span>
        </div>
      ))}
    </div>
  );
}

export default function ComparePage() {
  const { data: reposData } = useRepositories();
  const repos = reposData?.items ?? [];
  const [repoA, setRepoA] = useState("");
  const [repoB, setRepoB] = useState("");

  const idA = repoA || repos[0]?.id || "";
  const idB = repoB || repos[1]?.id || "";

  const { data: comparison, isLoading } = useComparison(idA, idB);

  const select = (value: string, setter: (v: string) => void) => (
    <select
      className="rounded-lg border border-white/10 bg-surface-100 px-3 py-2 text-sm text-slate-300 focus:outline-none"
      value={value}
      onChange={(e) => setter(e.target.value)}
    >
      {repos.map((r) => <option key={r.id} value={r.id}>{r.full_name}</option>)}
    </select>
  );

  return (
    <div className="animate-fade-in">
      <Header title="Compare Repositories" subtitle="Side-by-side metric comparison" />
      <div className="px-8 py-6 space-y-6">
        <div className="flex items-center gap-4 flex-wrap">
          {select(idA, setRepoA)}
          <ArrowLeftRight className="h-5 w-5 text-slate-500" />
          {select(idB, setRepoB)}
        </div>

        {isLoading && <PageSpinner />}
        {comparison && (
          <Card>
            <div className="grid grid-cols-2 gap-6 divide-x divide-white/8">
              <CompareCol repo={comparison.repo_a} />
              <div className="pl-6">
                <CompareCol repo={comparison.repo_b} />
              </div>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}