# backend/app/services/ingestion_service.py

from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
import uuid

from app.models.repository import Repository, SyncStatus
from app.models.commit import Commit
from app.models.pull_request import PullRequest, PRState
from app.models.issue import Issue, IssueState
from app.models.contributor import Contributor
from app.services.github_service import GitHubService
from app.services.health_score_service import HealthScoreService


class IngestionService:
    """
    Drives a full repository sync:
      1. Repository metadata
      2. Languages
      3. Commits
      4. Pull requests
      5. Issues
      6. Contributors
      7. Health score calculation
    """

    def __init__(self, db: AsyncSession, github: GitHubService) -> None:
        self.db = db
        self.github = github

    async def sync_repository(self, repository_id: uuid.UUID) -> None:
        """
        Entry point for Celery task.
        Updates sync_status throughout so the frontend can poll progress.
        """
        repo = await self._get_repo(repository_id)
        if not repo:
            raise ValueError(f"Repository {repository_id} not found")

        try:
            repo.sync_status = SyncStatus.SYNCING
            await self.db.flush()

            await self._sync_metadata(repo)
            await self._sync_commits(repo)
            await self._sync_pull_requests(repo)
            await self._sync_issues(repo)
            await self._sync_contributors(repo)

            # Calculate health score from freshly ingested data
            health_svc = HealthScoreService(self.db)
            await health_svc.calculate_and_store(repo)

            repo.sync_status = SyncStatus.COMPLETED
            repo.last_synced_at = datetime.now(timezone.utc)
            repo.sync_error = None
            await self.db.flush()

        except Exception as exc:
            repo.sync_status = SyncStatus.FAILED
            repo.sync_error = str(exc)[:1000]
            await self.db.flush()
            raise

    # ── Metadata ────────────────────────────────────

    async def _sync_metadata(self, repo: Repository) -> None:
        data = await self.github.get_repository(repo.full_name)
        languages = await self.github.get_repository_languages(repo.full_name)

        repo.description = data.get("description")
        repo.homepage = data.get("homepage")
        repo.language = data.get("language")
        repo.topics = data.get("topics", [])
        repo.languages_data = languages
        repo.stars_count = data.get("stargazers_count", 0)
        repo.forks_count = data.get("forks_count", 0)
        repo.watchers_count = data.get("watchers_count", 0)
        repo.open_issues_count = data.get("open_issues_count", 0)
        repo.size_kb = data.get("size", 0)
        repo.is_private = data.get("private", False)
        repo.is_fork = data.get("fork", False)
        repo.is_archived = data.get("archived", False)
        repo.github_created_at = self._parse_dt(data.get("created_at"))
        repo.github_updated_at = self._parse_dt(data.get("updated_at"))
        repo.github_pushed_at = self._parse_dt(data.get("pushed_at"))
        await self.db.flush()

    # ── Commits ─────────────────────────────────────

    async def _sync_commits(self, repo: Repository) -> None:
        # Delete existing commits for a clean re-sync
        await self.db.execute(
            delete(Commit).where(Commit.repository_id == repo.id)
        )

        raw_commits = await self.github.get_commits(repo.full_name)

        for raw in raw_commits:
            commit_data = raw.get("commit", {})
            author_data = commit_data.get("author", {})
            github_author = raw.get("author") or {}

            commit = Commit(
                repository_id=repo.id,
                sha=raw["sha"],
                message=commit_data.get("message", "")[:2000],
                author_name=author_data.get("name"),
                author_email=author_data.get("email"),
                author_github_login=github_author.get("login"),
                committed_at=self._parse_dt(author_data.get("date")),
                url=raw.get("html_url"),
            )
            self.db.add(commit)

        await self.db.flush()

    # ── Pull Requests ───────────────────────────────

    async def _sync_pull_requests(self, repo: Repository) -> None:
        await self.db.execute(
            delete(PullRequest).where(PullRequest.repository_id == repo.id)
        )

        raw_prs = await self.github.get_pull_requests(repo.full_name, state="all")

        for raw in raw_prs:
            created_at = self._parse_dt(raw.get("created_at"))
            merged_at = self._parse_dt(raw.get("merged_at"))

            # Derive state
            if raw.get("merged_at"):
                state = PRState.MERGED
            elif raw.get("state") == "closed":
                state = PRState.CLOSED
            else:
                state = PRState.OPEN

            # Merge time in hours
            time_to_merge = None
            if created_at and merged_at:
                delta = merged_at - created_at
                time_to_merge = delta.total_seconds() / 3600

            pr = PullRequest(
                repository_id=repo.id,
                github_pr_number=raw["number"],
                title=raw.get("title", "")[:1000],
                body=(raw.get("body") or "")[:5000],
                state=state,
                author_login=(raw.get("user") or {}).get("login"),
                is_merged=bool(raw.get("merged_at")),
                additions=raw.get("additions", 0),
                deletions=raw.get("deletions", 0),
                changed_files=raw.get("changed_files", 0),
                comments_count=raw.get("comments", 0),
                review_comments_count=raw.get("review_comments", 0),
                commits_count=raw.get("commits", 0),
                github_created_at=created_at,
                github_updated_at=self._parse_dt(raw.get("updated_at")),
                github_closed_at=self._parse_dt(raw.get("closed_at")),
                github_merged_at=merged_at,
                time_to_merge_hours=time_to_merge,
            )
            self.db.add(pr)

        await self.db.flush()

    # ── Issues ──────────────────────────────────────

    async def _sync_issues(self, repo: Repository) -> None:
        await self.db.execute(
            delete(Issue).where(Issue.repository_id == repo.id)
        )

        raw_issues = await self.github.get_issues(repo.full_name, state="all")

        for raw in raw_issues:
            created_at = self._parse_dt(raw.get("created_at"))
            closed_at = self._parse_dt(raw.get("closed_at"))

            time_to_close = None
            if created_at and closed_at:
                delta = closed_at - created_at
                time_to_close = delta.total_seconds() / 3600

            labels = [lbl["name"] for lbl in raw.get("labels", [])]

            issue = Issue(
                repository_id=repo.id,
                github_issue_number=raw["number"],
                title=raw.get("title", "")[:1000],
                body=(raw.get("body") or "")[:5000],
                state=IssueState.CLOSED if raw.get("state") == "closed" else IssueState.OPEN,
                author_login=(raw.get("user") or {}).get("login"),
                labels=labels,
                comments_count=raw.get("comments", 0),
                github_created_at=created_at,
                github_updated_at=self._parse_dt(raw.get("updated_at")),
                github_closed_at=closed_at,
                time_to_close_hours=time_to_close,
            )
            self.db.add(issue)

        await self.db.flush()

    # ── Contributors ────────────────────────────────

    async def _sync_contributors(self, repo: Repository) -> None:
        await self.db.execute(
            delete(Contributor).where(Contributor.repository_id == repo.id)
        )

        raw_contributors = await self.github.get_contributors(repo.full_name)

        for raw in raw_contributors:
            contributor = Contributor(
                repository_id=repo.id,
                github_login=raw.get("login", "unknown"),
                avatar_url=raw.get("avatar_url"),
                github_url=raw.get("html_url"),
                contributions_count=raw.get("contributions", 0),
            )
            self.db.add(contributor)

        await self.db.flush()

    # ── Helpers ─────────────────────────────────────

    async def _get_repo(self, repository_id: uuid.UUID) -> Repository | None:
        result = await self.db.execute(
            select(Repository).where(Repository.id == repository_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    def _parse_dt(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None