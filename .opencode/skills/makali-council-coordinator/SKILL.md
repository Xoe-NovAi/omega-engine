---
# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

name: "makali-council-coordinator"
description: "Unified MultiAgentCoordinator for MaKaLi Parallel Council — meditation mode (10-voice sequential) and council mode (parallel nodes → oversouls → synthesis). Handles paging, local discovery, web research grounding."
---

# 🔱 MaKaLi Council Coordinator Skill
# ⬡ OMEGA ⬡ KALI ⬡ trc_council ⬡ v1.1-GENERALIZED
#
# Unified MultiAgentCoordinator for MaKaLi Parallel Council.
# Handles both meditation mode (10-voice sequential) and council mode (parallel nodes → oversouls → Kali).
# Generalized for any sovereign topic with paging, local discovery, and web research grounding.

## Purpose
Orchestrate the 5-stage MaKaLi Parallel Council using `task()` tool, file-based handoffs, and Hivemind coordination. Zero-inference-cost Report Digestion Layer (Phase 1.5) optimizes node outputs for oversoul consumption. Mandatory research grounding via Sovereign Search Protocol (T0-T6) and pageable recursive specialists.

## Architecture (v2 — Entity Architecture Topology)
```
Session agent (kali) ──launches──▶ MAKALI (Council Orchestrator)
                                        │
            ┌───────────────────────────┼───────────────────────────┐
            ▼                           ▼                           ▼
    KALI (Synthesis Arm)         MA'AT (Build Arm)           LILITH (Run Arm)
    cross-side audit,            dispatches N1–N5            dispatches N6–N10
    dissent adjudication         (incl. N2 Persistence)      
    verdict DRAFT                
            │                           │                           │
            └──────────┬────────────────┴───────────┬───────────────┘
                       ▼                            ▼
                 [Digestion 1.5]              [Digestion 1.5]
                       └────────────┬───────────────┘
                                    ▼
                     Kali Arm synthesis ▶ MaKaLi fusion ▶ SOVEREIGN DECREE

Phase 0: Preconditions    → SSOT hydration + TASK_REGISTRY check + Hivemind init
Phase 1: Nodes            → 10 independent reports (serial per side, parallel across arms)
Phase 1.5: Digestion      → stack-cat + Python → 2 optimized digests (ZERO inference cost)
Phase 2: Arms             → Ma'at reads BUILD_SIDE_DIGESTED, Lilith reads RUN_SIDE_DIGESTED
Phase 3: Kali Synthesis   → reads both digests + arm reports → SYNTHESIS_ARM_REPORT.md
Phase 4: Research         → Sovereign Search (T0-T6) + pageable specialists + meditate pipeline
Phase 5: MaKaLi Fusion    → fuses all artifacts → SOVEREIGN_DECREE.md
Phase 6: Integration      → Quality gates + tracker updates + Hivemind verdict
```

## Usage
```bash
# Full council (cloud models)
/council-cloud "topic"

# Local-first council (local models for Nodes/Oversouls)
/council-local "topic"

# Fast local council (qwen3-1.7b all tiers)
/council-fast "topic"

# Meditation (10-voice sequential, single inference)
/meditate "topic"
```

## Inputs
- `topic`: The question/problem for the council
- `mode`: "council" (default, parallel) | "meditation" (sequential, 10-voice)
- `profile`: Hardware profile preset (local_16gb, local_8gb, cloud_unconstrained, hybrid_local_nodes)
- `config_path`: Path to custom council config (default: `config/council.yaml`)
- `session_id`: Unique identifier for this council run

## Stage 0: Preconditions
Before any dispatch, ALL agents MUST:
1. **Hydrate from SSOTs** (read in order):
   - `SOVEREIGN_MANDATES.md` v3.8.0 (27 Laws — M7, M11, M13, M15, M18, M23, M26, M27 critical)
   - `SOVEREIGN_ARK_BLUEPRINT.md` §4–§5 (Priority Stack + Immediate Next Steps)
   - `STRATEGY_CORPUS_MAP.md` (fine-grained preservation map)
   - `ACTIVE_SPRINT.json` (current workstreams + blockers)
   - `TASK_REGISTRY.json` (existing subagent sessions — check for resumable pageable work)
   - `GAP_REGISTRY.json` (open research gaps — R1-R99 immutable)
   - Your entity's `soul.yaml` + `proposed_lessons.yaml` (per M11)
   - `data/coordination/SESSION_ANCHOR.md` (session continuity anchor)
2. **Initialize Hivemind presence**:
   - `omega-hub_hivemind_post_context` with intent="command", task_current="MaKaLi council: $TOPIC"
   - `omega-hub_hivemind_workspace_lock_acquire` for domain="council-$TOPIC_SLUG"
   - Heartbeat every 5 min via `omega-hub_hivemind_heartbeat`
3. **Check for pageable recursive specialists**:
   - Query `TASK_REGISTRY.json` for existing sessions matching topic (tags: `["research", "pageable", "topic:$TOPIC_SLUG"]`)
   - If found: RESUME via `task_id` (preserves role memory + standing orders)
   - If not found: SPAWN new with `task()` and register in `TASK_REGISTRY.json`
