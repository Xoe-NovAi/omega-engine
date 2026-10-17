# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Corpus store — SQLite (FTS5 lexical + sqlite-vec 1024 semantic) persistence.

[D-1024-DIM-NATIVE-20260926] The vector collection is declared at the
canonical width 1024 and rejects any other width at CREATE time. The
session corpus (384/minilm) is a separate DB and is untouched here
(one-space-per-collection).

Design notes:
- `chunks_vec.rowid` == `chunks.id`, so a KNN hit maps straight to its
  chunk/document without a join table.
- Upsert is by (doc_id, content hash): a file whose bytes are unchanged is
  skipped on re-index, which is what makes incremental runs cheap.
- No async: this module is synchronous SQLite; callers offload to a thread
  via anyio.to_thread (see indexer) to keep the event loop responsive.
"""

from __future__ import annotations

import re
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

CANONICAL_DIM = 1024  # [D-1024-DIM-NATIVE-20260926]

# Terms for FTS5 query construction (letters/digits/underscore, 2+ chars).
_TERM_RE = re.compile(r"[\w]{2,}", re.UNICODE)

SCHEMA = f"""
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS documents (
    doc_id     TEXT PRIMARY KEY,
    source_id  TEXT NOT NULL,
    tier       INTEGER NOT NULL,
    uri        TEXT NOT NULL,
    title      TEXT,
    sha256     TEXT NOT NULL,
    bytes      INTEGER,
    mtime      REAL,
    n_chunks   INTEGER DEFAULT 0,
    status     TEXT DEFAULT 'pending',
    indexed_at TEXT,
    UNIQUE(source_id, uri)
);
CREATE INDEX IF NOT EXISTS idx_documents_sha ON documents(sha256);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);

