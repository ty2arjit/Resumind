import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._types import pg_enum, uuid_column
from app.models.enums import AnalysisMode, AnalysisStatus


class Analysis(Base):
    """One analysis run (spec §40, §44).

    Score fields are nullable: a row is created in PENDING state before the
    (future) scoring engine has produced anything, so Analysis is usable as
    a request/job record from Phase 1 onward rather than only after scoring
    exists.
    """

    __tablename__ = "analyses"

    id: Mapped[uuid.UUID] = mapped_column(uuid_column(), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(uuid_column(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    resume_version_id: Mapped[uuid.UUID] = mapped_column(
        uuid_column(), ForeignKey("resume_versions.id", ondelete="CASCADE"), nullable=False
    )
    job_description_id: Mapped[uuid.UUID | None] = mapped_column(
        uuid_column(), ForeignKey("job_descriptions.id", ondelete="SET NULL")
    )
    target_profile_id: Mapped[uuid.UUID | None] = mapped_column(
        uuid_column(), ForeignKey("target_profiles.id", ondelete="SET NULL")
    )
    mode: Mapped[AnalysisMode] = mapped_column(pg_enum(AnalysisMode, "analysis_mode"), nullable=False)
    status: Mapped[AnalysisStatus] = mapped_column(
        pg_enum(AnalysisStatus, "analysis_status"), default=AnalysisStatus.PENDING
    )

    algorithm_version: Mapped[str | None] = mapped_column(String)
    scoring_config_version: Mapped[str | None] = mapped_column(String)
    embedding_model_version: Mapped[str | None] = mapped_column(String)

    ats_alignment_score: Mapped[float | None] = mapped_column(Float)
    resume_quality_score: Mapped[float | None] = mapped_column(Float)
    target_fit_score: Mapped[float | None] = mapped_column(Float)

    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="analyses")
    resume_version: Mapped["ResumeVersion"] = relationship(back_populates="analyses")
    job_description: Mapped["JobDescription"] = relationship(back_populates="analyses")
    target_profile: Mapped["TargetProfile"] = relationship(back_populates="analyses")

    requirement_matches: Mapped[list["RequirementMatch"]] = relationship(
        back_populates="analysis", cascade="all, delete-orphan"
    )
    score_breakdowns: Mapped[list["ScoreBreakdown"]] = relationship(
        back_populates="analysis", cascade="all, delete-orphan"
    )
    recommendations: Mapped[list["Recommendation"]] = relationship(
        back_populates="analysis", cascade="all, delete-orphan"
    )
