"""Role normalization (spec §10-11). Same resolution order as skill
normalization, minus the ambiguity list — role phrasing is closer to
natural language than technology names, so an unrecognized role is just
UNKNOWN rather than a candidate for a separate ambiguity registry.
"""

from app.modules.normalization.registry import get_role_registry
from app.modules.normalization.schemas import NormalizationMethod, NormalizationStatus, NormalizedRole
from app.modules.normalization.text_utils import clean_text, formatting_key, normalized_text


def normalize_role(raw_role: str) -> NormalizedRole:
    registry = get_role_registry()
    cleaned = clean_text(raw_role)
    norm_text = normalized_text(raw_role)

    def result(canonical: str | None, method: NormalizationMethod, status: NormalizationStatus, confidence: float) -> NormalizedRole:
        return NormalizedRole(
            raw_role=raw_role,
            normalized_text=norm_text,
            canonical_role=canonical,
            parent_role=registry.parent_of.get(canonical) if canonical else None,
            normalization_method=method,
            normalization_status=status,
            confidence=confidence,
            knowledge_version=registry.knowledge_version,
        )

    if cleaned in registry.parent_of:
        return result(cleaned, NormalizationMethod.EXACT, NormalizationStatus.RESOLVED, 1.0)

    canonical = registry.alias_index.get(norm_text)
    if canonical is not None:
        return result(canonical, NormalizationMethod.ALIAS, NormalizationStatus.RESOLVED, 1.0)

    canonical = registry.formatting_index.get(formatting_key(cleaned))
    if canonical is not None:
        return result(canonical, NormalizationMethod.FORMATTING_NORMALIZATION, NormalizationStatus.RESOLVED, 1.0)

    return result(None, NormalizationMethod.UNKNOWN, NormalizationStatus.UNKNOWN, 0.0)
