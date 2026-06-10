# backend/app/services/github_service.py

from typing import Any, AsyncGenerator
import httpx
from datetime import datetime, timezone

from app.core.config import settings


class GitHubAPIError(Exception):
    def __init__(self, message: str, status_code: int = 0):
        self.status_code = status_code
        super().__init__(message)


class GitHubService:
    """
    Async GitHub REST API v3 client.
    Handles auth headers, pagination, and rate limit detection.
    One instance per ingestion job — constructed with the user's access token.
    """

    BASE_URL = settings.github_api_base_url
    PER_PAGE = 100  # max allowed by GitHub

    def __init__(self, access_token: str) -> None:
        self._token = access_token
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers=self._base_headers(),
            timeout=60.0,
        )

    def _base_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    # ── Generic helpers ─────────────────────────────

    async def _get(self, path: str, params: dict | None = None) -> Any:
        response = await self._client.get(path, params=params)
        self._check_response(response)
        return response.json()

    async def _paginate(
        self,
        path: str,
        params: dict | None = None,
        max_pages: int = 50,
    ) -> AsyncGenerator[list[dict], None]:
        """Yield one page of results at a time."""
        page = 1
        base_params = dict(params or {})
        base_params["per_page"] = self.PER_PAGE

        while page <= max_pages:
            base_params["page"] = page
            response = await self._client.get(path, params=base_params)
            self._check_response(response)
            data = response.json()

            if not data:
                break

            yield data

            # GitHub signals last page via Link header absence
            if "next" not in response.headers.get("Link", ""):
                break

            page += 1

    def _check_response(self, response: httpx.Response) -> None:
        if response.status_code == 403:
            raise GitHubAPIError("GitHub rate limit exceeded or forbidden", 403)
        if response.status_code == 404:
            raise GitHubAPIError("Resource not found on GitHub", 404)
        if response.status_code >= 400:
            raise GitHubAPIError(
                f"GitHub API error: {response.status_code} {response.text}",
                response.status_code,
            )

    # ── Repository ──────────────────────────────────

    async def get_repository(self, full_name: str) -> dict[str, Any]:
        """Fetch repository metadata by full_name e.g. 'torvalds/linux'."""
        return await self._get(f"/repos/{full_name}")

    async def get_repository_languages(self, full_name: str) -> dict[str, int]:
        """Return language breakdown as {language: bytes}."""
        return await self._get(f"/repos/{full_name}/languages")

    async def get_user_repositories(self) -> list[dict[str, Any]]:
        """Fetch all repos the authenticated user has access to."""
        repos: list[dict] = []
        async for page in self._paginate("/user/repos", {"type": "all", "sort": "updated"}):
            repos.extend(page)
        return repos

    # ── Commits ─────────────────────────────────────

    async def get_commits(
        self,
        full_name: str,
        since: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch all commits, optionally since a given datetime."""
        params: dict[str, Any] = {}
        if since:
            params["since"] = since.isoformat()

        commits: list[dict] = []
        async for page in self._paginate(f"/repos/{full_name}/commits", params):
            commits.extend(page)
        return commits

    async def get_commit_detail(self, full_name: str, sha: str) -> dict[str, Any]:
        """Fetch a single commit with diff stats."""
        return await self._get(f"/repos/{full_name}/commits/{sha}")

    # ── Pull Requests ───────────────────────────────

    async def get_pull_requests(
        self,
        full_name: str,
        state: str = "all",
    ) -> list[dict[str, Any]]:
        """Fetch PRs. state = 'open' | 'closed' | 'all'."""
        prs: list[dict] = []
        async for page in self._paginate(
            f"/repos/{full_name}/pulls",
            {"state": state, "sort": "updated", "direction": "desc"},
        ):
            prs.extend(page)
        return prs

    # ── Issues ──────────────────────────────────────

    async def get_issues(
        self,
        full_name: str,
        state: str = "all",
    ) -> list[dict[str, Any]]:
        """
        Fetch issues. GitHub returns PRs in this endpoint too —
        filter them out by checking for absence of 'pull_request' key.
        """
        issues: list[dict] = []
        async for page in self._paginate(
            f"/repos/{full_name}/issues",
            {"state": state, "sort": "updated", "direction": "desc"},
        ):
            real_issues = [i for i in page if "pull_request" not in i]
            issues.extend(real_issues)
        return issues

    # ── Contributors ────────────────────────────────

    async def get_contributors(self, full_name: str) -> list[dict[str, Any]]:
        """Fetch contributor list with contribution counts."""
        contributors: list[dict] = []
        async for page in self._paginate(f"/repos/{full_name}/contributors"):
            contributors.extend(page)
        return contributors

    async def close(self) -> None:
        await self._client.aclose()