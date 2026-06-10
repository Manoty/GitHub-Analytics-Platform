# backend/tests/unit/test_security.py

import pytest
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_access_token,
    verify_refresh_token,
)
import uuid


def test_access_token_roundtrip():
    user_id = uuid.uuid4()
    token = create_access_token(subject=user_id)
    payload = verify_access_token(token)
    assert payload is not None
    assert payload["sub"] == str(user_id)
    assert payload["type"] == "access"


def test_refresh_token_roundtrip():
    user_id = uuid.uuid4()
    token = create_refresh_token(subject=user_id)
    payload = verify_refresh_token(token)
    assert payload is not None
    assert payload["sub"] == str(user_id)
    assert payload["type"] == "refresh"


def test_access_token_rejected_as_refresh():
    token = create_access_token(subject=uuid.uuid4())
    assert verify_refresh_token(token) is None


def test_refresh_token_rejected_as_access():
    token = create_refresh_token(subject=uuid.uuid4())
    assert verify_access_token(token) is None


def test_invalid_token_returns_none():
    assert verify_access_token("not.a.token") is None
    assert verify_refresh_token("not.a.token") is None