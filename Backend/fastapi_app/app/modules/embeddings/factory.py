"""Single place that decides which EmbeddingService implementation is
active. Matching/scoring code should call get_embedding_service() rather
than importing LocalSentenceTransformerEmbeddingService directly, so the
provider stays swappable (spec §21 architectural principle from Phase 1).
"""

from functools import lru_cache

from app.modules.embeddings.service import EmbeddingService


@lru_cache
def get_embedding_service() -> EmbeddingService:
    from app.modules.embeddings.local_model import LocalSentenceTransformerEmbeddingService

    return LocalSentenceTransformerEmbeddingService()
