// frontend/src/components/repositories/ConnectRepoModal.tsx

import { useState } from "react";
import { Search, GitBranch, Star, Lock } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { PageSpinner } from "@/components/ui/Spinner";
import { useGitHubRepos, useConnectRepo } from "@/hooks/useRepositories";
import { formatNumber } from "@/lib/utils";

interface Props { onClose: () => void }

export function ConnectRepoModal({ onClose }: Props) {
  const [search, setSearch] = useState("");
  const { data: repos, isLoading } = useGitHubRepos();
  const connect = useConnectRepo();

  const filtered = repos?.filter((r) =>
    r.full_name.toLowerCase().includes(search.toLowerCase())
  );

  const handleConnect = async (full_name: string) => {
    await connect.mutateAsync(full_name);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="w-full max-w-lg rounded-2xl border border-white/10 bg-surface-50 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-white/8 px-6 py-4">
          <h2 className="font-semibold text-white">Connect a Repository</h2>
          <button onClick={onClose} className="text-slate-500 hover:text-slate-300 text-xl leading-none">✕</button>
        </div>

        {/* Search */}
        <div className="px-6 py-3 border-b border-white/8">
          <div className="flex items-center gap-2 rounded-lg border border-white/10 bg-surface-100 px-3 py-2">
            <Search className="h-4 w-4 text-slate-500 flex-shrink-0" />
            <input
              className="flex-1 bg-transparent text-sm text-white placeholder:text-slate-600 focus:outline-none"
              placeholder="Search repositories…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              autoFocus
            />
          </div>
        </div>

        {/* List */}
        <div className="max-h-96 overflow-y-auto divide-y divide-white/5">
          {isLoading && <div className="py-10"><PageSpinner /></div>}
          {filtered?.map((repo) => (
            <div key={repo.github_id} className="flex items-center justify-between gap-4 px-6 py-3 hover:bg-white/3">
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-1.5">
                  {repo.is_private ? <Lock className="h-3.5 w-3.5 text-slate-500" /> : <GitBranch className="h-3.5 w-3.5 text-slate-500" />}
                  <span className="text-sm font-medium text-slate-200 truncate">{repo.full_name}</span>
                </div>
                {repo.description && (
                  <p className="mt-0.5 text-xs text-slate-600 truncate">{repo.description}</p>
                )}
                <div className="mt-1 flex items-center gap-3 text-xs text-slate-600">
                  {repo.language && <span>{repo.language}</span>}
                  <span className="flex items-center gap-1"><Star className="h-3 w-3" />{formatNumber(repo.stars_count)}</span>
                </div>
              </div>
              <Button
                size="sm"
                onClick={() => handleConnect(repo.full_name)}
                loading={connect.isPending}
              >
                Connect
              </Button>
            </div>
          ))}
          {!isLoading && filtered?.length === 0 && (
            <p className="py-10 text-center text-sm text-slate-600">No repositories found</p>
          )}
        </div>
      </div>
    </div>
  );
}