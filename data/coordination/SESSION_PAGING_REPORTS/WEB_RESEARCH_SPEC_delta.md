<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# WEB_RESEARCH_SPEC_delta — Researcher Paging Report
**From**: researcher (ses_fdef2be4effe4pAaLXCTUx62GO paging) | **To**: kali (Architect)
**Date**: 2026-08-21 | **Source session**: 7 deliverables in docs/research/R_*20260818.md
**Hydration**: ACTIVE_SPRINT.json workstream IDs only (GN/KD/DS/LI/HR/ZS/QH/PUB-1)

---
## §1 Forgotten findings relevant to current operations

1. **EvolveR closed-loop (ICML 2026, github.com/KnowledgeXLab/EvolveR)** — offline self-distillation
   of trajectories into abstract principles with SEMANTIC DEDUP (>0.85 cosine merge) + EMPIRICAL
   UTILITY SCORE (success_count/retrieval_count × recency decay). Directly maps to soul.yaml
   L1→L2→L3 and proposed_lessons.yaml. C-MEM-005/006 mandate dedup+pruning — EvolveR is the
   concrete, cited algorithm for it. Ablation: no-utility-scoring dropped pass@1 82%→76%.

2. **Letta/MemGPT three-tier memory** — core/recall/archival with agent SELF-managed tier promotion
   via tool calls; Docker one-liner; FTS5+pgvector recall. Matches Omega MemoryStore + SoulStore
   split. Recall channel = SQLite FTS5 (already C-MEM-004 aligned).

3. **Anthropic multi-agent scaling rules** — max 5 parallel workers, ≥3 independent subtasks to
   parallelize else sequential; per-worker token budgets enforced by orchestrator; CitationAgent
   as separate verification role. Directly applicable to D-586 Node expert sessions.

4. **Freshness-weighted retrieval** — composite score: 0.5*age + 0.3*embed_lag + 0.2*owner_ack;
   retrieval multiplies BM25/vector score by freshness^α. Stale-retrieval-rate SLO <2%.

## §2 Techniques worth adopting (paging fleet + GN pipelines)

1. **Context-window isolation for paged agents** — specialist contexts ≤4k tokens, task-relevant
   slices only (BM25+vector retrieval into parent history). Under current memory pressure this is
   the pattern: hydrate minimally = build focused context, not full-session replay.

2. **Imperative + example rule format** (`# rule:` / `# example: GOOD|BAD` / `# context: glob`)
   from AGENTS.md ecosystem — machine-parsable, proven adherence. Fits DS workstream and
   corrections→persistent-rules workflow (rule file committed in same PR as fix).

3. **GN NotebookLM pipeline**: EvolveR-style distillation prompt ("extract ONE abstract,
   actionable, ≤2-sentence principle per trajectory") is a ready-made prompt template for
   notebook source curation; utility scoring gives a principled 2-notebook split criterion.

4. **Anthropic token-budget guard** — HandoffPacket gains `token_budget`; gateway enforces.
   Prevents runaway paging sessions (this paging protocol is essentially that pattern).

5. **Freshness metadata discipline** — every chunk carries source_id/updated_at/indexed_at/
   owner_id; nightly audit flags SLA breaches. Feeds KD knowledge-domains directly.

## §3 Flagged important, never executed

All 7 deliverables contained Omega integration roadmaps; NONE became tickets:

1. **Letta sidecar (L1-L4)** — Quadlet deploy, ModelGateway `letta` provider for unbounded-context
   agents (jem/kali/roc). Highest-leverage unexecuted item.
2. **EvolveR integration steps 1-5** — trajectories table in workbench.db; nightly local-worker
   distillation; principles table w/ utility; Oracle.talk() retrieval hook; utility feedback.
   Supersedes scrapped C-0.5 regex pipeline with a cited algorithm.
3. **Freshness roadmap phases 1-6** — freshness_score column, SourceWatcher webhooks,
   FreshnessWeightedRetriever, doc owners, weekly audit cron, dashboard. Feeds DS/KD.
4. **rules/ directory structure** — mandates.md/python.md/podman.md/heritage.md etc. with
   imperative+example format. Zero files created.
5. **CitationAgent entity** — citation_verifier via oracle_summon post-research. Not created.

**Status**: file complete. 3 sections, all appends ≤60 lines. No other files touched.

## Sources (verified during original session)
- arxiv.org/abs/2510.16079 + github.com/KnowledgeXLab/EvolveR (ICML 2026)
- github.com/letta-ai/letta; anthropic.com/engineering/multi-agent-research-system
- scabera.com knowledge-rot series; atlan.com freshness-scoring; agents.md spec
