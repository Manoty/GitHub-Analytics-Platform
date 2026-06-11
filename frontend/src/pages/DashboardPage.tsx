// frontend/src/pages/DashboardPage.tsx

import { useRepositories } from "@/hooks/useRepositories";
import { Header } from "@/components/layout/Header";
import { RepositoryCard } from "@/components/repositories/RepositoryCard";
import { PageSpinner } from "@/components/ui/Spinner";
import { EmptyState } from "@/components/ui/EmptyState";
import { GitBranch } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/Button";
import { useAuth } from "@/hooks/useAuth";

export default function DashboardPage() {
  const { user } = useAuth();
  const { data, isLoading } = useRepositories();
  const repos = data?.items ?? [];

  return (
    <div className="animate-fade-in">
      <Header
        title={`Welcome back${user?.name ? `, ${user.name.split(" ")[0]}` : ""} 👋`}
        subtitle="Here's an overview of your connected repositories"
      />
      <div className="px-8 py-6">
        {isLoading && <PageSpinner />}
        {!isLoading && repos.length === 0 && (
          <EmptyState
            icon={GitBranch}
            title="No repositories connected"
            description="Connect a GitHub repository to start seeing analytics."
            action={
              <Link to="/repositories">
                <Button>Connect Repository</Button>
              </Link>
            }
          />
        )}
        {!isLoading && repos.length > 0 && (
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {repos.map((repo) => <RepositoryCard key={repo.id} repo={repo} />)}
          </div>
        )}
      </div>
    </div>
  );
}