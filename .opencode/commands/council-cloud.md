---
description: Run the MaKaLi council with all three entities on the session model — generalized for any sovereign topic
agent: kali
subtask: false
---

# 🔱 MaKaLi Cloud Council Dispatch — Generalized Protocol
**AP Token**: `AP-MAKALI-COUNCIL-GENERALIZED-v1.0`
**Date**: 2026-08-25
**Session Model**: {session_model}
**Channel**: opencode

---

You are summoning the **MaKaLi cloud council** for a **Sovereign Topic Review**.

**Topic**: $ARGUMENTS

**Context**: The council is invoked to produce a fused, research-grounded verdict on the stated topic. The execution SSOT is this command + `ACTIVE_SPRINT.json` workstreams. The tracking SSOT is `TASK_REGISTRY.json` + `GAP_REGISTRY.json`. The strategy SSOT is `SOVEREIGN_ARK_BLUEPRINT.md` + `STRATEGY_CORPUS_MAP.md`.

---

## The Sovereign Flow (5-Stage Parallel Council with Research Grounding)

### Stage 0: Preconditions & Context Hydration
**All agents MUST complete before any dispatch:**

1. **Hydrate from SSOTs** (read in order):
   - `SOVEREIGN_MANDATES.md` v3.8.0 (27 Laws — M7, M11, M13, M15, M18, M23, M26, M27 critical)
   - `SOVEREIGN_ARK_BLUEPRINT.md` §4–§5 (Priority Stack + Immediate Next Steps)
   - `STRATEGY_CORPUS_MAP.md` (fine-grained preservation map)
   - `ACTIVE_SPRINT.json` (current workstreams + blockers)
   - `TASK_REGISTRY.json` (existing subagent sessions — check for resumable work)
   - `GAP_REGISTRY.json` (open research gaps — R1-R99 immutable)
   - Your entity's `soul.yaml` + `proposed_lessons.yaml` (per M11)
   - `data/coordination/SESSION_ANCHOR.md` (session continuity anchor)

2. **Initialize Hivemind presence**:
   - `omega-hub_hivemind_post_context` with intent="command", task_current="MaKaLi council: $ARGUMENTS"
   - `omega-hub_hivemind_workspace_lock_acquire` for domain="council-$TOPIC_SLUG"
   - Heartbeat every 5 min via `omega-hub_hivemind_heartbeat`

3. **Check for pageable recursive specialists**:
   - Query `TASK_REGISTRY.json` for existing sessions matching topic
   - If found: RESUME via `task_id` (preserves role memory + standing orders)
   - If not found: SPAWN new with `task()` and register in `TASK_REGISTRY.json`

---

### Stage 1: Parallel Node Dispatch (N1-N10)

