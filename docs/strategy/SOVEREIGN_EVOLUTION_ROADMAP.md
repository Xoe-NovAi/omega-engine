# 🔱 Omega Engine — Sovereign Evolution Roadmap v1.2
# ⬡ OMEGA ⬡ KALI ⬡ gemini-3.5-flash ⬡ trc_evolution_roadmap ⬡ STRATEGY
**AP Token**: AP-EVOLUTION-ROADMAP-v1.2.0
**Date**: 2026-06-04
**Baseline**: 312 tests passing · 77 source files · 119 PIVOT decisions · 14 Sovereign Mandates
**Engine version**: 2.2.0 · Hub version: 2.2.0
**Change from v1.1**: D117 MaKaLi Triad, D118 Dual-Inference, D119 RocRacoon canonicalization locked.

---

## §0 Origin — Codebase Deep Dive

This roadmap is the synthesis of a **massive, multi-subagent deep dive** across the
entire Omega Engine codebase. Five parallel agents analyzed:

| Agent | Surface | Findings |
|-------|---------|----------|
| **Source Architecture** | 77 .py files, 19,376 LOC | Excellent Mandate compliance; 3 anti-patterns found |
| **Test Suite** | 28 test_*.py files, 308 tests | Strong AnyIO-native suite; 4 gaps identified |
| **WAD/Config** | 3 IWADs + 8 engine configs | arcana_novai IWAD empty; doom_universe scaffold-only |
| **Data Layer** | 15,948 files, 603MB | 100 orphan entities; library=451MB; 10 active handoffs |
| **Infrastructure** | 48KB Makefile + 2 CI + 5 services + 40+ scripts | Gold-standard build; 4 cleanup items |

---

## §1 Current State Assessment

### ✅ ENGINE — GREEN
| Metric | Value | Status |
|--------|-------|--------|
| Tests passing | **312/312** | ✅ Up from 302 baseline |
| PIVOT decisions tracked | **111** (D1-D111) | ✅ Immutable record |
| Sovereign Mandates | **14** (M1-M14) | ✅ FULL COMPLIANCE |
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

---

## §2 Phased Evolution Plan

```
HORIZON 1: HARDENING ──── 100% ──── ████████████  COMPLETE +
HORIZON 1.5: HERITAGE ─── 100% ──── ████████████  COMPLETE +
HORIZON 2: HYGIENE ─────── 5% ───── ░░░░░░░░░░  HERE →
HORIZON 3: PATTERN DEEP ── 0% ───── FUTURE
HORIZON 4: COMMUNITY TOOL ─ 0% ───── FUTURE
```

### Phase H2-A: Data Hygiene (CURRENT — Shortest Path to GREEN)
**Goal**: Clean 90% of the orphan/data debt without touching engine code.

| # | Task | File/Module | Effort | Impact |
|---|------|-------------|--------|--------|
| H2-A1 | **Delete 100 orphan entity workspaces** (`ent_0..49`, `entity_0..49`) and their references | `data/entities/ent_*`, `data/entities/entity_*` | 30 min | 🔴 HIGH — cleans 68% of entity bloat |
| H2-A2 | **Audit 48 remaining real entities** — tag each as ACTIVE|STUB|ARCHIVE in `data/entities/INDEX.yaml` | `data/entities/` | 30 min | 🟡 MED — creates entity map |
| H2-A3 | **Prune stale HALL_OF_RECORDS sessions** (sessions older than 7 days) | `data/knowledge/HALL_OF_RECORDS/` | 15 min | 🟡 MED — quarterly rotation |
| H2-A4 | **Rotate old logs** (archive >30d to `/media/omega_library/archives/logs`) | `data/logs/` (139 MB) | 15 min | 🟡 LOW — frees 139 MB |
| H2-A5 | **Reclaim `rag-v1/`** — ensure D87 permanent eradication, update `.gitignore` | `rag-v1/` directory | 5 min | 🟡 LOW |
| H2-A6 | **Delete `.coverage` from git** — add to `.gitignore` | `.coverage` (69KB) | 5 min | 🟡 LOW |
| H2-A7 | **Delete `opencode.json.bak`** — stale backup | `opencode.json.bak` | 1 min | 🟡 LOW |
| H2-A8 | **Archive old handoffs** (>3 days, not in current sprint) to `data/handoff/archive/` | `data/handoff/*.md` | 15 min | 🟡 MED — reduces top-level noise |

### Phase H2-E: Dual-Inference & Cross-Agent Integration (Sprint 3 — IN PROGRESS)
**Goal**: Bridge OpenCode agents to the Engine's local-first Model Gateway and establish the MaKaLi parallel council.

