import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._types import uuid_column


class EvaluationCase(Base):
    """A labelled benchmark case for the future evaluation framework
    (spec §52-56)."""

    __tablename__ = "evaluation_cases"

    id: Mapped[uuid.UUID] = mapped_column(uuid_column(), primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    job_description_text: Mapped[str] = mapped_column(Text, nullable=False)
    resume_text: Mapped[str] = mapped_column(Text, nullable=False)
    ground_truth: Mapped[dict] = mapped_column(JSONB, nullable=False)
    human_overall_score: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    results: Mapped[list["EvaluationResult"]] = relationship(
        back_populates="evaluation_case", cascade="all, delete-orphan"
    )


class EvaluationResult(Base):
    """One benchmark run's result for one EvaluationCase, tied to the
    algorithm version it was measured against (spec §56 — regression
    testing)."""

    __tablename__ = "evaluation_results"

    id: Mapped[uuid.UUID] = mapped_column(uuid_column(), primary_key=True)
    evaluation_case_id: Mapped[uuid.UUID] = mapped_column(
        uuid_column(), ForeignKey("evaluation_cases.id", ondelete="CASCADE"), nullable=False
    )
    algorithm_version: Mapped[str] = mapped_column(String, nullable=False)
    metrics: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    evaluation_case: Mapped["EvaluationCase"] = relationship(back_populates="results")
