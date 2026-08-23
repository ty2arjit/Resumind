"""Domain normalization (spec §12-13)."""

from app.modules.normalization.registry import get_domain_registry
from app.modules.normalization.schemas import NormalizationMethod, NormalizationStatus, NormalizedDomain
from app.modules.normalization.text_utils import clean_text, formatting_key, normalized_text


def normalize_domain(raw_domain: str) -> NormalizedDomain:
    registry = get_domain_registry()
    cleaned = clean_text(raw_domain)
    norm_text = normalized_text(raw_domain)

    def result(canonical: str | None, method: NormalizationMethod, status: NormalizationStatus, confidence: float) -> NormalizedDomain:
        return NormalizedDomain(
            raw_domain=raw_domain,
            normalized_text=norm_text,
            canonical_domain=canonical,
            parent_domain=registry.parent_of.get(canonical) if canonical else None,
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
