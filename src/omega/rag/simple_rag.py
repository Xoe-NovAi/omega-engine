# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Omega Engine — Simple RAG (factual path)
# AP: AP-RAG-SIMPLE-v1.0.0
# ⬡ OMEGA ⬡ LILITH ⬡ rag.simple_rag ⬡ S3
#
# Simple RAG: top-k retrieval + single generation. No iteration.
# [heritage: quake3-1999] netchan — single-shot, low-latency response path.

from __future__ import annotations

import logging
from typing import List, Optional

import anyio

logger = logging.getLogger(__name__)


class SimpleRAG:
    """Direct RAG for factual queries. One retrieval, one generation."""

    def __init__(self, model_gateway=None, memory_store=None, top_k: int = 5):
        self.model_gateway = model_gateway
        self.memory_store = memory_store
        self.top_k = top_k

    async def answer(self, query: str, top_k: Optional[int] = None) -> str:
        """Retrieve top-k chunks and generate a single answer.

        [M1: AnyIO] Retrieval is wrapped in to_thread for blocking I/O.
        Degrades gracefully: if no store/gateway, returns a honest fallback.
        """
        k = top_k or self.top_k
        contexts: List[str] = []
        try:
            if self.memory_store is not None:

                def _retrieve():
                    try:
                        return self.memory_store.search_fts(query, limit=k)
                    except Exception:  # noqa: BLE001 — retrieval is best-effort
                        return []

                results = await anyio.to_thread.run_sync(_retrieve)
                contexts = [r.get("text", "") for r in results if isinstance(r, dict)]
        except Exception as e:  # noqa: BLE001 — never let retrieval crash the path
            logger.warning("SimpleRAG retrieval failed (non-fatal): %s", e)

        if self.model_gateway is None:
            # Offline / no-gateway fallback — return retrieved context or notice.
            if contexts:
                return "\n\n".join(contexts[:k])
            return f"[SimpleRAG] No model gateway available to answer: {query}"

        try:
            res = await self.model_gateway.generate(
                model_name="default",
                system_prompt="Answer the query using only the provided context. Be concise.",
                user_query=f"CONTEXT:\n{chr(10).join(contexts)}\n\nQUERY: {query}",
                temperature=0.2,
                max_tokens=1024,
            )
            return res.text
        except Exception as e:  # noqa: BLE001 — graceful degradation
            logger.warning("SimpleRAG generation failed (non-fatal): %s", e)
            return f"[SimpleRAG] Generation unavailable: {query}"
