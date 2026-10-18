# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Regression tests for the corpus runtime defects found in the v1.6.0a6 review.

Why these exist: tests/test_corpus.py never constructs ``CorpusEmbedder`` and never
makes a retrieval arm fail, so three NameErrors shipped in the debut wheel:

* ``embedder.py`` used ``Path`` without importing it, so ``CorpusEmbedder()`` raised
  on any cgroup-v2 Linux host (the whole project's target platform).
* ``search.py`` used ``sqlite3`` and ``logger`` without defining them, so the
  ``except (sqlite3.OperationalError, ...)`` clause itself raised NameError and the
  documented lexical/semantic fallback never ran.
* ``indexer.py`` used ``logger`` without defining it (covered statically by
  tests/test_no_undefined_names.py).

Model-FREE and side-effect-free: no GGUF is loaded, the pytest process is never
really pinned (``os.sched_setaffinity`` is stubbed) and no real cgroup file is read
or written. M1: AnyIO only. This module never imports asyncio.
"""

from __future__ import annotations

import io
import sqlite3
from pathlib import Path

import anyio
import pytest

from omega.corpus import embedder as emb
from omega.corpus.search import CorpusSearch

CGROUP_V2_LINE = "0::/omega-test.slice\n"


def _fake_open(content: str):
    """Serve ``content`` for /proc/self/cgroup; defer to the real open otherwise."""
    real_open = open

    def _open(path, *args, **kwargs):
        if str(path) == "/proc/self/cgroup":
            return io.StringIO(content)
        return real_open(path, *args, **kwargs)

    return _open


@pytest.fixture
def cgroup_v2(monkeypatch):
    monkeypatch.setattr(emb, "open", _fake_open(CGROUP_V2_LINE), raising=False)


@pytest.fixture
def no_real_pinning(monkeypatch):
    calls: list[tuple[int, set[int]]] = []
    monkeypatch.setattr(
        emb.os, "sched_setaffinity", lambda pid, cpus: calls.append((pid, set(cpus))),
        raising=False,
    )
    monkeypatch.setattr(emb, "physical_core_ids", lambda: [0, 2, 4, 6])
    monkeypatch.delenv("OMEGA_CORPUS_NO_AFFINITY", raising=False)
    return calls


def test_cgroup_cpuset_path_resolves_on_cgroup_v2(cgroup_v2):
    path = emb._cgroup_cpuset_path()
    assert isinstance(path, Path)
    assert path.name == "cpuset.cpus.effective"


def test_apply_cgroup_cpuset_degrades_cleanly(cgroup_v2):
    assert emb._apply_cgroup_cpuset([0, 2]) is False


def test_pin_to_physical_cores_falls_back_to_affinity(cgroup_v2, no_real_pinning):
    chosen = emb.pin_to_physical_cores(2)
    assert chosen == [0, 2]
    assert no_real_pinning == [(0, {0, 2})]


def test_pin_respects_no_affinity_env(monkeypatch, no_real_pinning):
    monkeypatch.setenv("OMEGA_CORPUS_NO_AFFINITY", "1")
    assert emb.pin_to_physical_cores(2) is None
    assert no_real_pinning == []


def test_corpus_embedder_constructs_on_cgroup_v2(cgroup_v2, no_real_pinning):
    e = emb.CorpusEmbedder(n_threads=2, n_ctx=512)
    assert e._n_threads == 2
    assert e._n_ctx == 512
    assert e._affinity == [0, 2]


class _FakeStore:
    def __init__(self, fts_exc: Exception | None = None, fts_ids=(), knn_ids=()):
        self._fts_exc = fts_exc
        self._fts_ids = list(fts_ids)
        self._knn_ids = list(knn_ids)

    def fts(self, query, k):
        if self._fts_exc is not None:
            raise self._fts_exc
        return [{"id": i, "score": -1.0} for i in self._fts_ids]

    def knn(self, embedding, k):
        return [{"id": i, "distance": 0.1} for i in self._knn_ids]

    def rrf_fuse(self, semantic, lexical, top_k):
        ids = []
        for rows in (semantic, lexical):
            for r in rows:
                if r["id"] not in ids:
                    ids.append(r["id"])
        return [{"id": i, "rrf": 1.0 / (60 + n + 1)} for n, i in enumerate(ids[:top_k])]

    def chunk_by_id(self, cid):
        return {"id": cid, "title": f"t{cid}", "uri": f"u{cid}", "tier": 1, "text": "x"}


class _FailingEmbedder:
    def __init__(self, exc: Exception):
        self._exc = exc

    async def get_embedding(self, text, is_query=False):
        raise self._exc


@pytest.mark.parametrize(
    "exc",
    [
        sqlite3.OperationalError("fts5: syntax error"),
        sqlite3.DatabaseError("malformed"),
    ],
)
def test_search_survives_fts_errors(exc):
    search = CorpusSearch(_FakeStore(fts_exc=exc), embedder=object())
    assert anyio.run(search.search, "anything", 5, True) == []


@pytest.mark.parametrize(
    "exc",
    [FileNotFoundError("model missing"), RuntimeError("non-canonical embedding")],
)
def test_search_semantic_failure_falls_back_to_lexical(exc):
    store = _FakeStore(fts_ids=[7])
    search = CorpusSearch(store, embedder=_FailingEmbedder(exc))
    hits = anyio.run(search.search, "anything", 5, False)
    assert [h.id for h in hits] == [7]
    assert hits[0].lexical is True
    assert hits[0].semantic is False


def test_search_unexpected_error_is_not_swallowed():
    store = _FakeStore(fts_ids=[1])
    search = CorpusSearch(store, embedder=_FailingEmbedder(ZeroDivisionError("bug")))
    with pytest.raises(ZeroDivisionError):
        anyio.run(search.search, "anything", 5, False)