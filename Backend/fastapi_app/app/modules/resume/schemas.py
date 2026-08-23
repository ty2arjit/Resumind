"""Structured resume schema (spec §4, §19).

These are the module's internal Pydantic types — the output of
ResumeParser.parse(). Separate from app/schemas (Phase 1's API-facing
schemas) because this shape is parser-internal and will keep evolving
through Phase 2 iterations without needing to touch API contracts.
"""

import enum

from pydantic import BaseModel, Field


class DocumentFormat(str, enum.Enum):
    PDF = "pdf"
    DOCX = "docx"


class ExtractionStatus(str, enum.Enum):
    OK = "ok"
    LOW_TEXT = "low_text"
    EMPTY = "empty"


class CanonicalSection(str, enum.Enum):
    SUMMARY = "SUMMARY"
    EDUCATION = "EDUCATION"
    EXPERIENCE = "EXPERIENCE"
    PROJECTS = "PROJECTS"
    SKILLS = "SKILLS"
    CERTIFICATIONS = "CERTIFICATIONS"
    ACHIEVEMENTS = "ACHIEVEMENTS"
    PUBLICATIONS = "PUBLICATIONS"
    LEADERSHIP = "LEADERSHIP"
    EXTRACURRICULAR = "EXTRACURRICULAR"
    INTERESTS = "INTERESTS"
    CONTACT = "CONTACT"
    OTHER = "OTHER"


class WarningCode(str, enum.Enum):
    LOW_EXTRACTED_TEXT = "low_extracted_text"
    POSSIBLE_SCANNED_PDF = "possible_scanned_pdf"
    EMPTY_DOCUMENT = "empty_document"
    AMBIGUOUS_SECTION = "ambiguous_section"
    MALFORMED_DATE = "malformed_date"
    UNSUPPORTED_LAYOUT = "unsupported_layout"
    DUPLICATE_CONTENT_REMOVED = "duplicate_content_removed"
    MISSING_EXPECTED_SECTION = "missing_expected_section"
    AMBIGUOUS_EXPERIENCE_HEADER = "ambiguous_experience_header"
    AMBIGUOUS_EDUCATION_ENTRY = "ambiguous_education_entry"
    MULTIPLE_SECTIONS_MERGED = "multiple_sections_merged"


class ParsingWarning(BaseModel):
    code: WarningCode
    message: str
    section: CanonicalSection | None = None


class DocumentMeta(BaseModel):
    format: DocumentFormat
    page_count: int | None = None
    raw_text: str
    cleaned_text: str
    extraction_status: ExtractionStatus = ExtractionStatus.OK


class DetectedSection(BaseModel):
    canonical_type: CanonicalSection
    heading_text: str
    confidence: float = Field(ge=0.0, le=1.0)
    start_line: int
    end_line: int


class ContactInfo(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    linkedin: str | None = None
    github: str | None = None
    website: str | None = None
    location: str | None = None


class DateRange(BaseModel):
    start_text: str | None = None
    end_text: str | None = None
    start_normalized: str | None = None  # "YYYY-MM" or "YYYY"
    end_normalized: str | None = None
    is_current: bool = False
    duration_months: int | None = None


class EducationEntry(BaseModel):
    institution: str | None = None
    degree: str | None = None
    field: str | None = None
    dates: DateRange | None = None
    gpa: str | None = None
    percentage: str | None = None
    coursework: list[str] = []
    raw_text: str


class Evidence(BaseModel):
    """A single bullet, structurally decomposed. NOT a requirement match —
    this only records what the resume states (spec §20)."""

    text: str
    section: CanonicalSection
    position: str | None = None  # e.g. the role/project this bullet belongs to
    actions: list[str] = []
    technologies: list[str] = []
    metrics: list[str] = []
    objects: list[str] = []


class ExperienceEntry(BaseModel):
    organization: str | None = None
    role: str | None = None
    location: str | None = None
    dates: DateRange | None = None
    bullets: list[str] = []
    technologies: list[str] = []
    raw_header: str


class ProjectEntry(BaseModel):
    name: str | None = None
    description: str | None = None
    bullets: list[str] = []
    technologies: list[str] = []
    links: list[str] = []
    raw_header: str


class SkillCategory(BaseModel):
    category: str  # e.g. "programming_languages", "frameworks", "other"
    category_label: str | None = None  # raw label from the resume, if any
    items: list[str] = []


class StructuredResume(BaseModel):
    document: DocumentMeta
    sections: list[DetectedSection] = []

    contact: ContactInfo = ContactInfo()
    summary: str | None = None

    education: list[EducationEntry] = []
    experience: list[ExperienceEntry] = []
    projects: list[ProjectEntry] = []
    skills: list[SkillCategory] = []

    certifications: list[str] = []
    achievements: list[str] = []
    leadership: list[str] = []
    extracurriculars: list[str] = []
    publications: list[str] = []
    interests: list[str] = []

    evidence: list[Evidence] = []
    warnings: list[ParsingWarning] = []
