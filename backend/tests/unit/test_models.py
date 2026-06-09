# backend/tests/unit/test_models.py

import pytest
from datetime import datetime, timezone
from app.models.user import User
from app.models.repository import Repository, SyncStatus
from app.models.commit import Commit
from app.models.pull_request import PullRequest, PRState
from app.models.issue import Issue, IssueState
from app.models.contributor import Contributor
from app.models.repository_health import RepositoryHealth


def test_user_repr():
    user = User(github_id=1, username="octocat")
    assert "octocat" in repr(user)


def test_repository_defaults():
    repo = Repository(
        github_id=999,
        full_name="octocat/hello-world",
        name="hello-world",
        owner_id=None,
    )
    assert repo.sync_status == SyncStatus.PENDING
    assert repo.is_connected is True
    assert repo.stars_count == 0


def test_pull_request_state_enum():
    pr = PullRequest(
        github_pr_number=1,
        state=PRState.MERGED,
        repository_id=None,
    )
    assert pr.state == PRState.MERGED
    assert pr.is_merged is False  # default; set by ingestion service


def test_issue_state_enum():
    issue = Issue(
        github_issue_number=42,
        state=IssueState.OPEN,
        repository_id=None,
    )
    assert issue.state == IssueState.OPEN


def test_health_score_grade():
    health = RepositoryHealth(
        repository_id=None,
        health_score=87.5,
        health_grade="Excellent",
    )
    assert health.health_grade == "Excellent"
    assert health.health_score == 87.5


def test_contributor_defaults():
    contributor = Contributor(
        github_login="torvalds",
        repository_id=None,
    )
    assert contributor.contributions_count == 0
    assert contributor.activity_score == 0.0