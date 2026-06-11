# backend/app/api/v1/endpoints/analytics.py

import uuid
from fastapi import APIRouter, HTTPException, Query
from app.api.deps import CurrentUser, DBSession
from app.services.analytics_service import AnalyticsService
from app.services.auth_service import AuthService
from app.schemas.analytics import (
    RepositoryOverview,
    CommitTrendPoint,
    PRTrendPoint,
    IssueTrendPoint,
    HeatmapPoint,
    ContributorStat,
    ProductivityMetrics,
    TrendSignals,
    LanguagePoint,
    RepositoryComparison,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def _analytics(db) -> AnalyticsService:
    return AnalyticsService(db)


# ── Overview ────────────────────────────────────────

@router.get(
    "/{repo_id}/overview",
    response_model=RepositoryOverview,
    summary="Repository overview metrics",
)
async def repository_overview(
    repo_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
):
    data = await _analytics(db).get_repository_overview(repo_id)
    return RepositoryOverview(**data)


# ── Commit trends ────────────────────────────────────

@router.get(
    "/{repo_id}/commits/trends",
    response_model=list[CommitTrendPoint],
    summary="Daily commit trend for the last N days",
)
async def commit_trends(
    repo_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    days: int = Query(default=90, ge=7, le=365),
):
    rows = await _analytics(db).get_commit_trends(repo_id, days)
    return [CommitTrendPoint(**r) for r in rows]


# ── PR trends ────────────────────────────────────────

@router.get(
    "/{repo_id}/prs/trends",
    response_model=list[PRTrendPoint],
    summary="Weekly PR trend for the last N days",
)
async def pr_trends(
    repo_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    days: int = Query(default=90, ge=7, le=365),
):
    rows = await _analytics(db).get_pr_trends(repo_id, days)
    return [PRTrendPoint(**r) for r in rows]


# ── Issue trends ─────────────────────────────────────

@router.get(
    "/{repo_id}/issues/trends",
    response_model=list[IssueTrendPoint],
    summary="Weekly issue trend for the last N days",
)
async def issue_trends(
    repo_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    days: int = Query(default=90, ge=7, le=365),
):
    rows = await _analytics(db).get_issue_trends(repo_id, days)
    return [IssueTrendPoint(**r) for r in rows]


# ── Heatmap ──────────────────────────────────────────

@router.get(
    "/{repo_id}/heatmap",
    response_model=list[HeatmapPoint],
    summary="Daily commit heatmap — last 365 days",
)
async def contribution_heatmap(
    repo_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    days: int = Query(default=365, ge=30, le=365),
):
    rows = await _analytics(db).get_contribution_heatmap(repo_id, days)
    return [HeatmapPoint(**r) for r in rows]


# ── Contributors ─────────────────────────────────────

@router.get(
    "/{repo_id}/contributors",
    response_model=list[ContributorStat],
    summary="Per-contributor stats",
)
async def contributor_stats(
    repo_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
):
    rows = await _analytics(db).get_contributor_stats(repo_id)
    return [ContributorStat(**r) for r in rows]


# ── Productivity ─────────────────────────────────────

@router.get(
    "/{repo_id}/productivity",
    response_model=ProductivityMetrics,
    summary="Engineering productivity metrics",
)
async def productivity_metrics(
    repo_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    days: int = Query(default=30, ge=7, le=90),
):
    data = await _analytics(db).get_productivity_metrics(repo_id, days)
    return ProductivityMetrics(**data)


# ── Trend signals ────────────────────────────────────

@router.get(
    "/{repo_id}/trends",
    response_model=TrendSignals,
    summary="30d vs prior 30d trend signals",
)
async def trend_signals(
    repo_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
):
    data = await _analytics(db).get_trend_signals(repo_id)
    return TrendSignals(**data)


# ── Languages ─────────────────────────────────────────

@router.get(
    "/{repo_id}/languages",
    response_model=list[LanguagePoint],
    summary="Language distribution",
)
async def language_distribution(
    repo_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
):
    rows = await _analytics(db).get_language_distribution(repo_id)
    return [LanguagePoint(**r) for r in rows]


# ── Comparison ────────────────────────────────────────

@router.get(
    "/compare",
    response_model=RepositoryComparison,
    summary="Compare two repositories side by side",
)
async def compare_repositories(
    current_user: CurrentUser,
    db: DBSession,
    repo_a: uuid.UUID = Query(..., description="First repository ID"),
    repo_b: uuid.UUID = Query(..., description="Second repository ID"),
):
    if repo_a == repo_b:
        raise HTTPException(status_code=400, detail="repo_a and repo_b must be different")

    data = await _analytics(db).compare_repositories(repo_a, repo_b)
    return RepositoryComparison(**data)