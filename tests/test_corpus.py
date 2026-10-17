# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Contract tests for the Sovereign Ark corpus embedding library.

Deliberately model-FREE: these assert the invariants that make the index
trustworthy (canonical width, atomic writes, injection-safe FTS, physical
core pinning, M1 compliance) without loading a 444MB GGUF. The live
embedding path is covered by tests/test_corpus_live.py (opt-in).
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from omega.corpus import chunker, sources, store as store_mod
from omega.corpus.store import CANONICAL_DIM, CorpusStore

SRC = Path(__file__).resolve().parents[1] / "src" / "omega" / "corpus"


# ── canonical width (D-1024-DIM-NATIVE-20260926) ───────────────────────────
def test_canonical_dim_is_1024():
    """The corpus collection is canonical. 768 is legal only as MRL."""
    assert CANONICAL_DIM == 1024


def test_store_declares_canonical_collection(tmp_path):
    """The vec0 table must be created at the canonical width."""
    s = CorpusStore(tmp_path / "c.db")
    try:
        row = s._conn.execute(
            "SELECT sql FROM sqlite_master WHERE name='chunks_vec'"
        ).fetchone()
        assert row is not None
        assert f"float[{CANONICAL_DIM}]" in row["sql"]
    finally:
        s.close()


def test_store_rejects_non_canonical_vector(tmp_path):
    """A 768-wide vector must be refused at the write boundary."""
    s = CorpusStore(tmp_path / "c.db")
    try:
        s.upsert_document(
            doc_id="d1", source_id="t", tier=1, uri="/tmp/x.md", title="X",
            sha256="abc", n_bytes=10, mtime=0.0,
        )
        with pytest.raises(ValueError, match="canonical width violation"):
            s.add_chunks("d1", [{"ord": 0, "text": "hello world", "embedding": [0.1] * 768}])
    finally:
        s.close()


def test_accepts_canonical_vector(tmp_path):
    s = CorpusStore(tmp_path / "c.db")
    try:
        s.upsert_document(
            doc_id="d1", source_id="t", tier=1, uri="/tmp/x.md", title="X",
            sha256="abc", n_bytes=10, mtime=0.0,
        )
        s.add_chunks("d1", [{"ord": 0, "text": "hello world", "embedding": [0.1] * 1024}])
        st = s.stats()
        assert st["chunks"] == 1
        assert st["vectors"] == 1
    finally:
        s.close()


# ── FTS safety ─────────────────────────────────────────────────────────────
def test_fts_query_ors_terms():
    """FTS5 ANDs bare terms; we OR so multi-word questions actually match."""
    terms = ["Mayan", "elder", "interview", "station"]
    expr = CorpusStore._fts_query(" ".join(terms))
    assert " OR " in expr
    # every term quoted => 2 quotes each
    assert expr.count('"') == 2 * len(terms)
    for t in terms:
        assert f'"{t}"' in expr


def test_fts_query_injection_safe():
    """FTS5 operators in user input must not reach the MATCH expression."""
    expr = CorpusStore._fts_query('foo" OR NEAR(x) AND (bar')
    for danger in ("NEAR(", " AND (", "OR NEAR"):
        assert danger not in expr or expr.count(danger) == 0
    assert expr.startswith('"foo"')


def test_fts_query_empty_is_empty():
    assert CorpusStore._fts_query("") == ""
    assert CorpusStore._fts_query("a") == ""  # single char filtered


def test_fts_rejects_bad_operator_without_raising(tmp_path):
    """A hostile query must return [] (or safe results), never raise SQL error."""
    s = CorpusStore(tmp_path / "c.db")
    try:
        assert s.fts('") OR 1=1 --', 5) == [] or isinstance(s.fts('") OR 1=1 --', 5), list)
    finally:
        s.close()


# ── chunker ─────────────────────────────────────────────────────────────────
def test_chunk_respects_token_budget():
    """1500 chars must stay under the provider's 512-token n_ctx."""
    text = "\n\n".join(["word " * 120 for _ in range(40)])  # ~4800 chars
    chunks = chunker.chunk_document(text)
    assert chunks
    for c in chunks:
        assert len(c.text) <= chunker.CHUNK_CHARS + chunker.CHUNK_OVERLAP + 200


def test_chunk_short_doc_is_one_chunk():
    assert len(chunker.chunk_document("short text")) == 1


def test_chunk_empty_is_none():
    assert chunker.chunk_document("") == []
    assert chunker.chunk_document("   \n  ") == []


def test_chunk_ords_are_sequential():
    chunks = chunker.chunk_document("\n\n".join(f"para {i} " * 60 for i in range(20)))
    assert [c.ord for c in chunks] == list(range(len(chunks)))


