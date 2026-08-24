"""Builds the top-level `qualifications` view (spec §11, §21) from
QUALIFICATION-typed requirements. Degree/field extraction mirrors the
resume parser's education.py at a conceptual level, but stays independent
since the two sides mean different things (a candidate's actual degree vs
a JD's required degree) — not worth a shared abstraction for two short
regexes.
"""

import re

from app.modules.job.schemas import QualificationEntry, Requirement

_DEGREE_RE = re.compile(
    r"\b(B\.?\s?Tech|M\.?\s?Tech|B\.?\s?E|M\.?\s?E|Bachelor(?:'?s)?|Master(?:'?s)?|"
    r"B\.?\s?Sc|M\.?\s?Sc|Ph\.?\s?D|Doctorate|Diploma|MBA|BBA|BCA|MCA)\b",
    re.IGNORECASE,
)
_FIELD_RE = re.compile(r"\b(?:in|of)\s+([A-Za-z][A-Za-z &,\-]{2,60})", re.IGNORECASE)


def build_qualifications(requirements: list[Requirement]) -> list[QualificationEntry]:
    qualifications = []
    for req in requirements:
        if req.type.value != "QUALIFICATION":
            continue
        degree_match = _DEGREE_RE.search(req.text)
        field_match = _FIELD_RE.search(req.text)
        qualifications.append(
            QualificationEntry(
                text=req.text,
                degree=degree_match.group(0).strip() if degree_match else None,
                field=field_match.group(1).strip(" .,") if field_match else None,
                raw_text=req.text,
            )
        )
    return qualifications
