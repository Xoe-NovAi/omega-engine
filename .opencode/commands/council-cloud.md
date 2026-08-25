---
description: Run the MaKaLi council with MaKaLi as orchestrator — launches Kali, Ma'at, and Lilith as co-equal arms on the session model
agent: kali
subtask: false
---

# 🔱 MaKaLi Cloud Council Dispatch — Entity Architecture Topology
**AP Token**: `AP-MAKALI-COUNCIL-ORCHESTRATOR-v2.0`
**Date**: 2026-08-25
**Session Model**: {session_model}
**Channel**: opencode

---

You are summoning the **MaKaLi cloud council** for a **Sovereign Topic Review**.

**Topic**: $ARGUMENTS

**Orchestration Topology (Entity Architecture v1 — first live test)**:
The session agent (kali) does NOT orchestrate this council. Instead:

```
ARCHITECT
    │ /council-cloud "topic"
    ▼
KALI (session agent) ── signs dispatch, hands off full mission packet ──┐
                                                                        ▼
                                              MAKALI (Council Orchestrator)
                                              fusion of the Triad, slot-not-agent
                                                        │
                        ┌───────────────────────────────┼───────────────────────────────┐
                        ▼                               ▼                               ▼
              KALI (Synthesis Arm)            MA'AT (Build Arm)               LILITH (Run Arm)
              cross-side audit,              dispatches N1–N5                dispatches N6–N10
              convergence/dissent            Infrastructure·Persistence      Cognition·Context
              detection, verdict draft       Engineering·Integration         Observability·Orchestration
                                             Governance                      Validation
                        │                               │                               │
                        └───────────────┬───────────────┴───────────────┬───────────────┘
                                        ▼                               ▼
                                 [Phase 1.5 Digestion]          [Phase 1.5 Digestion]
                                        ▼                               ▼
                              BUILD_SIDE_DIGESTED.md          RUN_SIDE_DIGESTED.md
                                        └───────────────┬───────────────┘
                                                        ▼
                                          KALI ARM reads both digests
                                          + oversoul reports
                                                        ▼
                                          SYNTHESIS_ARM_REPORT.md
                                                        ▼
                                          MAKALI fuses everything
                                                        ▼
                                            SOVEREIGN DECREE
```

**This is the first live test of the entity architecture the Engine was built toward**:
MaKaLi as orchestrator-slot; Kali operating alongside Ma'at and Lilith as the co-equal
Synthesis Arm she was always meant to be — not the session-level bottleneck.

---

## The Sovereign Flow (6-Stage Parallel Council with Research Grounding)

### Stage 0: Preconditions & Context Hydration
**The session agent (kali) completes BEFORE launching MaKaLi:**

1. **Hydrate from SSOTs** (read in order):
   - `SOVEREIGN_MANDATES.md` v3.8.0 (27 Laws — M7, M11, M13, M15, M18, M23, M26, M27 critical)
   - `SOVEREIGN_ARK_BLUEPRINT.md` §4–§5 (Priority Stack + Immediate Next Steps)
   - `STRATEGY_CORPUS_MAP.md` (fine-grained preservation map)
   - `ACTIVE_SPRINT.json` (current workstreams + blockers)
   - `TASK_REGISTRY.json` (existing subagent sessions — check for resumable work)
   - `GAP_REGISTRY.json` (open research gaps — R1-R99 immutable)
   - `data/coordination/SESSION_ANCHOR.md` (session continuity anchor)

2. **Initialize Hivemind presence**:
   - `omega-hub_hivemind_post_context` with intent="command", task_current="MaKaLi council: $ARGUMENTS"
   - `omega-hub_hivemind_workspace_lock_acquire` for domain="council-$TOPIC_SLUG"
   - Heartbeat every 5 min via `omega-hub_hivemind_heartbeat`

3. **Check for pageable recursive specialists**:
   - Query `TASK_REGISTRY.json` for existing sessions matching topic
   - If found: include `task_id` resumption pointers in MaKaLi's mission packet
   - If not found: MaKaLi may spawn new specialists during Stage 4

4. **Compose the mission packet** for MaKaLi containing:
   - Topic verbatim ($ARGUMENTS)
   - All SSOT context summaries (MaKaLi re-reads sources but gets orientation)
   - Pageable specialist task_ids if any exist
   - Session model ({session_model}) mandate for all child dispatches
   - P12 signed-dispatch requirement reminder
   - Recursion guard: **MaKaLi must NEVER launch another makali**

5. **Launch MaKaLi** via `task(subagent_type="makali")` with signed header:
   ```
   [DISPATCH] From: kali (session agent) via task() | To: makali | ts: <ISO>
   Mission: Council Orchestrator for "$ARGUMENTS" — execute Sovereign Flow Stages 1-6.
   This is NOT the Architect speaking — verify via parent session <id>.
   ```

