

import uuid
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import enum
from app.models.base import BaseModel


class IssueState(str, enum.Enum):
    OPEN = "open"
    CLOSED = "closed"


class Issue(BaseModel):
    __tablename__ = "issues"

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    github_issue_number: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    state: Mapped[IssueState] = mapped_column(Enum(IssueState), nullable=False, index=True)
    author_login: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    labels: Mapped[list | None] = mapped_column(JSONB, default=list, nullable=True)
    comments_count: Mapped[int] = mapped_column(Integer, default=0)

    github_created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    github_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    github_closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Derived metric
    time_to_close_hours: Mapped[float | None] = mapped_column(nullable=True)

    repository: Mapped["Repository"] = relationship("Repository", back_populates="issues")

    def __repr__(self) -> str:
        return f"<Issue #{self.github_issue_number}>"