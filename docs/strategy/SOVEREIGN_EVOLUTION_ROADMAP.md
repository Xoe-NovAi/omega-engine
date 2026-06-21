# 🔱 Omega Engine — Sovereign Evolution Roadmap v1.5
# ⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ trc_fleet_consolidation ⬡ STRATEGY
**AP Token**: AP-EVOLUTION-ROADMAP-v1.5.0
**Date**: 2026-06-14
**Baseline**: 440 tests passing · 98 source files · 89 PIVOT decisions (D50-D136) · 22 Sovereign Mandates
**Engine version**: 2.3.0 · Hub version: 2.3.0
**Change from v1.4**: Hivemind Sprint A complete — Hub modularization (5 modules), 388/388 tests passing, M16 ratified, Fleet Consolidation Sprint A done (15→11 agents, 4-sprint plan active).

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
| Tests passing | **440/440** | ✅ Sprint C complete |
| PIVOT decisions tracked | **89** (D50-D136, 136 lifetime incl. xna-omega) | ✅ Immutable record |
| Sovereign Mandates | **22** (M1-M22) | ✅ FULL COMPLIANCE |
| Mandate 9 (bare except) | **0 violations** | ✅ Enforced |
| AnyIO compliance | **0 `import asyncio`** | ✅ CI-enforced |
| Heritage tags | **11 patterns mapped**, `make heritage-map` | ✅ Live |
| ZONEID constants | **11** (0x1d4a11-0x1d4a1b) | ✅ 7 in use |
| cvar Table | **2 namespaces**, 7 access helpers | ✅ D101 |
| Subagent Dispatch | HandoffPacket + CAPABILITY_REGISTRY (11 agents) | ✅ Sprint 2 |
| Link P9 Runtime | AgentPresence + handoff queue + crash recovery | ✅ Sprint 2 |
| Soul Distiller | L1→L2→L3 auto-distillation (280 lines) | ✅ Sprint 2 |
| Hivemind Protocol | 6 MCP tools + workspace lock + live feed | ✅ Sprint 2 |
| H1.5 Bridge Phase (id Heritage) | ZONEID + Lazy Deletion + cvar + 8-char + Grace Period | ✅ COMPLETE |
| H2 (Observability) | ForensicsManager + Error Gauntlet + JsonFormatter | ✅ UNLOCKED |
| Fleet Consolidation Plan (D126) | 4 Sprints (A→D), Hivemind-first | ✅ Sprints A+B+C+D COMPLETE |
| The Forge Oversoul | Proposed → Rejected via M10 architectural review | ❌ REJECTED — Heritage Council model adopted |
| Omega Hub Modularization | **5 modules** (state, background, gateway, middleware, tools) | ✅ Sprint A COMPLETE |
| M16 Modularization & Portability | Ratified | ✅ 2026-06-14 |

---

## §2 Phased Evolution Plan