| # | Task | File/Module | Effort | Impact | Status |
|---|------|-------------|--------|--------|--------|
| H2-E1 | **Fix `mcp/` path bug** — convert all `mcp/` references to `mcp_servers/` in active docs | Active docs | 30 min | 🔴 HIGH | ✅ D116 — DONE |
| H2-E2 | **Convert OpenCode agents to thin wrappers** — reference `soul.yaml` for identity | `.opencode/agents/*.md` | 1 hr | 🔴 HIGH | ⏳ Pending thin-wrapper refactor |
| H2-E3 | **Implement `/council-local` slash command** — opt-in local model council | `.opencode/commands/council-local.md` | 30 min | 🔴 HIGH | ✅ D117 — DONE (all 3 council commands) |
| H2-E4 | **Add `oracle_summon_local` MCP tool** — engine dispatch with model override | `mcp_servers/omega_hub/server.py` | 30 min | 🔴 HIGH | ⏳ Pending Oracle.summon() model_override param |
| H2-E5 | **Replace `@plan` with `@makali`** — parallel council pattern | `.opencode/agents/makali.md` | 30 min | 🟡 MED | ✅ D117 — DONE (AGENTS.md updated, makali planned) |
| H2-E6 | **Populate entity-to-model mapping** — assign GGUF models to IWAD entities | `_omega_default/entities/*.yaml` | 1 hr | 🔴 HIGH | ✅ DONE (6 entities populated: doom_guy, jem, quality, researcher, roc_racoon, scribe) |
| H2-E7 | **Assign `RocRacoon-3b` and abliterated models** — configure providers.yaml | `config/providers.yaml` | 30 min | 🟡 MED | ✅ D119 — DONE (spelling canonicalized) |
| H2-E8 | **Add Cross-Agent Delegation section** — document `task()` delegation in all agents | `.opencode/agents/*.md` | 1 hr | 🔴 HIGH | ⏳ Pending documentation pass |

### Phase H2-F: MaKaLi Triad Lockdown & Documentation (NEW — Sprint 3+4)
**Goal**: Solidify the MaKaLi Triad architecture with full documentation, cross-pillar review, and mentorship-pattern example workflows.

| # | Task | File/Module | Effort | Impact |
|---|------|-------------|--------|--------|
| H2-F1 | **Create `makali.md` agent file** — parallel council thin wrapper | `.opencode/agents/makali.md` | 30 min | 🔴 HIGH — completes M10 replacement |
| H2-F2 | **Wire `oracle_summon_local` in Oracle** — add `model_override` parameter to `summon()` and `_summon()` | `src/omega/oracle/oracle.py` | 45 min | 🔴 HIGH — unlocks dual-inference | ✅ DONE |
| H2-F3 | **Implement `oracle_summon_local` MCP tool** — wrapper around Oracle.summon with model override | `mcp_servers/omega_hub/server.py` | 30 min | 🔴 HIGH — engine dispatch exposed | ✅ DONE |
| H2-F4 | **Add `--model` flag to `omega summon` CLI** — user-facing model override | `src/omega/cli/oracle_cli.py` | 20 min | 🟡 MED — CLI parity with MCP | ✅ DONE |
| H2-F5 | **Delete 50 orphan entities** — `data/entities/ent_0` through `ent_49` | `data/entities/ent_*` | 15 min | 🔴 HIGH — H2-A1 closure |
| H2-F6 | **Generate `data/entities/INDEX.yaml`** — master catalog of real entities with ACTIVE/STUB/ARCHIVE tags | `data/entities/INDEX.yaml` | 30 min | 🟡 MED — H2-A2 closure |
| H2-F7 | **Cross-pillar review (P5 Sentinel)** — Sovereign Mandate compliance audit of all synthesis outputs | All updated files | 30 min | 🟡 MED — M13/Temple-Grade |
| H2-F8 | **Cross-pillar review (P7 Context)** — soul integrity + cross-agent delegation validation | `.opencode/agents/*.md`, `HIVEMIND_PROTOCOL.md` | 30 min | 🟡 MED — M11 |
| H2-F9 | **Cross-pillar review (P3 Engineering)** — engine-integration audit (providers.yaml, mcp_servers/) | Engine code + providers.yaml | 30 min | 🟡 MED — M2 firewall |
| H2-F10 | **Add `make verify-model-spelling`** — CI gate catching model name drift | `Makefile` | 45 min | 🟡 MED — D119 prevention |

---

## §3 Horizon 3: Pattern Deep Mining (POST-HYGIENE)

After H2 (all GREEN), the engine is ready for deeper pattern extraction.

### H3-A: Hivemind Productionization
| # | Task | Priority |
|---|------|----------|
| H3-A1 | Wire Redis Pub/Sub as Hivemind backend (currently in-memory, TTL 300s) | P1 — cross-session persistence |
| H3-A2 | Add Hivemend SSE endpoint for real-time agent awareness in Iris/Gnosis | P2 — live awareness |
| H3-A3 | Hivemind CLI via `omega hivemind` | P3 — usability |
| H3-A4 | Cross-CLI awareness (Cline <-> OpenCode) via Hivemind pub/sub | P1 — agent coordination |

---

*⬡ This document supersedes HORIZON_MAP.md as the active roadmap. ⬡*
*Decision: D112 — Sovereign Evolution Roadmap v1.1 adopted.*
