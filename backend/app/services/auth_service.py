# backend/app/services/auth_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Any

from app.models.user import User
from app.core.github_client import GitHubOAuthClient
from app.core.security import create_access_token, create_refresh_token
from app.core.config import settings


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.github = GitHubOAuthClient()

    # ── OAuth flow ──────────────────────────────────

    def build_github_oauth_url(self) -> str:
        """Return the GitHub OAuth authorization URL."""
        scopes = "read:user user:email repo"
        return (
            f"https://github.com/login/oauth/authorize"
            f"?client_id={settings.github_client_id}"
            f"&redirect_uri={settings.github_redirect_uri}"
            f"&scope={scopes}"
        )

    async def handle_oauth_callback(self, code: str) -> dict[str, Any]:
        """
        Full OAuth callback flow:
        1. Exchange code → GitHub access token
        2. Fetch GitHub user profile + primary email
        3. Upsert User in DB
        4. Issue our own JWT pair
        """
        # 1 — Exchange
        github_token = await self.github.exchange_code_for_token(code)

        # 2 — Profile
        profile = await self.github.get_user_profile(github_token)
        primary_email = await self.github.get_primary_email(github_token)

        # 3 — Upsert
        user = await self._upsert_user(profile, primary_email, github_token)

        # 4 — Issue tokens
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user,
        }

    async def refresh_tokens(self, user_id: str) -> dict[str, Any]:
        """Issue a fresh access + refresh token pair."""
        user = await self.get_user_by_id(user_id)
        if not user or not user.is_active:
            raise ValueError("User not found or inactive")

        return {
            "access_token": create_access_token(subject=user.id),
            "refresh_token": create_refresh_token(subject=user.id),
            "token_type": "bearer",
        }

    # ── User queries ────────────────────────────────

    async def get_user_by_id(self, user_id: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_user_by_github_id(self, github_id: int) -> User | None:
        result = await self.db.execute(
            select(User).where(User.github_id == github_id)
        )
        return result.scalar_one_or_none()

    # ── Internal helpers ────────────────────────────

    async def _upsert_user(
        self,
        profile: dict[str, Any],
        email: str | None,
        github_token: str,
    ) -> User:
        """Create or update the User row from a GitHub profile dict."""
        github_id = profile["id"]
        existing = await self.get_user_by_github_id(github_id)

        if existing:
            # Update mutable fields on every login
            existing.username = profile.get("login", existing.username)
            existing.avatar_url = profile.get("avatar_url", existing.avatar_url)
            existing.name = profile.get("name", existing.name)
            existing.bio = profile.get("bio", existing.bio)
            existing.company = profile.get("company", existing.company)
            existing.location = profile.get("location", existing.location)
            existing.github_url = profile.get("html_url", existing.github_url)
            existing.email = email or existing.email
            existing.access_token = github_token
            await self.db.flush()
            return existing

        user = User(
            github_id=github_id,
            username=profile.get("login", ""),
            email=email,
            avatar_url=profile.get("avatar_url"),
            name=profile.get("name"),
            bio=profile.get("bio"),
            company=profile.get("company"),
            location=profile.get("location"),
            github_url=profile.get("html_url"),
            access_token=github_token,
        )
        self.db.add(user)
        await self.db.flush()
        return user