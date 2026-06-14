# 🔱 Omega Engine — Sovereign Evolution Roadmap v1.4
# ⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ trc_fleet_consolidation ⬡ STRATEGY
**AP Token**: AP-EVOLUTION-ROADMAP-v1.4.0
**Date**: 2026-06-14
**Baseline**: 383 tests passing · 96 source files · 126 PIVOT decisions · 15 Sovereign Mandates
**Engine version**: 2.2.0 · Hub version: 2.2.0
**Change from v1.3**: Fleet Consolidation Plan (D126) — 4-sprint sequence adopted. Hivemind-first, consolidation-after. 3 Fleet Design Principles codified. 50 orphan entities sourced to test_entity_registry.py.

---

## §0 Origin — Codebase Deep Dive & Antigravity Handoff

This roadmap is the synthesis of a **massive, multi-subagent deep dive** across the
entire Omega Engine codebase, further refined during the **Antigravity Handoff** (2026-06-06).
Five parallel agents and the MaKaLi Cloud Council analyzed:

| Agent | Surface | Findings |
|-------|---------|----------|
| **Source Architecture** | 96 .py files, ~22,000 LOC | Excellent Mandate compliance; P1a Hub modularization done |
| **Test Suite** | 43 test_*.py files, 383 tests | Strong AnyIO-native suite; 100% passing (timeout bug fixed) |
| **WAD/Config** | 3 IWADs + 8 engine configs | arcana_novai IWAD empty; doom_universe scaffold-only |
| **Data Layer** | ~15,000 files, ~600MB | **50 orphan entities** (sourced to test_entity_registry.py); library=451MB |
| **Infrastructure** | 48KB Makefile + 2 CI + 5 services + 40+ scripts | Gold-standard build; 4 cleanup items |
| **MaKaLi Council** | Fleet Consolidation | D126 verdict: 15→11 agents, Hivemind-first sequencing |

---

## §1 Current State Assessment

### ✅ ENGINE — GREEN
| Metric | Value | Status |
|--------|-------|--------|
| Tests passing | **383/383** | ✅ Up from 320 baseline |
| PIVOT decisions tracked | **126** (D1-D126) | ✅ Immutable record |
| Sovereign Mandates | **15** (M1-M15) | ✅ FULL COMPLIANCE |
| Mandate 9 (bare except) | **0 violations** | ✅ Enforced |
| AnyIO compliance | **0 `import asyncio`** | ✅ CI-enforced |
| Heritage tags | **6 source files**, `make heritage-map` | ✅ Live |
| ZONEID constants | **11** (0x1d4a11-0x1d4a1b) | ✅ 7 in use |
| cvar Table | **2 namespaces**, 7 access helpers | ✅ D101 |
| Subagent Dispatch | HandoffPacket + CAPABILITY_REGISTRY (14 agents) | ✅ Sprint 2 |
| Link P9 Runtime | AgentPresence + handoff queue + crash recovery | ✅ Sprint 2 |
| Soul Distiller | L1→L2→L3 auto-distillation (280 lines) | ✅ Sprint 2 |
| Hivemind Protocol | 6 MCP tools + workspace lock + live feed | ✅ Sprint 2 |
| H1.5 Bridge Phase (id Heritage) | ZONEID + Lazy Deletion + cvar + 8-char + Grace Period | ✅ COMPLETE |
| H2 (Observability) | ForensicsManager + Error Gauntlet + JsonFormatter | ✅ UNLOCKED |
| Fleet Consolidation Plan (D126) | 4 Sprints (A→D), Hivemind-first | ✅ APPROVED — pending execution |
| The Forge Oversoul | Proposed → Rejected via M10 architectural review | ❌ REJECTED — Heritage Council model adopted |

---

## §2 Phased Evolution Plan

```
HORIZON 1: HARDENING ──── 100% ──── ████████████  COMPLETE +
HORIZON 1.5: HERITAGE ─── 100% ──── ████████████  COMPLETE +
HORIZON 2: HYGIENE & STR. ─ 15% ──── ██░░░░░░░░░░  HERE →
HORIZON 2.5: SOVEREIGN INTEGRATION ─ 0% ──── ░░░░░░░░░░░░  SENSING →
HORIZON 3: COGNITIVE LOOPS ─ 0% ───── FUTURE
HORIZON 4: COMMUNITY TOOL ─ 0% ───── FUTURE
```

