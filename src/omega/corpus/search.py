# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Corpus search — hybrid semantic (1024-dim canonical) + lexical (FTS5).

Combines KNN and BM25 via Reciprocal Rank Fusion, matching the engine's
existing hybrid convention (see omega.memory.hybrid_search). A pure-semantic
index misses exact identifiers ("3-Stage Offline Build System", "D-1024-DIM-
NATIVE"); a pure-lexical index misses paraphrase. RRF gets both without
having to calibrate two score scales that don't share units.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import anyio

from .store import CorpusStore


@dataclass
class SearchHit:
    id: int
    title: str
    uri: str
    tier: int
    text: str
    rrf: float
    distance: Optional[float] = None
    semantic: bool = False
    lexical: bool = False


class CorpusSearch:
    def __init__(self, store: CorpusStore, embedder=None):
        self.store = store
        self._embedder = embedder

    @property
    def embedder(self):
        if self._embedder is None:
            from .embedder import CorpusEmbedder

            self._embedder = CorpusEmbedder()
        return self._embedder

    async def _embed_query(self, q: str):
        vec = await self.embedder.get_embedding(q, is_query=True)
        if vec is None or len(vec) != 1024:
            raise RuntimeError("non-canonical query embedding [D-1024-DIM-NATIVE-20260926]")
        return list(vec)

    async def search(self, query: str, top_k: int = 10, lexical_only: bool = False) -> List[SearchHit]:
        # Lexical arm
        try:
            lex_rows = await anyio.to_thread.run_sync(self.store.fts, query, top_k * 3)
        except Exception:
            lex_rows = []

        # Semantic arm (canonical 1024)
        sem_rows = []
        dist_by_id = {}
        if not lexical_only:
            try:
                qvec = await self._embed_query(query)
                sem_rows = await anyio.to_thread.run_sync(self.store.knn, qvec, top_k * 3)
                for r in sem_rows:
                    dist_by_id[r["id"]] = r["distance"]
            except Exception:
                sem_rows = []

        fused = await anyio.to_thread.run_sync(self.store.rrf_fuse, sem_rows, lex_rows, top_k)
        lex_ids = {r["id"] for r in lex_rows}
        sem_ids = {r["id"] for r in sem_rows}

        hits: List[SearchHit] = []
        for item in fused:
            row = await anyio.to_thread.run_sync(self.store.chunk_by_id, item["id"])
            if not row:
                continue
            hits.append(
                SearchHit(
                    id=row["id"],
                    title=row["title"] or "",
                    uri=row["uri"] or "",
                    tier=row["tier"],
                    text=row["text"],
                    rrf=item["rrf"],
                    distance=dist_by_id.get(item["id"]),
                    semantic=row["id"] in sem_ids,
                    lexical=row["id"] in lex_ids,
                )
            )
        return hits
