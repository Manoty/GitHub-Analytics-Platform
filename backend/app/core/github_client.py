# backend/app/core/github_client.py

from typing import Any
import httpx
from app.core.config import settings


class GitHubOAuthClient:
    """Handles GitHub OAuth token exchange and user profile fetch."""

    OAUTH_TOKEN_URL = "https://github.com/login/oauth/access_token"
    USER_URL = f"{settings.github_api_base_url}/user"
    USER_EMAILS_URL = f"{settings.github_api_base_url}/user/emails"

    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            timeout=30.0,
            headers={"Accept": "application/json"},
        )

    async def exchange_code_for_token(self, code: str) -> str:
        """Exchange GitHub OAuth code for an access token."""
        response = await self._client.post(
            self.OAUTH_TOKEN_URL,
            json={
                "client_id": settings.github_client_id,
                "client_secret": settings.github_client_secret,
                "code": code,
            },
        )
        response.raise_for_status()
        data = response.json()

        if "error" in data:
            raise ValueError(f"GitHub OAuth error: {data.get('error_description', data['error'])}")

        return data["access_token"]

    async def get_user_profile(self, access_token: str) -> dict[str, Any]:
        """Fetch the authenticated GitHub user's profile."""
        response = await self._client.get(
            self.USER_URL,
            headers=self._auth_headers(access_token),
        )
        response.raise_for_status()
        return response.json()

    async def get_user_emails(self, access_token: str) -> list[dict[str, Any]]:
        """Fetch all emails for the authenticated user."""
        response = await self._client.get(
            self.USER_EMAILS_URL,
            headers=self._auth_headers(access_token),
        )
        response.raise_for_status()
        return response.json()

    async def get_primary_email(self, access_token: str) -> str | None:
        """Return the primary verified email address."""
        try:
            emails = await self.get_user_emails(access_token)
            for entry in emails:
                if entry.get("primary") and entry.get("verified"):
                    return entry["email"]
        except Exception:
            pass
        return None

    def _auth_headers(self, access_token: str) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def close(self) -> None:
        await self._client.aclose()


github_oauth_client = GitHubOAuthClient()