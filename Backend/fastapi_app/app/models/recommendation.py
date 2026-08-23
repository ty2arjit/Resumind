import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._types import uuid_column


class Recommendation(Base):
    """A rule-based recommendation attached to an Analysis (spec §41)."""

    __tablename__ = "recommendations"

    id: Mapped[uuid.UUID] = mapped_column(uuid_column(), primary_key=True)
    analysis_id: Mapped[uuid.UUID] = mapped_column(uuid_column(), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False)

    text: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(String)
    priority: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    analysis: Mapped["Analysis"] = relationship(back_populates="recommendations")
