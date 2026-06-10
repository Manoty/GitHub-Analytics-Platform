# backend/app/schemas/repository.py

import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.repository import SyncStatus


class RepositoryBase(BaseModel):
    full_name: str
    name: str
    description: str | None = None
    language: str | None = None
    stars_count: int = 0
    forks_count: int = 0
    is_private: bool = False


class RepositoryRead(RepositoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    github_id: int
    owner_id: uuid.UUID
    topics: list[str] | None = []
    languages_data: dict | None = {}
    watchers_count: int = 0
    open_issues_count: int = 0
    is_fork: bool = False
    is_archived: bool = False
    is_connected: bool = True
    sync_status: SyncStatus
    last_synced_at: datetime | None = None
    github_created_at: datetime | None = None
    github_updated_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class RepositoryConnect(BaseModel):
    full_name: str  # e.g. "torvalds/linux"


class RepositoryListResponse(BaseModel):
    items: list[RepositoryRead]
    total: int


class GitHubRepoPreview(BaseModel):
    """Shape returned when listing user's GitHub repos before connecting."""
    github_id: int
    full_name: str
    name: str
    description: str | None = None
    language: str | None = None
    stars_count: int
    forks_count: int
    is_private: bool
    github_updated_at: datetime | None = None