### Phase H2-A: Data Hygiene (CURRENT — Shortest Path to GREEN)
**Goal**: Clean 90% of the orphan/data debt without touching engine code.

| # | Task | File/Module | Effort | Impact |
|---|------|-------------|--------|--------|
| H2-A1 | **Delete 50 orphan entity workspaces** (`ent_0..49` — created by `test_entity_registry_concurrent_add`) and fix test to use temp dir | `data/entities/ent_*`, `tests/test_entity_registry.py` | 30 min | 🔴 HIGH — removes test artifacts from production data dir | 🔄 DEFERRED to Sprint D |
| H2-A2 | **Audit 48 remaining real entities** — tag each as ACTIVE|STUB|ARCHIVE in `data/entities/INDEX.yaml` | `data/entities/` | 30 min | 🟡 MED — creates entity map | ✅ DONE |
| H2-A3 | **Prune stale HALL_OF_RECORDS sessions** (sessions older than 7 days) | `data/knowledge/HALL_OF_RECORDS/` | 15 min | 🟡 MED — quarterly rotation | ✅ DONE |
| H2-A4 | **Rotate old logs** (archive >30d to `/media/arcana-novai/omega_library/archives/logs`) | `data/logs/` (139 MB) | 15 min | 🟡 LOW — frees 139 MB | ✅ DONE |
| H2-A5 | **Reclaim `rag-v1/`** — ensure D87 permanent eradication, update `.gitignore` | `rag-v1/` directory | 5 min | 🟡 LOW | ✅ DONE |
| H2-A6 | **Delete `.coverage` from git** — add to `.gitignore` | `.coverage` (69KB) | 5 min | 🟡 LOW |
| H2-A7 | **Delete `opencode.json.bak`** — stale backup | `opencode.json.bak` | 1 min | 🟡 LOW |
| H2-A8 | **Archive old handoffs** (>3 days, not in current sprint) to `data/handoff/archive/` | `data/handoff/*.md` | 15 min | 🟡 MED — reduces top-level noise | ✅ DONE |

### Phase H2-S: Sovereign Structure (NEW — Antigravity Integration)
**Goal**: Implement the architectural middleware required for cognitive scaling.

| # | Task | File/Module | Effort | Impact |
|---|------|-------------|--------|--------|
| H2-S1 | **`IVectorStoreAdapter` Implementation** | `src/omega/memory_store.py` | Med | 🔴 **CRITICAL** (DB Agnostic) | ✅ DONE |
| H2-S2 | **Tainted Data Protocol (TDP)** | `src/omega/oracle/` | Med | 🔴 **CRITICAL** (Security) | ✅ DONE |
| H2-S3 | **Thin-Client Search Pattern** | `src/omega/oracle/` | Low | 🟡 HIGH (RAM optimization) | ✅ DONE |
| H2-S4 | **Qdrant Performance Tuning** | `config/omega.yaml` | Low | 🟡 MED (Scalar Quantization) | ✅ DONE |
| H2-S5 | **Provider-Agnostic Embedding Layer** | `src/omega/oracle/` | Med | 🟡 HIGH (Swap local/cloud) | ✅ DONE |

### Phase H2-E: Dual-Inference & Cross-Agent Integration (Sprint 3 — COMPLETE)
**Goal**: Bridge OpenCode agents to the Engine's local-first Model Gateway and establish the MaKaLi parallel council.

