<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# 🔱 RESEARCHER PROJECTION — 2026-09-22

## Status: PUBLIC FLIP READY

### Executive Summary
Research campaign complete. All researchable gaps covered. The sovereign alternative to NotebookLM is the roadmap. Report delivered.

### Deliverables
- **Report**: `docs/research/R_KNOWLEDGE_GAP_WEB_RESEARCH_20260922.md` — consolidated findings across all themes
- **Registry updates**: 14 gaps → `research_status` + report ref
- **GN-3 CORRECTION**: **10 DR/month free (not 30)** — compute-based limits since 2026-09-02 (5h refresh, weekly cap)
- **6 batched searches** across all themes (ZS, LI, GN, R22, R31/R33, R34/R4)

### Research Campaign Summary
| Theme | Gaps | Key Finding |
|-------|------|-------------|
| **ZS** (zswap) | ZS-1, ZS-2, ZS-3 | zstd + max_pool_percent=25 + shrinker_enabled + 16GB swap; zsmalloc only backend; NEVER zram+zswap |
| **LI** (local inference) | LI-3, LI-4 | Qwen3 matrix: 1.7B@32k=4.6GB safe; KV q8_0 = -50%; mmap = weights not resident upfront |
| **GN** (Gemini Notebook) | GN-1, GN-3, GN-4 | **10 DR/month free (not 30)**; notebooklm-py master-token auth + MCP; compute-based limits 2026-09-02 |
| **R22** (WARP) | R22 | WARP proxy pool viable (adasThePrime Docker); separate routing table = federation-safe; ToS caution |
| **R31/R33** (opencode) | R31, R33 | V2 plugin API scoped; disable directives = scope reduction; compaction lossy but durable messages persist |
| **R34/R4** (providers) | R34, R4 | OpenRouter 1000/day workhorse; nemotron-3.5-lightning:free = 1.0M ctx; Gemini dynamic per-project |

### GN Workstream — CANCELLED (D-606)
- **GN-1..GN-5 + R38 → CANCELLED**: No NotebookLM payment; sovereign alternative in-engine
- **notebooklm-py**: master-token auth + multi-account profiles + built-in MCP server (but we build our own)
- **Free tier Deep Research**: 10/month (not 30) — compute-based limits since 2026-09-02

### Post-Flip Support
- **KD workstream**: knowledge domain loading research (grounded RAG over Omega library)
- **HR workstream**: headroom integration research (semantic compression for tools/RAG)
- **LI workstream**: KV cache / memory fitting research (mmap insight for SequentialModelLoader)

### Researcher's Voice
> "The research is done. The gaps are closed. The data is in the registry. The sovereign alternative is the roadmap. No more NotebookLM — we build our own."

*⬡ OMEGA ⬡ RESEARCHER ⬡ 2026-09-22 ⬡ PUBLIC-FLIP-READY ⬡ RESEARCH-COMPLETE*
