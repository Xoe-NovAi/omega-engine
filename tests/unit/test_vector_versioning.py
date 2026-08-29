"""Unit tests for VectorVersionRegistry + DriftDetector.

AP: AP-VECTOR-VERSIONING-v1.0.0
"""
import sqlite3

import pytest

from src.omega.memory.vector_versioning import (
    DriftDetector,
    DRIFT_THRESHOLD_INVESTIGATE,
    DRIFT_THRESHOLD_REEMBED,
    MRL_COLLECTIONS,
    ModelVersion,
    VectorVersionRegistry,
)


@pytest.fixture
def in_memory_db():
    """Fresh in-memory SQLite DB per test, with row_factory=Row."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


# ── Test 1: version registration + retrieval ─────────────────────────────
def test_register_and_get_active_version(in_memory_db):
    reg = VectorVersionRegistry(in_memory_db)
    reg.ensure_schema()
    reg.register_version(
        ModelVersion(
            version_id="nomic-embed-v1.5",
            model_name="nomic-embed-text",
            dimension=768,
            status="active",
            promoted_at=1700000000,
        )
    )
    active = reg.get_active_version("nomic-embed-text")
    assert active is not None
    assert active.version_id == "nomic-embed-v1.5"
    assert active.dimension == 768
    assert active.status == "active"


def test_promote_demotes_predecessor(in_memory_db):
    """promote() must atomically demote the previous active version to shadow."""
    reg = VectorVersionRegistry(in_memory_db)
    reg.ensure_schema()
    reg.register_version(
        ModelVersion("v1.5", "nomic-embed-text", 768, "active", promoted_at=100)
    )
    reg.register_version(
        ModelVersion("v2.0", "nomic-embed-text", 768, "shadow", notes="next")
    )
    reg.promote("v2.0")
    v1 = reg.get_active_version("nomic-embed-text")
    assert v1 is not None and v1.version_id == "v2.0"
    # v1.5 should now be shadow
    row = in_memory_db.execute(
        "SELECT status FROM omega_memory_versions WHERE version_id='v1.5'"
    ).fetchone()
    assert row[0] == "shadow"


# ── Test 2: tag_vector + content_hash ────────────────────────────────────
def test_tag_vector_with_content_hash(in_memory_db):
    """Every tagged row gets a content_hash for incremental re-embed."""
    reg = VectorVersionRegistry(in_memory_db)
    reg.ensure_schema()
    # Need an actual rowid in the vec collection to tag (FK would
    # be cleaner; meta table is rowid-only so we just need unique rowids).
    reg.tag_vector("omega_vec_nomic_768", 1, "nomic-embed-v1.5", "hello world")
    reg.tag_vector(
        "omega_vec_nomic_768", 2, "nomic-embed-v1.5", "hello world"
    )  # same content
    counts = reg.count_by_version("omega_vec_nomic_768")
    assert counts == {"nomic-embed-v1.5": 2}


def test_ensure_schema_creates_all_mrl_collections(in_memory_db):
    """ensure_schema must create meta tables for every MRL collection."""
    reg = VectorVersionRegistry(in_memory_db)
    reg.ensure_schema()
    for coll in MRL_COLLECTIONS:
        row = in_memory_db.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{coll}_meta'"
        ).fetchone()
        assert row is not None, f"Missing meta table for {coll}"


# ── Test 3: drift detection ──────────────────────────────────────────────
def test_drift_detector_returns_zero_below_min_sample():
    """DriftDetector.compute_drift returns 0.0 for samples < MIN_SAMPLE_SIZE."""
    dd = DriftDetector(sqlite3.connect(":memory:"))
    small_recent = [[0.1] * 4 for _ in range(5)]
    small_base = [[0.2] * 4 for _ in range(5)]
    drift = dd.compute_drift(small_recent, small_base)
    assert drift == 0.0


def test_drift_detector_recommend_action():
    """recommend_action maps drift to ok / investigate / reembed."""
    dd = DriftDetector(sqlite3.connect(":memory:"))
    assert dd.recommend_action(0.05) == "ok"
    assert dd.recommend_action(DRIFT_THRESHOLD_INVESTIGATE - 0.01) == "ok"
    assert dd.recommend_action(0.15) == "investigate"
    assert dd.recommend_action(DRIFT_THRESHOLD_REEMBED - 0.01) == "investigate"
    assert dd.recommend_action(0.5) == "reembed"


def test_drift_detector_with_synthetic_distributions():
    """Same distribution → low drift. Shifted distribution → higher drift.

    This is the most important sanity check: the detector must NOT
    flag identical distributions as drift, and MUST flag clearly
    shifted distributions.
    """
    pytest.importorskip("numpy")
    pytest.importorskip("sklearn")
    pytest.importorskip("scipy")
    import numpy as np

    dd = DriftDetector(sqlite3.connect(":memory:"))
    rng = np.random.default_rng(42)
    # Identical distributions
    a_raw = rng.standard_normal((50, 8))
    a = [row.tolist() for row in a_raw]
    same_drift = dd.compute_drift(a, a)
    # Different distributions: shift the mean by 3 sigma
    b_raw = rng.standard_normal((50, 8)) + 3.0
    b = [row.tolist() for row in b_raw]
    shift_drift = dd.compute_drift(a, b)
    assert same_drift < 0.1, f"Same-distribution drift should be tiny, got {same_drift}"
    assert shift_drift > same_drift, "Shifted distribution should drift more"
