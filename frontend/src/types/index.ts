// frontend/src/types/index.ts

export interface User {
  id: string;
  github_id: number;
  username: string;
  email: string | null;
  name: string | null;
  avatar_url: string | null;
  bio: string | null;
  company: string | null;
  location: string | null;
  github_url: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export type SyncStatus = "pending" | "syncing" | "completed" | "failed";

export interface Repository {
  id: string;
  github_id: number;
  owner_id: string;
  full_name: string;
  name: string;
  description: string | null;
  language: string | null;
  topics: string[];
  languages_data: Record<string, number>;
  stars_count: number;
  forks_count: number;
  watchers_count: number;
  open_issues_count: number;
  is_private: boolean;
  is_fork: boolean;
  is_archived: boolean;
  is_connected: boolean;
  sync_status: SyncStatus;
  last_synced_at: string | null;
  github_created_at: string | null;
  github_updated_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface GitHubRepoPreview {
  github_id: number;
  full_name: string;
  name: string;
  description: string | null;
  language: string | null;
  stars_count: number;
  forks_count: number;
  is_private: boolean;
  github_updated_at: string | null;
}

export interface RepositoryListResponse {
  items: Repository[];
  total: number;
}

// ── Analytics ─────────────────────────────────────

export interface RepositoryOverview {
  total_commits: number;
  total_pull_requests: number;
  merged_pull_requests: number;
  total_issues: number;
  closed_issues: number;
  total_contributors: number;
  avg_pr_merge_hours: number | null;
  avg_issue_close_hours: number | null;
  health_score: number | null;
  health_grade: string | null;
  health_insights: string[];
}

export interface CommitTrendPoint {
  date: string | null;
  commit_count: number;
  author_count: number;
}

export interface PRTrendPoint {
  week: string | null;
  opened: number;
  merged: number;
  closed: number;
}

export interface IssueTrendPoint {
  week: string | null;
  opened: number;
  closed: number;
}

export interface HeatmapPoint {
  date: string;
  count: number;
}

export interface ContributorStat {
  github_login: string;
  avatar_url: string | null;
  contributions_count: number;
  commit_count: number;
  pr_count: number;
  issue_count: number;
  total_additions: number;
  total_deletions: number;
  last_commit_at: string | null;
}

export interface ProductivityMetrics {
  period_days: number;
  commits: number;
  prs_merged: number;
  issues_closed: number;
  active_contributors: number;
  avg_pr_merge_hours: number | null;
  avg_issue_close_hours: number | null;
  deployment_frequency_per_week: number;
  contributor_velocity: number;
}

export interface TrendSignal {
  current_30d: number;
  previous_30d: number;
  pct_change: number | null;
  direction: "increasing" | "declining" | "stable" | "neutral";
}

export interface TrendSignals {
  commits: TrendSignal;
  pull_requests: TrendSignal;
}

export interface LanguagePoint {
  language: string;
  bytes: number;
  percentage: number;
}

export interface RepoComparisonSide {
  id: string;
  full_name: string | null;
  stars: number;
  forks: number;
  total_commits: number;
  total_pull_requests: number;
  merged_pull_requests: number;
  total_issues: number;
  closed_issues: number;
  total_contributors: number;
  avg_pr_merge_hours: number | null;
  avg_issue_close_hours: number | null;
  health_score: number | null;
  health_grade: string | null;
  health_insights: string[];
}

export interface RepositoryComparison {
  repo_a: RepoComparisonSide;
  repo_b: RepoComparisonSide;
}