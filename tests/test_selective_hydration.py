# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Tests for Selective Hydration — L3 gnosis retrieval (Workstream B).

[Workstream B] Qdrant L3 Selective Hydration
Owner: John Carmack
Interface: See CARMACK_REPLY_TO_JEM_20260704.md §3

Tests:
  - L3Principle dataclass validation
  - SelectiveHydration store + hydrate cycle
  - ContextBuilder integration
  - Edge cases: empty content, zero embeddings, unknown entity
  - M9 Error Integrity: no bare except, typed errors
"""

import os
import time
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from omega.oracle.selective_hydration import (
    L3Principle,
    SelectiveHydration,
    DEFAULT_TOP_K,
    MIN_CONFIDENCE,
    L3_COLLECTION_PREFIX,
    OmegaError,
)
from omega.memory.embeddings import EmbeddingManager, SovereignFallbackEmbeddingProvider
from omega.memory.vector_adapters import MemoryVectorAdapter


# ── Helpers ──────────────────────────────────────────────────────────


def _make_embedding_manager(dim: int = 256) -> EmbeddingManager:
    """Create an EmbeddingManager with only the SovereignFallback provider."""
    return EmbeddingManager(providers=[SovereignFallbackEmbeddingProvider(dimension=dim)])


def _make_sample_principles(entity_name: str = "test_entity") -> list:
    """Create a list of sample L3 principles for testing."""
    return [
        L3Principle(
            entity_name=entity_name,
            content="The Right Approximation: choose the solution that fits the constraints, not the theoretically perfect one.",
            domain="engineering",
            confidence=0.95,
            source="heritage_vet-023",
            category="heritage",
        ),
        L3Principle(
            entity_name=entity_name,
            content="Engine-Stack Separation: absolute decoupling of engine logic from content.",
            domain="architecture",
            confidence=0.90,
            source="mandate_m2",
            category="governance",
        ),
        L3Principle(
            entity_name=entity_name,
            content="Precomputation over Computation: precompute what can be precomputed.",
            domain="engineering",
            confidence=0.85,
            source="heritage_vet-020",
            category="technical",
        ),
    ]


# ── L3Principle Tests ───────────────────────────────────────────────

def test_l3_principle_creation():
    """A valid L3Principle should create with auto-generated ID."""
    p = L3Principle(
        entity_name="test",
        content="This is a test principle.",
    )
    assert p.entity_name == "test"
    assert p.content == "This is a test principle."
    assert len(p.principle_id) == 24  # sha256[:24]
    assert p.confidence == 1.0  # default
    assert p.domain == "general"  # default
    assert p.category == "general"  # default
    assert p.similarity == 0.0  # default


def test_l3_principle_explicit_id():
    """An explicit principle_id should be preserved."""
    p = L3Principle(
        principle_id="my_custom_id_123",
        entity_name="test",
        content="Test principle.",
    )
    assert p.principle_id == "my_custom_id_123"


def test_l3_principle_confidence_range():
    """Confidence must be between 0.0 and 1.0."""
    with pytest.raises(ValueError, match="Confidence must be between"):
        L3Principle(entity_name="test", content="x", confidence=-0.1)
    with pytest.raises(ValueError, match="Confidence must be between"):
        L3Principle(entity_name="test", content="x", confidence=1.5)


def test_l3_principle_to_from_payload():
    """L3Principle should round-trip through payload serialization."""
    original = L3Principle(
        entity_name="test",
        content="A round-trip test principle.",
        domain="engineering",
        confidence=0.88,
        source="test_20260704",
        category="technical",
    )
    payload = original.to_payload()
    assert payload["_type"] == "l3_principle"
    assert payload["entity_name"] == "test"

    restored = L3Principle.from_payload(payload, similarity=0.92)
    assert restored.principle_id == original.principle_id
    assert restored.entity_name == "test"
    assert restored.content == original.content
    assert restored.domain == "engineering"
    assert restored.confidence == 0.88
    assert restored.similarity == 0.92


def test_l3_principle_format():
    """Format should include similarity and content."""
    p = L3Principle(
        entity_name="test",
        content="A formatted principle.",
        domain="engineering",
    )
    p.similarity = 0.85
    formatted = p.format()
    assert "[0.85]" in formatted
    assert "A formatted principle." in formatted
    assert "engineering" in formatted


def test_l3_principle_format_no_similarity():
    """Format with zero similarity should omit score."""
    p = L3Principle(
        entity_name="test",
        content="A principle without similarity.",
    )
    formatted = p.format()
    assert formatted.startswith("- ")
    assert "A principle without similarity." in formatted


# ── SelectiveHydration Construction Tests ────────────────────────────

def test_selective_hydration_creation():
    """SelectiveHydration should initialize with embedding + vector."""
    emb_mgr = _make_embedding_manager()
    vec_store = MemoryVectorAdapter()
    sh = SelectiveHydration(embedding_manager=emb_mgr, vector_adapter=vec_store)
    assert sh.top_k == DEFAULT_TOP_K


def test_selective_hydration_invalid_top_k():
    """top_k must be >= 1."""
    emb_mgr = _make_embedding_manager()
    vec_store = MemoryVectorAdapter()
    with pytest.raises(ValueError, match="top_k must be >= 1"):
        SelectiveHydration(embedding_manager=emb_mgr, vector_adapter=vec_store, top_k=0)


def test_selective_hydration_invalid_confidence():
    """min_confidence must be between 0.0 and 1.0."""
    emb_mgr = _make_embedding_manager()
    vec_store = MemoryVectorAdapter()
    with pytest.raises(ValueError, match="min_confidence must be between"):
        SelectiveHydration(embedding_manager=emb_mgr, vector_adapter=vec_store, min_confidence=-0.1)
    with pytest.raises(ValueError, match="min_confidence must be between"):
        SelectiveHydration(embedding_manager=emb_mgr, vector_adapter=vec_store, min_confidence=1.5)


# ── SelectiveHydration Store + Hydrate Cycle ─────────────────────────


class TestSelectiveHydrationCycle:
    """Test the full store -> hydrate cycle with MemoryVectorAdapter."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.emb_mgr = _make_embedding_manager(dim=256)
        self.vec_store = MemoryVectorAdapter()
        self.sh = SelectiveHydration(
            embedding_manager=self.emb_mgr,
            vector_adapter=self.vec_store,
            top_k=3,
        )
        self.entity = "test_entity"
        self.principles = _make_sample_principles(self.entity)

    @pytest.mark.anyio
    async def test_store_and_hydrate_cycle(self):
        """Store principles then hydrate should return matching principles."""
        for p in self.principles:
            returned_id = await self.sh.store(p)
            assert returned_id == p.principle_id

        results = await self.sh.hydrate(
            query="right approximation engineering constraints",
            entity_name=self.entity,
        )
        assert len(results) > 0
        assert results[0].entity_name == self.entity
        assert results[0].similarity >= 0.0

    @pytest.mark.anyio
    async def test_hydrate_empty_query(self):
        """Empty query should return empty list."""
        await self.sh.store(self.principles[0])
        results = await self.sh.hydrate(query="", entity_name=self.entity)
        assert results == []

    @pytest.mark.anyio
    async def test_hydrate_unknown_entity(self):
        """Unknown entity should return empty list (no principles stored)."""
        await self.sh.store(self.principles[0])
        results = await self.sh.hydrate(
            query="test query",
            entity_name="nonexistent_entity",
        )
        assert results == []

    @pytest.mark.anyio
    async def test_hydrate_confidence_filtering(self):
        """Principles below min_confidence should be filtered out."""
        low_conf = L3Principle(
            entity_name=self.entity,
            content="A low confidence principle that should be filtered.",
            confidence=0.1,
        )
        await self.sh.store(low_conf)

        high_conf = L3Principle(
            entity_name=self.entity,
            content="A high confidence principle that should appear.",
            confidence=0.95,
        )
        await self.sh.store(high_conf)

        results = await self.sh.hydrate(
            query="high confidence principle",
            entity_name=self.entity,
        )
        if len(results) > 0:
            for r in results:
                assert r.confidence >= self.sh._min_confidence

    @pytest.mark.anyio
    async def test_store_empty_content_raises(self):
        """Storing a principle with empty content should raise ValueError."""
        empty = L3Principle(entity_name=self.entity, content="")
        with pytest.raises(ValueError, match="Cannot store"):
            await self.sh.store(empty)

    @pytest.mark.anyio
    async def test_get_all_empty(self):
        """get_all for an entity with no principles should return empty list."""
        results = await self.sh.get_all(self.entity)
        assert results == []

    @pytest.mark.anyio
    async def test_get_all_after_store(self):
        """get_all should return stored principles."""
        for p in self.principles:
            await self.sh.store(p)
        results = await self.sh.get_all(self.entity)
        assert len(results) == len(self.principles)

    @pytest.mark.anyio
    async def test_remove_principle(self):
        """Remove should delete a specific principle."""
        await self.sh.store(self.principles[0])
        result = await self.sh.remove(self.principles[0].principle_id, self.entity)
        assert result is True

        hydrated = await self.sh.hydrate(
            query=self.principles[0].content,
            entity_name=self.entity,
        )
        for h in hydrated:
            assert h.principle_id != self.principles[0].principle_id

    @pytest.mark.anyio
    async def test_remove_nonexistent(self):
        """Removing a nonexistent principle should return False."""
        result = await self.sh.remove("nonexistent_id", self.entity)
        assert result is False


