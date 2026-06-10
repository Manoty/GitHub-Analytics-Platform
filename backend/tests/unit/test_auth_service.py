# backend/tests/unit/test_auth_service.py

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.auth_service import AuthService


@pytest.mark.asyncio
async def test_build_oauth_url(db_session):
    service = AuthService(db_session)
    url = service.build_github_oauth_url()
    assert "github.com/login/oauth/authorize" in url
    assert "client_id" in url
    assert "scope" in url


@pytest.mark.asyncio
async def test_handle_oauth_callback_creates_user(db_session):
    service = AuthService(db_session)

    mock_profile = {
        "id": 12345,
        "login": "testuser",
        "avatar_url": "https://avatars.githubusercontent.com/u/12345",
        "name": "Test User",
        "bio": None,
        "company": None,
        "location": None,
        "html_url": "https://github.com/testuser",
    }

    with (
        patch.object(service.github, "exchange_code_for_token", new=AsyncMock(return_value="gh_token")),
        patch.object(service.github, "get_user_profile", new=AsyncMock(return_value=mock_profile)),
        patch.object(service.github, "get_primary_email", new=AsyncMock(return_value="test@example.com")),
    ):
        result = await service.handle_oauth_callback("oauth_code_123")

    assert "access_token" in result
    assert "refresh_token" in result
    assert result["user"].username == "testuser"
    assert result["user"].email == "test@example.com"


@pytest.mark.asyncio
async def test_handle_oauth_callback_updates_existing_user(db_session):
    service = AuthService(db_session)

    mock_profile = {
        "id": 99999,
        "login": "existinguser",
        "avatar_url": "https://avatars.githubusercontent.com/u/99999",
        "name": "Existing User",
        "bio": "Updated bio",
        "company": "ACME",
        "location": "Earth",
        "html_url": "https://github.com/existinguser",
    }

    with (
        patch.object(service.github, "exchange_code_for_token", new=AsyncMock(return_value="gh_token")),
        patch.object(service.github, "get_user_profile", new=AsyncMock(return_value=mock_profile)),
        patch.object(service.github, "get_primary_email", new=AsyncMock(return_value="existing@example.com")),
    ):
        # First call creates
        result1 = await service.handle_oauth_callback("code_1")
        # Second call updates
        result2 = await service.handle_oauth_callback("code_2")

    assert result1["user"].id == result2["user"].id
    assert result2["user"].bio == "Updated bio"