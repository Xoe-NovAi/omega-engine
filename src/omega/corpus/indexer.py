# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Corpus indexer — walks sources, chunks, embeds, and upserts.

M1 AnyIO: every blocking call (SQLite, file I/O, llama-cpp inference)
is dispatched with `anyio.to_thread.run_sync`. This module never imports
asyncio.

M23 Failure integrity: if the canonical embedder cannot be constructed the
run ABORTS. It does not fall back to deterministic hashing, because a
hashed corpus would answer "I have your Ark vision" with nonsense that
*looks* like an answer. Loud failure beats confident noise.

Resumable: a document is skipped when its content hash already exists with
status='done', so an interrupted run costs only the unfinished tail.
"""

from __future__ import annotations

import fnmatch
import hashlib
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import anyio

from .chunker import chunk_document, extract_text, title_from_text
from .sources import DEFAULT_SUFFIXES, CorpusSource, resolve_sources
from .store import CANONICAL_DIM, CorpusStore


@dataclass
class IndexReport:
    files_seen: int = 0
    files_indexed: int = 0
    files_skipped_unchanged: int = 0
    files_failed: int = 0
    chunks_written: int = 0
    errors: List[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "files_seen": self.files_seen,
            "files_indexed": self.files_indexed,
            "skipped_unchanged": self.files_skipped_unchanged,
            "failed": self.files_failed,
            "chunks_written": self.chunks_written,
            "errors": self.errors[:20],
        }


def _stat(path: Path):
    return path.stat()


def _read_text(path: Path) -> str:
    """Read a file as UTF-8, replacing undecodable bytes.

    anyio.to_thread.run_sync forwards positional args only, so the error
    policy is wrapped here rather than passed as a kwarg.
    """
    return path.read_text(encoding="utf-8", errors="ignore")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 16), b""):
            h.update(block)
    return h.hexdigest()


class CorpusIndexer:
    def __init__(self, store: CorpusStore, embedder=None):
        self.store = store
        self._embedder = embedder
        self.report = IndexReport()
        # Run-scoped knobs, set by run() before any file is indexed.
        self._max_chunks_per_doc: Optional[int] = None

    # ── embedder (lazy; canonical-only) ───────────────────────────────────
    @property
    def embedder(self):
        if self._embedder is None:
            # CorpusEmbedder binds the CANONICAL provider directly rather than
            # EmbeddingManager because:
            #  - the manager's get_embedding() has no `is_query` control, and
            #    Qwen3-Embedding only prefixes the instruction on QUERIES;
            #  - the manager short-circuits to a ZERO vector when
            #    OMEGA_ENV == "test", which would silently poison the corpus;
            #  - the manager cannot pin threads to physical cores.
            # Fail-loud: constructing this raises if the canonical GGUF or its
            # llama.cpp build (--pooling last) is missing.
            from .embedder import CorpusEmbedder

            self._embedder = CorpusEmbedder()
        return self._embedder

    def _register(self, doc_id, source_id, tier, uri, title, sha, n_bytes, mtime) -> None:
        """Positional shim for the store's kwargs-only upsert."""
        self.store.upsert_document(
            doc_id=doc_id, source_id=source_id, tier=tier, uri=uri, title=title,
            sha256=sha, n_bytes=n_bytes, mtime=mtime, status="pending",
        )

    async def _embed_one(self, text: str, is_query: bool) -> List[float]:
        vec = await self.embedder.get_embedding(text, is_query=is_query)
        if vec is None:
            raise RuntimeError("embedder returned None (canonical width guard tripped)")
        if len(vec) != CANONICAL_DIM:
            raise ValueError(
                f"non-canonical embedding width {len(vec)} != {CANONICAL_DIM} "
                "[D-1024-DIM-NATIVE-20260926]"
            )
        return list(vec)

    # ── file discovery ────────────────────────────────────────────────────
    def _iter_files(self, src: CorpusSource):
        suffixes = tuple(src.suffixes or DEFAULT_SUFFIXES)
        seen: set[Path] = set()
        for root in src.roots:
            if not root.exists():
                continue
            for dirpath, dirnames, filenames in os.walk(root):
                # prune excluded / hidden dirs
                dirnames[:] = [
                    d
                    for d in dirnames
                    if not any(x in d for x in src.exclude)
                    and (src.include_hidden or not d.startswith("."))
                ]
                for fn in filenames:
                    if not fn.lower().endswith(suffixes):
                        continue
                    if any(x in fn for x in src.exclude):
                        continue
                    p = Path(dirpath) / fn
                    if p in seen:
                        continue
                    seen.add(p)
                    yield p

    # ── per-file indexing (thread-offloaded) ──────────────────────────────
    async def _index_file(self, src: CorpusSource, path: Path) -> None:
        try:
            raw = await anyio.to_thread.run_sync(_read_text, path)
        except (OSError, UnicodeDecodeError) as exc:  # unreadable file — skip, record
            self.report.files_failed += 1
            self.report.errors.append(f"{path}: read {exc}")
            return
        if not raw.strip():
            return
        text = extract_text(raw, path.suffix)
        if len(text) < 120:
            return
        chunks = chunk_document(text)
        if not chunks:
            return
        cap = self._max_chunks_per_doc
        if cap and len(chunks) > cap:
            # Keep the head of the document: these files open with the thesis.
            chunks = chunks[:cap]

        doc_id = f"{src.source_id}:{path}"
        sha = await anyio.to_thread.run_sync(_sha256, path)
        title = title_from_text(text, fallback=path.name)
        st = await anyio.to_thread.run_sync(_stat, path)

        # Register, then embed each chunk, then upsert atomically.
        await anyio.to_thread.run_sync(
            self._register,
            doc_id, src.source_id, src.tier, str(path), title, sha, st.st_size, st.st_mtime,
        )

        rows = []
        for ch in chunks:
            emb = await self._embed_one(ch.text, is_query=False)
            rows.append({"ord": ch.ord, "text": ch.text, "embedding": emb})

        await anyio.to_thread.run_sync(self.store.add_chunks, doc_id, rows)
        self.report.files_indexed += 1
        self.report.chunks_written += len(rows)

    async def _maybe_skip(self, src: CorpusSource, path: Path) -> bool:
        """True if already indexed with identical content hash."""
        try:
            sha = await anyio.to_thread.run_sync(_sha256, path)
        except OSError as exc:
            logger.debug("Failed computing sha256 for %s: %s", path, exc)
            return False
        doc_id = f"{src.source_id}:{path}"
        already = await anyio.to_thread.run_sync(self.store.already_indexed, doc_id, sha)
        return bool(already)

    # ── main ──────────────────────────────────────────────────────────────
    async def run(
        self,
        source_ids: Optional[List[str]] = None,
        limit: Optional[int] = None,
        force: bool = False,
        progress=None,
        path_glob: Optional[str] = None,
        max_chunks_per_doc: Optional[int] = None,
    ) -> IndexReport:
        self._max_chunks_per_doc = max_chunks_per_doc
        sources = resolve_sources(source_ids)
        if not sources:
            self.report.errors.append("no corpus source roots present")
            return self.report

        for src in sources:
            for path in self._iter_files(src):
                if path_glob and not fnmatch.fnmatch(path.name, path_glob):
                    continue
                if limit is not None and self.report.files_seen >= limit:
                    return self.report
                self.report.files_seen += 1
                if not force and await self._maybe_skip(src, path):
                    self.report.files_skipped_unchanged += 1
                    continue
                await self._index_file(src, path)
                if progress and self.report.files_indexed % 25 == 0:
                    progress(self.report)
        return self.report
