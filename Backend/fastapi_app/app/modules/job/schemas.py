"""Structured job description schema (spec §17, §21).

RequirementType and ImportanceLevel are reused directly from
app.models.enums rather than redefined here — those are the Master
Specification's own taxonomy (§6, §7) and already back the Postgres
`requirements`/`requirement_matches` tables from Phase 1, so a JD-parsed
Requirement and a persisted Requirement row speak the same vocabulary from
day one.
"""

import enum

from pydantic import BaseModel, Field

from app.models.enums import ImportanceLevel, RequirementType
from app.modules.resume.schemas import ExtractionStatus


class JDDocumentFormat(str, enum.Enum):
    PDF = "pdf"
    DOCX = "docx"
    TEXT = "text"


class JDDocumentMeta(BaseModel):
    """Like resume.schemas.DocumentMeta, but with a TEXT format — a resume
    is never pasted as raw text, but a JD very often is (spec §1), so this
    stays a JD-specific type rather than overloading the resume one."""

    format: JDDocumentFormat
    page_count: int | None = None
    raw_text: str
    cleaned_text: str
    extraction_status: ExtractionStatus = ExtractionStatus.OK


class JDCanonicalSection(str, enum.Enum):
    ABOUT_COMPANY = "ABOUT_COMPANY"
    SUMMARY = "SUMMARY"  # About the Role / Job Summary / Position Summary
    RESPONSIBILITIES = "RESPONSIBILITIES"
    QUALIFICATIONS_REQUIRED = "QUALIFICATIONS_REQUIRED"
    QUALIFICATIONS_PREFERRED = "QUALIFICATIONS_PREFERRED"
    SKILLS = "SKILLS"
    EXPERIENCE = "EXPERIENCE"
    EDUCATION = "EDUCATION"
    BENEFITS = "BENEFITS"
    ABOUT_YOU = "ABOUT_YOU"
    OTHER = "OTHER"


class LogicalOperator(str, enum.Enum):
    AND = "AND"
    OR = "OR"


class JDWarningCode(str, enum.Enum):
    LOW_EXTRACTED_TEXT = "low_extracted_text"
    POSSIBLE_SCANNED_PDF = "possible_scanned_pdf"
    EMPTY_DOCUMENT = "empty_document"
    AMBIGUOUS_SECTION = "ambiguous_section"
    LOW_CONFIDENCE_CLASSIFICATION = "low_confidence_classification"
    DUPLICATE_REQUIREMENTS = "duplicate_requirements"
    MALFORMED_EXPERIENCE_RANGE = "malformed_experience_range"
    UNSUPPORTED_LAYOUT = "unsupported_layout"
    MISSING_EXPECTED_SECTION = "missing_expected_section"


class JDParsingWarning(BaseModel):
    code: JDWarningCode
    message: str
    section: JDCanonicalSection | None = None


class JDDetectedSection(BaseModel):
    canonical_type: JDCanonicalSection
    heading_text: str
    confidence: float = Field(ge=0.0, le=1.0)
    start_line: int
    end_line: int


class JobMetadata(BaseModel):
    title: str | None = None
    company: str | None = None
    location: str | None = None
    employment_type: str | None = None
    experience: str | None = None  # raw text, e.g. "2-4 years"
    department: str | None = None
    work_mode: str | None = None  # remote / hybrid / on-site


class ExperienceRequirement(BaseModel):
    min_years: float | None = None
    max_years: float | None = None
    context: str | None = None
    raw_text: str


class QualificationEntry(BaseModel):
    text: str
    degree: str | None = None
    field: str | None = None
    raw_text: str


class Responsibility(BaseModel):
    text: str
    action: str | None = None
    object: str | None = None
    source_section: JDCanonicalSection | None = None


class Requirement(BaseModel):
    id: str
    text: str
    type: RequirementType
    canonical_entity: str | None = None  # normalization is Phase 4
    importance: ImportanceLevel = ImportanceLevel.UNKNOWN
    weight: float
    critical: bool = False
    confidence: float = Field(ge=0.0, le=1.0)
    source_section: JDCanonicalSection | None = None
    actions: list[str] = []
    technologies: list[str] = []
    experience: ExperienceRequirement | None = None
    operator: LogicalOperator | None = None


class StructuredJD(BaseModel):
    document: JDDocumentMeta
    metadata: JobMetadata = JobMetadata()
    sections: list[JDDetectedSection] = []

    requirements: list[Requirement] = []
    responsibilities: list[Responsibility] = []
    skills: list[str] = []
    qualifications: list[QualificationEntry] = []
    experience_requirements: list[ExperienceRequirement] = []

    warnings: list[JDParsingWarning] = []
