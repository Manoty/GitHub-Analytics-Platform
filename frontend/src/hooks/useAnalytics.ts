// frontend/src/hooks/useAnalytics.ts

import { useQuery } from "@tanstack/react-query";
import { analyticsApi } from "@/lib/api";
import type {
  RepositoryOverview, CommitTrendPoint, PRTrendPoint,
  IssueTrendPoint, HeatmapPoint, ContributorStat,
  ProductivityMetrics, TrendSignals, LanguagePoint,
  RepositoryComparison,
} from "@/types";

const q = (key: unknown[], fn: () => Promise<any>, enabled = true) => ({
  queryKey: key,
  queryFn: async () => (await fn()).data,
  enabled,
});

export const useOverview = (repoId: string) =>
  useQuery<RepositoryOverview>(q(["overview", repoId], () => analyticsApi.overview(repoId), !!repoId));

export const useCommitTrends = (repoId: string, days = 90) =>
  useQuery<CommitTrendPoint[]>(q(["commit-trends", repoId, days], () => analyticsApi.commitTrends(repoId, days), !!repoId));

export const usePRTrends = (repoId: string, days = 90) =>
  useQuery<PRTrendPoint[]>(q(["pr-trends", repoId, days], () => analyticsApi.prTrends(repoId, days), !!repoId));

export const useIssueTrends = (repoId: string, days = 90) =>
  useQuery<IssueTrendPoint[]>(q(["issue-trends", repoId, days], () => analyticsApi.issueTrends(repoId, days), !!repoId));

export const useHeatmap = (repoId: string) =>
  useQuery<HeatmapPoint[]>(q(["heatmap", repoId], () => analyticsApi.heatmap(repoId), !!repoId));

export const useContributors = (repoId: string) =>
  useQuery<ContributorStat[]>(q(["contributors", repoId], () => analyticsApi.contributors(repoId), !!repoId));

export const useProductivity = (repoId: string, days = 30) =>
  useQuery<ProductivityMetrics>(q(["productivity", repoId, days], () => analyticsApi.productivity(repoId, days), !!repoId));

export const useTrendSignals = (repoId: string) =>
  useQuery<TrendSignals>(q(["trends", repoId], () => analyticsApi.trends(repoId), !!repoId));

export const useLanguages = (repoId: string) =>
  useQuery<LanguagePoint[]>(q(["languages", repoId], () => analyticsApi.languages(repoId), !!repoId));

export const useComparison = (repoA: string, repoB: string) =>
  useQuery<RepositoryComparison>(q(
    ["comparison", repoA, repoB],
    () => analyticsApi.compare(repoA, repoB),
    !!(repoA && repoB && repoA !== repoB),
  ));