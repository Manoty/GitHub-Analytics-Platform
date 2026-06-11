# backend/app/schemas/analytics.py

from __future__ import annotations
from pydantic import BaseModel
from typing import Any


class RepositoryOverview(BaseModel):
    total_commits: int
    total_pull_requests: int
    merged_pull_requests: int
    total_issues: int
    closed_issues: int
    total_contributors: int
    avg_pr_merge_hours: float | None
    avg_issue_close_hours: float | None
    health_score: float | None
    health_grade: str | None
    health_insights: list[str]


class CommitTrendPoint(BaseModel):
    date: str | None
    commit_count: int
    author_count: int


class PRTrendPoint(BaseModel):
    week: str | None
    opened: int
    merged: int
    closed: int


class IssueTrendPoint(BaseModel):
    week: str | None
    opened: int
    closed: int


class HeatmapPoint(BaseModel):
    date: str
    count: int


class ContributorStat(BaseModel):
    github_login: str
    avatar_url: str | None
    contributions_count: int
    commit_count: int
    pr_count: int
    issue_count: int
    total_additions: int
    total_deletions: int
    last_commit_at: str | None


class ProductivityMetrics(BaseModel):
    period_days: int
    commits: int
    prs_merged: int
    issues_closed: int
    active_contributors: int
    avg_pr_merge_hours: float | None
    avg_issue_close_hours: float | None
    deployment_frequency_per_week: float
    contributor_velocity: float


class TrendSignal(BaseModel):
    current_30d: int
    previous_30d: int
    pct_change: float | None
    direction: str


class TrendSignals(BaseModel):
    commits: TrendSignal
    pull_requests: TrendSignal


class LanguagePoint(BaseModel):
    language: str
    bytes: int
    percentage: float


class RepoComparisonSide(BaseModel):
    id: str
    full_name: str | None
    stars: int
    forks: int
    total_commits: int
    total_pull_requests: int
    merged_pull_requests: int
    total_issues: int
    closed_issues: int
    total_contributors: int
    avg_pr_merge_hours: float | None
    avg_issue_close_hours: float | None
    health_score: float | None
    health_grade: str | None
    health_insights: list[str]


class RepositoryComparison(BaseModel):
    repo_a: RepoComparisonSide
    repo_b: RepoComparisonSide