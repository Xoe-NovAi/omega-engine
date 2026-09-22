# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Omega Engine — Iterative RAG (complex path)
# AP: AP-RAG-ITERATIVE-v1.0.0
# ⬡ OMEGA ⬡ LILITH ⬡ rag.iterative_rag ⬡ S3
#
# Iterative RAG: ReAct-style loop for complex, multi-hop queries.
# [heritage: quake3-1999] netchan — multi-step reasoning with bounded iterations.

from __future__ import annotations

import logging
from typing import List

import anyio

logger = logging.getLogger(__name__)


class IterativeRAG:
    """Multi-step RAG for complex queries. Max 3 iterations (bounded)."""

    MAX_ITERATIONS = 3

    def __init__(self, model_gateway=None, memory_store=None, max_iterations: int = MAX_ITERATIONS):
        self.model_gateway = model_gateway
        self.memory_store = memory_store
        self.max_iterations = max_iterations

    async def answer(self, query: str) -> str:
        """Iterative retrieval and reasoning with a bounded ReAct loop.

        Returns the synthesized answer with a confidence note. Degrades
        gracefully if no gateway/store is available (M9: typed, never silent).
        """
        sub_questions: List[str] = [query]
        evidence: List[str] = []

        if self.model_gateway is None:
            return f"[IterativeRAG] No model gateway available to reason over: {query}"

        for i in range(self.max_iterations):
            try:
                # Step 1: decompose / refine the next sub-question
                decomp = await self.model_gateway.generate(
                    model_name="default",
                    system_prompt=(
                        "You are a research planner. Given the query and what is already "
                        "known, output the single next sub-question to investigate, or "
                        "OUTPUT: DONE if enough is known to answer."
                    ),
                    user_query=f"ORIGINAL: {query}\nKNOWN: {chr(10).join(evidence)}\nSTEP: {i + 1}",
                    temperature=0.2,
                    max_tokens=256,
                )
                if "DONE" in decomp.text.upper():
                    break
                sub_questions.append(decomp.text.strip())

                # Step 2: retrieve evidence for the latest sub-question
                if self.memory_store is not None:

                    def _retrieve(q: str):
                        try:
                            return self.memory_store.search_fts(q, limit=3)
                        except Exception as e:  # noqa: BLE001
                            logger.debug("IterativeRAG FTS retrieval failed: %s", e)
                            return []

                    results = await anyio.to_thread.run_sync(_retrieve, sub_questions[-1])
                    evidence.extend(r.get("text", "") for r in results if isinstance(r, dict))
            except Exception as e:  # noqa: BLE001 — bounded loop must not crash
                logger.warning("IterativeRAG step %d failed (non-fatal): %s", i + 1, e)
                break

        try:
            final = await self.model_gateway.generate(
                model_name="default",
                system_prompt="Synthesize a complete, cited answer from the gathered evidence.",
                user_query=f"ORIGINAL QUERY: {query}\nEVIDENCE:\n{chr(10).join(evidence)}",
                temperature=0.3,
                max_tokens=2048,
            )
            return final.text
        except Exception as e:  # noqa: BLE001
            logger.warning("IterativeRAG final synthesis failed (non-fatal): %s", e)
            return f"[IterativeRAG] Synthesis unavailable after {len(evidence)} evidence items."
