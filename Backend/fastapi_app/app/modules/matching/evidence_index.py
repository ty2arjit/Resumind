"""Builds the matchable evidence pool from a Phase 2 StructuredResume
(spec §2 — "consume Phase 2 output", never re-parse it).

Built once per resume and reused across every requirement comparison,
rather than re-derived per call.
"""

from app.modules.matching.schemas import EvidenceContext, MatchableEvidence
from app.modules.resume.schemas import CanonicalSection, StructuredResume

_SECTION_TO_CONTEXT = {
    CanonicalSection.EXPERIENCE: EvidenceContext.EXPERIENCE,
    CanonicalSection.PROJECTS: EvidenceContext.PROJECT,
}


def build_evidence_index(resume: StructuredResume) -> list[MatchableEvidence]:
    items: list[MatchableEvidence] = []
    counter = 0

    def next_id() -> str:
        nonlocal counter
        counter += 1
        return f"ev_{counter:03d}"

    for evidence in resume.evidence:
        context = _SECTION_TO_CONTEXT.get(evidence.section, EvidenceContext.OTHER)
        items.append(
            MatchableEvidence(
                id=next_id(),
                text=evidence.text,
                context=context,
                technologies=evidence.technologies,
                actions=evidence.actions,
                position=evidence.position,
            )
        )

    for category in resume.skills:
        for skill in category.items:
            items.append(
                MatchableEvidence(
                    id=next_id(),
                    text=skill,
                    context=EvidenceContext.SKILLS,
                    technologies=[skill],
                )
            )

    for entry in resume.education:
        items.append(
            MatchableEvidence(
                id=next_id(),
                text=entry.raw_text,
                context=EvidenceContext.EDUCATION,
                position=entry.institution,
            )
        )

    for cert_text in resume.certifications:
        items.append(MatchableEvidence(id=next_id(), text=cert_text, context=EvidenceContext.CERTIFICATION))

    for achievement_text in resume.achievements:
        items.append(MatchableEvidence(id=next_id(), text=achievement_text, context=EvidenceContext.OTHER))

    if resume.summary:
        items.append(MatchableEvidence(id=next_id(), text=resume.summary, context=EvidenceContext.SUMMARY))

    return items