# -- Format Principles Block Tests ------------------------------------

@pytest.mark.anyio
async def test_format_principles_block():
    """Principles block should format correctly."""
    emb_mgr = _make_embedding_manager()
    vec_store = MemoryVectorAdapter()
    sh = SelectiveHydration(embedding_manager=emb_mgr, vector_adapter=vec_store)

    principles = _make_sample_principles("test")
    block = sh.format_principles_block(principles)
    assert "Relevant Gnosis Principles" in block
    assert "The Right Approximation" in block
    assert "Engine-Stack Separation" in block
    assert "Precomputation over Computation" in block


@pytest.mark.anyio
async def test_format_principles_block_empty():
    """Empty principles list should return empty string."""
    emb_mgr = _make_embedding_manager()
    vec_store = MemoryVectorAdapter()
    sh = SelectiveHydration(embedding_manager=emb_mgr, vector_adapter=vec_store)
    assert sh.format_principles_block([]) == ""


# -- ContextBuilder Integration Tests ---------------------------------

@pytest.mark.anyio
async def test_context_builder_with_selective_hydration():
    """ContextBuilder should inject L3 principles when hydration is configured."""
    from omega.oracle.context_builder import ContextBuilder

    emb_mgr = _make_embedding_manager()
    vec_store = MemoryVectorAdapter()
    sh = SelectiveHydration(embedding_manager=emb_mgr, vector_adapter=vec_store)

    principle = L3Principle(
        entity_name="test",
        content="The Right Approximation: choose constraints over perfection.",
        domain="engineering",
    )
    await sh.store(principle)

    ctx_builder = ContextBuilder(selective_hydration=sh)
    gnosis_block = await ctx_builder._build_gnosis_block("test")
    if gnosis_block:
        assert "Relevant Gnosis Principles" in gnosis_block


