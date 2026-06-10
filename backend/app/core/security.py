# backend/app/core/security.py

from datetime import datetime, timedelta, timezone
from typing import Any
import uuid

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ─── Token schemas ─────────────────────────────────

def create_access_token(
    subject: str | uuid.UUID,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Create a short-lived JWT access token."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.jwt_access_token_expire_minutes)

    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": now,
        "exp": expire,
        "type": "access",
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(subject: str | uuid.UUID) -> str:
    """Create a long-lived JWT refresh token."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.jwt_refresh_token_expire_days)

    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": now,
        "exp": expire,
        "type": "refresh",
        "jti": str(uuid.uuid4()),  # unique token ID for revocation support
    }

    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT.
    Raises JWTError on failure — callers handle the exception.
    """
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )


def verify_access_token(token: str) -> dict[str, Any] | None:
    """Return payload dict or None if token is invalid/expired."""
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None


def verify_refresh_token(token: str) -> dict[str, Any] | None:
    """Return payload dict or None if refresh token is invalid/expired."""
    try:
        payload = decode_token(token)
        if payload.get("type") != "refresh":
            return None
        return payload
    except JWTError:
        return None