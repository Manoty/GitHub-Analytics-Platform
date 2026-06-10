# backend/app/api/deps.py

from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.security import verify_access_token
from app.models.user import User
from app.services.auth_service import AuthService

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Extract and validate the Bearer JWT.
    Returns the User or raises 401.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise credentials_exception

    payload = verify_access_token(credentials.credentials)
    if payload is None:
        raise credentials_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    service = AuthService(db)
    user = await service.get_user_by_id(user_id)

    if user is None or not user.is_active:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Alias that also checks is_active (already checked above, kept for clarity)."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# Type alias for use in endpoint signatures
CurrentUser = Annotated[User, Depends(get_current_active_user)]
DBSession = Annotated[AsyncSession, Depends(get_db)]