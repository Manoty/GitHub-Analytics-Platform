# backend/app/api/v1/endpoints/repositories.py

import uuid
from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from sqlalchemy import select, func

from app.api.deps import CurrentUser, DBSession
from app.models.repository import Repository, SyncStatus
from app.models.user import User
from app.schemas.repository import (
    RepositoryRead,
    RepositoryConnect,
    RepositoryListResponse,
    GitHubRepoPreview,
)
from app.services.github_service import GitHubService
from app.tasks.ingestion_tasks import sync_repository_task

router = APIRouter(prefix="/repositories", tags=["Repositories"])


@router.get("", response_model=RepositoryListResponse, summary="List connected repositories")
async def list_repositories(
    current_user: CurrentUser,
    db: DBSession,
    skip: int = 0,
    limit: int = 20,
):
    total_result = await db.execute(
        select(func.count(Repository.id)).where(Repository.owner_id == current_user.id)
    )
    total = total_result.scalar_one()

    result = await db.execute(
        select(Repository)
        .where(Repository.owner_id == current_user.id)
        .order_by(Repository.updated_at.desc())
        .offset(skip)
        .limit(limit)
    )
    repos = result.scalars().all()
    return RepositoryListResponse(items=list(repos), total=total)


@router.get("/github", response_model=list[GitHubRepoPreview], summary="List user GitHub repos")
async def list_github_repositories(current_user: CurrentUser):
    """Fetch all repos from GitHub the user has access to (not yet connected)."""
    if not current_user.access_token:
        raise HTTPException(status_code=400, detail="No GitHub token available")

    github = GitHubService(access_token=current_user.access_token)
    try:
        raw_repos = await github.get_user_repositories()
    finally:
        await github.close()

    return [
        GitHubRepoPreview(
            github_id=r["id"],
            full_name=r["full_name"],
            name=r["name"],
            description=r.get("description"),
            language=r.get("language"),
            stars_count=r.get("stargazers_count", 0),
            forks_count=r.get("forks_count", 0),
            is_private=r.get("private", False),
            github_updated_at=r.get("updated_at"),
        )
        for r in raw_repos
    ]


@router.post("", response_model=RepositoryRead, status_code=status.HTTP_201_CREATED, summary="Connect a repository")
async def connect_repository(
    payload: RepositoryConnect,
    current_user: CurrentUser,
    db: DBSession,
):
    """Connect a GitHub repo and immediately queue an ingestion sync."""
    # Check not already connected
    existing = await db.execute(
        select(Repository).where(
            Repository.owner_id == current_user.id,
            Repository.full_name == payload.full_name,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Repository already connected")

    # Fetch metadata from GitHub to populate initial record
    github = GitHubService(access_token=current_user.access_token)
    try:
        data = await github.get_repository(payload.full_name)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=f"Repository not found on GitHub: {exc}")
    finally:
        await github.close()

    repo = Repository(
        owner_id=current_user.id,
        github_id=data["id"],
        full_name=data["full_name"],
        name=data["name"],
        description=data.get("description"),
        language=data.get("language"),
        stars_count=data.get("stargazers_count", 0),
        forks_count=data.get("forks_count", 0),
        watchers_count=data.get("watchers_count", 0),
        open_issues_count=data.get("open_issues_count", 0),
        is_private=data.get("private", False),
        sync_status=SyncStatus.PENDING,
    )
    db.add(repo)
    await db.flush()
    await db.refresh(repo)

    # Queue ingestion
    sync_repository_task.delay(str(repo.id), str(current_user.id))

    return repo


@router.get("/{repo_id}", response_model=RepositoryRead, summary="Get repository detail")
async def get_repository(repo_id: uuid.UUID, current_user: CurrentUser, db: DBSession):
    result = await db.execute(
        select(Repository).where(
            Repository.id == repo_id,
            Repository.owner_id == current_user.id,
        )
    )
    repo = result.scalar_one_or_none()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    return repo


@router.post("/{repo_id}/sync", response_model=RepositoryRead, summary="Trigger re-sync")
async def trigger_sync(repo_id: uuid.UUID, current_user: CurrentUser, db: DBSession):
    result = await db.execute(
        select(Repository).where(
            Repository.id == repo_id,
            Repository.owner_id == current_user.id,
        )
    )
    repo = result.scalar_one_or_none()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    if repo.sync_status == SyncStatus.SYNCING:
        raise HTTPException(status_code=409, detail="Sync already in progress")

    repo.sync_status = SyncStatus.PENDING
    await db.flush()

    sync_repository_task.delay(str(repo.id), str(current_user.id))
    return repo


@router.delete("/{repo_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Disconnect repository")
async def disconnect_repository(repo_id: uuid.UUID, current_user: CurrentUser, db: DBSession):
    result = await db.execute(
        select(Repository).where(
            Repository.id == repo_id,
            Repository.owner_id == current_user.id,
        )
    )
    repo = result.scalar_one_or_none()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    await db.delete(repo)
    await db.flush()