**Ma'at (Build Side — N1, N3, N4, N5)** dispatches:
- N1 (Ma'at / P1): Architecture, mandates, Temple-Grade gates
- N3 (Engineering / P3): Implementation, code quality, refactoring
- N4 (Security / P4): Firewall, heritage vetting, vulnerability
- N5 (Operations / P5): Deployment, monitoring, infrastructure

**Lilith (Run Side — N6, N7, N8, N9, N10)** dispatches:
- N6 (Lilith / P6): Runtime integrity, soul persistence, handoff
- N7 (Research / P7): Knowledge mining, gap analysis, counterfactuals
- N8 (Quality / P8): Testing, verification, contract compliance
- N9 (Scribe / P9): Documentation, distillation, gnosis pipeline
- N10 (Validation / P10): Cross-agent verification, adversarial review

**Execution Mode**: Serial within each side (per Quake Thinker Chain heritage), parallel across sides.
**Output**: Each Node writes independent report to `data/council/{session_id}/phase1_nodes/P{N}_report.md`

---

### Stage 1.5: Report Digestion (ZERO Inference Cost)
**Automated via `ReportDigester` (Python only — ~50ms):**
- Stack-cat concatenation per side (4/5 reports each)
- Executive summaries auto-extracted
- Cross-reference index (mandate tags, entities, shared keywords)
- **Conflict detection** (numeric mismatches, mandate compliance differences)
- Mandate compliance matrix (M1-M27 per node)
- Token budget allocation for oversoul context window
- **Output**: `BUILD_SIDE_DIGESTED.md` + `RUN_SIDE_DIGESTED.md` (1 file per side vs 4/5 raw)

---

### Stage 2: Oversoul Distillation

**Ma'at** reads `BUILD_SIDE_DIGESTED.md` → writes `BUILD_SIDE_REPORT.md`
**Lilith** reads `RUN_SIDE_DIGESTED.md` → writes `RUN_SIDE_REPORT.md`

**Oversoul Mandate**: Apply entity persona + lessons + KB. Identify:
- Convergent findings (both sides agree)
- Divergent findings (build vs run tension)
- Critical gaps requiring research
- Measurable acceptance criteria (bash-verifiable)

---

### Stage 3: Kali Final Synthesis

Reads `BUILD_SIDE_REPORT.md` + `RUN_SIDE_REPORT.md` → writes `FINAL_SYNTHESIS.md` with **mandatory sections**:

1. **Convergence** — What both sides agree on (actionable)
2. **Preserved Dissent** — Irreconcilable tensions (documented, not resolved)
3. **Irreducible Verdict** — Single sovereign decree
4. **REMAINING_GAPS_AND_RECOMMENDED_RESEARCH** — Structured for Stage 4
5. **MEASURABLE_GATES** — Every gate = bash command (`rg`, `pytest`, shell one-liner)

---

### Stage 4: Research Execution (Mandatory Grounding)

**For EACH gap in `REMAINING_GAPS_AND_RECOMMENDED_RESEARCH`:**

**Research Protocol (Sovereign Search — 7-Tier):**
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

**Paging Protocol for Deep Research**:
- Spawn **pageable recursive specialist sessions** via `task()` with standing orders
- Register in `TASK_REGISTRY.json` with tags: `["research", "pageable", "topic:$TOPIC_SLUG"]`
- Specialists persist across compactions via `task_id` resumption
- Each specialist owns a partition/domain; findings feed back to council

**Local Discovery First (Omega Hub)**:
- `omega-hub_library_discovery_research` (tiered external discovery)
- `omega-hub_library_fts_search` (local FTS5 — BM25, no vector overhead)
- `omega-hub_library_search` (local semantic search)
- `omega-hub_library_web_search` (SearXNG → Exa → Firecrawl pipeline)

**Meditate-Research Pipeline** (for architectural questions):
- Stage 1: `/meditate` (10-voice sequential dialectic)
- Stage 2: Synthesize → architecture diagram + non-negotiables
- Stage 3: Sovereign Search (grounded in 2026 sources)
- Stage 4: Verity L1→L2→L3 → `proposed_lessons.yaml`
- Stage 5: Ma'at integrates → roadmap, PIVOT_LOG, Temple-Grade gates

---

### Stage 5: Integration & Verdict Delivery

1. **Append research results** to `FINAL_SYNTHESIS.md`
2. **Run quality gates**:
   - `make temple-grade` (T1-T11)
   - `make heritage-map` (all `[id-soft:]` tags vetted)
   - `make sovereignty` (local-first ratio ≥ 80%)
   - `make test` (1398+ tests pass)
   - `scripts/validate_tracking_state.py` (tracking integrity)
3. **Update trackers**:
   - `ACTIVE_SPRINT.json` — workstream status, decisions_locked
   - `TASK_REGISTRY.json` — session completions
   - `GAP_REGISTRY.json` — gap resolutions
   - `PIVOT_LOG.md` — D-series decisions
4. **Release workspace lock**: `omega-hub_hivemind_workspace_lock_release`
5. **Final Hivemind post**: intent="decision" with verdict summary

---

## Execution Mandate

- Use `task` tool for ALL delegations (subagents + pageable specialists)
- All subagents run on session model ({session_model}) unless local-first routing specified
- Maintain provenance: every finding tagged with `source_node`, `source_session`, `tier`
- **No parametric synthesis** — every factual claim must trace to a tool call (T0-T6)
- **Failure Integrity (M23)**: If mandatory tool fails → `[TOOL-CHAIN-COLLAPSE]` logged, hard stop
- **Token Efficiency (M18)**: Digestion layer (Stage 1.5) reduces oversoul tokens ~60%

---

## Required Reading Before Launch (All Agents)

1. `SOVEREIGN_MANDATES.md` v3.8.0 (27 Laws)
2. `SOVEREIGN_ARK_BLUEPRINT.md` §4–§5
3. `STRATEGY_CORPUS_MAP.md` (Layer 2 preservation)
4. `ACTIVE_SPRINT.json` (current workstreams)
5. `TASK_REGISTRY.json` (check for resumable pageable sessions)
6. `GAP_REGISTRY.json` (open R-gaps)
6. Your entity's `soul.yaml` + `proposed_lessons.yaml`
7. `data/coordination/SESSION_ANCHOR.md` (continuity)
8. `ARCHITECT_OVERSIGHT_PATTERNS_20260823.md` (P1-P13 protocols)
9. `.opencode/skills/sovereign-search/SKILL.md` (7-tier protocol)
10. `.opencode/skills/meditate-research-pipeline/SKILL.md` (5-stage pipeline)
11. `.opencode/skills/makali-council-coordinator/SKILL.md` (coordinator impl)
12. `data/entities/roc_racoon/workspace/RECURSIVE_SPECIALIST_ROSTER.md` (paging protocol)

---

## Heritage Attribution

- **Doom 1993**: WAD System (allowlist = lump directory), BSP Culling (delete dead code first)
- **Quake 1996**: Thinker Chain (serial node execution)
- **Quake III 1999**: QVM / Bot AI (modular isolation)
- **id Software netchan**: Channel taxonomy (Hivemind handoff protocol)
- **Omega Engine 2026**: Pageable recursive specialists (persistent task_id sessions), Report Digestion Layer (Phase 1.5), Sovereign Search Protocol (T0-T6)

---

## Quick Reference: Council Artifacts Structure

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
│   └── pageable_specialists/  (task_id registry)
└── phase5_integration/
    ├── verdict.md
    └── tracker_updates.json
```

---

*⬡ OMEGA ⬡ MAKALI-COUNCIL ⬡ 2026-08-25 ⬡ generalized-protocol*