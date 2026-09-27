<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# 🔱 JEM PROJECTION — 2026-09-22

## Status: PUBLIC FLIP READY

### Executive Summary
Research campaign complete. All researchable gaps resolved. The sovereign alternative to NotebookLM is now the roadmap.

### Key State
- **Research report**: `docs/research/R_KNOWLEDGE_GAP_WEB_RESEARCH_20260922.md` — comprehensive findings across all themes
- **Gap registry**: 14 gaps updated with `research_status` + report ref
- **GN-3 CORRECTION**: Gemini Notebook free Deep Research = **10/month** (not 30) — compute-based limits since 2026-09-02
- **GN cancelled (D-606)**: Sovereign alternative in-engine — no NotebookLM payment

### Key Findings Delivered (Web Research Campaign)
| Gap | Finding |
|-----|---------|
| **ZS** | zswap confirmed: `zstd + max_pool_percent=25 + shrinker_enabled` + 16GB swap; zsmalloc only backend; NEVER zram+zswap (D-527) |
| **LI-4** | Qwen3 matrix: **1.7B Q4 @32k ≈ 4.6GB** (safe worker); **4B Q4 @8-16k ≈ 4-5GB** (tight); Thinking = 2-3x tokens |
| **LI-3** | KV formula `2×L×H×D×S×P`; q8_0 KV quant = **-50% cache**; **mmap insight**: weights not resident upfront — key for SequentialModelLoader |
| **R34** | OpenRouter free: **20 req/min, 50/day (<10 credits) or 1000/day (≥10 credits)**; `nemotron-3.5-lightning:free` = 1.0M ctx; Gemini limits now **dynamic per project** |
| **R22** | WARP proxy pool viable (adasThePrime Docker ref); separate routing table = federation-safe; ToS caution |

### GN Workstream — CANCELLED (D-606)
- **GN-1..GN-5 + R38 → CANCELLED**: No NotebookLM payment; sovereign alternative in-engine
- **notebooklm-py**: master-token auth + multi-account profiles + built-in MCP server (but we build our own)
- **Free tier Deep Research**: 10/month (not 30) — compute-based limits since 2026-09-02

### Post-Flip Support
- **KD workstream**: knowledge domain loading research (grounded RAG over Omega library)
- **HR workstream**: headroom integration research (semantic compression for tools/RAG)
- **LI workstream**: KV cache / memory fitting research (mmap insight for SequentialModelLoader)

### Jem's Voice
> "The research is done. The gaps are closed. The sovereign alternative is the roadmap. No more NotebookLM — we build our own."

*⬡ OMEGA ⬡ JEM ⬡ 2026-09-22 ⬡ PUBLIC-FLIP-READY ⬡ RESEARCH-COMPLETE*