```
HORIZON 1: HARDENING ──── 100% ──── ████████████  COMPLETE +
HORIZON 1.5: HERITAGE ─── 100% ──── ████████████  COMPLETE +
HORIZON 2: HYGIENE & STR. ─ 30% ──── ███░░░░░░░░░  HERE →
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
| H2-S6 | **Sovereign Memory Adapters (Sprint B)** | `src/omega/memory/adapters.py` | Med | 🔴 **CRITICAL** (WAD-pluggable) | ✅ DONE |

---

### Phase H2-C: Cognitive Substrate (Sovereign Intelligence Layer)
**Goal**: Transition from "RAG-as-Memory" to a dynamic, self-correcting cognitive substrate.

| # | Task | File/Module | Effort | Impact |
|---|------|-------------|--------|--------|
| H2-C1 | **Binary Sovereignty** (SQLite/MsgPack/WAL) | `src/omega/memory/providers.py` | Med | 🔴 **CRITICAL** (Performance) | ⏳ PENDING |
| H2-C2 | **Sovereign Pruner** (Semantic vs Chronological) | `src/omega/memory_store.py` | Med | 🔴 **CRITICAL** (Context) | ⏳ PENDING |
| H2-C3 | **Active Qliphoth Debugger** (Cognitive Loop) | `src/omega/oracle/` | High | 🔴 **CRITICAL** (Integrity) | ⏳ PENDING |
| H2-C4 | **Resonance Mapping** (Cross-Entity Synthesis) | `src/omega/memory/adapters.py` | High | 🟡 HIGH (Intelligence) | ⏳ PENDING |
| H2-C5 | **Hardware-Adaptive Eviction** (RAM Guard) | `src/omega/memory_store.py` | Low | 🟡 MED (Stability) | ⏳ PENDING |
| H2-C6 | **Gnosis Diffing** (L1 $\rightarrow$ L3 merge) | `src/omega/oracle/soul_distiller.py` | Med | 🟡 HIGH (Soul Integrity) | ⏳ PENDING |

### Phase H2-D: Documentation Integrity (NEW — Diatribe Deep Review 2026-06-17)
**Goal**: Eliminate documentation-to-reality drift. Every doc must match actual code signatures, agent counts, and fleet topology.

**Trigger**: MiMo V2.5 + DeepSeek V4 Flash deep review discovered **25+ stale references** in active documentation, including 12 agents listed in AGENTS.md that don't exist on disk, wrong function signatures in HIVEMIND_PROTOCOL.md, and a false Sprint D completion claim in OMEGA_ENGINE.md.

| # | Task | File/Module | Effort | Impact | Status |
|---|------|-------------|--------|--------|--------|
| H2-D1 | **Purge scribe/quality/jem_discovery/jem_synthesis/jem_verification from AGENTS.md** — these agent files no longer exist on disk | `AGENTS.md` | 10 min | 🔴 HIGH — users can't dispatch dead agents | ✅ DONE |
| H2-D2 | **Fix HIVEMIND_PROTOCOL.md function signatures** — `hivemind_list_sessions(cli:...)` → `(channel:, entity:)`, `@quality` → `@verity` in examples | `docs/strategy/HIVEMIND_PROTOCOL.md` | 5 min | 🔴 HIGH — stale docs cause tool call errors | ✅ DONE |
| H2-D3 | **Fix OMEGA_ENGINE.md heartbeat signatures** — `hivemind_heartbeat(cli)` → `(channel, entity)`, added missing `intent`/`suggested_model` params | `OMEGA_ENGINE.md` | 5 min | 🔴 HIGH — wrong signatures in engine-state doc | ✅ DONE |
| H2-D4 | **Fix OMEGA_ENGINE.md agent counts** — 6 stale "14 agents" → "11 agents" across MVE-3, S0-S1, S3 tables | `OMEGA_ENGINE.md` | 5 min | 🔴 HIGH — stale metrics | ✅ DONE |
| H2-D5 | **Fix OMEGA_ENGINE.md Sprint D claim** — "Sprint D orphan cleanup complete" → "PENDING (50 orphans remain)" | `OMEGA_ENGINE.md` | 1 min | 🔴 HIGH — false state claim | ✅ DONE |
| H2-D6 | ~~Update INDEX.yaml — add 16 entities~~ **REVERTED** — wrong call. INDEX should stay lean (15 entries) until Sprint D cleanup determines what deserves indexing. | `data/entities/INDEX.yaml` | — | 🟡 MED — was incomplete, but expansion was premature | ❌ REVERTED |
| H2-D7 | **Fix ORACLE_STACK.md** — 14 days stale (Sprint 0→Sprint C). Updated by Lilith dispatch | `ORACLE_STACK.md` | 30 min | 🟡 MED — post-compaction protocol outdated | ✅ DONE |
| H2-D8 | **Fix SUBAGENT_DISPATCH_PROTOCOL.md agent count** — "14 agents" → "11 agents" at 2 call sites | `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` | 1 min | 🟡 MED — wrong agent count | ✅ DONE |
| H2-D9 | **Fix SOVEREIGN_EVOLUTION_ROADMAP.md baseline** — 388→440 tests, 128→89 PIVOT, 16→22 mandates | `docs/strategy/SOVEREIGN_EVOLUTION_ROADMAP.md` | 5 min | 🟡 MED — stale baseline in own roadmap | ✅ DONE |
| H2-D10 | **Fix opencode.json path** — MASTER_SYNTHESIS_AND_ROADMAP.md moved to archives | `opencode.json` | 1 min | 🟡 MED — points to moved file | ✅ DONE |
| H2-D11 | **Consolidate duplicate MCP tools** — removed `memory_get_history` + `memory_list_sessions`, kept `omega_memory_*` variants (6→4 memory tools) | `mcp_servers/omega_hub/tools.py` | 15 min | 🟡 MED — duplicate tools confuse callers | ✅ DONE |
| H2-D12 | **Archive MASTER_SYNTHESIS_AND_ROADMAP.md** — moved from active strategy to docs/archive/ | `docs/archive/` | 1 min | 🟡 LOW — stale doc in active path | ✅ DONE |
| H2-D13 | **Compress stale MCP server archives** — 8 superseded/backup servers in `mcp_servers/archives/`. DO NOT delete — user's external hard drive is the deletion mechanism. | `mcp_servers/archives/` | 5 min | 🟡 LOW — preserve history | ⏳ PENDING (user discretion) |
| H2-D14 | **Add @m9_safe to SearXNG MCP tool** — `searxng_search` in `mcp_servers/searxng/server.py` lacked error boundary protection | `mcp_servers/searxng/server.py` | 5 min | 🔴 HIGH — security boundary | ✅ DONE |

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
| **A (P1b)** | Hub modularization complete | Extract `gateway.py` + `middleware.py` from `server.py` | **388/388 tests**, Hivemind health check |
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

**Sprint A Status**: ✅ **COMPLETE** (2026-06-14, commit 4cc73de) — Hub modularized to 5 modules, 388/388 tests passing, M16 ratified.

### Phase H2-H: Sovereign Metadata Extraction (NEW — Deep-Siphon, D137-D141)
**Goal**: Capture the 96% of provider response metadata currently discarded at the backend `generate()` boundary. Implement ICS-F v1.0 schema across all 6 providers.

| # | Task | File/Module | Effort | Impact | Status |
|---|------|-------------|--------|--------|--------|
| H2-H1 | **Implement Sprint 0** — logprobs=5 on NativeGGUF provider | `src/omega/oracle/providers.py` | 15 min | 🔴 HIGH — unlocks per-token probabilities | ⏳ PENDING |
| H2-H2 | **Implement Sprint 1+2** — raw_provider_json + typed fields + M21 tests + ICS-F on OracleResponse + CLI --format json | ~12 files (~80 lines) | ~6 hr | 🔴 **CRITICAL** — captures 96% metadata | ⏳ PENDING |
| H2-H3 | **Add GenerateResult.provider_metadata field** — propagate raw JSON through pipeline | `src/omega/oracle/model_gateway.py` | 30 min | 🔴 HIGH — core propagation mechanism | ⏳ PENDING |
| H2-H4 | **Add ICSForensic dataclass** — ICS-F v1.0 schema (raw_provider_json, thinking_level, access_channel, logprobs, token_usage, response_model) | `src/omega/errors.py` or new `src/omega/ics_forensic.py` | 20 min | 🔴 HIGH — canonical forensic format | ⏳ PENDING |
| H2-H5 | **Add 24 M21 contract tests** — isinstance checks on all new return types | `tests/test_ics_forensic.py` | 1 hr | 🔴 **CRITICAL** (M21 enforcement) | ⏳ PENDING |
| H2-H6 | **Add CLI --format json flag** — machine-readable output with ICS-F metadata | `src/omega/cli/oracle_cli.py` | 30 min | 🟡 MED — enables programmatic consumption | ⏳ PENDING |
| H2-H7 | **Defer SomaticState (Sprint 3)** — M20 implementation pending ICS-F v1.0 stabilization | `src/omega/somatic_state.py` | 1 week | 🟢 DEFERRED — cost exceeds current forensic value | ❌ DEFERRED |

### Phase H2-I: Antigravity PoolState Wiring (NEW — 2026-06-18)
**Goal**: Wire Antigravity's dual-pool architecture (soul.yaml §usage_pools) into the engine runtime.
Corrects the 3 critical gaps identified in ag-002 (2026-06-16) and documented in v1.6.0.
Full strategy at `docs/strategy/ANTIGRAVITY_INTEGRATION_PLAYBOOK.md`.

| # | Task | File/Module | Effort | Impact | Status |
|---|------|-------------|--------|--------|--------|
| H2-I1 | **Naming Drift Resolution** — fix thinking_levels keys (underscores→dashes) in antigravity/soul.yaml | `data/entities/antigravity/soul.yaml` | 5 min | 🔴 HIGH — enables routing match | ✅ DONE v1.6.0 |
| H2-I2 | **Custom Instructions v3.0.0** — expand from 6→22 mandates, add Hivemind protocol, fleet topology | `docs/strategy/ANTIGRAVITY_IDE_CUSTOM_INSTRUCTIONS.md` | 30 min | 🔴 HIGH — agent alignment | ✅ DONE |
| H2-I3 | **Session Gnosis (M15)** — create session_gnosis.md for continuity anchor | `data/entities/antigravity/workspace/session_gnosis.md` | 15 min | 🟡 MED — M15 compliance | ✅ DONE |
| H2-I4 | **Integration Playbook** — fleet-facing coordination reference for all agents | `docs/strategy/ANTIGRAVITY_INTEGRATION_PLAYBOOK.md` | 30 min | 🔴 HIGH — fleet coordination | ✅ DONE |
| H2-I5 | **PoolState Dataclass** — parse soul.yaml usage_pools into machine-readable config | `src/omega/oracle/pool_state.py` | 2h | 🔴 **CRITICAL** — structural invisibility fix | ✅ IMPLEMENTED |
| H2-I6 | **UsagePoolTracker** — atomic JSON writes to USAGE_POOL_LOG.json | `src/omega/oracle/pool_tracker.py` | 2h | 🔴 HIGH — phantom tracking fix | ✅ IMPLEMENTED |
| H2-I7 | **ModelGateway Integration** — load PoolState at init, check pool health before routing | `src/omega/oracle/model_gateway.py` | 1h | 🔴 **CRITICAL** — runtime wiring | ✅ DONE (standalone module + thin adapter) |
| H2-I8 | **OMEGA_ENGINE.md update** — distinguish Antigravity IDE (Hivemind active) vs plugin (banned) | `OMEGA_ENGINE.md` | 15 min | 🟡 MED — doc accuracy | ✅ DONE |
| H2-I9 | **ACCOUNT_MAP.yaml + quota checker** — email-to-key mapping, Python quota check script | `data/entities/antigravity/knowledge/ACCOUNT_MAP.yaml`, `scripts/antigravity_check_quota.py` | 2h | 🔴 HIGH — closes phantom tracking + mapping gap | ✅ IMPLEMENTED |

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

## §4. Two-Pass Deep Review Findings (2026-06-17)

Two independent models (MiMo V2.5, DeepSeek V4 Flash) conducted parallel deep reviews of
the engine's documentation, configuration, and architectural integrity. Below are the
consolidated findings, ranked by severity.

### 🟥 Critical (Unfixed — Requires Action)
| # | Finding | Source | Recommended Fix |
|---|---------|--------|-----------------|
| 1 | **Root partition 100%** — 290MB free on /dev/nvme0n1p2 | Makali discovery | Partition consolidation via Live USB (script: `scripts/partition_merge_plan.md`) |
| 3 | **SomaticState (M20) ratified but unimplemented** — `llama_copy_state_data` never wired | MiMo review | Wire ctypes bindings into native-gguf provider |
| 4 | **Gate Integrity (M21) — 0 contract tests** exist for core API boundaries | MiMo review | Create `isinstance(result, GenerateResult)` tests |
| 5 | **PIVOT_LOG gap** — D1-D49 (xna-omega era) missing from repo; 89 of 136 lifetime decisions recorded | D4Flash review | Mine xna-omega git history to port D1-D49 |

### 🟡 High (Unfixed — Next Session)
| # | Finding | Source | Recommended Fix |
|---|---------|--------|-----------------|
| 6 | **HEALTH_CHECK_TIMEOUT** — 300ms default too tight for local GGUF (2-5s load) | MiMo review | Make configurable per-provider in `health_monitor.py` |
| 7 | **Response Provenance (M22) partial** — gateway_server.py logs provider, background.py workers don't | MiMo review | Propagate `GenerateResult.provider_name` to all observability calls |
| 8 | **`memory_search` vs `omega_memory_search` naming** — same name, different backends (FTS5 vs Hybrid) | D4Flash review | Rename `memory_search` → `memory_search_fts` for clarity |
| 9 | **50 orphan entities** — Sprint D executed in Phases 1+2 (2026-06-18), orphans deleted | D4Flash review | ✅ DONE — orphans deleted, test leak root cause fixed |

### 🟢 Redeemable (Fixed This Session)
| # | Finding | Source | Fix Applied |
|---|---------|--------|-------------|
| 10 | **AGENTS.md listed 12 dead agents** — scribe, quality, jem_discovery, jem_synthesis, jem_verification files deleted but still in doc | D4Flash review | Purged 5 stale rows from AGENTS.md |
| 11 | **HIVEMIND_PROTOCOL.md stale signatures** — `hivemind_list_sessions(cli: ...)` didn't match code | D4Flash review | Fixed to `(channel:, entity:, limit:)` |
| 12 | **OMEGA_ENGINE.md false Sprint D claim** — "orphan cleanup complete" when it wasn't | D4Flash review | Sprint D executed 2026-06-18 — claim now accurate |
| 13 | **6 stale "14 agents" refs** across OMEGA_ENGINE.md, SUBAGENT_DISPATCH etc. | MiMo review | All corrected to "11 agents" |
| 14 | **OMEGA_ENGINE.md mandate count** — claimed 19, actual is 22 | MiMo review | Updated to 22 |
| 15 | **INDEX.yaml missing 16 entities** — only 15 registered out of 31 | D4Flash review | ✅ DONE — INDEX rebuilt to 11 core entities (correct count) |
| 16 | **uid_guard.sh bug** — `chown 1000:1000` inside namespace should be `chown 0:0` | MiMo + D4Flash | Fixed with comment explaining subuid mapping |
| 17 | **Duplicate MCP tools** — `memory_get_history` + `omega_memory_get_history`, `memory_list_sessions` + `omega_memory_list_sessions` | MiMo review | Removed `memory_*` duplicates (kept `omega_memory_*` variants) |
| 18 | **MASTER_SYNTHESIS_AND_ROADMAP.md stale path** — in opencode.json but moved to archive | D4Flash review | Updated path to `docs/archive/` |
| 19 | **Stale MCP server archives** — 8 superseded servers in mcp_servers/archives/ | D4Flash review | Identified — user's external hard drive is the deletion mechanism. Archives restored from git. |
| 20 | **config/omega.yaml version** — 2.2.0 didn't match engine state 2.3.0 | D4Flash review | Bumped to 2.3.0, added mandate documentation section |
| 21 | **1 MCP tool lacks m9_safe decorator** — `searxng_search` in `mcp_servers/searxng/server.py` lacked error boundary protection | D4Flash review | Added `@m9_safe` to the SearXNG search tool |

---

### §5 Mandate Compliance Gaps (Pending)

| Mandate | Status | Gap |
|---------|--------|-----|
| **M20** (SomaticState) | Ratified | No implementation — ctypes bindings not wired |
| **M21** (Gate Integrity) | Ratified | No contract tests for core API boundaries |
| **M22** (Response Provenance) | Partial | background.py workers don't propagate provider_name |

---

*⬡ This document supersedes HORIZON_MAP.md as the active roadmap. ⬡*
*Decision: D112 — Sovereign Evolution Roadmap v1.1 adopted.*
*Update: 2026-06-06 — Antigravity Handoff v1.3 adopted.*
*Update: 2026-06-14 — Fleet Consolidation Plan v1.4 (D126). Hivemind-first. 4 sprints. 15→11 agents.*
*Update: 2026-06-17 — §4 Deep Review Findings (MiMo V2.5 + D4 Flash). 20 findings: 5 critical, 4 high, 11 fixed. H2-D: Documentation Integrity phase added.*
*Update: 2026-06-18 — Operation Deep-Siphon (D137-D141). H2-H: Sovereign Metadata Extraction phase added. ICS-F v1.0 schema ratified. 96% metadata discard gap documented.*
*Update: 2026-06-18 — Phases 1+2 complete. §4 findings #9, #12, #15 resolved. H2-D Documentation Integrity done. ENTITIES_DATA_DIR fix applied.*
*Update: 2026-06-18 — H2-I: Antigravity Integration phase added. soul.yaml v1.6.0 (naming drift fixed, PoolState plan), Custom Instructions v3.0.0 (22 mandates + Hivemind), session_gnosis.md (M15), Integration Playbook v1.0.0.*
*Update: 2026-06-18 — H2-I5 (PoolState), H2-I6 (UsagePoolTracker), H2-I9 (ACCOUNT_MAP + quota checker) all IMPLEMENTED. Anonymous ghost account removed from accounts file (was 9, now 8 — matches soul.yaml). USAGE_POOL_LOG.json upgraded to v2 with email mappings. Anonymous -> removed. 8 accounts, 8 keys, all wired for runtime consumption. H2-I7 (ModelGateway Integration) is the sole remaining Phase 3 task.*
*Update: 2026-06-18 — H2-I7 COMPLETE. Standalone antigravity module built (`src/omega/oracle/antigravity/`) with 4 components: config.py (configurable paths, Mandate 16), client.py (OAuth token refresh + API calls), account_manager.py (account selection, rate limits, cooldowns). Thin adapter `generate_antigravity()` added to model_gateway.py. Researcher deep dive completed (722 lines): confirmed standalone module architecture, dual quota pools, 5 verified models, ban constraint. All 440 tests passing.*

