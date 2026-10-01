<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 ENTITY_SPEC Delta — Session Paging Report
**From**: roc_racoon (dormant session ses_fdef2be4effe4pAaLXCTUx62GO successor)
**Date**: 2026-08-21
**Original Work**: Deep Local Entity Specialization & Knowledge Management Discovery — Second Pass (7 deliverables, 2026-08-18)
**Hydration Sources**: `data/coordination/ACTIVE_SPRINT.json` (PUBLIC-DEBUT-01, updated 2026-08-20), `docs/specs/PROJECT_INDEX.md` (2026-08-20)
**AP Token**: `AP-ENTITY-SPEC-DELTA-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_paging_delta ⬡ ACTIVE

---

## §1 Original Deliverables (Reference Index)

| # | File | Status vs Current State |
|---|------|------------------------|
| 1 | `data/coordination/ENTITY_KNOWLEDGE_DEEP_DIVE_20260818.md` | **HIGHLY RELEVANT to KD/DS** — see §2.1 |
| 2 | `data/coordination/ENTITY_SOUL_COMPARISON_20260818.md` | Relevant to soul persistence gate + CI-2 model routing — see §2.2 |
| 3 | `data/coordination/KNOWLEDGE_PROMOTION_GATE_20260818.md` | **CRITICAL for KD/DS design** — see §2.3 |
| 4 | `data/coordination/AGENT_SPECIALIZATION_PATTERNS_20260818.md` | Relevant to Node Expert Sessions D-586/D-587 — see §2.4 |
| 5 | `data/coordination/LATTICE_NODE_MECHANICS_20260818.md` | **URGENT for D-586/D-587** — N1 slot congestion — see §2.5 |
| 6 | `data/coordination/FLEET_CONSOLIDATION_MECHANICS_20260818.md` | Reference playbook; D-558 parks fleet architecture — see §3.4 |
| 7 | `data/coordination/MNEMESYNE_CURRENT_MAPPING_20260818.md` | Dormant artifact; extraction never executed — see §3.5 |

---

## §2 Forgotten Findings Directly Applicable to Current State

### 2.1 KD/DS Workstream: The Only Working Local Template Is roc_racoon's INDEX.yaml

The ratified KD workstream (runtime modules + workspace authoring + curator model) maps onto the DOCUMENTATION-SYSTEM (DS) subtasks DS-1..DS-5 in ACTIVE_SPRINT.json. My deep dive found:

- **Only 7 of 14 entities have `knowledge/` dirs** (doom_guy, lilith, jem, researcher, maat, quality, roc_racoon). Knowledge persistence correlates with active mining/research workflows, not with entity importance.
- **roc_racoon's INDEX.yaml is the ONLY populated topic catalog in the engine**: schema = `id / title / summary / files[] / cross_references[{agent, topic, relation}] / applicability[] / era`. Every promoted file carries frontmatter: `promoted_from`, `promoted_at`, `insight_level`, optional `emergency`.
- **Jem's markdown INDEX is the superior human+LLM format**: status tags (🟢 CANONICAL / 🟡 SUPERSEDED / 🟡 STALE), canonical-subdir layout (`knowledge/SOVEREIGN_IDENTITY/` holds 4 master specs; root files marked superseded).
- **Researcher's `quarantine/` + `raw/` staging subdirs are a working precedent for DS-4's validated-copy sync flow** (`scripts/sync_domain_docs.py`).

**Recommendation for DS-1 meta-doc**: adopt roc_racoon's topic schema as the domain catalog format and jem's status-tag convention; do not invent a third format.

### 2.2 Soul Persistence Gate — My Gap Analysis Is Now Half-Closed

Gate note says: proposed_lessons.yaml → session_end.py preserves → next session hydrates via get_soul_prompt(). My promotion-gate analysis mapped the full pipeline:

```
workspace (T1) → [D-kal-170 mandatory disk write] → Scribe L1→L2→L3 →
proposed_lessons.yaml → user approval → approved_lessons.yaml → soul.yaml
```

Steps 2→3 (distillation) and now hydration are automated. **Still manual and unenforced: workspace→knowledge promotion and INDEX population.** The gate verification covers soul continuity but NOT knowledge-directory continuity — an entity can persist its soul while its knowledge/ dir stays stale.

### 2.3 The T1→T2 Gate Anti-Pattern — Design Lesson for KD

`knowledge/INDEX.yaml` header comments promise "Topics are promoted from workspace/ → knowledge/ via the T1→T2 gate" — yet 4 of 7 entities have empty `topics: []` despite containing promoted content. The gate was **documented but never enforced or automated**. This is the exact failure mode KD domains must avoid: any new domain structure (DS-2/DS-3) must ship with its validator/enforcer at creation time, not as a follow-up. Reusable enforcement already exists: `scripts/validate_llm_docs.py` (frontmatter schema, answer-first sections, token budgets per doc_type) can be extended with a domain-catalog check rather than writing a new validator.

Also relevant: SUBAGENT_DISPATCH_PROTOCOL §0/§8a experience table proves reference-only context delivery fails 100% of the time (3 identical jem dispatches: 2 empty results, 1 success only after full inline embedding). **KD curator-model dispatches must inline domain content**, and there is still no pre-dispatch validation enforcing this.

### 2.4 Agent Specialization Inventory for Node Expert Sessions (D-586/D-587)

My agent-file matrix documented how specialization is encoded in three layers (frontmatter temperature/task_tool_type; role instructions + mandate focus; constraints/heuristics). Directly usable as charter material for the 10 Node sessions:
- Temperature gradient: john_carmack 0.2 (audit), verity 0.4 (compliance), others 0.5.
- task_tool_type specialization: explore (roc_racoon), verity, node, buildmaster (maat), general.
- Per-agent mandate focus lists (e.g., maat→M2/M6/M16/M21; lilith→M5/M11/M15/M17) — natural charter seeds for build-side vs run-side Node sessions.
- grokster carries the only agent-specific mandate (M26 Epistemic Closure Reflex).

### 2.5 URGENT for D-586/D-587: dispatch.yaml Role Collision

`config/wads/_omega_default/entities/dispatch.yaml` assigns **seven entities to role N1** (doom_guy, roc_racoon, jem, john_carmack, makali, researcher, verity). These are primary specialists, not pillar nodes — the actual pillar slots are served by the single `node` agent (`node_slot: "NX"`). Additionally **makali appears twice** (role N1 AND role MAKALI_COUNCIL — duplicate entity entry). If D-586/D-587 spin up 10 Node sessions with charters, this collision makes slot identity ambiguous. Fix: reserve N1-N10 for pillar nodes; introduce distinct role constants for specialists (HERITAGE_ARCHITECT, MINER, RESEARCH_ORCHESTRATOR, S3_CONSULTANT, COUNCIL_ORCHESTRATOR, MASTER_RESEARCHER, COMPLIANCE_GUARDIAN); dedupe makali.

Note: D-558 parks fleet architecture per Carmack ("only DeepSeek-assisted IntentRouter extraction survives") — so this fix should be framed as a **dispatch.yaml data correction**, not fleet redesign, to stay inside debut scope.

---

## §3 Flagged But Never Executed (Outstanding Items)

1. **T1→T2 promotion automation** (my Rec #1, 2026-08-18): extend Scribe distiller with `promote_to_knowledge` flag + auto-INDEX. Never built. Now feeds directly into DS-1/DS-4 design.
2. **Inline-context pre-dispatch validation** (my Rec #2): protocol documents it; no wrapper enforces it. Still open.
3. **N1 slot congestion fix** (my Rec #3): still present in dispatch.yaml; urgency raised by D-586/D-587.
4. **`quality.md` missing from `.opencode/agents/`**: referenced by AGENT_FLEET.md, has soul.yaml + knowledge/INDEX.yaml, no agent file. Never created or explicitly deleted. M10 hygiene item.
5. **Mnemosyne extraction (art_mnemosyne)**: D-385 called for migration script; jem triage budgets 2 L1 sessions; 27 files/284KB at `/media/arcana-novai/omega_library/data_archive/mnemosyne/`. Never extracted. Post-debut candidate; Qliphoth taxonomy + Da'at-as-compaction mappings already preserved in lilith/roc_racoon souls.
6. **INDEX.yaml population** for doom_guy/researcher/maat/quality: still empty.
7. **PUB-1 allowlist consideration**: my seven 20260818 deliverables document internal fleet architecture, entity workspace contents, and coordination mechanics. PUB-1 acceptance requires "no agent workspace dumps" in public ref — these coordination docs should be reviewed against PUBLIC_ALLOWLIST.txt before release branch cut.

---

## §4 What Changed Since Original Session (Reconciliation)

- Three debut gates COMPLETED (local inference E2E, soul persistence, one-click install) — validates my pipeline map's automated segments.
- Sprint collapsed to PUBLIC-DEBUT-01 three-item critical path; SDP/Qdrant/fleet-migration/Scribe-extension all PARKED post-debut (D-538) — so items §3.1/§3.5 correctly remain deferred.
- CI-2 model routing (kali=nemotron pin, verity=cheap critic, researcher/maat/lilith/node UNPINNED) is consistent with my finding that model assignment lives in dispatch.yaml/WAD config, not soul.yaml.
- KD workstream appears in tracker as DOCUMENTATION-SYSTEM (DS-1..DS-5); treat them as one program.

---

## §5 Top Actions I'd Resubmit (Local Evidence Only)

1. **Before DS-1 is authored**: read `ENTITY_KNOWLEDGE_DEEP_DIVE_20260818.md` + `KNOWLEDGE_PROMOTION_GATE_20260818.md`; adopt roc_racoon topic schema + jem status tags; wire validate_llm_docs.py extension into DS-4 sync script from day one.
2. **Before D-586/D-587 charters finalize**: correct dispatch.yaml role collisions (§2.5) — data-only change, M2-compliant, no fleet redesign.
3. **During PUB-1 allowlist cut**: review the seven ENTITY_SPEC deliverables + SESSION_PAGING_REPORTS for public-ref exclusion.
