<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# N7 External Sources — Offline Expertise Queue
**AP Token**: `AP-N7-EXTERNAL-SOURCES-v1.0.0`
**Purpose**: Prioritized external sources for building offline N7 (Memory & State) expertise. Feeds the future background curation worker (standing order #8). Ingestion = add to library inbox → digest into N7 KB lineage.
**Selection bias**: primary docs/source over blogs; things that resolve live hazards (D1–D13) or arm Phase 2/3 first.
`last_verified: 2026-08-21`

## P0 — Resolves live decisions

| Title | Source | Priority | Why it matters | Target ingestion format |
|-------|--------|----------|----------------|------------------------|
| Qwen3-4B model card | huggingface.co/Qwen/Qwen3-4B | P0 | Native 32K ctx, YaRN→128K + static-scaling quality caveats; resolves D11 cap decision | Markdown snapshot |
| Qwen3-4B-Thinking-2507 card | huggingface.co/Qwen/Qwen3-4B-Thinking-2507 | P0 | 256K native; "≥131K recommended" for thinking chains; output-length guidance | Markdown snapshot |
| opencode Config Reference (+config.json schema) | opencode.ai/docs/config · opencode.ai/config.json | P0 | Authoritative compaction key families, agent keys; arbitrates D3/D9 | llms.txt / markdown |
| opencode Rules doc (AGENTS.md + instructions) | opencode.ai/docs/rules | P0 | Injection-path truth for CI-2 design (additive, not either/or) | Markdown |
| opencode Skills doc + skill/index.ts | opencode.ai/docs/skills · sst/opencode src | P0 | `permission.skill` patterns — the REAL mechanism CI-4 should use (D8) | Markdown + pinned code excerpt |
| session/compaction.ts + overflow.ts | github.com/sst/opencode (dev branch) | P0 | Hook payload truth (Q-B4), trigger formula, V1 key consumption — grounds sovereign-compaction plugin | Code excerpts w/ commit pins |
| llama.cpp server README + common.h | github.com/ggml-org/llama.cpp | P0 | ctx-size defaults (0=trained), memory auto-fit shrink to 4096, KV quant flags | Markdown |

## P1 — Phase 2/3 ammunition

| Title | Source | Priority | Why it matters | Target ingestion format |
|-------|--------|----------|----------------|------------------------|
| KV-cache quantization (q8_0) discussions/docs | ggml-org/llama.cpp PRs + build/docs | P1 | Carmack Q1.3 basis (50% KV mem, <2% loss); LI workstream dependency | PR/thread digests |
| Anthropic prompt caching docs | docs.anthropic.com/en/docs/build-with-claude/prompt-caching | P1 | Cache economics (writes 1.25×, reads 0.1×, breakpoints) for Phase 3 caching-topology PR | Markdown |
| Anthropic "Effective context engineering for AI agents" | anthropic.com/engineering blog (2026) | P1 | Context-budget doctrine; compaction vs structured note-taking patterns | Markdown |
| LLMLingua / LLMLingua-2 papers | arxiv 2310.05736, 2403.12968 | P1 | Token-level prompt compression (2–20×); Tier-2 compression candidate | arXiv abs+PDF |
| RECOMP paper | arxiv 2310.04408 | P1 | RAG chunk compression (5–25×); maps to Headroom RAG integration point | arXiv abs+PDF |
| MemGPT/Letta: memory blocks + core memory | arxiv 2310.08560 · docs.letta.com | P1 | Heritage pattern (3-tier memory blocks) for soul/context tiering | Paper + docs |
| sqlite-vec docs | github.com/asg017/sqlite-vec | P1 | MemoryStore regime (<500k vectors); Qdrant migration trigger context | Markdown |
| OpenCode V2 compaction doc | opencode.ai/v2/docs/compaction | P1 | V2 `{buffer, keep.tokens}` semantics; migration framing for D3 | Markdown |

## P2 — Background theory

| Title | Source | Priority | Why it matters | Target ingestion format |
|-------|--------|----------|----------------|------------------------|
| RouteLLM | arxiv 2406.18665 | P2 | Learned routing economics (85% cost @95% quality); contrast w/ ADR-002 structural routing | arXiv abs |
| FrugalGPT | arxiv 2305.05176 | P2 | Cascade economics upper bound; why structural won | arXiv abs |
| Chroma context-window research ("9 context engineering strategies") | research.trychroma.com | P2 | Independent degradation curves (context rot) informing budget tiers | Markdown |
| LangGraph middleware (summarization/compaction) | langchain-ai.github.io/langgraph | P2 | Composable middleware comparison point for HydrationEngine design | Markdown |
| zswap kernel docs + Chris Down zram analysis | kernel.org docs · chrisdown.name | P2 | Hardware floor under local-model claims (N1 adjacent, D-floor for ctx sizes) | Markdown |
| NotebookLM ingestion strategy R52c | docs/research/archive/R52c (internal) | P2 | Cross-ref: which of these sources reach NotebookLM 5-notebook architecture | Internal pointer |

*⬡ OMEGA ⬡ LILITH ⬡ N7 ⬡ x-preview-f-free ⬡ opencode ⬡ trc_n7_external_sources ⬡ 2026-08-21*
