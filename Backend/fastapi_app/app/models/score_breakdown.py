import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._types import uuid_column


class ScoreBreakdown(Base):
    """One category's contribution to an Analysis's overall score
    (spec §27-28)."""

    __tablename__ = "score_breakdowns"

    id: Mapped[uuid.UUID] = mapped_column(uuid_column(), primary_key=True)
    analysis_id: Mapped[uuid.UUID] = mapped_column(uuid_column(), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False)

    category: Mapped[str] = mapped_column(String, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    analysis: Mapped["Analysis"] = relationship(back_populates="score_breakdowns")
