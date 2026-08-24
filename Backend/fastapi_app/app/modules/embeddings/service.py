"""EmbeddingService abstraction (spec §21, §50).

This is the ONLY interface the matching engine (Phase 5) is allowed to
depend on for semantic similarity — no module outside this package may
import a specific model/provider directly. That keeps the pretrained model
choice swappable later without touching matching/scoring code.

Per architecture decision 3: the concrete implementation must be a LOCAL
pretrained model (not Gemini, not a hosted embedding API). Which model is
selected, and the actual inference code, are Phase 5 work — this file only
establishes the contract and the cache-key convention so nothing has to be
rewritten when that implementation lands.
"""

import hashlib
from abc import ABC, abstractmethod

Vector = list[float]


class EmbeddingService(ABC):
    """Contract every embedding provider implementation must satisfy."""

    #: Identifies the concrete model/version producing these vectors — used
    #: both in the cache key and stored on Analysis.embedding_model_version
    #: (spec §44) so historical results stay attributable to the model that
    #: produced them.
    model_version: str

    @abstractmethod
    def embed(self, text: str) -> Vector:
        """Embed a single piece of text."""

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[Vector]:
        """Embed multiple texts, batched for efficiency (spec §58)."""

    @abstractmethod
    def similarity(self, a: Vector, b: Vector) -> float:
        """Similarity between two vectors, normalized to [0, 1]."""


class EmbeddingServiceUnavailableError(RuntimeError):
    """Raised by NotImplementedEmbeddingService — a clear signal that the
    real Phase 5 implementation hasn't been wired in yet, instead of a
    silent no-op or a fabricated vector."""


class NotImplementedEmbeddingService(EmbeddingService):
    """Placeholder so code can depend on EmbeddingService today via
    dependency injection, and get a real implementation later without any
    call-site changes. Intentionally fails loudly rather than returning
    fake similarity scores.
    """

    model_version = "unset"

    def embed(self, text: str) -> Vector:
        raise EmbeddingServiceUnavailableError(
            "No EmbeddingService implementation is configured yet (Phase 5)."
        )

    def embed_batch(self, texts: list[str]) -> list[Vector]:
        raise EmbeddingServiceUnavailableError(
            "No EmbeddingService implementation is configured yet (Phase 5)."
        )

    def similarity(self, a: Vector, b: Vector) -> float:
        raise EmbeddingServiceUnavailableError(
            "No EmbeddingService implementation is configured yet (Phase 5)."
        )


def cache_key(text: str, model_version: str) -> str:
    """hash(text + model_version), per spec §50."""
    payload = f"{model_version}:{text}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
