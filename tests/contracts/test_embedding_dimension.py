# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Contract tests: the write path MUST emit the canonical dimension (1024).

[D-1024-DIM-NATIVE-20260926] Native 1024 (Qwen3-Embedding-0.6B) IS canonical.
MRL truncation remains AVAILABLE but is NOT the canonical path, so a provider
whose NATIVE width is below 1024 can never serve the canonical collection.
"""
import asyncio
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