4. Load config from `config/council.yaml` + profile override
5. Auto-detect hardware (RAM, CPU, thermal)
6. Select execution mode (parallel/batch/serial)
7. Initialize WAL checkpoint
8. Check circuit breaker state
9. Verify provider availability for assigned model tiers

## Phase 1: Node Dispatch
1. For each node in Ma'at's domain (N1 Infrastructure, **N2 Persistence**, N3 Engineering, N4 Integration, N5 Governance):
   - Dispatch `task()` with node agent, topic, output path
   - Nodes write independent reports — NO inter-node reads (M2 Firewall)
2. For each node in Lilith's domain (N6, N7, N8, N9, N10):
   - Dispatch `task()` with node agent, topic, output path
3. Execute according to mode:
   - `parallel`: All 10 nodes simultaneously (cloud profile)
   - `batch_4`: 4 at a time (16GB profile)
   - `batch_2`: 2 at a time (8GB profile)
   - `serial_independent`: One at a time (constrained) — **DEFAULT per Quake Thinker Chain**
4. Wait for ALL completions — verify report files exist
5. WAL checkpoint: Phase 1 complete

## Phase 1.5: Report Digestion
1. Run `ReportDigester` on node outputs:
   - stack-cat concatenation of all 4/5 reports per side
   - Executive summaries (auto-extracted via Python)
   - Cross-reference index (mandate tags, entities, shared keywords)
   - **Conflict detection** (numeric mismatches, mandate compliance differences)
   - Mandate compliance matrix ([M1]-[M27] per node)
   - Token budget allocation for oversoul context window
2. Python only — ZERO inference cost (~50ms for typical reports)
3. Write: `BUILD_SIDE_DIGESTED.md` + `RUN_SIDE_DIGESTED.md`
4. M23: If digestion fails, fall back to raw stack-cat concatenation
5. WAL checkpoint: Phase 1.5 complete

**Oversoul Input Improvement**: 
Before Phase 2, each oversoul reads 1 file (digested) instead of 4/5 raw reports.
- Token reduction: ~60%
- Added intelligence: cross-references, conflict map, mandate matrix, budget allocation

## Phase 2: Oversoul Distillation
1. Dispatch Ma'at task:
   - Read `BUILD_SIDE_DIGESTED.md` (1 file, optimized)
   - Apply Ma'at persona, lessons, KB (Build Side expertise)
   - Write `BUILD_SIDE_REPORT.md`
2. Dispatch Lilith task:
   - Read `RUN_SIDE_DIGESTED.md` (1 file, optimized)
   - Apply Lilith persona, lessons, KB (Run Side expertise)
   - Write `RUN_SIDE_REPORT.md`
3. Wait for BOTH completions
4. WAL checkpoint: Phase 2 complete

## Phase 3: Kali Final Synthesis
1. Dispatch Kali task:
   - Read `BUILD_SIDE_REPORT.md` + `RUN_SIDE_REPORT.md` (2 files only)
   - Apply Kali persona, lessons, and Oversight expertise
   - Write `FINAL_SYNTHESIS.md` with **mandatory sections**:
     - **Convergence** — What both sides agree on (actionable)
     - **Preserved Dissent** — Irreconcilable tensions (documented, not resolved)
     - **Irreducible Verdict** — Single sovereign decree
     - **REMAINING_GAPS_AND_RECOMMENDED_RESEARCH** — Structured for Stage 4
     - **MEASURABLE_GATES** — Every gate = bash command (`rg`, `pytest`, shell one-liner)
2. Wait for completion
3. Parse research gaps from synthesis output
4. WAL checkpoint: Phase 3 complete

## Phase 4: Research Execution (Mandatory — No Parametric Synthesis)
**For EACH gap in `REMAINING_GAPS_AND_RECOMMENDED_RESEARCH`:**

### 4.1 Sovereign Search Protocol (7-Tier)
```
T0: Local Cache (.firecrawl/, MemoryStore, library FTS5) → CHECK FIRST
T1: websearch (broad, recency, "2026" or "latest" in query)
T2: webfetch (deep extraction, structured content)
T3: SearXNG (semantic refinement, niche discovery)
T4: Parallel Search (MCP: high-quality LLM-optimized results)
T5: Exa (high-precision seeds, academic/technical)
T6: Firecrawl (full-page scrape, cache to T0 on success)
```

**Credit-Sensing Guard**: Before T5/T6 → check Firecrawl credits. <100 = AUTO-DOWNGRADE to T1/T2/T4.

**Error Handling Matrix**: 401/402/429/500/Timeout/Connection Refused → immediate fallback + Hivemind log.

### 4.2 Local Discovery First (Omega Hub)
- `omega-hub_library_discovery_research` (tiered external discovery)
- `omega-hub_library_fts_search` (local FTS5 — BM25, no vector overhead)
- `omega-hub_library_search` (local semantic search)
- `omega-hub_library_web_search` (SearXNG → Exa → Firecrawl pipeline)

