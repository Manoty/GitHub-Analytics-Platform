# backend/tests/unit/test_ingestion.py

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from app.services.ingestion_service import IngestionService


def test_parse_dt_valid():
    result = IngestionService._parse_dt("2024-01-15T10:30:00Z")
    assert result is not None
    assert result.year == 2024


def test_parse_dt_none():
    assert IngestionService._parse_dt(None) is None


def test_parse_dt_invalid():
    assert IngestionService._parse_dt("not-a-date") is None


def test_parse_dt_with_offset():
    result = IngestionService._parse_dt("2024-06-01T12:00:00+03:00")
    assert result is not None
    assert result.tzinfo is not None