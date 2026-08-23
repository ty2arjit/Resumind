"""Python mirrors of the Postgres enum types Prisma created.

Values must stay in lockstep with the `enum` blocks in
Backend/prisma/schema.prisma — Prisma owns the migration, this file just
describes the same types for SQLAlchemy.
"""

import enum


class RequirementType(str, enum.Enum):
    SKILL = "SKILL"
    RESPONSIBILITY = "RESPONSIBILITY"
    EXPERIENCE = "EXPERIENCE"
    QUALIFICATION = "QUALIFICATION"
    PREFERRED_SKILL = "PREFERRED_SKILL"
    DOMAIN_KNOWLEDGE = "DOMAIN_KNOWLEDGE"
    OTHER = "OTHER"


class ImportanceLevel(str, enum.Enum):
    REQUIRED = "REQUIRED"
    PREFERRED = "PREFERRED"
    OPTIONAL = "OPTIONAL"
    UNKNOWN = "UNKNOWN"


class MatchStrength(str, enum.Enum):
    MISSING = "MISSING"
    WEAK = "WEAK"
    PARTIAL = "PARTIAL"
    STRONG = "STRONG"
    VERY_STRONG = "VERY_STRONG"
    UNKNOWN = "UNKNOWN"


class AnalysisMode(str, enum.Enum):
    JD = "JD"
    TARGET_PROFILE = "TARGET_PROFILE"
    COMBINED = "COMBINED"


class AnalysisStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class DocumentSourceType(str, enum.Enum):
    PDF = "PDF"
    DOCX = "DOCX"
    TEXT = "TEXT"
