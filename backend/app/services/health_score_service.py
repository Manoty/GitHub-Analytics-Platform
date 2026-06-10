# backend/app/services/health_score_service.py

from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.repository import Repository
from app.models.commit import Commit
from app.models.pull_request import PullRequest, PRState
from app.models.issue import Issue, IssueState
from app.models.contributor import Contributor
from app.models.repository_health import RepositoryHealth


class HealthScoreService:
    """
    Calculates a 0–100 health score from four dimensions:
      - Commit frequency   (30%)
      - Issue resolution   (25%)
      - PR merge speed     (25%)
      - Contributor diversity (20%)
    """

    WEIGHTS = {
        "commit_frequency": 0.30,
        "issue_resolution": 0.25,
        "pr_merge_speed": 0.25,
        "contributor_diversity": 0.20,
    }

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def calculate_and_store(self, repo: Repository) -> RepositoryHealth:
        now = datetime.now(timezone.utc)
        thirty_days_ago = now - timedelta(days=30)

        # ── Raw metrics ──────────────────────────────
        commits_30d = await self._count_commits_since(repo.id, thirty_days_ago)
        avg_pr_merge_hours = await self._avg_pr_merge_hours(repo.id)
        avg_issue_close_hours = await self._avg_issue_close_hours(repo.id)
        total_contributors = await self._count_contributors(repo.id)
        active_contributors = await self._count_active_contributors(repo.id, thirty_days_ago)

        # ── Component scores (0–100) ─────────────────
        commit_score = self._score_commit_frequency(commits_30d)
        pr_score = self._score_pr_merge_speed(avg_pr_merge_hours)
        issue_score = self._score_issue_resolution(avg_issue_close_hours)
        diversity_score = self._score_contributor_diversity(
            total_contributors, active_contributors
        )

        # ── Weighted total ───────────────────────────
        total = (
            commit_score * self.WEIGHTS["commit_frequency"]
            + issue_score * self.WEIGHTS["issue_resolution"]
            + pr_score * self.WEIGHTS["pr_merge_speed"]
            + diversity_score * self.WEIGHTS["contributor_diversity"]
        )
        total = round(min(max(total, 0), 100), 2)
        grade = self._grade(total)
        insights = self._generate_insights(
            commits_30d, avg_pr_merge_hours, avg_issue_close_hours,
            total_contributors, active_contributors, total
        )

        # ── Persist ──────────────────────────────────
        health = RepositoryHealth(
            repository_id=repo.id,
            health_score=total,
            health_grade=grade,
            commit_frequency_score=commit_score,
            pr_merge_speed_score=pr_score,
            issue_resolution_score=issue_score,
            contributor_diversity_score=diversity_score,
            commits_last_30_days=commits_30d,
            avg_pr_merge_hours=avg_pr_merge_hours or 0.0,
            avg_issue_close_hours=avg_issue_close_hours or 0.0,
            active_contributors_last_30_days=active_contributors,
            total_contributors=total_contributors,
            insights=insights,
            calculated_at=now,
        )
        self.db.add(health)
        await self.db.flush()
        return health

    # ── Scoring functions ────────────────────────────

    @staticmethod
    def _score_commit_frequency(commits_30d: int) -> float:
        """
        >= 30 commits/month → 100
        0 commits           → 0
        Linear interpolation in between.
        """
        return min(commits_30d / 30 * 100, 100)

    @staticmethod
    def _score_pr_merge_speed(avg_hours: float | None) -> float:
        """
        <= 24h  → 100
        >= 336h (2 weeks) → 0
        """
        if avg_hours is None:
            return 50.0  # no data → neutral
        if avg_hours <= 24:
            return 100.0
        if avg_hours >= 336:
            return 0.0
        return round((1 - (avg_hours - 24) / (336 - 24)) * 100, 2)

    @staticmethod
    def _score_issue_resolution(avg_hours: float | None) -> float:
        """
        <= 48h  → 100
        >= 720h (30 days) → 0
        """
        if avg_hours is None:
            return 50.0
        if avg_hours <= 48:
            return 100.0
        if avg_hours >= 720:
            return 0.0
        return round((1 - (avg_hours - 48) / (720 - 48)) * 100, 2)

    @staticmethod
    def _score_contributor_diversity(total: int, active: int) -> float:
        """
        >= 10 total contributors AND >= 3 active last 30d → 100
        Single contributor → 10 (not 0, because solo projects are valid)
        """
        if total == 0:
            return 0.0
        total_score = min(total / 10 * 60, 60)
        active_score = min(active / 3 * 40, 40)
        return round(total_score + active_score, 2)

    @staticmethod
    def _grade(score: float) -> str:
        if score >= 80:
            return "Excellent"
        if score >= 60:
            return "Good"
        if score >= 40:
            return "Fair"
        return "Poor"

    # ── Insight generation ───────────────────────────

    @staticmethod
    def _generate_insights(
        commits_30d: int,
        avg_pr_hours: float | None,
        avg_issue_hours: float | None,
        total_contributors: int,
        active_contributors: int,
        score: float,
    ) -> list[str]:
        insights = []

        if commits_30d == 0:
            insights.append("No commits in the last 30 days — repository may be inactive.")
        elif commits_30d < 5:
            insights.append(f"Low commit activity: only {commits_30d} commits in the last 30 days.")
        else:
            insights.append(f"Healthy commit activity: {commits_30d} commits in the last 30 days.")

        if avg_pr_hours is not None:
            if avg_pr_hours <= 24:
                insights.append("PRs are being merged quickly (under 24 hours on average).")
            elif avg_pr_hours <= 72:
                insights.append(f"PR merge time is acceptable at {avg_pr_hours:.0f} hours average.")
            else:
                insights.append(
                    f"PR merge time is slow at {avg_pr_hours:.0f} hours average — consider review process improvements."
                )

        if avg_issue_hours is not None:
            if avg_issue_hours <= 48:
                insights.append("Issues are being resolved rapidly.")
            elif avg_issue_hours > 720:
                insights.append("Issue backlog is growing — average close time exceeds 30 days.")

        if total_contributors == 1:
            insights.append("Single contributor — bus factor risk is high.")
        elif active_contributors == 0:
            insights.append("No contributors active in the last 30 days.")
        else:
            insights.append(
                f"{active_contributors} of {total_contributors} contributors active in the last 30 days."
            )

        return insights

    # ── DB queries ───────────────────────────────────

    async def _count_commits_since(self, repo_id, since: datetime) -> int:
        result = await self.db.execute(
            select(func.count(Commit.id)).where(
                Commit.repository_id == repo_id,
                Commit.committed_at >= since,
            )
        )
        return result.scalar_one() or 0

    async def _avg_pr_merge_hours(self, repo_id) -> float | None:
        result = await self.db.execute(
            select(func.avg(PullRequest.time_to_merge_hours)).where(
                PullRequest.repository_id == repo_id,
                PullRequest.state == PRState.MERGED,
                PullRequest.time_to_merge_hours.isnot(None),
            )
        )
        return result.scalar_one()

    async def _avg_issue_close_hours(self, repo_id) -> float | None:
        result = await self.db.execute(
            select(func.avg(Issue.time_to_close_hours)).where(
                Issue.repository_id == repo_id,
                Issue.state == IssueState.CLOSED,
                Issue.time_to_close_hours.isnot(None),
            )
        )
        return result.scalar_one()

    async def _count_contributors(self, repo_id) -> int:
        result = await self.db.execute(
            select(func.count(Contributor.id)).where(
                Contributor.repository_id == repo_id
            )
        )
        return result.scalar_one() or 0

    async def _count_active_contributors(self, repo_id, since: datetime) -> int:
        result = await self.db.execute(
            select(func.count(Commit.author_github_login.distinct())).where(
                Commit.repository_id == repo_id,
                Commit.committed_at >= since,
                Commit.author_github_login.isnot(None),
            )
        )
        return result.scalar_one() or 0