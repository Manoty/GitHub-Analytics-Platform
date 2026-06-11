// frontend/src/components/repositories/RepositoryCard.tsx

import { Star, GitFork, Circle } from "lucide-react";
import { Link } from "react-router-dom";
import { Card } from "@/components/ui/Card";
import { SyncStatusBadge } from "./SyncStatusBadge";
import { formatNumber, formatDate } from "@/lib/utils";
import type { Repository } from "@/types";

export function RepositoryCard({ repo }: { repo: Repository }) {
  return (
    <Link to={`/repositories/${repo.id}`}>
      <Card className="hover:border-brand-500/40 hover:bg-surface-100 transition-all cursor-pointer">
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="font-semibold text-white truncate">{repo.full_name}</h3>
              {repo.is_private && (
                <span className="text-xs text-slate-600 border border-white/10 rounded px-1.5 py-0.5">Private</span>
              )}
            </div>
            {repo.description && (
              <p className="mt-1 text-sm text-slate-500 line-clamp-2">{repo.description}</p>
            )}
          </div>
          <SyncStatusBadge status={repo.sync_status} />
        </div>

        <div className="mt-4 flex items-center gap-4 text-xs text-slate-600 flex-wrap">
          {repo.language && (
            <span className="flex items-center gap-1.5">
              <Circle className="h-2.5 w-2.5 fill-brand-400 text-brand-400" />
              {repo.language}
            </span>
          )}
          <span className="flex items-center gap-1">
            <Star className="h-3.5 w-3.5" />
            {formatNumber(repo.stars_count)}
          </span>
          <span className="flex items-center gap-1">
            <GitFork className="h-3.5 w-3.5" />
            {formatNumber(repo.forks_count)}
          </span>
          <span className="ml-auto">Updated {formatDate(repo.github_updated_at)}</span>
        </div>
      </Card>
    </Link>
  );
}