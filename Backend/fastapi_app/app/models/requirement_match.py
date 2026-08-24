import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._types import pg_enum, uuid_column
from app.models.enums import MatchStrength


class RequirementMatch(Base):
    """The result of matching one Requirement against one Analysis's resume
    (spec §17, §26). Signal columns mirror the scoring formula components
    (w_k/w_s/w_e/w_c) so a score can be explained back to its inputs."""

    __tablename__ = "requirement_matches"
    __table_args__ = (UniqueConstraint("analysis_id", "requirement_id"),)

    id: Mapped[uuid.UUID] = mapped_column(uuid_column(), primary_key=True)
    analysis_id: Mapped[uuid.UUID] = mapped_column(uuid_column(), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False)
    requirement_id: Mapped[uuid.UUID] = mapped_column(
        uuid_column(), ForeignKey("requirements.id", ondelete="CASCADE"), nullable=False
    )

    match_strength: Mapped[MatchStrength] = mapped_column(
        pg_enum(MatchStrength, "match_strength"), default=MatchStrength.UNKNOWN
    )
    score: Mapped[float | None] = mapped_column(Float)

    keyword_signal: Mapped[float | None] = mapped_column(Float)
    semantic_signal: Mapped[float | None] = mapped_column(Float)
    evidence_signal: Mapped[float | None] = mapped_column(Float)
    context_signal: Mapped[float | None] = mapped_column(Float)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    analysis: Mapped["Analysis"] = relationship(back_populates="requirement_matches")
    requirement: Mapped["Requirement"] = relationship(back_populates="matches")
    evidence: Mapped[list["Evidence"]] = relationship(back_populates="requirement_match", cascade="all, delete-orphan")
