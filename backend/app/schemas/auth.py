# backend/app/schemas/auth.py

from pydantic import BaseModel
from app.schemas.user import UserRead


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenWithUser(TokenResponse):
    user: UserRead


class RefreshRequest(BaseModel):
    refresh_token: str


class GitHubOAuthURLResponse(BaseModel):
    url: str