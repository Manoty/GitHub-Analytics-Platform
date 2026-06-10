# backend/app/api/v1/endpoints/auth.py

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, DBSession
from app.core.config import settings
from app.core.security import verify_refresh_token
from app.schemas.auth import GitHubOAuthURLResponse, RefreshRequest, TokenResponse, TokenWithUser
from app.schemas.user import UserRead
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get(
    "/login",
    response_model=GitHubOAuthURLResponse,
    summary="Get GitHub OAuth URL",
)
async def github_login(db: DBSession):
    """Return the GitHub OAuth authorization URL for the frontend to redirect to."""
    service = AuthService(db)
    url = service.build_github_oauth_url()
    return GitHubOAuthURLResponse(url=url)


@router.get(
    "/callback",
    summary="GitHub OAuth callback",
)
async def github_callback(
    code: Annotated[str, Query(description="OAuth code from GitHub")],
    db: DBSession,
):
    """
    GitHub redirects here after the user authorises.
    Exchange the code, upsert the user, issue JWT pair,
    then redirect the browser to the frontend with tokens in the query string.
    (Frontend swaps them into memory/secure storage immediately.)
    """
    service = AuthService(db)
    try:
        result = await service.handle_oauth_callback(code)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="GitHub OAuth exchange failed",
        )

    # Redirect to frontend — tokens are transient in query params, frontend
    # moves them to memory immediately and should not log this URL.
    redirect_url = (
        f"{settings.frontend_url}/auth/callback"
        f"?access_token={result['access_token']}"
        f"&refresh_token={result['refresh_token']}"
    )
    return RedirectResponse(url=redirect_url, status_code=302)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh JWT access token",
)
async def refresh_token(payload: RefreshRequest, db: DBSession):
    """
    Accept a valid refresh token and return a new access + refresh token pair.
    Old refresh token is implicitly invalidated on the client side.
    """
    token_data = verify_refresh_token(payload.refresh_token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    service = AuthService(db)
    try:
        tokens = await service.refresh_tokens(token_data["sub"])
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))

    return TokenResponse(**tokens)


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get current user profile",
)
async def get_me(current_user: CurrentUser):
    """Return the profile of the currently authenticated user."""
    return current_user


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout (client-side token discard)",
)
async def logout(current_user: CurrentUser):
    """
    Stateless logout — the client must discard the tokens.
    A future enhancement can maintain a Redis token denylist here.
    """
    return None