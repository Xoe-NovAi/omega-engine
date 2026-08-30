---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

description: Run the MaKaLi council with Ma'at and Lilith on local engine-routed models (Kali stays on session model)
agent: kali
subtask: false
---

# 🔱 MaKaLi Local Council Dispatch — Generalized Protocol
**AP Token**: `AP-MAKALI-LOCAL-GENERALIZED-v1.0`
**Date**: 2026-08-25
**Session Model**: {session_model}
**Channel**: opencode

---

You are summoning the **MaKaLi local council** for this query: $ARGUMENTS

**Local-First Mandate (M7)**: All Node + Oversoul reasoning routes through local provider fabric.
Kali (Grand Oversight) stays on session model for synthesis quality.

---

## The Sovereign Flow (Local-First Multi-Tiered Dispatch)

### Stage 0: Preconditions (Same as Cloud)
- Hydrate from SSOTs (Mandates, Ark, Corpus Map, Sprint, Task Registry, Gap Registry, Soul, Anchor)
- Initialize Hivemind + workspace lock
- Check `TASK_REGISTRY.json` for pageable recursive specialists → RESUME if found

### Stage 1: Parallel Node Dispatch (Local Routing)

**Ma'at (Build Side — N1, N3, N4, N5)** — each Node uses `oracle_summon_local`:
- N1 (Ma'at): `lmstudio/qwen3-4b-thinking` — architecture, mandates
- N3 (Engineering): `lmstudio/qwen3-4b-thinking` — implementation, refactoring
- N4 (Security): `lmstudio/qwen3-4b` — firewall, heritage, vuln
- N5 (Operations): `lmstudio/qwen3-4b` — deployment, monitoring

**Lilith (Run Side — N6, N7, N8, N9, N10)** — each Node uses `oracle_summon_local`:
- N6 (Lilith): `lmstudio/krikri-8b` — runtime, soul, handoff
- N7 (Research): `lmstudio/qwen3-4b-thinking` — mining, gaps, counterfactuals
- N8 (Quality): `lmstudio/qwen3-4b` — testing, contracts
- N9 (Scribe): `lmstudio/qwen3-4b` — docs, distillation, gnosis
- N10 (Validation): `lmstudio/qwen3-4b-thinking` — adversarial review

**Execution**: Serial within side (Thinker Chain), parallel across sides.
**Output**: `data/council/{session_id}/phase1_nodes/P{N}_report.md`

### Stage 1.5: Report Digestion (Python Only — ZERO Inference)
- Same as cloud: stack-cat + executive summaries + cross-ref + conflict detection + mandate matrix
- Output: `BUILD_SIDE_DIGESTED.md` + `RUN_SIDE_DIGESTED.md`

### Stage 2: Oversoul Distillation (Local)

**Ma'at**: `oracle_summon_local` with `lmstudio/qwen3-4b-thinking` → reads digested → writes `BUILD_SIDE_REPORT.md`
**Lilith**: `oracle_summon_local` with `lmstudio/krikri-8b` → reads digested → writes `RUN_SIDE_REPORT.md`

### Stage 3: Kali Final Synthesis (Session Model)
- Reads both oversoul reports → writes `FINAL_SYNTHESIS.md` with Convergence, Preserved Dissent, Irreducible Verdict, RESEARCH_GAPS, MEASURABLE_GATES

### Stage 4: Research Execution (Local-First Sovereign Search)
**Protocol**: T0 (local cache) → T1 (websearch) → T2 (webfetch) → T3 (SearXNG) → T4 (Parallel Search) → T5/T6 (Exa/Firecrawl ONLY if credits > 100)
**Local Discovery**: `omega-hub_library_discovery_research`, `omega-hub_library_fts_search`, `omega-hub_library_search`
**Pageable Specialists**: Spawn via `task()` with local models, register in `TASK_REGISTRY.json`
**Meditate-Research Pipeline**: Available for architectural questions

### Stage 5: Integration & Gates
- `make temple-grade`, `make heritage-map`, `make sovereignty`, `make test`, `validate_tracking_state.py`
- Update all trackers, release lock, final Hivemind post

---

## Execution Mandate
- **Local transparency**: Every Node/Oversoul call logs `provider_name` from actual response (M22)
- **Model inheritance**: Child agents inherit parent model unless `oracle_summon_local` specifies otherwise
- **No parametric synthesis**: Every factual claim traces to tool call
- **M23 Failure Integrity**: Tool failure → `[TOOL-CHAIN-COLLAPSE]` logged, hard stop

---

## Required Reading (All Agents)
Same as cloud council + `.opencode/skills/sovereign-search/SKILL.md` + `.opencode/skills/meditate-research-pipeline/SKILL.md` + `RECURSIVE_SPECIALIST_ROSTER.md`

---

*⬡ OMEGA ⬡ MAKALI-LOCAL ⬡ 2026-08-25 ⬡ generalized-protocol*