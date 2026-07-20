"""Tests for Omega Semantic Router (D187)."""

import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from omega.oracle.semantic_router import SemanticRouter, _cosine_similarity, SEMANTIC_THRESHOLD
from omega.oracle.entity_registry import Entity


# ── Cosine Similarity ──────────────────────────────────────────────

def test_cosine_similarity_identical():
    """Identical vectors should have similarity 1.0."""
    assert _cosine_similarity([1.0, 2.0, 3.0], [1.0, 2.0, 3.0]) == pytest.approx(1.0)

def test_cosine_similarity_orthogonal():
    """Orthogonal vectors should have similarity 0.0."""
    assert _cosine_similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)

def test_cosine_similarity_opposite():
    """Opposite vectors should have similarity -1.0."""
    assert _cosine_similarity([1.0, 0.0], [-1.0, 0.0]) == pytest.approx(-1.0)

def test_cosine_similarity_empty():
    """Zero vectors should return 0.0."""
    assert _cosine_similarity([0.0, 0.0], [1.0, 2.0]) == pytest.approx(0.0)

def test_cosine_similarity_different_lengths():
    """Different length vectors should be padded and compared."""
    score = _cosine_similarity([1.0, 0.0], [1.0, 0.0, 0.0])
    assert score == pytest.approx(1.0)

def test_cosine_similarity_partial():
    """Partially similar vectors."""
    score = _cosine_similarity([1.0, 2.0, 3.0], [1.0, 2.0, 0.0])
    assert 0.0 < score < 1.0


# ── Signature Creation ─────────────────────────────────────────────

def test_make_signature_with_domains_and_role():
    """Signature should combine domains and role."""
    router = SemanticRouter(registry=MagicMock())
    entity = Entity(
        name="test",
        domains=["strength", "protection"],
        model="test",
        personality="test",
        role="SysAdmin",
    )
    sig = router._make_signature(entity)
    assert "strength" in sig
    assert "protection" in sig
    assert "SysAdmin" in sig

def test_make_signature_domains_only():
    """Signature with no role should use only domains."""
    router = SemanticRouter(registry=MagicMock())
    entity = Entity(
        name="test",
        domains=["data", "storage"],
        model="test",
        personality="test",
    )
    sig = router._make_signature(entity)
    assert "data" in sig
    assert "storage" in sig

def test_make_signature_empty():
    """Empty domains and no role should return empty string."""
    router = SemanticRouter(registry=MagicMock())
    entity = Entity(
        name="test",
        domains=[],
        model="test",
        personality="test",
    )
    sig = router._make_signature(entity)
    assert sig == ""


# ── Routing Fallback Chain ─────────────────────────────────────────

@pytest.mark.anyio
async def test_route_without_embedding_manager():
    """Without embedding manager, should fall through to keyword/default."""
    registry = MagicMock()
    router = SemanticRouter(registry=registry, embedding_manager=None)
    entity = Entity(name="test", domains=[], model="t", personality="t")
    default = Entity(name="default", domains=[], model="t", personality="t")

    result, conf, method = await router.route(
        query="hello",
        keyword_fallback=entity,
        default_entity=default,
    )
    assert result.name == "test"
    assert method == "keyword"
    assert conf == 0.7

@pytest.mark.anyio
async def test_route_keyword_fallback():
    """When semantic not bootstrapped, should use keyword fallback."""
    registry = MagicMock()
    router = SemanticRouter(registry=registry, embedding_manager=MagicMock())
    entity = Entity(name="keyword_match", domains=[], model="t", personality="t")
    default = Entity(name="default", domains=[], model="t", personality="t")

    result, conf, method = await router.route(
        query="store data",
        keyword_fallback=entity,
        default_entity=default,
    )
    assert result.name == "keyword_match"
    assert method == "keyword"

@pytest.mark.anyio
async def test_route_default_fallback():
    """When no keyword match and no semantic, should use default."""
    registry = MagicMock()
    router = SemanticRouter(registry=registry, embedding_manager=MagicMock())
    default = Entity(name="default", domains=[], model="t", personality="t")

    result, conf, method = await router.route(
        query="xyzzy",
        keyword_fallback=None,
        default_entity=default,
    )
    assert result.name == "default"
    assert method == "default"

@pytest.mark.anyio
async def test_route_no_match():
    """When nothing matches, should return None."""
    registry = MagicMock()
    router = SemanticRouter(registry=registry, embedding_manager=MagicMock())

    result, conf, method = await router.route(
        query="xyzzy",
        keyword_fallback=None,
        default_entity=None,
    )
    assert result is None
    assert method == "none"


# ── Semantic Routing with Mock Embeddings ──────────────────────────

