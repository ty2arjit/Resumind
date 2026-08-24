"""Skill/technology entity normalization (spec §2-4, §7-9).

Resolution order — first match wins, each strictly more permissive than
the last:

  1. Ambiguous-term check (short-circuits everything else — spec §20)
  2. EXACT: cleaned raw text is byte-identical to a canonical name
  3. CASE_NORMALIZATION: identical case-insensitively, but not exactly
  4. ALIAS: matches a registered alias string (case-insensitively)
  5. FORMATTING_NORMALIZATION: matches after collapsing separator
     punctuation/whitespace (spec §2's "Case/Formatting Normalization"
     stage) — catches "ReactJS"/"React JS" against the registered
     "React.js" alias without listing every spacing variant by hand
  6. UNKNOWN — never guessed.
"""

from app.modules.normalization.registry import SkillRegistry, get_skill_registry
from app.modules.normalization.schemas import NormalizationMethod, NormalizationStatus, NormalizedEntity
from app.modules.normalization.text_utils import clean_text, formatting_key, normalized_text


def normalize_skill(raw_value: str) -> NormalizedEntity:
    registry = get_skill_registry()
    cleaned = clean_text(raw_value)
    norm_text = normalized_text(raw_value)

    def result(
        canonical: str | None,
        method: NormalizationMethod,
        status: NormalizationStatus,
        confidence: float,
    ) -> NormalizedEntity:
        return NormalizedEntity(
            raw_value=raw_value,
            normalized_text=norm_text,
            canonical_value=canonical,
            entity_type=registry.canonical_types.get(canonical) if canonical else None,
            normalization_method=method,
            normalization_status=status,
            confidence=confidence,
            knowledge_version=registry.knowledge_version,
        )

    if norm_text in registry.ambiguous_terms:
        return result(None, NormalizationMethod.UNKNOWN, NormalizationStatus.AMBIGUOUS, 0.0)

    if cleaned in registry.canonical_types:
        return result(cleaned, NormalizationMethod.EXACT, NormalizationStatus.RESOLVED, 1.0)

    canonical = registry.alias_index.get(norm_text)
    if canonical is not None:
        if canonical.lower() == norm_text:
            return result(canonical, NormalizationMethod.CASE_NORMALIZATION, NormalizationStatus.RESOLVED, 1.0)
        return result(canonical, NormalizationMethod.ALIAS, NormalizationStatus.RESOLVED, 1.0)

    canonical = registry.formatting_index.get(formatting_key(cleaned))
    if canonical is not None:
        return result(canonical, NormalizationMethod.FORMATTING_NORMALIZATION, NormalizationStatus.RESOLVED, 1.0)

    return result(None, NormalizationMethod.UNKNOWN, NormalizationStatus.UNKNOWN, 0.0)
