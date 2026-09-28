# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Contract tests: the write path MUST emit the canonical dimension (1024).

[D-1024-DIM-NATIVE-20260926] Native 1024 (Qwen3-Embedding-0.6B) IS canonical.
MRL truncation remains AVAILABLE but is NOT the canonical path, so a provider
whose NATIVE width is below 1024 can never serve the canonical collection.
"""
import asyncio
import contextlib
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from omega.memory.embedding_strategy import get_embedding_strategy

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

CANONICAL = 1024
CANONICAL_COLLECTION = "omega_vec_qwen_1024"


# ── Canonical dimension ──────────────────────────────────────────────────

def test_canonical_dimension_is_1024():
    """EmbeddingStrategy.canonical_dimension must be 1024 (native, D-1024)."""
    strategy = get_embedding_strategy()
    assert strategy.canonical_dimension == CANONICAL


def test_mrl_is_available_but_not_canonical():
    """mrl_dimensions starts at the native/canonical width.

    1024 is an identity truncation; everything below is a fallback tier.
    """
    strategy = get_embedding_strategy()
    dims = strategy.mrl_dimensions
    assert dims[0] == CANONICAL
    assert set(dims) >= {1024, 768, 512, 256, 128, 64}


def test_vec0_lock_dimension_is_canonical():
    """The vec0 lock must agree with canonical_dimension (no silent widening)."""
    strategy = get_embedding_strategy()
    lock = strategy.data["vec0_lock"]
    assert lock["enabled"] is True
    assert lock["dimension"] == CANONICAL
    assert lock["dimension"] == strategy.canonical_dimension


def test_all_collections_have_dimension():
    """Every collection in strategy must declare a dimension."""
    strategy = get_embedding_strategy()
    for name, cfg in strategy.get_collections().items():
        assert "dimension" in cfg, f"Collection {name} missing dimension"
        assert isinstance(cfg["dimension"], int), f"Collection {name} dimension not int"
        assert cfg["dimension"] > 0, f"Collection {name} dimension not positive"


# ── Adapter constants + collection naming ────────────────────────────────

def test_adapter_constants_are_canonical():
    """Both adapters must agree on the canonical dimension and collection."""
    from omega.memory import sqlite_vec_adapter as base
    from omega.memory import sqlite_vec_adapter_optimized as opt

    for mod in (base, opt):
        assert mod.CANONICAL_DIMENSION == CANONICAL, mod.__name__
        assert mod.CANONICAL_COLLECTION == CANONICAL_COLLECTION, mod.__name__
        assert mod.COLLECTIONS[CANONICAL_COLLECTION]["dimension"] == CANONICAL
        assert mod.CANONICAL_COLLECTION in mod.COLLECTIONS


def test_retired_768_names_are_aliases_not_definitions():
    """`*_768` canonical names are gone from COLLECTIONS but aliased, not lost."""
    from omega.memory.sqlite_vec_adapter import (
        COLLECTIONS,
        LEGACY_COLLECTION_ALIASES,
        resolve_collection_name,
    )

    for stale in ("omega_vec_qwen_768", "omega_vec_library_768"):
        assert stale not in COLLECTIONS, f"{stale} must not be a live collection"
        assert stale in LEGACY_COLLECTION_ALIASES, f"{stale} must stay aliased"
        target = LEGACY_COLLECTION_ALIASES[stale]
        assert target in COLLECTIONS, f"alias target {target} must be live"
        assert resolve_collection_name(stale, COLLECTIONS) == target
        assert COLLECTIONS[target]["dimension"] == CANONICAL


def test_unknown_collection_still_raises():
    """Alias resolution must never silently redirect an unknown name."""
    from omega.memory.sqlite_vec_adapter import COLLECTIONS, resolve_collection_name

    with pytest.raises(ValueError, match="Unknown collection"):
        resolve_collection_name("omega_vec_does_not_exist", COLLECTIONS)


def test_no_stale_canonical_768_constant():
    """No module may still declare 768 as the CANONICAL dimension."""
    pattern = "CANONICAL_DIMENSION = 768"
    result = _rg_or_grep(pattern, "src")
    assert not result.strip(), f"Stale canonical constant:\n{result}"


def test_no_retired_collection_defaults_in_src():
    """No default/definition may still point at the retired *_768 names.

    Allowed: the alias table and read-only fallback lookups in
    sqlite_vec_adapter.py / spatial_graph.py (explicitly whitelisted).
    """
    allowed_files = {
        "src/omega/memory/sqlite_vec_adapter.py",
        "src/omega/memory/spatial_graph.py",
        "src/omega/memory/vector_versioning.py",  # LEGACY_META_RENAMES alias map
    }
    hits = []
    for path in sorted((REPO_ROOT / "src").rglob("*.py")):
        rel = str(path.relative_to(REPO_ROOT))
        if rel in allowed_files:
            continue
        for lineno, line in enumerate(path.read_text().splitlines(), 1):
            if "omega_vec_qwen_768" in line or "omega_vec_library_768" in line:
                hits.append(f"{rel}:{lineno}: {line.strip()}")
    assert not hits, f"Retired collection names outside the alias/fallback layer:\n" + "\n".join(hits)


# ── Provider chain ───────────────────────────────────────────────────────

def test_write_path_primary_matches_canonical():
    """The provider the write path answers with must be canonical-width.

    Under D-1024 the first provider is what EmbeddingManager short-circuits
    to in test mode and what it returns first in production.
    """
    from omega.memory.embeddings import EmbeddingManager

    strategy = get_embedding_strategy()
    manager = EmbeddingManager()
    assert manager._providers, "provider chain must not be empty"
    primary = manager._providers[0]
    assert primary.dimension == strategy.canonical_dimension, (
        f"primary provider {primary.__class__.__name__} dimension "
        f"{primary.dimension} != canonical {strategy.canonical_dimension}"
    )


def test_memory_store_write_path_matches_canonical():
    """MemoryStore's default chain must be built from canonical-capable providers.

    EmbeddingGemma (768 native) and potion (768 native) can never emit 1024
    — MRL only truncates — so they must not sit on the write path.
    """
    src = (REPO_ROOT / "src/omega/memory_store.py").read_text()
    assert "Qwen3GGUFEmbeddingProvider(target_dim=target_dim)" in src, (
        "MemoryStore write path must use the native-1024 Qwen3 provider"
    )
    assert "GemmaGGUFEmbeddingProvider(" not in src, (
        "Gemma is 768-native and cannot serve the 1024 canonical collection"
    )

    # The sovereign fallback must default to the canonical width too.
    from omega.memory.embeddings import SovereignFallbackEmbeddingProvider

    strategy = get_embedding_strategy()
    assert SovereignFallbackEmbeddingProvider().dimension == strategy.canonical_dimension


# ── Adapter behaviour ────────────────────────────────────────────────────

def test_adapter_rejects_wrong_dim():
    """Adapter must reject wrong-dim upsert with explicit error."""
    from omega.memory.sqlite_vec_adapter import SQLiteVecAdapter

    async def test():
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            path = f.name

        adapter = SQLiteVecAdapter(db_path=path)
        try:
            # 256-dim into the 1024-dim canonical collection
            with pytest.raises(RuntimeError, match="EMBEDDING DIMENSION MISMATCH"):
                await adapter.upsert(
                    entity_name="test",
                    vector=[0.1] * 256,  # Wrong dimension
                    metadata={"content": "test"},
                    collection=CANONICAL_COLLECTION,
                )
        finally:
            await adapter.close()

    asyncio.run(test())


def test_adapter_accepts_correct_dim():
    """Adapter must accept canonical-dim upsert without error."""
    from omega.memory.sqlite_vec_adapter import SQLiteVecAdapter

    async def test():
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            path = f.name

        adapter = SQLiteVecAdapter(db_path=path)
        try:
            result = await adapter.upsert(
                entity_name="test",
                vector=[0.1] * CANONICAL,
                metadata={"content": "test"},
                collection=CANONICAL_COLLECTION,
            )
            assert isinstance(result, str)  # UUID returned
        finally:
            await adapter.close()

    asyncio.run(test())


def test_adapter_accepts_legacy_collection_name():
    """A pre-D-1024 caller naming `omega_vec_qwen_768` must be redirected,
    not rejected — the alias is the migration path for external callers."""
    from omega.memory.sqlite_vec_adapter import SQLiteVecAdapter

    async def test():
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            path = f.name

        adapter = SQLiteVecAdapter(db_path=path)
        try:
            result = await adapter.upsert(
                entity_name="test",
                vector=[0.1] * CANONICAL,
                metadata={"content": "test"},
                collection="omega_vec_qwen_768",
            )
            assert isinstance(result, str)
            # …and the data landed in the canonical table, not a dead one.
            conn = adapter._get_conn()
            rows = conn.execute(
                f"SELECT COUNT(*) FROM {CANONICAL_COLLECTION}"
            ).fetchone()[0]
            assert rows == 1
            stale = conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='omega_vec_qwen_768'"
            ).fetchone()
            assert stale is None, "legacy table must not be created by an aliased write"
        finally:
            await adapter.close()

    asyncio.run(test())


def test_adapter_recreates_wrong_dim_vec_table():
    """A vec0 table already created at another width must be DROP+recreated,
    not left to raise 'vector dim mismatch' on every future write.

    Data note: the old vectors are discarded (768 blobs cannot be widened
    without re-embedding) and the row count is logged; metadata + FTS rows
    are untouched.
    """
    from omega.memory.sqlite_vec_adapter import (
        SQLiteVecAdapter,
        get_vec_table_declared_dim,
    )

    async def test():
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            path = f.name

        adapter = SQLiteVecAdapter(db_path=path)
        try:
            await adapter._ensure_initialized()
            conn = adapter._get_conn()
            # Simulate a pre-D-1024 table that survived the rename.
            conn.execute(
                f"CREATE VIRTUAL TABLE {CANONICAL_COLLECTION} USING vec0("
                "embedding float[768] distance_metric=cosine, "
                "entity_name TEXT partition key)"
            )
            conn.commit()
            assert get_vec_table_declared_dim(conn, CANONICAL_COLLECTION) == 768

            await adapter.upsert(
                entity_name="test",
                vector=[0.1] * CANONICAL,
                metadata={"content": "test"},
                collection=CANONICAL_COLLECTION,
            )
            assert get_vec_table_declared_dim(conn, CANONICAL_COLLECTION) == CANONICAL
        finally:
            await adapter.close()

    asyncio.run(test())


# ── M23 fail-loud: no silent cross-model substitution (D-1024) ───────────

@contextlib.contextmanager
def _production_embedding_path():
    """Run with OMEGA_ENV unset.

    EmbeddingManager.get_embedding short-circuits to a zero vector when
    OMEGA_ENV == "test" (it avoids loading the Qwen3 GGUF in the test
    suite). Every test below exercises the REAL provider-walk logic, so the
    short-circuit must be off — otherwise the guard is never reached and the
    test would pass for the wrong reason.
    """
    previous = os.environ.pop("OMEGA_ENV", None)
    try:
        yield
    finally:
        if previous is not None:
            os.environ["OMEGA_ENV"] = previous


def test_config_has_no_nomic_fallback_provider():
    """The priority-1 nomic_fallback entry must be GONE from the chain.

    It was a natively-768 nomic-embed-text provider that answered whenever
    the canonical Qwen3-1024 provider was unavailable, then wrote to
    omega_vec_nomic_768 — a different collection than the caller targeted —
    so no width check could see the substitution.
    """
    strategy = get_embedding_strategy()
    provider_ids = [p["id"] for p in strategy.get_providers()]
    assert "nomic_fallback" not in provider_ids, (
        f"nomic_fallback is a cross-model substitution path: {provider_ids}"
    )
    weights = strategy.data["fusion"]["weights"]
    assert "nomic_fallback" not in weights, (
        "fusing a non-canonical space with canonical is the same cross-model error"
    )


def test_legacy_collections_are_marked_deprecated():
    """Legacy pre-D-1024 tiers stay registered (Step 19/20 have targets) but
    must be explicitly flagged as a different, non-canonical semantic space."""
    strategy = get_embedding_strategy()
    collections = strategy.get_collections()
    for name in ("omega_vec_nomic_768", "omega_vec_nomic_512", "omega_vec_nomic_256"):
        cfg = collections[name]
        assert cfg.get("deprecated") is True, f"{name} must be flagged deprecated"
        assert cfg.get("deprecated_by") == CANONICAL_COLLECTION
        assert "removal" in cfg, f"{name} needs a removal note for Steps 19/20"
        assert "NOT comparable" in cfg.get("semantic_space", ""), (
            f"{name} must state it is not comparable with the canonical space"
        )


def test_mrl_ladder_survives_the_fallback_removal():
    """MRL truncation is LEGAL and must not be stripped.

    The ruling is: a 1024-D Qwen3 vector truncated to 768/512/256/128/64 is
    compliant. Only a NATIVE 768-D vector from a different model is illegal.
    This test guards against an overcorrection that deletes the ladder.
    """
    strategy = get_embedding_strategy()
    assert set(strategy.mrl_dimensions) >= {1024, 768, 512, 256, 128, 64}

    primary = strategy.get_provider_config("qwen3_primary")
    assert primary["mrl_enabled"] is True
    assert primary["default_mrl"] == CANONICAL, "canonical is the default, not a truncation"
    assert set(primary["mrl_dimensions"]) >= {768, 512, 256, 128, 64}


def test_mrl_truncated_canonical_is_accepted():
    """A Qwen3 provider explicitly configured for MRL truncation must NOT be
    refused by the width guard — same model, narrower width, legal."""
    from omega.memory.embeddings import (
        EmbeddingManager,
        SovereignFallbackEmbeddingProvider,
    )

    class MRLCanonicalProvider(SovereignFallbackEmbeddingProvider):
        """Canonical-width model emitting an explicitly-targeted MRL view."""

        def __init__(self, target_dim):
            super().__init__(dimension=CANONICAL)
            self._target_dim = target_dim

        @property
        def dimension(self):
            return self._target_dim

        async def get_embedding(self, text):
            return [0.1] * self._target_dim

    async def test():
        manager = EmbeddingManager(providers=[MRLCanonicalProvider(768)])
        with _production_embedding_path():
            vec, provider_name = await manager.get_embedding("hello")
        assert len(vec) == 768
        assert provider_name == "MRLCanonicalProvider"

    asyncio.run(test())


def test_ollama_provider_requires_explicit_model():
    """OllamaEmbeddingProvider must not default to nomic-embed-text.

    A no-arg construction would silently produce a natively-768 nomic vector
    for whatever caller asked for it. The model must be named explicitly.
    """
    from omega.memory.embeddings import OllamaEmbeddingProvider

    with pytest.raises(ValueError, match="requires an explicit model"):
        OllamaEmbeddingProvider()

    # Explicit use for a legacy collection is still allowed.
    p = OllamaEmbeddingProvider(model="nomic-embed-text:v1.5")
    assert p.dimension == 768


def test_canonical_unavailable_raises_naming_the_decision():
    """NEGATIVE TEST — canonical provider unavailable must RAISE, not substitute.

    This is the exact defect: with Qwen3 forced unavailable, the old chain
    answered with a 768-D nomic vector. The new chain must raise an error that
    names D-1024-DIM-NATIVE-20260926 and mentions the legal MRL alternative.
    """
    from omega.memory.embeddings import (
        EmbeddingManager,
        EmbeddingProviderUnavailableError,
        IEmbeddingProvider,
        SovereignFallbackEmbeddingProvider,
    )

    class DeadCanonicalProvider(IEmbeddingProvider):
        """Canonical-width provider that is unavailable."""

        def __init__(self):
            self._dimension = CANONICAL

        @property
        def dimension(self):
            return self._dimension

        async def get_embedding(self, text):
            raise FileNotFoundError(
                "Qwen3 GGUF model not found: /models/embeddings/Qwen3-Embedding-0.6B-Q5_K_M.gguf"
            )

    class NativeNomic768(SovereignFallbackEmbeddingProvider):
        """Stands in for nomic-embed-text: natively 768-D, NO target_dim.

        The absence of `_target_dim` is what marks this as a different model
        rather than an MRL view — exactly how the guard tells them apart.
        """

        def __init__(self):
            super().__init__(dimension=768)

        @property
        def dimension(self):
            return 768

        async def get_embedding(self, text):
            return [0.1] * 768

    async def test():
        manager = EmbeddingManager(
            providers=[DeadCanonicalProvider(), NativeNomic768()]
        )
        with _production_embedding_path(), pytest.raises(
            EmbeddingProviderUnavailableError
        ) as exc:
            await manager.get_embedding("some text")

        message = str(exc.value)
        assert "D-1024-DIM-NATIVE-20260926" in message
        assert "Qwen3-Embedding-0.6B" in message
        assert "1024" in message
        # The legal alternative must be named so the operator knows what IS ok.
        assert "MRL" in message
        # The refused provider must be listed, proving nomic was attempted
        # and rejected rather than silently accepted.
        assert "NativeNomic768" in message
        assert "768" in message

    asyncio.run(test())


def test_cross_model_substitution_is_refused_before_return():
    """A provider that answers at the wrong width must not reach the caller.

    Even when a later provider in the chain would have succeeded, the
    wrong-width answer is discarded — the manager verifies BEFORE returning.
    """
    from omega.memory.embeddings import (
        EmbeddingManager,
        SovereignFallbackEmbeddingProvider,
    )

    class NativeNomic768(SovereignFallbackEmbeddingProvider):
        def __init__(self):
            super().__init__(dimension=768)

        @property
        def dimension(self):
            return 768

        async def get_embedding(self, text):
            return [0.1] * 768

    async def test():
        # Chain ends in the canonical-width sovereign emitter.
        manager = EmbeddingManager(
            providers=[NativeNomic768(), SovereignFallbackEmbeddingProvider(dimension=CANONICAL)]
        )
        with _production_embedding_path():
            vec, provider_name = await manager.get_embedding("hello")
        # The 768 answer was refused; the canonical-width provider answered.
        assert len(vec) == CANONICAL
        assert provider_name == "SovereignFallbackEmbeddingProvider"

    asyncio.run(test())


def test_circuit_breaker_refuses_wrong_width_provider():
    """The circuit breaker is failover, not substitution.

    A natively-768 provider registered on the chain must be refused, and the
    chain must fall through to the canonical-width sovereign emitter.
    """
    from omega.memory.embedding_circuit_breaker import EmbeddingCircuitBreaker
    from omega.memory.embeddings import SovereignFallbackEmbeddingProvider

    class NativeNomic768(SovereignFallbackEmbeddingProvider):
        def __init__(self):
            super().__init__(dimension=768)

        @property
        def dimension(self):
            return 768

        async def get_embedding(self, text):
            return [0.1] * 768

    async def test():
        breaker = EmbeddingCircuitBreaker([NativeNomic768()])
        with _production_embedding_path():
            vec = await breaker.embed("hello")
        assert len(vec) == CANONICAL, (
            f"breaker returned {len(vec)}-dim; a sub-canonical vector escaped"
        )

    asyncio.run(test())


def test_strategy_provider_key_is_id():
    """Provider lookup must use 'id' field from YAML, not 'name'."""
    strategy = get_embedding_strategy()
    providers = strategy.get_providers()

    for p in providers:
        assert "id" in p, f"Provider missing 'id' field: {p}"
        # Verify we can look up by id
        found = strategy.get_provider_config(p["id"])
        assert found is not None, f"Cannot find provider by id: {p['id']}"
        assert found["id"] == p["id"]


def test_health_check_reports_dim_match():
    """Adapter get_status must report dimension match + migration state."""
    from omega.memory.sqlite_vec_adapter import SQLiteVecAdapter

    async def test():
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            path = f.name

        adapter = SQLiteVecAdapter(db_path=path)
        try:
            status = await adapter.get_status()
            assert "canonical_dimension" in status
            assert "strategy_dimension" in status
            assert "dimension_match" in status
            assert status["dimension_match"] is True
            assert status["canonical_dimension"] == CANONICAL
            assert status["canonical_collection"] == CANONICAL_COLLECTION
            # Migration inventory: empty == nothing left to re-embed.
            assert status["legacy_vec_tables"] == {}
            assert status["legacy_vec_rows"] == 0
        finally:
            await adapter.close()

    asyncio.run(test())


# ── helper ───────────────────────────────────────────────────────────────

def _rg_or_grep(pattern: str, target: str) -> str:
    """Search the tree with ripgrep when present, grep otherwise."""
    if shutil.which("rg"):
        cmd = ["rg", "-n", pattern, target]
    else:
        cmd = ["grep", "-rn", pattern, target]
    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd=str(REPO_ROOT)
    )
    return result.stdout
