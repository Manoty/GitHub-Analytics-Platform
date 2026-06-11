// frontend/src/hooks/useRepositories.ts

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { reposApi } from "@/lib/api";
import type { Repository, RepositoryListResponse, GitHubRepoPreview } from "@/types";

export function useRepositories() {
  return useQuery<RepositoryListResponse>({
    queryKey: ["repositories"],
    queryFn: async () => (await reposApi.list()).data,
  });
}

export function useRepository(id: string) {
  return useQuery<Repository>({
    queryKey: ["repository", id],
    queryFn: async () => (await reposApi.get(id)).data,
    enabled: !!id,
  });
}

export function useGitHubRepos() {
  return useQuery<GitHubRepoPreview[]>({
    queryKey: ["github-repos"],
    queryFn: async () => (await reposApi.listGitHub()).data,
  });
}

export function useConnectRepo() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (full_name: string) => reposApi.connect(full_name),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["repositories"] }),
  });
}

export function useSyncRepo() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => reposApi.sync(id),
    onSuccess: (_, id) => {
      qc.invalidateQueries({ queryKey: ["repository", id] });
      qc.invalidateQueries({ queryKey: ["repositories"] });
    },
  });
}

export function useDisconnectRepo() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => reposApi.disconnect(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["repositories"] }),
  });
}