| # | Task | File/Module | Effort | Impact | Status |
|---|------|-------------|--------|--------|--------|
| H2-E1 | **Fix `mcp/` path bug** — convert all `mcp/` references to `mcp_servers/` in active docs | Active docs | 30 min | 🔴 HIGH | ✅ D116 — DONE |
| H2-E2 | **Convert OpenCode agents to thin wrappers** — reference `soul.yaml` for identity | `.opencode/agents/*.md` | 1 hr | 🔴 HIGH | ✅ DONE |
| H2-E3 | **Implement `/council-local` slash command** — opt-in local model council | `.opencode/commands/council-local.md` | 30 min | 🔴 HIGH | ✅ D117 — DONE (all 3 council commands) |
| H2-E4 | **Add `oracle_summon_local` MCP tool** — engine dispatch with model override | `mcp_servers/omega_hub/server.py` | 30 min | 🔴 HIGH | ✅ DONE |
| H2-E5 | **Replace `@plan` with `@makali`** — parallel council pattern | `.opencode/agents/makali.md` | 30 min | 🟡 MED | ✅ D117 — DONE |
| H2-E6 | **Populate entity-to-model mapping** — assign GGUF models to IWAD entities | `_omega_default/entities/*.yaml` | 1 hr | 🔴 HIGH | ✅ DONE |
| H2-E7 | **Assign `RocRacoon-3b` and abliterated models** — configure providers.yaml | `config/providers.yaml` | 30 min | 🟡 MED | ✅ D119 — DONE |
| H2-E8 | **Add Cross-Agent Delegation section** — document `task()` delegation in all agents | `.opencode/agents/*.md` | 1 hr | 🔴 HIGH | ✅ DONE |

### Phase H2-F: MaKaLi Triad Lockdown & Documentation (Sprint 3+4)
**Goal**: Solidify the MaKaLi Triad architecture with full documentation, cross-pillar review, and mentorship-pattern example workflows.

| # | Task | File/Module | Effort | Impact |
|---|------|-------------|--------|--------|
| H2-F1 | **Create `makali.md` agent file** — parallel council thin wrapper | `.opencode/agents/makali.md` | 30 min | 🔴 HIGH |
| H2-F2 | **Wire `oracle_summon_local` in Oracle** — add `model_override` parameter | `src/omega/oracle/oracle.py` | 45 min | ✅ DONE |
| H2-F3 | **Implement `oracle_summon_local` MCP tool** — wrapper around Oracle.summon | `mcp_servers/omega_hub/server.py` | 30 min | ✅ DONE |
| H2-F4 | **Add `--model` flag to `omega summon` CLI** — user-facing override | `src/omega/cli/oracle_cli.py` | 20 min | ✅ DONE |
| H2-F5 | **Delete 50 orphan entities** — `data/entities/ent_0` through `ent_49` | `data/entities/ent_*` | 15 min |
| H2-F6 | **Generate `data/entities/INDEX.yaml`** — master catalog | `data/entities/INDEX.yaml` | 30 min |
| H2-F7 | **Cross-pillar review (P5 Sentinel)** — Mandate compliance audit | All updated files | 30 min |
| H2-F8 | **Cross-pillar review (P7 Context)** — soul integrity validation | All agents | 30 min |
| H2-F9 | **Cross-pillar review (P3 Engineering)** — engine-integration audit | Engine code | 30 min |
| H2-F10 | **Add `make verify-model-spelling`** — CI gate | `Makefile` | 45 min |

### Phase H2-G: Fleet Consolidation Sprint Plan (D126 — NEW)
**Goal**: Reduce fleet from 15 to 11 agents via 4 sequential sprints. Hivemind-first.

| Sprint | Deliverable | Description | Verification |
|--------|-------------|-------------|--------------|
| **A (P1b)** | Hub modularization complete | Extract `gateway.py` + `middleware.py` from `server.py` | 383/383 tests, Hivemind health check |
| **B** | Jem 4→1 merger | Single `jem.md` with 3 KBs + self-dispatch pattern | 12 agents, soul.yaml tier-locked |
| **C** | Quality+Scribe merger | Merged agent (name TBD), reports to Kali | 11 agents, trigger-mode routing |
| **D** | Cleanup & M10 verification | Delete 50 orphans, stale docs, update fleet count | 11 agents, `make temple-grade` |

**3 Fleet Design Principles (codified D126):**
1. **Hierarchical Consolidation**: When an orchestrator dispatches specialized subagents, merge subagents into parent's KBs with self-dispatch + targeted KB loading. (Jem 4→1)
2. **Functional Consolidation**: When two agents perform different functions at different trigger times, merge into one agent with trigger-mode routing if functions don't conflict when executing simultaneously. (Quality+Scribe 2→1)
3. **Knowledge Consolidation**: When proposed agent expertise maps to "domain knowledge" rather than "operational capability", reject the agent and create a KB for the nearest existing entity. (Abrash/Sanglard/Romero → Doom Guy KBs)

