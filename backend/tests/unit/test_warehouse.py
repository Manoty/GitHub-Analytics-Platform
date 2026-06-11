# backend/tests/unit/test_warehouse.py

import pytest
from unittest.mock import MagicMock, patch


def test_warehouse_is_singleton():
    from app.utils.warehouse import WarehouseManager
    a = WarehouseManager()
    b = WarehouseManager()
    assert a is b


def test_grade_boundaries():
    from app.services.health_score_service import HealthScoreService
    assert HealthScoreService._grade(100) == "Excellent"
    assert HealthScoreService._grade(80) == "Excellent"
    assert HealthScoreService._grade(79) == "Good"
    assert HealthScoreService._grade(60) == "Good"
    assert HealthScoreService._grade(59) == "Fair"
    assert HealthScoreService._grade(40) == "Fair"
    assert HealthScoreService._grade(39) == "Poor"
    assert HealthScoreService._grade(0) == "Poor"