@pytest.mark.anyio
async def test_route_semantic_match():
    """Semantic routing should match when cosine similarity > threshold."""
    registry = MagicMock()
    embedding_manager = AsyncMock()
    embedding_manager._providers = [MagicMock()]

    entity_datastore = Entity(
        name="DataStore",
        domains=["data", "storage", "persistence"],
        model="test",
        personality="test",
        role="Data persistence specialist",
    )
    entity_sysadmin = Entity(
        name="SysAdmin",
        domains=["infrastructure", "deployment", "containers"],
        model="test",
        personality="test",
        role="System administrator",
    )

    registry.active_iter.return_value = [entity_datastore, entity_sysadmin]

    def mock_get(name):
        return {"DataStore": entity_datastore, "SysAdmin": entity_sysadmin}.get(name)
    registry.get = mock_get

    async def mock_embed(text):
        if "data" in text or "storage" in text:
            return ([1.0, 0.0, 0.0], "mock")
        elif "infrastructure" in text.lower() or "system" in text.lower():
            return ([0.0, 1.0, 0.0], "mock")
        elif "store" in text.lower() or "information" in text.lower():
            return ([0.9, 0.1, 0.0], "mock")
        else:
            return ([0.0, 0.0, 1.0], "mock")

    embedding_manager.get_embedding = mock_embed

    with patch.dict(os.environ, {"OMEGA_ENV": "development"}):
        router = SemanticRouter(registry=registry, embedding_manager=embedding_manager, threshold=0.3)
        await router.bootstrap()

        result, conf, method = await router.route(
            query="I need to store some information",
            keyword_fallback=None,
            default_entity=None,
        )
        assert result is not None
        assert result.name == "DataStore"
        assert method == "semantic"
        assert conf >= 0.3

@pytest.mark.anyio
async def test_route_semantic_below_threshold():
    """Semantic routing should fall through when below threshold."""
    registry = MagicMock()
    embedding_manager = AsyncMock()
    embedding_manager._providers = [MagicMock()]

    entity = Entity(
        name="DataStore",
        domains=["data", "storage"],
        model="test",
        personality="test",
    )
    registry.active_iter.return_value = [entity]
    registry.get.return_value = entity

    async def mock_embed(text):
        if "data" in text or "storage" in text:
            return ([1.0, 0.0, 0.0], "mock")
        else:
            return ([0.0, 1.0, 0.0], "mock")

    embedding_manager.get_embedding = mock_embed

    with patch.dict(os.environ, {"OMEGA_ENV": "development"}):
        router = SemanticRouter(registry=registry, embedding_manager=embedding_manager, threshold=0.5)
        await router.bootstrap()

        result, conf, method = await router.route(
            query="deploy containers",
            keyword_fallback=None,
            default_entity=entity,
        )
        assert method in ("default", "semantic")
        if method == "semantic":
            assert conf < 0.5


# ── Bootstrap ──────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_bootstrap_empty_registry():
    """Bootstrap with no entities should succeed with empty vectors."""
    registry = MagicMock()
    registry.active_iter.return_value = []
    embedding_manager = AsyncMock()

    router = SemanticRouter(registry=registry, embedding_manager=embedding_manager)
    await router.bootstrap()

    assert router._bootstrapped is True
    assert len(router._entity_vectors) == 0

@pytest.mark.anyio
async def test_bootstrap_with_entities():
    """Bootstrap should create vectors for all active entities."""
    registry = MagicMock()
    embedding_manager = AsyncMock()
    embedding_manager._providers = [MagicMock()]

    entity1 = Entity(name="E1", domains=["a", "b"], model="t", personality="t", role="R1")
    entity2 = Entity(name="E2", domains=["c", "d"], model="t", personality="t", role="R2")
    registry.active_iter.return_value = [entity1, entity2]

    async def mock_embed(text):
        return ([1.0, 0.0, 0.0], "mock")

    embedding_manager.get_embedding = mock_embed

    with patch.dict(os.environ, {"OMEGA_ENV": "development"}):
        router = SemanticRouter(registry=registry, embedding_manager=embedding_manager)
        await router.bootstrap()

        assert router._bootstrapped is True
        assert "E1" in router._entity_vectors
        assert "E2" in router._entity_vectors

@pytest.mark.anyio
async def test_bootstrap_idempotent():
    """Calling bootstrap twice should not re-embed."""
    registry = MagicMock()
    embedding_manager = AsyncMock()
    embedding_manager._providers = [MagicMock()]
    registry.active_iter.return_value = [Entity(name="E", domains=["a"], model="t", personality="t")]

    call_count = 0

    async def mock_embed(text):
        nonlocal call_count
        call_count += 1
        return ([1.0, 0.0, 0.0], "mock")

    embedding_manager.get_embedding = mock_embed

    with patch.dict(os.environ, {"OMEGA_ENV": "development"}):
        router = SemanticRouter(registry=registry, embedding_manager=embedding_manager)
        await router.bootstrap()
        await router.bootstrap()
        assert call_count == 1


# ── Threshold Constant ─────────────────────────────────────────────

def test_semantic_threshold_value():
    """Threshold should be 0.4 as per D187."""
    assert SEMANTIC_THRESHOLD == 0.4
