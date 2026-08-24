import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._types import uuid_column


class Evidence(Base):
    """A resume bullet/snippet retrieved as support for a RequirementMatch
    (spec §9, §24-25). The original text is always preserved for
    explainability."""

    __tablename__ = "evidence"

    id: Mapped[uuid.UUID] = mapped_column(uuid_column(), primary_key=True)
    requirement_match_id: Mapped[uuid.UUID] = mapped_column(
        uuid_column(), ForeignKey("requirement_matches.id", ondelete="CASCADE"), nullable=False
    )

    text: Mapped[str] = mapped_column(Text, nullable=False)
    section: Mapped[str | None] = mapped_column(String)
    position: Mapped[str | None] = mapped_column(String)
    technologies: Mapped[list | None] = mapped_column(JSONB)
    actions: Mapped[list | None] = mapped_column(JSONB)
    objects: Mapped[list | None] = mapped_column(JSONB)
    metrics: Mapped[list | None] = mapped_column(JSONB)
    relevance_score: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    requirement_match: Mapped["RequirementMatch"] = relationship(back_populates="evidence")
