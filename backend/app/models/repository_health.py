

import uuid
from sqlalchemy import Float, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
from app.models.base import BaseModel


class RepositoryHealth(BaseModel):
    __tablename__ = "repository_health"

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Overall score 0–100
    health_score: Mapped[float] = mapped_column(Float, nullable=False)
    health_grade: Mapped[str] = mapped_column(String(20), nullable=False)  # Excellent/Good/Fair/Poor

    # Component scores (each 0–100)
    commit_frequency_score: Mapped[float] = mapped_column(Float, default=0.0)
    issue_resolution_score: Mapped[float] = mapped_column(Float, default=0.0)
    pr_merge_speed_score: Mapped[float] = mapped_column(Float, default=0.0)
    contributor_diversity_score: Mapped[float] = mapped_column(Float, default=0.0)

    # Raw metrics behind the scores
    commits_last_30_days: Mapped[int] = mapped_column(Integer, default=0)
    avg_issue_close_hours: Mapped[float] = mapped_column(Float, default=0.0)
    avg_pr_merge_hours: Mapped[float] = mapped_column(Float, default=0.0)
    active_contributors_last_30_days: Mapped[int] = mapped_column(Integer, default=0)
    total_contributors: Mapped[int] = mapped_column(Integer, default=0)

    # Insight blurbs auto-generated
    insights: Mapped[list | None] = mapped_column(JSONB, default=list, nullable=True)

    calculated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    repository: Mapped["Repository"] = relationship("Repository", back_populates="health_scores")

    def __repr__(self) -> str:
        return f"<RepositoryHealth {self.health_grade} ({self.health_score})>"