### 4.3 Paging Protocol for Deep Research
- Spawn **pageable recursive specialist sessions** via `task()` with standing orders
- Register in `TASK_REGISTRY.json` with tags: `["research", "pageable", "topic:$TOPIC_SLUG"]`
- Specialists persist across compactions via `task_id` resumption
- Each specialist owns a partition/domain; findings feed back to council
- Reference: `data/entities/roc_racoon/workspace/RECURSIVE_SPECIALIST_ROSTER.md`

### 4.4 Meditate-Research Pipeline (for Architectural Questions)
- Stage 1: `/meditate` (10-voice sequential dialectic)
- Stage 2: Synthesize → architecture diagram + non-negotiables
- Stage 3: Sovereign Search (grounded in 2026 sources)
- Stage 4: Verity L1→L2→L3 → `proposed_lessons.yaml`
- Stage 5: Ma'at integrates → roadmap, PIVOT_LOG, Temple-Grade gates

## Phase 5: Integration & Verdict Delivery
1. Append research results to `FINAL_SYNTHESIS.md`
2. Run quality gates:
   - `make temple-grade` (T1-T11)
   - `make heritage-map` (all `[id-soft:]` tags vetted)
   - `make sovereignty` (local-first ratio ≥ 80%)
   - `make test` (1398+ tests pass)
   - `scripts/validate_tracking_state.py` (tracking integrity)
3. Update trackers:
   - `ACTIVE_SPRINT.json` — workstream status, decisions_locked
   - `TASK_REGISTRY.json` — session completions
   - `GAP_REGISTRY.json` — gap resolutions
   - `PIVOT_LOG.md` — D-series decisions
4. Release workspace lock: `omega-hub_hivemind_workspace_lock_release`
5. Final Hivemind post: intent="decision" with verdict summary

## Output Structure
```
data/council/{session_id}/
├── phase1_nodes/
│   ├── P1_report.md ... P10_report.md
├── phase1.5_digested/
│   ├── BUILD_SIDE_DIGESTED.md
│   └── RUN_SIDE_DIGESTED.md
├── phase2_oversouls/
│   ├── BUILD_SIDE_REPORT.md
│   └── RUN_SIDE_REPORT.md
├── phase3_kali/
│   └── FINAL_SYNTHESIS.md
├── phase4_research/
│   ├── research_gaps.md
│   ├── research_results/
│   └── pageable_specialists/  (task_id registry per specialist)
└── phase5_integration/
    ├── verdict.md
    └── tracker_updates.json
```

## Resilience
- **WAL**: Write-Ahead Log for crash recovery (atomic .tmp → .json writes)
- **Circuit Breaker**: Opens at >30% error rate over 10 minutes
- **Fallback Chain**: digestion fails → raw concat; local model fails → cloud; abort on M2/M7 violation
- **Jitter Retry**: Exponential backoff with random jitter (base: 1s, max: 30s)
- **Hivemind Integration**: Auto-capture stage outputs, semantic search across runs

## Mandate Compliance
- **M1 AnyIO**: All async operations use AnyIO, not asyncio
- **M2 Firewall**: No node reads another node's report at write time
- **M7 Local-First**: Tries local model tiers before cloud; cloud = safety net
- **M11 Soul Integrity**: Agents hydrate from soul.yaml + proposed_lessons.yaml
- **M13 Temple-Grade**: Each stage produces typed, verifiable outputs
- **M15 Continuity**: Session anchor + pageable specialists survive compaction
- **M18 Token Efficiency**: Digestion layer (Phase 1.5) reduces oversoul tokens by ~60%
- **M22 Provenance**: Every response logs actual `provider_name` (not configured intent)
- **M23 Failure Integrity**: Tool failure → `[TOOL-CHAIN-COLLAPSE]` logged, hard stop
- **M26 Doc Standards**: All reference docs pass `make doc-llm-validate`
- **M27 Tracking Integrity**: 5-Tier Tracking Architecture enforced

## Related Files
- `config/council.yaml` — Main config
- `config/council/profiles/*.yaml` — Hardware profiles
- `src/omega/council/coordinator.py` — MultiAgentCoordinator implementation
- `src/omega/council/report_digestion.py` — ReportDigester (Phase 1.5)
- `src/omega/council/models.py` — Data models
- `src/omega/council/failure_layer.py` — Circuit breaker, WAL, retry
- `docs/strategy/MAKALI_PARALLEL_COUNCIL_ARCHITECTURE.md` — Full architecture specification
- `docs/research/R_REPORT_DIGESTION_LAYER_OPTIMIZATION_20260719.md` — Digestion layer research
- `.opencode/skills/sovereign-search/SKILL.md` — 7-tier search protocol
- `.opencode/skills/meditate-research-pipeline/SKILL.md` — 5-stage pipeline
- `data/entities/roc_racoon/workspace/RECURSIVE_SPECIALIST_ROSTER.md` — Paging protocol

---

*⬡ OMEGA ⬡ KALI ⬡ MAKALI-COUNCIL-COORDINATOR v1.1 ⬡ 2026-08-25*