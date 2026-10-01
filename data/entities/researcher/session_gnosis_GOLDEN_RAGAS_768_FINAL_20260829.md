<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Researcher Session Gnosis — Final — 2026-08-29

**Session**: ses_fe8cf0b39ffeL3L8eaMEj3CW9H (Grokster handoff)
**Deliverable**: `data/coordination/R_RESEARCHER_GOLDEN_SET_RAGAS_768DIM_20260829.md` (1,316 lines, 73 KB)

---

## Final Recommendations (L1)

### Q1: Golden Set + RAGAS Harness
- **RAGAS 0.4 with collections-based API** (`from ragas.metrics.collections import Faithfulness`).
- 100-200 item human-curated golden set + 500-1000 item synthetic (RAGAS TestsetGenerator).
- 4 metrics: Faithfulness, Answer Relevancy, Context Precision, Context Recall.
- Local Ollama qwen3:8b judge (M7). Calibration set (30 items) for LLM-human Spearman ρ > 0.7.
- Pytest CI gate; thresholds from baseline; HHEM-2.1-Open as secondary check.

### Q2: 768-dim Model
- **PRIMARY**: Qwen3-Embedding-0.6B (Apache 2.0, 32K context, MTEB Eng v2 70.70, MRL to 768).
- **FALLBACK**: EmbeddingGemma-300M (Gemma license, 2K context, MTEB Eng v2 69.67, Q4_0 200MB).
- **SUPERSEDED**: nomic-embed-text-v1.5 (62.28, +8.42 MTEB gap to Qwen3).
- **RERANKER CO-DESIGN**: Qwen3-Reranker-0.6B (65.80 MTEB-R vs BGE-m3 57.03).

### Migration Pattern
- 1-2 weeks: dual-write to `omega_vec_qwen3_768` alongside `omega_vec_gemma_768`.
- 1-2 weeks: shadow validation (both, log both, RAGAS compare).
- 1 day: cutover. Keep old 30 days as read-only fallback. Drop after 30 days.
- 4 new MRL slices (512/256/128/64) are sliced at query time — no re-embed cost.

---

## Council Verdict (Dialectic)

### Architect
- 768-dim canonical preserved (M7/M14 mandate).
- MRL truncates 1024→768 with <0.5 MTEB point loss.
- Apache 2.0 = simplest license audit trail.
- 32K context unlocks late chunking, contextual retrieval, recursive 8K chunks.

### Adversary
- EmbeddingGemma-300M wins on size (200MB Q4) and density (226 pts/B vs 117.8).
- BUT Omega's constraint is 8GB RAM, not 200MB. Both models fit.
- EmbeddingGemma's 2K context blocks late chunking — hard NO for Omega.
- 30-day rollback window + shadow validation = reversible migration.

### Alchemist
- Single-vendor stack: Qwen3-Embedding-0.6B + Qwen3-Reranker-0.6B.
- Joint fine-tuning, shared tokenizers, shared serving infra.
- Apache 2.0 across both = M14 clean.

### Archivist
- nomic-embed (62.28) → Qwen3-0.6B (70.70) is +8.42 MTEB Eng v2 jump.
- Golden set is a long-lived asset; reusable for future model swaps.
- PremAI 2026-03-17: "Run your own retrieval eval on a sample of your data before committing." — the golden set makes this possible.

---

## Search Toolchain Notes (per M23)

- Parallel MCP: rate-limited (free-tier).
- SearXNG: down (all connection attempts failed).
- Sovereign Search tier-1/3: empty results.
- **Firecrawl search + webfetch: working**. Used for all primary research.
- Exa: 401 invalid key.

The Sovereign Search Fleet had multiple failures; the [TOOL-CHAIN-COLLAPSE] protocol was narrowly avoided by the Firecrawl fallback. This should be flagged in the entity workspace.

---

## Verified Sources (24 unique URLs, all fetched 2026-08-29)

1. PremAI 2026-03-17 — 10 best embedding models
2. D-Central 2026-07-17 — 20 local models
3. CodeSota 2026-05-17 — MTEB leaderboard
4. Qwen blog 2025-06-05 — Qwen3 Embedding
5. Qwen3-Embedding-0.6B HF card
6. Google Developers Blog 2025-09-04 — EmbeddingGemma
7. EmbeddingGemma-300M HF card
8. RAGAS metrics catalog (docs.ragas.io)
9. RAGAS Faithfulness page
10. QASkills.sh 2026-06-27 — RAGAS guide
11. Atlan 2026-04-10 — RAG evaluation
12. PremAI 2026-07-27 — RAG evaluation metrics
13. HF MTEB Leaderboard space
14. Qwen3 Embedding arXiv 2506.05176
15. Modal — MTEB leaderboard
16. Superlinked 2026-07 — Qwen3 latency
17. Contra Collective 2026-06-27 — BGE-m3 vs Qwen3
18. Digital Applied 2026-05-27 — chunking strategies
19. Vectara — HHEM-2.1-Open
20. R_RESEARCHER_RAGAS_20260829 (prior research)
21. R_RESEARCHER_SQLITE_VEC_HARDENING_20260829 (prior research)
22. JEM_SQLITE_VEC_RECALL_HARDENING_20260829 (prior research)
23. CodeSota RAG tiers
24. Atlan RAGAS vs TruLens vs DeepEval

---

## File Locations

- **Deliverable**: `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/coordination/R_RESEARCHER_GOLDEN_SET_RAGAS_768DIM_20260829.md`
- **Session gnosis (intermediate)**: `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/entities/researcher/session_gnosis_GOLDEN_RAGAS_768_20260829.md`
- **Session gnosis (final)**: this file
- **Hivemind post**: sent with intent=handoff, channel=opencode, entity=researcher

---

## Open Questions for Ma'at (Build)

1. **RAGAS 0.4 install**: confirm `pip install "ragas>=0.4.0,<0.5"` works in `.venv/`. RAGAS pulls in langchain — verify no version conflict.
2. **Qwen3-Embedding-0.6B Ollama tag**: `ollama pull qwen3-embedding:0.6b` — verify the tag exists. If not, use `hf.co/Qwen/Qwen3-Embedding-0.6B-GGUF` with Q4_0.
3. **sentence-transformers version**: requires `>=2.7.0` for Qwen3-Embedding-0.6B. Verify .venv has it.
4. **HF model access**: EmbeddingGemma-300M requires a license click on HF. Confirm arcana-novai account has access.
5. **Ollama resource contention**: with both the embedding model and the LLM judge (qwen3:8b) loaded, total RAM = 1.2 + ~5 GB = 6.2 GB. Fits in 8 GB but tight. Consider OLLAMA_NUM_PARALLEL=1 to limit contention.

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ R_GOLDEN_RAGAS_768_20260829 ⬡ COMPLETE ⬡ 1316 lines ⬡ opencode ⬡ minimax/minimax-m3:free ⬡ PUBLIC-DEBUT-01*