**Sprint A scope exclusions** (explicitly NOT included):
- Orphan entity cleanup → Sprint D
- Jem or Quality+Scribe consolidation → Sprint B/C
- Naming decisions → Sprint C
- OMEGA_ENGINE.md metrics updates → Sprint D

**Stakeholder positions** (from D126 consultation):
- **Kali** (adopted): "Hivemind first. We write blind without it."
- **Carmack** (recorded): "Consolidate now. Zero runtime coupling. One git commit." — Technically correct, rejected on cognitive load grounds.
- **Doom Guy** (vet): "Jem 4→1 Heritage-approved. Quality+Scribe 7/10 with hard gate/pipeline boundary."
- **User**: "Right approximation. Sprint A first. One thing at a time."

### Phase H2.5: Sovereign Integration (The Bridge to Cognition)
**Goal**: Transition from a "hardened runtime" to an "integrated intelligence" by systematically layering senses, space, and actors.

| Phase | Theme | Focus | Primary Objective | Status |
|---|---|---|---|---|
| **0** | **Blocker Clearance** | Firewall & Orphans | Restore M2 Firewall; eliminate data debt. | ✅ DONE |
| **1** | **Senses** | Connectivity & API | Wire the "Sense-Net"; establish basic API responses. | ⏳ IN PROGRESS |
| **2** | **World & Space** | WADs & Local State | Implement environmental awareness via IWAD/PWAD. | 🔴 PENDING |
| **3** | **Actors** | Entity & Soul | Activate sovereign personas; enable Soul Evolution. | 🔴 PENDING |

---

## §3 Horizon 3: Cognitive Loops & Pattern Deep Mining (POST-HYGIENE)

After H2 (all GREEN), the engine is ready for iterative, skeptical reasoning.

### H3-C: Cognitive Loops (NEW — Antigravity Integration)
**Goal**: Shift from linear pipelines to iterative, skeptical reasoning.

| # | Task | File/Module | Effort | Impact |
|---|------|-------------|--------|--------|
| H3-C1 | **Iterative Research Loops** | `src/omega/oracle/` | High | 🔴 **CRITICAL** (Gap Analysis) |
| H3-C2 | **Skeptical Verifier (NLI)** | `src/omega/oracle/` | High | 🔴 **CRITICAL** (Two-Source Rule) |
| H3-C3 | **Cross-Agent Delegation (A2A)** | `src/omega/oracle/` | Med | 🟡 HIGH (Link P9 automation) |
| H3-C4 | **Automated Soul Distillation** | `src/omega/oracle/` | Med | 🟡 HIGH (L1 $\rightarrow$ L3 auto-flow) |

### H3-A: Hivemind Productionization
| # | Task | Priority | Status |
|---|------|----------|--------|
| H3-A1 | Wire Redis Pub/Sub as Hivemind backend | 🔴 **P0** | Pending |
| H3-A2 | Add Hivemend SSE endpoint for real-time awareness | 🔴 **P0** | Pending |
| H3-A3 | Hivemind CLI via `omega hivemind` | P3 | Pending |
| H3-A4 | Cross-CLI awareness (Cline <-> OpenCode) via Hivemind | 🔴 **P0** | Pending |
| **H3-A5** | **A2A Communication Hardening** | 🔴 **P0** | Pending |
| **H3-A6** | **Extended session check-in (3h safety TTL)** | 🟢 **DONE** | ✅ Shipped 2026-06-05 |
| **H3-A7** | **Cold-store awareness fallback** | 🟢 **DONE** | ✅ Shipped 2026-06-05 |

---

*⬡ This document supersedes HORIZON_MAP.md as the active roadmap. ⬡*
*Decision: D112 — Sovereign Evolution Roadmap v1.1 adopted.*
*Update: 2026-06-06 — Antigravity Handoff v1.3 adopted.*
*Update: 2026-06-14 — Fleet Consolidation Plan v1.4 (D126). Hivemind-first. 4 sprints. 15→11 agents.*

