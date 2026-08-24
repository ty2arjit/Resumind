"""Builds the richer EvidenceItem pool from a Phase 2 StructuredResume.

Mirrors app.modules.matching.evidence_index's traversal order and ID
scheme exactly ("ev_001", "ev_002", ...) so a Phase 6 EvidenceItem and
the corresponding Phase 5 MatchableEvidence for the same resume always
share the same id. It is a richer VIEW of the same underlying resume
data (adds metrics/objects/organization, already present on Phase 2's
structures, for display and quality analysis) — not a second
implementation of matching or extraction logic.
"""

from app.modules.evidence.schemas import EvidenceItem, EvidenceSourceType
from app.modules.resume.schemas import CanonicalSection, StructuredResume

_SECTION_TO_SOURCE = {
    CanonicalSection.EXPERIENCE: EvidenceSourceType.EXPERIENCE_BULLET,
    CanonicalSection.PROJECTS: EvidenceSourceType.PROJECT_BULLET,
}


def build_evidence_pool(resume: StructuredResume, resume_version_id: str | None = None) -> list[EvidenceItem]:
    items: list[EvidenceItem] = []
    counter = 0

    def next_id() -> str:
        nonlocal counter
        counter += 1
        return f"ev_{counter:03d}"

    organization_by_position: dict[str, str | None] = {
        entry.role: entry.organization for entry in resume.experience if entry.role
    }

    for evidence in resume.evidence:
        source = _SECTION_TO_SOURCE.get(evidence.section, EvidenceSourceType.OTHER)
        items.append(
            EvidenceItem(
                id=next_id(),
                resume_version_id=resume_version_id,
                text=evidence.text,
                section=source,
                source_type="BULLET",
                position=evidence.position,
                organization=organization_by_position.get(evidence.position or ""),
                technologies=evidence.technologies,
                actions=evidence.actions,
                metrics=evidence.metrics,
                objects=evidence.objects,
            )
        )

    for category in resume.skills:
        for skill in category.items:
            items.append(
                EvidenceItem(
                    id=next_id(),
                    resume_version_id=resume_version_id,
                    text=skill,
                    section=EvidenceSourceType.SKILLS_SECTION,
                    source_type="SKILL_MENTION",
                    technologies=[skill],
                )
            )

    for entry in resume.education:
        items.append(
            EvidenceItem(
                id=next_id(),
                resume_version_id=resume_version_id,
                text=entry.raw_text,
                section=EvidenceSourceType.EDUCATION,
                source_type="EDUCATION_ENTRY",
                position=entry.institution,
            )
        )

    for cert_text in resume.certifications:
        items.append(
            EvidenceItem(
                id=next_id(),
                resume_version_id=resume_version_id,
                text=cert_text,
                section=EvidenceSourceType.CERTIFICATION,
                source_type="CERTIFICATION_ENTRY",
            )
        )

    for achievement_text in resume.achievements:
        items.append(
            EvidenceItem(
                id=next_id(),
                resume_version_id=resume_version_id,
                text=achievement_text,
                section=EvidenceSourceType.ACHIEVEMENT,
                source_type="ACHIEVEMENT_ENTRY",
            )
        )

    if resume.summary:
        items.append(
            EvidenceItem(
                id=next_id(),
                resume_version_id=resume_version_id,
                text=resume.summary,
                section=EvidenceSourceType.SUMMARY,
                source_type="SUMMARY",
            )
        )

    return items
