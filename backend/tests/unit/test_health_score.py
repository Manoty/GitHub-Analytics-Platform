# backend/tests/unit/test_health_score.py

import pytest
from app.services.health_score_service import HealthScoreService


def test_commit_frequency_scoring():
    assert HealthScoreService._score_commit_frequency(0) == 0.0
    assert HealthScoreService._score_commit_frequency(30) == 100.0
    assert HealthScoreService._score_commit_frequency(15) == 50.0
    assert HealthScoreService._score_commit_frequency(100) == 100.0  # capped


def test_pr_merge_speed_scoring():
    assert HealthScoreService._score_pr_merge_speed(None) == 50.0
    assert HealthScoreService._score_pr_merge_speed(24) == 100.0
    assert HealthScoreService._score_pr_merge_speed(336) == 0.0
    score = HealthScoreService._score_pr_merge_speed(48)
    assert 0 < score < 100


def test_issue_resolution_scoring():
    assert HealthScoreService._score_issue_resolution(None) == 50.0
    assert HealthScoreService._score_issue_resolution(48) == 100.0
    assert HealthScoreService._score_issue_resolution(720) == 0.0


def test_contributor_diversity_scoring():
    assert HealthScoreService._score_contributor_diversity(0, 0) == 0.0
    assert HealthScoreService._score_contributor_diversity(10, 3) == 100.0
    assert HealthScoreService._score_contributor_diversity(1, 1) > 0


def test_grade():
    assert HealthScoreService._grade(85) == "Excellent"
    assert HealthScoreService._grade(65) == "Good"
    assert HealthScoreService._grade(45) == "Fair"
    assert HealthScoreService._grade(20) == "Poor"


def test_insights_inactive_repo():
    insights = HealthScoreService._generate_insights(0, None, None, 1, 0, 10)
    assert any("inactive" in i.lower() or "no commits" in i.lower() for i in insights)
    assert any("bus factor" in i.lower() for i in insights)


def test_insights_healthy_repo():
    insights = HealthScoreService._generate_insights(25, 12.0, 30.0, 8, 4, 85)
    assert any("healthy" in i.lower() for i in insights)
    assert any("quickly" in i.lower() or "rapidly" in i.lower() for i in insights)