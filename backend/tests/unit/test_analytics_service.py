# backend/tests/unit/test_analytics_service.py

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.analytics_service import AnalyticsService


@pytest.mark.asyncio
async def test_language_distribution_empty(db_session):
    service = AnalyticsService(db_session)
    import uuid
    result = await service.get_language_distribution(uuid.uuid4())
    assert result == []


@pytest.mark.asyncio
async def test_productivity_metrics_structure(db_session):
    service = AnalyticsService(db_session)
    import uuid
    result = await service.get_productivity_metrics(uuid.uuid4(), days=30)
    assert "commits" in result
    assert "prs_merged" in result
    assert "issues_closed" in result
    assert "active_contributors" in result
    assert "deployment_frequency_per_week" in result
    assert "contributor_velocity" in result
    assert result["period_days"] == 30


@pytest.mark.asyncio
async def test_trend_signals_structure(db_session):
    service = AnalyticsService(db_session)
    import uuid
    result = await service.get_trend_signals(uuid.uuid4())
    assert "commits" in result
    assert "pull_requests" in result
    assert "direction" in result["commits"]
    assert "pct_change" in result["commits"]


@pytest.mark.asyncio
async def test_repository_overview_structure(db_session):
    service = AnalyticsService(db_session)
    import uuid
    result = await service.get_repository_overview(uuid.uuid4())
    assert "total_commits" in result
    assert "total_pull_requests" in result
    assert "total_contributors" in result
    assert "health_score" in result
    assert result["total_commits"] == 0