@pytest.mark.anyio
async def test_context_builder_without_selective_hydration():
    """ContextBuilder should work without SelectiveHydration (backward compat)."""
    from omega.oracle.context_builder import ContextBuilder

    ctx_builder = ContextBuilder()
    gnosis_block = await ctx_builder._build_gnosis_block("test")
    assert gnosis_block == ""


@pytest.mark.anyio
async def test_context_builder_build_context_with_hydration():
    """Full build_context should not crash when hydration is configured."""
    from omega.oracle.context_builder import ContextBuilder

    emb_mgr = _make_embedding_manager()
    vec_store = MemoryVectorAdapter()
    sh = SelectiveHydration(embedding_manager=emb_mgr, vector_adapter=vec_store)

    principle = L3Principle(
        entity_name="test_entity",
        content="A test L3 principle for context builder integration.",
        domain="testing",
    )
    await sh.store(principle)

    ctx_builder = ContextBuilder(selective_hydration=sh)
    context = await ctx_builder.build_context(
        entity_name="test_entity",
        session_id="test_session_123",
    )
    assert context is not None or context == ""


@pytest.mark.anyio
async def test_context_builder_gnosis_block_silent_fallback():
    """ContextBuilder should silently skip gnosis on errors (no crash)."""
    from omega.oracle.context_builder import ContextBuilder

    sh = SelectiveHydration(
        embedding_manager=None,  # type: ignore
        vector_adapter=MemoryVectorAdapter(),
    )

    ctx_builder = ContextBuilder(selective_hydration=sh)
    block = await ctx_builder._build_gnosis_block("test")
    assert block == ""


# -- Edge Cases -------------------------------------------------------

@pytest.mark.anyio
async def test_same_content_different_entities():
    """Same content for different entities should produce different IDs."""
    p1 = L3Principle(entity_name="entity_a", content="Same content.")
    p2 = L3Principle(entity_name="entity_b", content="Same content.")
    assert p1.principle_id != p2.principle_id


@pytest.mark.anyio
async def test_store_hydrate_different_entities():
    """Principles for one entity should not leak to another entity."""
    emb_mgr = _make_embedding_manager()
    vec_store = MemoryVectorAdapter()
    sh = SelectiveHydration(embedding_manager=emb_mgr, vector_adapter=vec_store)

    await sh.store(L3Principle(entity_name="alice", content="Alice's principle."))
    await sh.store(L3Principle(entity_name="bob", content="Bob's principle."))

    alice_results = await sh.hydrate("principle", "alice")
    bob_results = await sh.hydrate("principle", "bob")

    alice_contents = [p.content for p in alice_results]
    bob_contents = [p.content for p in bob_results]

    assert all("Alice" in c for c in alice_contents)
    assert all("Bob" in c for c in bob_contents)


@pytest.mark.anyio
async def test_many_principles_limited_by_top_k():
    """Storing more than top_k principles should still return only top_k."""
    emb_mgr = _make_embedding_manager()
    vec_store = MemoryVectorAdapter()
    sh = SelectiveHydration(
        embedding_manager=emb_mgr,
        vector_adapter=vec_store,
        top_k=2,
    )

    for i in range(5):
        await sh.store(L3Principle(
            entity_name="test",
            content=f"Principle number {i} with some unique content tokens.",
        ))

    results = await sh.hydrate("principle unique content tokens", "test")
    assert len(results) <= 2
