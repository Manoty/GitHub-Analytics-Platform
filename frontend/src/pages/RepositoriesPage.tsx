// frontend/src/pages/RepositoriesPage.tsx

import { useState } from "react";
import { Plus, RefreshCw } from "lucide-react";
import { Header } from "@/components/layout/Header";
import { Button } from "@/components/ui/Button";
import { RepositoryCard } from "@/components/repositories/RepositoryCard";
import { ConnectRepoModal } from "@/components/repositories/ConnectRepoModal";
import { PageSpinner } from "@/components/ui/Spinner";
import { EmptyState } from "@/components/ui/EmptyState";
import { GitBranch } from "lucide-react";
import { useRepositories, useSyncRepo, useDisconnectRepo } from "@/hooks/useRepositories";

export default function RepositoriesPage() {
  const [showModal, setShowModal] = useState(false);
  const { data, isLoading, refetch } = useRepositories();
  const repos = data?.items ?? [];

  return (
    <div className="animate-fade-in">
      <Header
        title="Repositories"
        subtitle={`${data?.total ?? 0} connected`}
        action={
          <div className="flex gap-2">
            <Button variant="secondary" size="sm" onClick={() => refetch()}>
              <RefreshCw className="h-3.5 w-3.5" />
            </Button>
            <Button size="sm" onClick={() => setShowModal(true)}>
              <Plus className="h-4 w-4" /> Connect
            </Button>
          </div>
        }
      />
      <div className="px-8 py-6">
        {isLoading && <PageSpinner />}
        {!isLoading && repos.length === 0 && (
          <EmptyState
            icon={GitBranch}
            title="No repositories"
            description="Connect a GitHub repository to get started."
            action={<Button onClick={() => setShowModal(true)}><Plus className="h-4 w-4" />Connect Repository</Button>}
          />
        )}
        {!isLoading && repos.length > 0 && (
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {repos.map((repo) => <RepositoryCard key={repo.id} repo={repo} />)}
          </div>
        )}
      </div>
      {showModal && <ConnectRepoModal onClose={() => setShowModal(false)} />}
    </div>
  );
}