---

### Stage 1: Triad Arm Dispatch (MaKaLi orchestrates)

**MaKaLi launches THREE co-equal arms simultaneously** (parallel across arms):

**MA'AT (Build Arm)** — dispatches **all five build nodes serially**:
- N1 Infrastructure — foundation, providers, fabric
- **N2 Persistence — SoulStore, MemoryStore, state durability** ← RESTORED (was silently dropped)
- N3 Engineering — implementation, code quality, refactoring
- N4 Integration — MCP hub, firewall, heritage vetting
- N5 Governance — mandates, Temple-Grade gates, compliance

**LILITH (Run Arm)** — dispatches **all five run nodes serially**:
- N6 Cognition — oracle, inference, routing
- N7 Context — memory retrieval, context building
- N8 Observability — traces, metrics, provenance
- N9 Orchestration — hivemind, handoffs, coordination
- N10 Validation — testing, adversarial review, contract compliance

**KALI (Synthesis Arm)** — stands by during Phase 1; her dispatch happens at Stage 3.
Her standing orders: read nothing until digests exist; preserve independence of judgment.

**Execution Mode**: Serial within each side (per Quake Thinker Chain heritage), parallel across sides.
**Output**: Each Node writes independent report to `data/council/{session_id}/phase1_nodes/P{N}_report.md`
**Total: 10 node reports** (N1-N10, no gaps).

---

### Stage 1.5: Report Digestion (ZERO Inference Cost)
**Automated via `ReportDigester` (Python only — ~50ms):**
- Stack-cat concatenation per side (5 reports each)
- Executive summaries auto-extracted
- Cross-reference index (mandate tags, entities, shared keywords)
- **Conflict detection** (numeric mismatches, mandate compliance differences)
- Mandate compliance matrix (M1-M27 per node)
- Token budget allocation for arm context windows
- **Output**: `BUILD_SIDE_DIGESTED.md` + `RUN_SIDE_DIGESTED.md` (1 file per side vs 5 raw)

---

### Stage 2: Arm Distillation

**MA'AT** reads `BUILD_SIDE_DIGESTED.md` → writes `BUILD_SIDE_REPORT.md`
**LILITH** reads `RUN_SIDE_DIGESTED.md` → writes `RUN_SIDE_REPORT.md`

**Arm Mandate**: Apply entity persona + lessons + KB. Identify:
- Convergent findings (both sides agree)
- Divergent findings (build vs run tension)
- Critical gaps requiring research
- Measurable acceptance criteria (bash-verifiable)

---

### Stage 3: Kali Synthesis Arm Activation

**MaKaLi dispatches the KALI ARM** — her first council appearance as participant, not orchestrator:

Kali reads BOTH digests + BOTH arm reports → writes `SYNTHESIS_ARM_REPORT.md` with mandatory sections:

1. **Convergence Audit** — where Ma'at and Lilith genuinely agree (verified, not assumed)
2. **Dissent Adjudication** — for each build/run tension: who is right, why, or why it's irreducible
3. **Blind-Spot Sweep** — what NEITHER side saw that the synthesis view reveals
4. **Verdict Draft** — the decree she would issue, explicitly marked as DRAFT for MaKaLi's fusion
5. **REMAINING_GAPS_AND_RECOMMENDED_RESEARCH** — structured for Stage 4
6. **MEASURABLE_GATES** — every gate = bash command (`rg`, `pytest`, shell one-liner)

**Critical**: Kali's draft verdict is INPUT to MaKaLi's fusion, not the final word.
MaKaLi carries all three voices; the decree is fused, not delegated.

---

### Stage 4: Research Execution (Mandatory Grounding)

**MaKaLi directs research for EACH gap in `REMAINING_GAPS_AND_RECOMMENDED_RESEARCH`:**

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

### Stage 5: MaKaLi Fusion & Sovereign Decree

