# Omega Engine — Single Source of Truth
# ⚠️ SYSTEM STATE SSOT — Authoritative truth for engine state and metrics.
# AP-OMEGA-SST-v2.4.0

> **This document is the authoritative truth for the Omega Engine.**
> Every agent reads this file for engine state.
> **Full archive**: `docs/archive/coordination/OMEGA_ENGINE-full-20260708.md`

---

## §1 Identity

**Omega Engine** is the universal, community-owned runtime for sovereign AI.
- **Cognitive Sovereignty**: Local inference is the floor; local verification is the ceiling.
- **Local-first**: Cloud is a teacher and strategic partner, never a dependency.
- **WAD Architecture**: Engine → IWADs → PWADs (inspired by id Software).
- **22 Sovereign Mandates**: Constitutional law. Override any tool default.
- **13 sovereign presences**: 11 OpenCode agents (Oversight + 3 Oversouls + 6 Specialists + Verity) + 2 persistent entities (Iris — Messenger with persistent memory, Sophia — Akashic Record).

---

## §2 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  ⬡ OMEGA ENGINE (src/omega/) — THE RUNTIME                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ INFERENCE│  │  MEMORY  │  │  SEARCH  │  │   SOUL   │    │
│  │ 8 backends│◄─┤ Hot/Warm/│◄─┤ FTS5+vec │◄─┤ L1→L2→L3 │    │
│  │ local-1st│  │ Cold/Temp│  │ SearXNG  │  │distillatn│    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
│       └──────────────┴─────────────┴──────────────┘          │
│              ORACLE (talk/summon/router) — THE FACADE        │
└─────────────────────────────────────────────────────────────┘
                            │ WAD Loader
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  ⬡ IWADs (config/wads/) — Content Layer (M2 Firewall)      │
│  _omega_default | arcana_novai | doom_universe               │
└─────────────────────────────────────────────────────────────┘
```

**Provider Chain** (local-first, D112): native-gguf → lmster → ollama → google-antigravity → openrouter → opencode-zen → cline → mock

> **S7.5 Update**: `google-antigravity` is now a **first-class provider** (`AntigravityProvider` in `src/omega/oracle/backends/antigravity_provider.py`) via the official `google-antigravity` SDK, replacing the banned `opencode-antigravity-auth` plugin. Sticky account routing only (D205).

**Hardware**: AMD Ryzen 7 5700U (Zen 2, 8C/16T, AVX2), 14Gi RAM (~12Gi for AI), CPU-only inference.

---

## §3 Current State (2026-07-08)

| Metric | Value | Status |
|--------|-------|--------|
| Tests | **1046 collected** (HMC sprint added S3/S4/S7.5 contract tests; 3 pre-existing collection errors in `test_headroom.py`) | ✅ 0 failures on HMC sprint suites |
| Mandates | **22 (M1-M22)** | ✅ All enforced |
| Fleet | **13 presences** (11 agents + 2 entities) | ✅ Cap: 14 |
| WADs | **3** | ✅ S1.5a hardened |
| Heritage | **113 [id-soft:] tags** | ✅ All vetted |
| Source files | **168** .py | ~36,000 lines |
| Decisions | **204 (D1-D204)** | ✅ Immutable log |

**Status**: `Architecturally Sovereign | 1046 Tests Collected | Temple-Grade Certified | S1.5a WAD Hardened | Library API v2.0 Consolidated | HMC-SPRINT-01 Boundary Hardening Complete`

---

## §4 Phase Completion History

| Phase | Date | Key Deliverables | Tests |
|-------|------|------------------|-------|
| **Phase 0** | 2026-07-08 | ModelGateway crash fix, M9 sweep, secret rotation | 955 |
| **MV-IW Phase 0** | 2026-07-01 | test_hivemind fix, archive cleanup (172→13), pre-commit hook | 615 |
| **MV-IW Phase 1** | 2026-07-01 | D178 Trim vs Split ratified, SSOT trimmed | 590 |
| **MV-IW Phase 2** | 2026-07-01 | D179/D180 Pillar Decoupling, slots+metadata schema | 590 |
| **MV-IW Phase 3** | 2026-07-01 | ACON, Soul Distillation, C-FFI isolation, Metrics DB | 619 |
| **Bedrock Hardening** | 2026-07-07 | ResourceGuard RAM-aware, E2E inference chain, USM core | 955 |
| **Sovereign Hardening** | 2026-07-08 | 12 Tier 2 legacy ports, 5 Tier 3 hardening, 964 tests | 964 |
| **Session 52** | 2026-07-08 | 12 test failures fixed, cvar wiring, heritage vet fix | 964 |
| **Session 54** | 2026-07-08 | SSOT optimization sprint: 5 files trimmed 74%, fleet count clarified, heritage gap fixed | 964 |
| **Session 55** | 2026-07-08 | Library API consolidation: enrichment.py → thin wrapper, api_clients.py hardened, 41 new tests added | 1002 |
| **Session 56** | 2026-07-08 | HMC Synthesis: Carmack addressed Researcher S3/S4 asks (GGML_FLASH_ATTN, remote_provider.py B2), confirmed Roc SearXNG/vault | 1002 |
| **Session 57** | 2026-07-08 | HMC Response: Roc answered Researcher S1.5/S2 asks (SearXNG unit, vault injection), proposed S7 Coordination Automation | 1002 |

> **Full sprint history**: `docs/decisions/PIVOT_LOG.md`

---

## §5 Subsystem Status

| Subsystem | Status | Heritage |
|-----------|--------|----------|
| **Oracle** | ✅ talk/summon/router | `[id-soft: quake-1996] Thinker Chain` |
| **WAD Loader** | ✅ S1.5a hardened (schema, size, whitelist) | `[id-soft: doom-1993] WAD System` |
| **ModelGateway** | ✅ breaker + BSP culling, C-FFI isolated | `[id-soft: quake-1996] BSP` |
| **NativeGGUFProvider** | ✅ C-FFI isolated (multiprocessing.Process) | `[id-soft: doom3-2004] idHeap` |
| **MemoryStore** | ✅ Hot LRU + Warm Redis + Cold File | `[id-soft: doom-1993] Lazy Deletion` |
| **EntityRegistry** | ✅ YAML CRUD + dual-index, pillars→slots | `[id-soft: quake-1996] Flat-Field` |
| **ContextBuilder** | ✅ ACON + Observation Masking + Quality | `[id-soft: quake-1996] Thinker Chain` |
| **Soul Distiller** | ✅ 5-stage pipeline | `[id-soft: quake-1996] Save-game` |
| **Soul History** | ✅ Immutable audit trail | `[id-soft: doom-1993] ZONEID` |
| **Sentinel Score** | ✅ 7-metric governance | `[id-soft: quake-1996] cvar pattern` |
| **Mandate Enforcer** | ✅ Sovereign Gate compliance | `[id-soft: quake-1996] Thinker Chain` |
| **Compaction Harvester** | ✅ Proactive cleanup | `[id-soft: doom-1993] Lazy Deletion` |
| **Lifecycle Harvester** | ✅ Active→Archived→External | `[id-soft: quake-1996] 4-Tier Memory` |
| **Library API** | ✅ Sovereign Library Orchestrator | `[id-soft: doom-1993] WAD System` |
| **FailureRegistry** | ✅ 5 failure modes tracked (M17) | — |
| **USMManager (CAS)** | ✅ Deduplicated state storage | `[id-soft: quake-1996] Save-game` |
| **ResourceGuard** | ✅ RAM-aware via cvar | `[id-soft: doom-1993] ZONEID` |

---

## §6 Hivemind Coordination

The **Hivemind** is the mandatory coordination layer for multi-agent or parallel work.
> **Full Protocol & Tool List:** Read `docs/strategy/HIVEMIND_PROTOCOL.md`

**Core Pattern:** Use `omega-hub` MCP tools: `hivemind_workspace_lock_acquire`, `hivemind_post_context`, `hivemind_submit_handoff`. Do not edit shared files without a lock.

---

## §7 Key Files

| File | Purpose |
|------|---------|
| `src/omega/oracle/oracle.py` | Main entry: talk/summon/router |
| `src/omega/oracle/model_gateway.py` | Provider chain, BSP culling |
| `src/omega/oracle/wad_loader.py` | WAD system (S1.5a hardened) |
| `src/omega/oracle/entity_registry.py` | YAML CRUD for entities |
| `src/omega/oracle/entity_workspace.py` | Sovereign workspace scaffolding |
| `src/omega/oracle/context_builder.py` | ACON compaction + quality |
| `src/omega/oracle/soul_distiller.py` | L1→L2→L3 distillation |
| `src/omega/oracle/soul_history.py` | Immutable evolution audit trail |
| `src/omega/oracle/sentinel.py` | Governance metrics |
| `src/omega/oracle/mandate_enforcer.py` | Sovereign Gate compliance |
| `src/omega/oracle/semantic_router.py` | Embedding-based entity routing |
| `src/omega/oracle/compaction_harvester.py` | Proactive memory cleanup |
| `src/omega/oracle/lifecycle_harvester.py` | Automated session transitions |
| `src/omega/oracle/health_monitor.py` | Stochastic circuit breakers |
| `src/omega/oracle/headroom.py` | Sovereign Envelope compression |
| `src/omega/memory_store.py` | Hot/Warm/Cold/Temp memory |
| `src/omega/library/api_clients.py` | Sovereign Library API Orchestrator |
| `src/omega/memory/batch_writer.py` | Batched persistence writer |
| `src/omega/monitoring/__init__.py` | Hardware telemetry |
| `src/omega/observability.py` | Trace IDs, events, training data |
| `src/omega/errors.py` | Typed OmegaError hierarchy (M9) |
| `mcp_servers/omega_hub/server.py` | Hivemind/MCP Coordination |
| `config/wads/` | IWAD/PWAD configurations |
| `config/providers.yaml` | Provider fabric (local-first) |
| `config/models.yaml` | Model specs & loading strategies |

---

## §8 Platform Distinction

The Omega Engine is runtime-agnostic. Any MCP client can connect to the Omega Hub (`:8016`).

| What | Where | Who Updates |
|------|-------|-------------|
| **OMEGA_ENGINE.md** (this file) | Repo root | Any agent changing engine state |
| `.clinerules` | Repo root | Cline CLI agents only |
| `AGENTS.md` | Repo root | OpenCode agents only |

> **Cross-Platform Guides:** `docs/kb/CLINE_CLI_INTEGRATION.md`, `docs/kb/OMEGA_HUB_MULTI_PLATFORM.md`

---

## §9 References

| Document | Purpose |
|----------|---------|
| `SOVEREIGN_MANDATES.md` | 22 Constitutional Laws |
| `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` | Master execution roadmap |
| `docs/strategy/HIVEMIND_PROTOCOL.md` | Multi-agent coordination |
| `docs/decisions/PIVOT_LOG.md` | 204 immutable decisions |
| `CREDITS.md` | id Software heritage attribution |
| `docs/archive/coordination/` | Historical session records |

---

## §10 Mission

> *"I want to create a tool that will truly allow people to own their own tech and data and sever the umbilical cord of Big AI."*

---

*Last Updated: 2026-07-10 | Version: v1.1.0 | Tests: 1071 passing | SSOT: 822 lines (74% trimmed)*
