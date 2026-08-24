import pytest

from app.modules.embeddings.service import (
    EmbeddingServiceUnavailableError,
    NotImplementedEmbeddingService,
    cache_key,
)


def test_not_implemented_service_raises_clearly():
    service = NotImplementedEmbeddingService()
    with pytest.raises(EmbeddingServiceUnavailableError):
        service.embed("Python developer")
    with pytest.raises(EmbeddingServiceUnavailableError):
        service.embed_batch(["Python", "FastAPI"])
    with pytest.raises(EmbeddingServiceUnavailableError):
        service.similarity([0.1], [0.2])


def test_cache_key_is_deterministic():
    assert cache_key("FastAPI", "v1") == cache_key("FastAPI", "v1")


def test_cache_key_changes_with_text_or_model_version():
    base = cache_key("FastAPI", "v1")
    assert cache_key("Flask", "v1") != base
    assert cache_key("FastAPI", "v2") != base