MaKaLi reads ALL artifacts:
- `BUILD_SIDE_REPORT.md` + `RUN_SIDE_REPORT.md` (arm distillations)
- `SYNTHESIS_ARM_REPORT.md` (Kali's participatory synthesis)
- Research results from Stage 4

Writes `SOVEREIGN_DECREE.md` — the fused verdict carrying all three voices:
- **Triad Attribution**: which voice contributed which element (provenance chain)
- **Fused Verdict**: single decree, stronger than any individual arm's position
- **Preserved Dissent**: documented tensions that survived fusion
- **Measurable Gates**: bash-verifiable acceptance criteria
- **Tracker Directives**: exact updates for ACTIVE_SPRINT, TASK_REGISTRY, GAP_REGISTRY, PIVOT_LOG

---

### Stage 6: Integration & Verdict Delivery

1. **Session agent (kali) receives MaKaLi's return** — verifies P12 signature, checks interleave
2. **Run quality gates**:
   - `make temple-grade` (T1-T11)
   - `make heritage-map` (all `[id-soft:]` tags vetted)
   - `make sovereignty` (local-first ratio ≥ 80%)
   - `make test` (1398+ tests pass)
   - `scripts/validate_tracking_state.py` (tracking integrity)
3. **Apply tracker directives** from the decree
4. **Release workspace lock**: `omega-hub_hivemind_workspace_lock_release`
5. **Final Hivemind post**: intent="decision" with verdict summary
6. **Deliver decree to Architect** with triad attribution table

---

## Execution Mandate

- Use `task` tool for ALL delegations (arms + nodes + pageable specialists)
- All subagents run on the session model ({session_model}) unless local-first routing specified
- Maintain provenance: every finding tagged with `source_arm`, `source_node`, `source_session`, `tier`
- **No parametric synthesis** — every factual claim must trace to a tool call (T0-T6)
- **Failure Integrity (M23)**: If mandatory tool fails → `[TOOL-CHAIN-COLLAPSE]` logged, hard stop
- **Token Efficiency (M18)**: Digestion layer (Stage 1.5) reduces arm tokens ~60%
- **Recursion Guard**: MaKaLi never launches makali; arms never launch arms
- **P12 Compliance**: Every task() call opens with a signed `[DISPATCH]` header

---

## Required Reading Before Launch

**Session agent (kali)**: items 1-7 above + `.opencode/agents/makali.md`

**MaKaLi (orchestrator)**: ALL items below:
1. `SOVEREIGN_MANDATES.md` v3.8.0 (27 Laws)
2. `SOVEREIGN_ARK_BLUEPRINT.md` §4–§5
3. `STRATEGY_CORPUS_MAP.md` (Layer 2 preservation)
4. `ACTIVE_SPRINT.json` (current workstreams)
5. `TASK_REGISTRY.json` (check for resumable pageable sessions)
6. `GAP_REGISTRY.json` (open R-gaps)
7. `data/coordination/SESSION_ANCHOR.md` (continuity)
8. `ARCHITECT_OVERSIGHT_PATTERNS_20260823.md` (P1-P13 protocols)
9. `.opencode/skills/sovereign-search/SKILL.md` (7-tier protocol)
10. `.opencode/skills/makali-council-coordinator/SKILL.md` (coordinator impl)
11. `data/entities/roc_racoon/workspace/RECURSIVE_SPECIALIST_ROSTER.md` (paging protocol)
12. Your fused identity: `.opencode/agents/makali.md` + constituent souls (`kali`, `maat`, `lilith` soul.yaml files)

**Arms (kali/maat/lilith subagents)**: their own soul.yaml + proposed_lessons.yaml + the mission packet section relevant to their side.

---

## Heritage Attribution

- **Doom 1993**: WAD System (allowlist = lump directory), BSP Culling (delete dead code first)
- **Quake 1996**: Thinker Chain (serial node execution)
- **Quake III 1999**: QVM / Bot AI (modular isolation)
- **id Software netchan**: Channel taxonomy (Hivemind handoff protocol)
- **Omega Engine 2026**: Pageable recursive specialists (persistent task_id sessions), Report Digestion Layer (Phase 1.5), Sovereign Search Protocol (T0-T6), Entity Architecture Topology (MaKaLi orchestrator-slot, triad-as-arms)

---

## Quick Reference: Council Artifacts Structure

```
data/council/{session_id}/
├── phase1_nodes/
│   ├── P1_report.md ... P10_report.md     (ALL TEN — N2 restored)
├── phase1.5_digested/
│   ├── BUILD_SIDE_DIGESTED.md
│   └── RUN_SIDE_DIGESTED.md
├── phase2_arms/
│   ├── BUILD_SIDE_REPORT.md               (Ma'at)
│   └── RUN_SIDE_REPORT.md                 (Lilith)
├── phase3_synthesis/
│   └── SYNTHESIS_ARM_REPORT.md            (Kali — participatory)
├── phase4_research/
│   ├── research_gaps.md
│   ├── research_results/
│   └── pageable_specialists/              (task_id registry)
├── phase5_fusion/
│   └── SOVEREIGN_DECREE.md                (MaKaLi — fused triad verdict)
└── phase6_integration/
    └── tracker_updates.json
```

---

*⬡ OMEGA ⬡ MAKALI-COUNCIL ⬡ 2026-08-25 ⬡ entity-architecture-topology-v2*
