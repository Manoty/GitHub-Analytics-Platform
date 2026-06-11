# backend/app/services/analytics_service.py

from typing import Any
import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text

from app.models.commit import Commit
from app.models.pull_request import PullRequest, PRState
from app.models.issue import Issue, IssueState
from app.models.contributor import Contributor
from app.models.repository import Repository
from app.models.repository_health import RepositoryHealth


class AnalyticsService:
    """
    All analytics queries live here.

    Design decision: we run aggregations directly against PostgreSQL via
    SQLAlchemy async for smaller datasets, and delegate to DuckDB for
    cross-repository comparisons and heavier aggregations.
    This keeps the architecture simple in Phase 5 without requiring
    a running dbt pipeline for basic dashboards.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Repository overview ──────────────────────────

    async def get_repository_overview(self, repo_id: uuid.UUID) -> dict[str, Any]:
        """Top-level counts + latest health score for one repository."""

        total_commits = await self._scalar(
            select(func.count(Commit.id)).where(Commit.repository_id == repo_id)
        )
        total_prs = await self._scalar(
            select(func.count(PullRequest.id)).where(PullRequest.repository_id == repo_id)
        )
        merged_prs = await self._scalar(
            select(func.count(PullRequest.id)).where(
                PullRequest.repository_id == repo_id,
                PullRequest.state == PRState.MERGED,
            )
        )
        total_issues = await self._scalar(
            select(func.count(Issue.id)).where(Issue.repository_id == repo_id)
        )
        closed_issues = await self._scalar(
            select(func.count(Issue.id)).where(
                Issue.repository_id == repo_id,
                Issue.state == IssueState.CLOSED,
            )
        )
        total_contributors = await self._scalar(
            select(func.count(Contributor.id)).where(
                Contributor.repository_id == repo_id
            )
        )
        avg_pr_merge = await self._scalar(
            select(func.avg(PullRequest.time_to_merge_hours)).where(
                PullRequest.repository_id == repo_id,
                PullRequest.state == PRState.MERGED,
            )
        )
        avg_issue_close = await self._scalar(
            select(func.avg(Issue.time_to_close_hours)).where(
                Issue.repository_id == repo_id,
                Issue.state == IssueState.CLOSED,
            )
        )

        # Latest health score snapshot
        health_result = await self.db.execute(
            select(RepositoryHealth)
            .where(RepositoryHealth.repository_id == repo_id)
            .order_by(RepositoryHealth.calculated_at.desc())
            .limit(1)
        )
        health = health_result.scalar_one_or_none()

        return {
            "total_commits": total_commits or 0,
            "total_pull_requests": total_prs or 0,
            "merged_pull_requests": merged_prs or 0,
            "total_issues": total_issues or 0,
            "closed_issues": closed_issues or 0,
            "total_contributors": total_contributors or 0,
            "avg_pr_merge_hours": round(avg_pr_merge, 2) if avg_pr_merge else None,
            "avg_issue_close_hours": round(avg_issue_close, 2) if avg_issue_close else None,
            "health_score": health.health_score if health else None,
            "health_grade": health.health_grade if health else None,
            "health_insights": health.insights if health else [],
        }

    # ── Commit trends ────────────────────────────────

    async def get_commit_trends(
        self,
        repo_id: uuid.UUID,
        days: int = 90,
    ) -> list[dict[str, Any]]:
        """
        Daily commit counts for the last N days.
        Returns [{date, commit_count, author_count}]
        """
        since = datetime.now(timezone.utc) - timedelta(days=days)

        result = await self.db.execute(
            text("""
                SELECT
                    DATE_TRUNC('day', committed_at) AS date,
                    COUNT(*) AS commit_count,
                    COUNT(DISTINCT author_github_login) AS author_count
                FROM commits
                WHERE repository_id = :repo_id
                  AND committed_at >= :since
                GROUP BY DATE_TRUNC('day', committed_at)
                ORDER BY date ASC
            """),
            {"repo_id": str(repo_id), "since": since},
        )
        rows = result.fetchall()
        return [
            {
                "date": str(row[0].date()) if row[0] else None,
                "commit_count": row[1],
                "author_count": row[2],
            }
            for row in rows
        ]

    # ── PR trends ────────────────────────────────────

    async def get_pr_trends(
        self,
        repo_id: uuid.UUID,
        days: int = 90,
    ) -> list[dict[str, Any]]:
        """
        Weekly PR opened vs merged counts for the last N days.
        Returns [{week, opened, merged, closed}]
        """
        since = datetime.now(timezone.utc) - timedelta(days=days)

        result = await self.db.execute(
            text("""
                SELECT
                    DATE_TRUNC('week', github_created_at) AS week,
                    COUNT(*) AS opened,
                    COUNT(*) FILTER (WHERE state = 'merged') AS merged,
                    COUNT(*) FILTER (WHERE state = 'closed') AS closed
                FROM pull_requests
                WHERE repository_id = :repo_id
                  AND github_created_at >= :since
                GROUP BY DATE_TRUNC('week', github_created_at)
                ORDER BY week ASC
            """),
            {"repo_id": str(repo_id), "since": since},
        )
        rows = result.fetchall()
        return [
            {
                "week": str(row[0].date()) if row[0] else None,
                "opened": row[1],
                "merged": row[2],
                "closed": row[3],
            }
            for row in rows
        ]

    # ── Issue trends ─────────────────────────────────

    async def get_issue_trends(
        self,
        repo_id: uuid.UUID,
        days: int = 90,
    ) -> list[dict[str, Any]]:
        """Weekly issue opened vs closed counts."""
        since = datetime.now(timezone.utc) - timedelta(days=days)

        result = await self.db.execute(
            text("""
                SELECT
                    DATE_TRUNC('week', github_created_at) AS week,
                    COUNT(*) AS opened,
                    COUNT(*) FILTER (WHERE state = 'closed') AS closed
                FROM issues
                WHERE repository_id = :repo_id
                  AND github_created_at >= :since
                GROUP BY DATE_TRUNC('week', github_created_at)
                ORDER BY week ASC
            """),
            {"repo_id": str(repo_id), "since": since},
        )
        rows = result.fetchall()
        return [
            {
                "week": str(row[0].date()) if row[0] else None,
                "opened": row[1],
                "closed": row[2],
            }
            for row in rows
        ]

    # ── Contributor analytics ────────────────────────

    async def get_contributor_stats(
        self,
        repo_id: uuid.UUID,
    ) -> list[dict[str, Any]]:
        """
        Per-contributor stats: commits, PRs, issues, additions, deletions.
        Joined from contributors + aggregated from commits/PRs/issues tables.
        """
        result = await self.db.execute(
            text("""
                SELECT
                    c.github_login,
                    c.avatar_url,
                    c.contributions_count,
                    COUNT(DISTINCT cm.id)  AS commit_count,
                    COUNT(DISTINCT pr.id)  AS pr_count,
                    COUNT(DISTINCT iss.id) AS issue_count,
                    COALESCE(SUM(cm.additions), 0) AS total_additions,
                    COALESCE(SUM(cm.deletions), 0) AS total_deletions,
                    MAX(cm.committed_at) AS last_commit_at
                FROM contributors c
                LEFT JOIN commits cm
                    ON cm.repository_id = c.repository_id
                    AND cm.author_github_login = c.github_login
                LEFT JOIN pull_requests pr
                    ON pr.repository_id = c.repository_id
                    AND pr.author_login = c.github_login
                LEFT JOIN issues iss
                    ON iss.repository_id = c.repository_id
                    AND iss.author_login = c.github_login
                WHERE c.repository_id = :repo_id
                GROUP BY c.github_login, c.avatar_url, c.contributions_count
                ORDER BY commit_count DESC
            """),
            {"repo_id": str(repo_id)},
        )
        rows = result.fetchall()
        return [
            {
                "github_login": row[0],
                "avatar_url": row[1],
                "contributions_count": row[2],
                "commit_count": row[3],
                "pr_count": row[4],
                "issue_count": row[5],
                "total_additions": row[6],
                "total_deletions": row[7],
                "last_commit_at": str(row[8]) if row[8] else None,
            }
            for row in rows
        ]

    # ── Contribution heatmap ─────────────────────────

    async def get_contribution_heatmap(
        self,
        repo_id: uuid.UUID,
        days: int = 365,
    ) -> list[dict[str, Any]]:
        """
        Daily commit counts keyed by date — used to render the
        GitHub-style contribution heatmap on the frontend.
        Returns [{date, count}]
        """
        since = datetime.now(timezone.utc) - timedelta(days=days)

        result = await self.db.execute(
            text("""
                SELECT
                    DATE_TRUNC('day', committed_at)::date AS date,
                    COUNT(*) AS count
                FROM commits
                WHERE repository_id = :repo_id
                  AND committed_at >= :since
                GROUP BY DATE_TRUNC('day', committed_at)::date
                ORDER BY date ASC
            """),
            {"repo_id": str(repo_id), "since": since},
        )
        rows = result.fetchall()
        return [{"date": str(row[0]), "count": row[1]} for row in rows]

    # ── Repository comparison ────────────────────────

    async def compare_repositories(
        self,
        repo_id_a: uuid.UUID,
        repo_id_b: uuid.UUID,
    ) -> dict[str, Any]:
        """
        Side-by-side metric comparison for two repositories.
        Returns a dict with keys 'repo_a' and 'repo_b'.
        """
        overview_a = await self.get_repository_overview(repo_id_a)
        overview_b = await self.get_repository_overview(repo_id_b)

        repo_a = await self._get_repo(repo_id_a)
        repo_b = await self._get_repo(repo_id_b)

        return {
            "repo_a": {
                "id": str(repo_id_a),
                "full_name": repo_a.full_name if repo_a else None,
                "stars": repo_a.stars_count if repo_a else 0,
                "forks": repo_a.forks_count if repo_a else 0,
                **overview_a,
            },
            "repo_b": {
                "id": str(repo_id_b),
                "full_name": repo_b.full_name if repo_b else None,
                "stars": repo_b.stars_count if repo_b else 0,
                "forks": repo_b.forks_count if repo_b else 0,
                **overview_b,
            },
        }

    # ── Productivity metrics ─────────────────────────

    async def get_productivity_metrics(
        self,
        repo_id: uuid.UUID,
        days: int = 30,
    ) -> dict[str, Any]:
        """
        Engineering productivity: PR velocity, issue throughput,
        contributor activity, deployment frequency proxy.
        """
        since = datetime.now(timezone.utc) - timedelta(days=days)

        commits_period = await self._scalar(
            select(func.count(Commit.id)).where(
                Commit.repository_id == repo_id,
                Commit.committed_at >= since,
            )
        )
        prs_merged = await self._scalar(
            select(func.count(PullRequest.id)).where(
                PullRequest.repository_id == repo_id,
                PullRequest.state == PRState.MERGED,
                PullRequest.github_merged_at >= since,
            )
        )
        issues_closed = await self._scalar(
            select(func.count(Issue.id)).where(
                Issue.repository_id == repo_id,
                Issue.state == IssueState.CLOSED,
                Issue.github_closed_at >= since,
            )
        )
        active_contributors = await self._scalar(
            select(func.count(Commit.author_github_login.distinct())).where(
                Commit.repository_id == repo_id,
                Commit.committed_at >= since,
                Commit.author_github_login.isnot(None),
            )
        )
        avg_pr_merge = await self._scalar(
            select(func.avg(PullRequest.time_to_merge_hours)).where(
                PullRequest.repository_id == repo_id,
                PullRequest.state == PRState.MERGED,
                PullRequest.github_merged_at >= since,
            )
        )
        avg_issue_close = await self._scalar(
            select(func.avg(Issue.time_to_close_hours)).where(
                Issue.repository_id == repo_id,
                Issue.state == IssueState.CLOSED,
                Issue.github_closed_at >= since,
            )
        )

        # Deployment frequency proxy: merged PRs to default branch per week
        deploy_freq = round((prs_merged or 0) / max(days / 7, 1), 2)

        return {
            "period_days": days,
            "commits": commits_period or 0,
            "prs_merged": prs_merged or 0,
            "issues_closed": issues_closed or 0,
            "active_contributors": active_contributors or 0,
            "avg_pr_merge_hours": round(avg_pr_merge, 2) if avg_pr_merge else None,
            "avg_issue_close_hours": round(avg_issue_close, 2) if avg_issue_close else None,
            "deployment_frequency_per_week": deploy_freq,
            "contributor_velocity": round(
                (commits_period or 0) / max(active_contributors or 1, 1), 2
            ),
        }

    # ── Trend detection ──────────────────────────────

    async def get_trend_signals(
        self,
        repo_id: uuid.UUID,
    ) -> dict[str, Any]:
        """
        Compare last 30 days vs prior 30 days to detect momentum.
        Returns percent change per metric + a direction label.
        """
        now = datetime.now(timezone.utc)
        current_start = now - timedelta(days=30)
        previous_start = now - timedelta(days=60)

        async def _count_commits(start, end):
            return await self._scalar(
                select(func.count(Commit.id)).where(
                    Commit.repository_id == repo_id,
                    Commit.committed_at >= start,
                    Commit.committed_at < end,
                )
            ) or 0

        async def _count_prs(start, end):
            return await self._scalar(
                select(func.count(PullRequest.id)).where(
                    PullRequest.repository_id == repo_id,
                    PullRequest.github_created_at >= start,
                    PullRequest.github_created_at < end,
                )
            ) or 0

        commits_current = await _count_commits(current_start, now)
        commits_previous = await _count_commits(previous_start, current_start)
        prs_current = await _count_prs(current_start, now)
        prs_previous = await _count_prs(previous_start, current_start)

        def _pct_change(current, previous) -> float | None:
            if previous == 0:
                return None
            return round((current - previous) / previous * 100, 1)

        def _direction(pct) -> str:
            if pct is None:
                return "neutral"
            if pct > 10:
                return "increasing"
            if pct < -10:
                return "declining"
            return "stable"

        commit_change = _pct_change(commits_current, commits_previous)
        pr_change = _pct_change(prs_current, prs_previous)

        return {
            "commits": {
                "current_30d": commits_current,
                "previous_30d": commits_previous,
                "pct_change": commit_change,
                "direction": _direction(commit_change),
            },
            "pull_requests": {
                "current_30d": prs_current,
                "previous_30d": prs_previous,
                "pct_change": pr_change,
                "direction": _direction(pr_change),
            },
        }

    # ── Language distribution ────────────────────────

    async def get_language_distribution(
        self,
        repo_id: uuid.UUID,
    ) -> list[dict[str, Any]]:
        """
        Return language breakdown as [{language, bytes, percentage}].
        Data comes from the languages_data JSONB field on the repository.
        """
        result = await self.db.execute(
            select(Repository.languages_data).where(Repository.id == repo_id)
        )
        row = result.scalar_one_or_none()
        if not row:
            return []

        total_bytes = sum(row.values()) or 1
        return sorted(
            [
                {
                    "language": lang,
                    "bytes": b,
                    "percentage": round(b / total_bytes * 100, 2),
                }
                for lang, b in row.items()
            ],
            key=lambda x: x["bytes"],
            reverse=True,
        )

    # ── Helpers ──────────────────────────────────────

    async def _scalar(self, stmt) -> Any:
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_repo(self, repo_id: uuid.UUID) -> Repository | None:
        result = await self.db.execute(
            select(Repository).where(Repository.id == repo_id)
        )
        return result.scalar_one_or_none()