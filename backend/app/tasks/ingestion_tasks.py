# backend/app/tasks/ingestion_tasks.py

import asyncio
import uuid
from celery import shared_task
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.tasks.celery_app import celery_app
from app.db.session import async_engine
from app.services.ingestion_service import IngestionService
from app.services.github_service import GitHubService
from app.models.user import User
from sqlalchemy import select


def _run(coro):
    """Run an async coroutine from a sync Celery task."""
    return asyncio.get_event_loop().run_until_complete(coro)


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name="tasks.sync_repository",
)
def sync_repository_task(self, repository_id: str, user_id: str):
    """
    Celery task: sync one repository.
    Retries up to 3 times on failure with a 60s delay.
    """
    async def _sync():
        AsyncSessionLocal = async_sessionmaker(
            bind=async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        async with AsyncSessionLocal() as session:
            # Fetch the user's GitHub token
            result = await session.execute(
                select(User).where(User.id == uuid.UUID(user_id))
            )
            user = result.scalar_one_or_none()
            if not user or not user.access_token:
                raise ValueError(f"User {user_id} not found or missing token")

            github = GitHubService(access_token=user.access_token)
            ingestion = IngestionService(db=session, github=github)

            try:
                await ingestion.sync_repository(uuid.UUID(repository_id))
                await session.commit()
            finally:
                await github.close()

    try:
        _run(_sync())
    except Exception as exc:
        raise self.retry(exc=exc)