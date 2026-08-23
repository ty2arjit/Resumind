"""Action normalization (spec §15). Reuses the action vocabulary already
established for resume/JD parsing (Backend/fastapi_app/app/modules/resume/
data/action_verbs.json is the source list of recognized verbs); this
module only adds the canonical grouping on top (action_canonical_map.json)
— it does not introduce a second action dictionary.
"""

from app.modules.normalization.registry import get_action_registry
from app.modules.normalization.schemas import NormalizationMethod, NormalizationStatus, NormalizedAction
from app.modules.normalization.text_utils import clean_text, normalized_text


def normalize_action(raw_action: str) -> NormalizedAction:
    registry = get_action_registry()
    cleaned = clean_text(raw_action)
    norm_text = normalized_text(raw_action)

    canonical = registry.mappings.get(norm_text)
    if canonical is None:
        return NormalizedAction(
            raw_action=raw_action,
            normalized_text=norm_text,
            canonical_action=None,
            normalization_method=NormalizationMethod.UNKNOWN,
            normalization_status=NormalizationStatus.UNKNOWN,
            confidence=0.0,
            knowledge_version=registry.knowledge_version,
        )

    method = NormalizationMethod.EXACT if cleaned == canonical else (
        NormalizationMethod.CASE_NORMALIZATION if cleaned.lower() == canonical.lower() else NormalizationMethod.ALIAS
    )
    return NormalizedAction(
        raw_action=raw_action,
        normalized_text=norm_text,
        canonical_action=canonical,
        normalization_method=method,
        normalization_status=NormalizationStatus.RESOLVED,
        confidence=1.0,
        knowledge_version=registry.knowledge_version,
    )
