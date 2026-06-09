

import uuid
from sqlalchemy import String, Text, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.models.base import BaseModel


class Contributor(BaseModel):
    __tablename__ = "contributors"

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    github_login: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    github_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    contributions_count: Mapped[int] = mapped_column(Integer, default=0)
    commits_count: Mapped[int] = mapped_column(Integer, default=0)
    pull_requests_count: Mapped[int] = mapped_column(Integer, default=0)
    issues_count: Mapped[int] = mapped_column(Integer, default=0)
    additions: Mapped[int] = mapped_column(Integer, default=0)
    deletions: Mapped[int] = mapped_column(Integer, default=0)
    first_contribution_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_contribution_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    activity_score: Mapped[float] = mapped_column(Float, default=0.0)

    repository: Mapped["Repository"] = relationship("Repository", back_populates="contributors")

    def __repr__(self) -> str:
        return f"<Contributor {self.github_login}>"