// frontend/src/pages/ContributorsPage.tsx

import { useState } from "react";
import { useRepositories } from "@/hooks/useRepositories";
import { useContributors } from "@/hooks/useAnalytics";
import { Header } from "@/components/layout/Header";
import { ContributorTable } from "@/components/contributors/ContributorTable";
import { PageSpinner } from "@/components/ui/Spinner";
import { EmptyState } from "@/components/ui/EmptyState";
import { Users } from "lucide-react";

export default function ContributorsPage() {
  const { data: reposData } = useRepositories();
  const repos = reposData?.items ?? [];
  const [selectedId, setSelectedId] = useState<string>("");
  const repoId = selectedId || repos[0]?.id || "";

  const { data: contributors, isLoading } = useContributors(repoId);

  return (
    <div className="animate-fade-in">
      <Header
        title="Contributors"
        subtitle="Per-contributor breakdown across repositories"
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
      <div className="px-8 py-6">
        {isLoading && <PageSpinner />}
        {!isLoading && (!contributors || contributors.length === 0) && (
          <EmptyState
            icon={Users}
            title="No contributor data"
            description="Sync a repository to see contributor analytics."
          />
        )}
        {!isLoading && contributors && contributors.length > 0 && (
          <ContributorTable contributors={contributors} />
        )}
      </div>
    </div>
  );
}