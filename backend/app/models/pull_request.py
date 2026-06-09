

import uuid
from sqlalchemy import String, Text, Integer, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import enum
from app.models.base import BaseModel


class PRState(str, enum.Enum):
    OPEN = "open"
    CLOSED = "closed"
    MERGED = "merged"


class PullRequest(BaseModel):
    __tablename__ = "pull_requests"

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    github_pr_number: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    state: Mapped[PRState] = mapped_column(Enum(PRState), nullable=False, index=True)
    author_login: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    is_merged: Mapped[bool] = mapped_column(Boolean, default=False)
    additions: Mapped[int] = mapped_column(Integer, default=0)
    deletions: Mapped[int] = mapped_column(Integer, default=0)
    changed_files: Mapped[int] = mapped_column(Integer, default=0)
    comments_count: Mapped[int] = mapped_column(Integer, default=0)
    review_comments_count: Mapped[int] = mapped_column(Integer, default=0)
    commits_count: Mapped[int] = mapped_column(Integer, default=0)

    # Timestamps
    github_created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    github_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    github_closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    github_merged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Derived metric — stored to avoid recalculation
    time_to_merge_hours: Mapped[float | None] = mapped_column(nullable=True)

    repository: Mapped["Repository"] = relationship("Repository", back_populates="pull_requests")

    def __repr__(self) -> str:
        return f"<PullRequest #{self.github_pr_number}>"