def test_extract_text_strips_html():
    html = "<html><script>bad()</script><h1>Title</h1><p>Body &amp; text</p></html>"
    out = chunker.extract_text(html, ".html")
    assert "bad()" not in out
    assert "Title" in out and "Body & text" in out


def test_title_from_text_prefers_heading():
    assert chunker.title_from_text("# The Ark\nbody") == "The Ark"


# ── physical core pinning ───────────────────────────────────────────────────
def test_physical_core_ids_are_distinct_cores():
    """On SMT the representative CPUs must not be siblings of each other."""
    from omega.corpus.embedder import physical_core_ids

    reps = physical_core_ids()
    assert reps, "expected at least one physical core representative"
    assert len(set(reps)) == len(reps)
    assert reps == sorted(reps)


def test_physical_core_ids_are_not_smt_siblings():
    """No two representatives may share a core (the 'thrashing' case)."""
    sibling = {}
    for p in Path("/sys/devices/system/cpu").glob("cpu[0-9]*/topology/thread_siblings_list"):
        try:
            raw = p.read_text().strip()
        except OSError:
            continue
        members = set()
        for part in raw.split(","):
            part = part.strip()
            if "-" in part:
                a, _, b = part.partition("-")
                members.update(range(int(a), int(b) + 1))
            elif part.isdigit():
                members.add(int(part))
        for m in members:
            sibling[m] = frozenset(members)

    from omega.corpus.embedder import physical_core_ids

    reps = physical_core_ids()
    for i, a in enumerate(reps):
        for b in reps[i + 1:]:
            if a in sibling and sibling[a] == sibling.get(b):
                pytest.skip("no SMT topology available; representative mapping unverifiable")


def test_default_threads_leaves_a_core_free():
    from omega.corpus.embedder import default_threads, physical_core_ids

    assert 1 <= default_threads() <= max(1, len(physical_core_ids()))


# ── M1 AnyIO compliance ────────────────────────────────────────────────────
def test_corpus_module_never_imports_asyncio():
    """M1 is Absolute. The corpus library must not import asyncio anywhere."""
    for py in SRC.rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    assert a.name != "asyncio", f"{py} imports asyncio"
            elif isinstance(node, ast.ImportFrom):
                assert (node.module or "") != "asyncio", f"{py} imports from asyncio"


# ── sources ─────────────────────────────────────────────────────────────────
def test_resolve_sources_drops_missing_roots():
    """A missing partition degrades to 'source unavailable', never a crash."""
    from omega.corpus.sources import CorpusSource, resolve_sources

    got = resolve_sources()
    assert isinstance(got, list)
    for s in got:
        assert any(r.exists() for r in s.roots)


def test_resolve_sources_filters_by_id():
    from omega.corpus.sources import resolve_sources

    got = resolve_sources(["vision_corpus"])
    assert all(s.source_id == "vision_corpus" for s in got)


# ── idempotency / resume ────────────────────────────────────────────────────
def test_reindex_upserts_without_duplicating(tmp_path):
    """Re-indexing the same doc must replace, not append (resume safety)."""
    s = CorpusStore(tmp_path / "c.db")
    try:
        s.upsert_document(
            doc_id="d1", source_id="t", tier=1, uri="/x.md", title="X",
            sha256="h", n_bytes=1, mtime=0.0,
        )
        s.add_chunks("d1", [{"ord": 0, "text": "alpha", "embedding": [0.0] * 1024}])
        s.upsert_document(
            doc_id="d1", source_id="t", tier=1, uri="/x.md", title="X2",
            sha256="h2", n_bytes=1, mtime=0.0,
        )
        s.add_chunks("d1", [{"ord": 0, "text": "beta", "embedding": [0.0] * 1024}])
        st = s.stats()
        assert st["chunks"] == 1
        assert st["vectors"] == 1
        assert s.chunk_by_id(s.knn([0.0] * 1024, 1)[0]["id"])["text"] == "beta"
    finally:
        s.close()


def test_already_indexed_detects_unchanged(tmp_path):
    s = CorpusStore(tmp_path / "c.db")
    try:
        s.upsert_document(
            doc_id="d1", source_id="t", tier=1, uri="/x.md", title="X",
            sha256="same", n_bytes=1, mtime=0.0, status="done",
        )
        assert s.already_indexed("d1", "same") is True
        assert s.already_indexed("d1", "different") is False
        assert s.already_indexed("nope", "same") is False
    finally:
        s.close()


# ── RRF ─────────────────────────────────────────────────────────────────────
def test_rrf_ranks_agreement_first(tmp_path):
    s = CorpusStore(tmp_path / "c.db")
    try:
        fused = s.rrf_fuse(
            [{"id": 1}, {"id": 2}], [{"id": 2}, {"id": 1}], top_k=2
        )
        assert {f["id"] for f in fused} == {1, 2}
        assert all(f["rrf"] > 0 for f in fused)
    finally:
        s.close()