CREATE TABLE IF NOT EXISTS chunks (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id   TEXT NOT NULL,
    ord      INTEGER NOT NULL,
    title    TEXT,
    uri      TEXT,
    tier     INTEGER,
    text     TEXT NOT NULL,
    FOREIGN KEY(doc_id) REFERENCES documents(doc_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_chunks_doc ON chunks(doc_id);

CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
    title, uri, body, tokenize='porter unicode61'
);

-- Canonical semantic collection.
CREATE VIRTUAL TABLE IF NOT EXISTS chunks_vec USING vec0(
    embedding float[{CANONICAL_DIM}]
);
"""


def _load_vec(conn: sqlite3.Connection) -> sqlite3.Connection:
    conn.enable_load_extension(True)
    try:
        import sqlite_vec

        sqlite_vec.load(conn)
    finally:
        conn.enable_load_extension(False)
    return conn


class CorpusStore:
    """Owns one corpus SQLite DB.

    Threading: every accessor is dispatched via `anyio.to_thread.run_sync`,
    which may land on different worker threads. SQLite's default
    thread-affinity check therefore cannot apply, so the connection is
    opened with `check_same_thread=False` and every access is serialised
    behind a re-entrant lock. Writes additionally run inside an explicit
    transaction, so a crash mid-document cannot leave a half-written
    chunk/vector set (the FTS row and its vec0 row are inserted together).
    """

    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._conn = _load_vec(
            sqlite3.connect(str(self.db_path), check_same_thread=False)
        )
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        with self._lock:
            self._conn.executescript(SCHEMA)
            self._conn.commit()

    @contextmanager
    def tx(self):
        with self._lock:
            try:
                yield self._conn
                self._conn.commit()
            except Exception:
                self._conn.rollback()
                raise

    def _read(self, sql: str, params: tuple = ()):
        with self._lock:
            return self._conn.execute(sql, params).fetchall()

    def close(self) -> None:
        with self._lock:
            try:
                self._conn.commit()
            finally:
                self._conn.close()

    # ── documents ─────────────────────────────────────────────────────────
    def upsert_document(
        self,
        *,
        doc_id: str,
        source_id: str,
        tier: int,
        uri: str,
        title: str,
        sha256: str,
        n_bytes: int,
        mtime: float,
        status: str = "pending",
    ) -> None:
        with self.tx() as c:
            c.execute(
                """INSERT INTO documents
                   (doc_id, source_id, tier, uri, title, sha256, bytes, mtime, status, indexed_at)
                   VALUES (?,?,?,?,?,?,?,?,?, datetime('now'))
                   ON CONFLICT(doc_id) DO UPDATE SET
                     source_id=excluded.source_id, tier=excluded.tier,
                     uri=excluded.uri, title=excluded.title, sha256=excluded.sha256,
                     bytes=excluded.bytes, mtime=excluded.mtime,
                     status=excluded.status, indexed_at=datetime('now')""",
                (doc_id, source_id, tier, uri, title, sha256, n_bytes, mtime, status),
            )

    def already_indexed(self, doc_id: str, sha256: str) -> bool:
        rows = self._read("SELECT sha256, status FROM documents WHERE doc_id=?", (doc_id,))
        row = rows[0] if rows else None
        return bool(row and row["sha256"] == sha256 and row["status"] == "done")

    def pending_docs(self) -> List[sqlite3.Row]:
        return self._read("SELECT doc_id FROM documents WHERE status!='done'")

    # ── chunks + vectors ──────────────────────────────────────────────────
    def add_chunks(self, doc_id: str, chunks: Sequence[dict]) -> None:
        """Insert chunks + FTS rows + vec rows atomically for one document."""
        with self.tx() as c:
            doc = c.execute(
                "SELECT uri, title, tier FROM documents WHERE doc_id=?", (doc_id,)
            ).fetchone()
            if not doc:
                raise KeyError(f"document not registered: {doc_id}")
            uri, title, tier = doc["uri"], doc["title"], doc["tier"]
            # Replace prior content for this doc (idempotent re-index).
            old = c.execute("SELECT id FROM chunks WHERE doc_id=?", (doc_id,)).fetchall()
            if old:
                ids = [r["id"] for r in old]
                qs = ",".join("?" * len(ids))
                c.execute(f"DELETE FROM chunks_fts WHERE rowid IN ({qs})", ids)
                c.execute(f"DELETE FROM chunks_vec WHERE rowid IN ({qs})", ids)
                c.execute(f"DELETE FROM chunks WHERE doc_id=?", (doc_id,))

            for ch in chunks:
                cur = c.execute(
                    "INSERT INTO chunks (doc_id, ord, title, uri, tier, text) VALUES (?,?,?,?,?,?)",
                    (doc_id, ch["ord"], title, uri, tier, ch["text"]),
                )
                rid = cur.lastrowid
                c.execute(
                    "INSERT INTO chunks_fts(rowid, title, uri, body) VALUES (?,?,?,?)",
                    (rid, title or "", uri, ch["text"]),
                )
                emb = ch["embedding"]
                if len(emb) != CANONICAL_DIM:
                    raise ValueError(
                        f"canonical width violation: got {len(emb)}, expected {CANONICAL_DIM}"
                        " [D-1024-DIM-NATIVE-20260926]"
                    )
                c.execute(
                    "INSERT INTO chunks_vec(rowid, embedding) VALUES (?, ?)",
                    (rid, _pack(emb)),
                )
            c.execute(
                "UPDATE documents SET status='done', n_chunks=?, indexed_at=datetime('now') WHERE doc_id=?",
                (len(chunks), doc_id),
            )

    # ── retrieval ─────────────────────────────────────────────────────────
    def knn(self, embedding: Sequence[float], k: int = 20) -> List[sqlite3.Row]:
        return self._read(
            "SELECT v.rowid AS id, v.distance AS distance FROM chunks_vec v "
            "WHERE v.embedding MATCH ? AND k = ?",
            (_pack(embedding), k),
        )

    @staticmethod
    def _fts_query(raw: str) -> str:
        """Turn a natural-language query into a safe FTS5 OR-expression.

        FTS5 ANDs bare terms, so a 7-word question matches nothing and the
        lexical arm silently contributes zero rows (observed 2026-10-17:
        every hybrid hit was semantic-only). OR-ing the terms lets BM25 rank
        the documents that carry MOST of the query's terms, which is the
        behaviour a reader expects. Each term is quoted so FTS5 operators in
        user input cannot leak into the expression.
        """
        terms = [t for t in _TERM_RE.findall(raw or "") if t]
        if not terms:
            return ""
        return " OR ".join(f'"{t}"' for t in terms)

    def fts(self, query: str, k: int = 20) -> List[sqlite3.Row]:
        expr = self._fts_query(query)
        if not expr:
            return []
        return self._read(
            "SELECT rowid AS id, bm25(chunks_fts) AS score FROM chunks_fts "
            "WHERE chunks_fts MATCH ? ORDER BY score LIMIT ?",
            (expr, k),
        )

    def chunk_by_id(self, cid: int) -> Optional[sqlite3.Row]:
        rows = self._read("SELECT * FROM chunks WHERE id=?", (cid,))
        return rows[0] if rows else None

    def rrf_fuse(
        self, semantic: Sequence[sqlite3.Row], lexical: Sequence[sqlite3.Row], top_k: int = 20
    ) -> List[dict]:
        """Reciprocal Rank Fusion — the engine's standard hybrid combiner.

        Fuses the two ranked id streams by 1/(k+rank); `k=60` is the
        reference constant from the original RRF paper (Cormack et al.).
        """
        RRF_K = 60
        scores: Dict[int, float] = {}
        for rows in (semantic, lexical):
            for rank, row in enumerate(rows):
                cid = row["id"]
                scores[cid] = scores.get(cid, 0.0) + 1.0 / (RRF_K + rank + 1)
        ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:top_k]
        return [{"id": cid, "rrf": score} for cid, score in ranked]

    # ── stats ─────────────────────────────────────────────────────────────
    def stats(self) -> dict:
        docs = self._read("SELECT COUNT(*) c FROM documents")[0]["c"]
        chunks = self._read("SELECT COUNT(*) c FROM chunks")[0]["c"]
        vecs = self._read("SELECT COUNT(*) c FROM chunks_vec")[0]["c"]
        by_tier = self._read(
            "SELECT tier, COUNT(*) c FROM documents GROUP BY tier ORDER BY tier"
        )
        by_source = self._read(
            "SELECT source_id, COUNT(*) c, SUM(n_chunks) ch FROM documents GROUP BY source_id"
        )
        return {
            "db": str(self.db_path),
            "documents": docs,
            "chunks": chunks,
            "vectors": vecs,
            "canonical_dim": CANONICAL_DIM,
            "by_tier": {r["tier"]: r["c"] for r in by_tier},
            "by_source": {r["source_id"]: {"docs": r["c"], "chunks": r["ch"]} for r in by_source},
        }


def _pack(vec: Sequence[float]) -> bytes:
    """Serialize a float vector for sqlite-vec (float32 little-endian)."""
    import struct

    return struct.pack(f"{len(vec)}f", *vec)
