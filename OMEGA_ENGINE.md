# Omega Engine — Single Source of Truth
# ⚠️ SYSTEM STATE SSOT — Authoritative truth for engine state and metrics.
# AP-OMEGA-SST-v2.7.0

> **This document is the authoritative truth for the Omega Engine.**
> Every agent reads this file for engine state.
> **Full archive**: `docs/archive/coordination/OMEGA_ENGINE-full-20260708.md`

---

## §1 Identity

**Omega Engine** is the universal, community-owned runtime for sovereign AI.
- **Cognitive Sovereignty**: Local inference is the floor; local verification is the ceiling.
- **Local-first**: Cloud is a teacher and strategic partner, never a dependency.
- **WAD Architecture**: Engine → IWADs → PWADs (inspired by id Software).
- **Standalone Packages**: Core capabilities published as independent PyPI packages (`omega-sieve`, `omega-doc-reader`) for community use.
- **Universal Reflection Substrate**: ONE foundational engine with infinite customizable layers (WADs), each custom to how a user understands their own sovereign journey. The ANAi Stack (Tarot/Pillars/Ma'at) and the Torment Stack (Hive/Nameless One/Sigil) are *two expressions of the same architecture* — proving the WAD customization power. Every user gets their own cosmology; the engine provides the deathless continuity substrate.

---

## §2 Current State (2026-07-22)

| Metric | Value | Status | LAST_VERIFIED |
|--------|-------|--------|---------------|
| **Strategy SSOT** | **`docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` v5.2** + `STRATEGY_CORPUS_MAP.md` | ✅ Unified; fine-grained corpus preserved | 2026-07-22 |
| **Current phase** | **Phase C — Infrastructure Hardening** (C-0…C-9) | 🔴 Active | 2026-07-22 |
| Tests | **1,572 collected** · **50/50 core+contract+chaos+SoulStore pass** · 77/77 contract historically green | ✅ C-0 complete, C-10/C-2'/C-6'/C-1' verified | 2026-07-22 |
| Mandates | **25 (M1-M25)** | ✅ All enforced (v3.7.0) | 2026-07-19 |
| **Mandate Compliance** | **21/25 FULL (84%)** — 2 Partial, 2 Fail | ⚠️ M5, M11 remain (Soul distillation pipeline) | 2026-07-22 |
| Fleet | **12 agents (cap 14 per M10)** | ✅ Clean | 2026-07-22 |
| WADs | **4** (arcana_novai, torment, omega_youtube_research, omega_youtube_worker) | ✅ S1.5a hardened | 2026-07-13 |
| **Third-Party Registry** | **18/19 repos cloned** — P0: 4/4, P1: 5/5, P2: 6/6, P3: 1/4 | ✅ P0-P2 Complete | 2026-07-18 |
| Heritage | **121 [id-soft:] tags**, **55+ general sources** | ✅ All vetted | 2026-07-13 |
| Shared modules | **4** (`omega-vetala`, `omega-sieve`, `omega-doc-reader`, `omega-meditation`) | ✅ 3 on PyPI, meditation compatible | 2026-07-20 |
| **Foundation Stabilization Campaign** | **RATIFIED** — Gate Α passed, Phase Β complete, Gate Β passing | ✅ 0 active/pending handoffs | 2026-07-20 |
| **Memory ADR (ADR-001)** | **RATIFIED** — sqlite_policy.py SSOT, 4 PRAGMA profiles | ✅ Gate Γ criterion met | 2026-07-20 |
| **Antigravity OAuth** | **PARTIAL** — Plugin present; auth often **API-key only**; re-login may be required for Path B | 🟡 G-1b path | 2026-07-22 |
| **Gemma 4 31B free workhorse** | **DEAD for fat OpenCode** — free-tier input TPM **16k** since **2026-07-15** (was workhorse May–Jul) | 🚨 **G-1 P0** — needs billing/OAuth | 2026-07-22 |
| **WARP Proxy Pool** | **OPERATIONAL** — 3-node pool active (8081/8082/8083); SystemCallFilter + port-template bugs fixed & committed | ✅ **W-1 FIXED** | 2026-07-22 |
| **Circuit Breakers** | **1 canonical** (`HealthMonitor.AsyncCircuitBreaker`) + 6 deprecated clones | ✅ C-6' Unified, sliding-window mode added | 2026-07-22 |

### Active Deferred Items
| Item | Status | Details |
|------|--------|---------|
| Firecrawl MCP | ⏳ Needs Streamable HTTP migration | SSE on :8015 |
| Local inference ratio ≥80% | 🟡 Aspirational target | Gate configurable, default OFF |
| Session Namespace Isolation (D-290) | 🟡 Design complete | 5 preconditions, 5 critical fixes pending |
| MIAP Phase 0 (D-291) | 🟡 Planned | ~6 sessions: ReplayMode, Two-Log, IntentionValidator |
| MACP Alignment (D-292) | 🟡 Planned | Aligns with IETF draft-li-dmsc-macp-05 |
| Experience Repository (D-294) | 🟡 Planned | AgentRR L0→L1→L2 via Scribe |
| Headless Subagent Pool (D-303) | 🟡 Planned | 24 accounts (8 Grok + 8 Copilot + 8 Cline) |
| Antigravity Two-Track (D-304) | ✅ **W-1 FIXED**; V-1 complete | WARP pool operational; AGY multi-account after vault |
| **G-1 Workhorse continuity** | 🚨 **P0 ACTIVE** — needs billing/OAuth | Forensic + critical path docs 2026-07-22 |
| **W-1 WARP pool bring-up** | ✅ **FIXED** — bugs committed, re-run fix script to apply | SystemCallFilter + port-template fixes |
| Hive Evolution (D-305) | 🟡 Architecture designed | Hivemind → Hive, 5 layers, 7 sprints |
| Arch Soul Integration (D-306) | 🟡 Design complete | Torment: Nameless One, companions, factions |
| Torment WAD (D-307) | 🟡 Scaffold defined | Awaiting Researcher Phase 1-4 |
| **D-308 Ubuntu 25.10** | 🚨 **P0 GATE** — Kernel 6.17, no free-threaded Python, AppArmor breaks rootless Podman | 13 actionable changes before Phase 2 |

### Recent Milestones (Completed)
D-281 Substrate Repair ✅ | D-282 sqlite-vec Strike 10 ✅ | D-283 Mnemosyne ✅ | MIAP merged ✅ | HMC Quad-Forge ✅ | D-298 Decision Workspace ✅ | D-300 Omega-Meditation ✅ | D-301 MaKaLi Council ✅ | D-302 CPR ✅ | **MaKaLi Apex Mind deployed (Sophia replaced)** ✅ | All Phase 5 ratified items ✅ | **C-10 Admission Control** ✅ | **C-2' RAM Truth** ✅ | **C-4a MCP Audit** ✅ | **C-5 MaKaLi Routing** ✅ | **C-6' Breaker Unification** ✅ | **C-1' SoulStore** ✅
*(For full details see `scripts/codex/ENGINE_CONDENSED.md` §5)*

---

## §3 Core Subsystems

| Subsystem | Module | Status | Description |
|-----------|--------|--------|-------------|
| **Oracle** | `src/omega/oracle/` | ✅ Operational | Intent detection, entity routing, Iris speculative decode |
| **Entity Registry** | `src/omega/oracle/entity_registry.py` | ✅ Operational | YAML-backed entity CRUD, auto-scaffolds sovereign workspaces |
| **Model Gateway** | `src/omega/oracle/model_gateway.py` | ✅ Operational | 8-backend provider fabric (native-gguf → lmster → Ollama → Google → OpenRouter → OpenCode → Copilot → Mock). P3 fixed graceful fallback + path/spec resolution |
| **Memory Store** | `src/omega/memory_store.py` | ✅ Operational | Hot/Warm/Cold/Temp tiers, hybrid FTS5+vector search |
| **Vector Store** | `src/omega/memory/sqlite_vec_adapter.py` | ✅ Strike 10 COMPLETE | `IVectorStoreAdapter` impl: sqlite-vec (FTS5 + vec0 + SQL edges). PRAGMA SSOT converged: cache_size 32MB, wal_autocheckpoint 500 |
| **Config Resolver** | `src/omega/governance/config_resolver.py` | ✅ Phase II COMPLETE | Pure Path constants, lazy `get_active_iwad()`, single source of truth for all WAD paths |
| **Hybrid Search** | `src/omega/memory/hybrid_search.py` | ✅ D-283 Phase 1 COMPLETE | RRF k=60 fusion of FTS5 + vector results. 20 contract tests + 8 RRF math vectors |
| **Recall Store** | `src/omega/memory/recall.py` | 🟡 D-283 Phase 2 DESIGN COMPLETE | Quality-weighted warm memory tier with power-law decay. 27/29 tests pass |
| **MIAP** | `src/omega/coordination/miap.py` | ✅ MERGED | Multi-Instance Agent Protocol for context collision prevention. 13 tests |
| **Soul Utils** | `src/omega/soul_utils.py` | ✅ Phase I COMPLETE | Multi-path soul context extractor for 31 entities |
| **WAD Loader** | `src/omega/oracle/wad_loader.py` | ✅ Operational | V2 schema with heritage fields. Sovereign WAD Protocol (SWP) pending |
| **Ingestion Pipeline** | `src/omega/ingestion/` | ✅ Operational | T1→T2→T3 tiered extraction, TriangulationVerifier, CAS |
| **Sovereign Sieve (Standalone)** | `packages/omega-sieve/` | ✅ v0.1.0 | `pip install omega-sieve` — T1(Trafilatura)→T2(Surgical)→T3(Crawl4AI) |
| **Document Reader (Standalone)** | `scripts/universal_doc_reader.py` | ✅ v1.0.0 | Reads .docx, .pdf, .odt, .rtf, .html, .md, .txt, .json, .yaml |
| **Observability** | `src/omega/observability.py` | ✅ Operational | Trace IDs, event logging, fine-tuning dataset collection |
| **Hivemind** | `mcp_servers/omega_hub/` | ✅ Operational | 6 MCP tools for cross-agent coordination, workspace locks, live feeds |
| **Hive (NEW)** | `src/omega/hive/` | 🟡 Design Complete | 5-layer collective consciousness: Sensorium, Thought Transmission, Neural Synchrony, Territorial Instinct, Incarnation Engine. Hivemind API compatible. |
| **MaKaLi Apex Mind (NEW)** | `config/wads/_omega_default/entities.yaml` | ✅ Deployed | Mastermind agent — deep research, genius blueprinting, high-level strategy, philosophical deep dives. Replaces Sophia (Akashic Record) in default WAD. NOT a builder — directs ground troops (Kali, Lilith, Maat, Pillars, Carmack). |
| **Arch Soul (NEW)** | `data/entities/arch/` | 🟡 Design Complete | User's sovereign journey externalized: 24 entity facets = Nameless One incarnations, Mandates = regret-prevention physics, Qliphoth = Fortress of Regrets, Death/Rebirth = session lifecycle hooks |
| **CLI** | `src/omega/cli/oracle_cli.py` | ✅ Operational | Typer CLI (talk, summon, list-entities, add-entity, entity-info, backends, version) |
| **Resource Guard** | `src/omega/oracle/resource_guard.py` | ✅ Operational | AnyIO Semaphore(1) — one model at a time (OOM protection) |
| **Admission Controller** | `src/omega/oracle/admission_controller.py` | ✅ C-10 COMPLETE | LocalInferenceAdmission singleton, Semaphore(1) + OOMProtector integration, fail-fast to cloud |
| **OOM Protector** | `src/omega/oracle/oom_protector.py` | ✅ C-2' COMPLETE | Three-signal fusion (PSI + MemAvailable + cgroup), 5-tier decision logic |
| **Health Monitor** | `src/omega/oracle/health_monitor.py` | ✅ C-6' COMPLETE | Canonical circuit breaker factory (get_breaker), CUSUM + sliding-window modes, 5-state FSM |
| **SoulStore** | `src/omega/soul_store.py` | ✅ C-1' COMPLETE | Atomic file writer: tempfile → write → fsync → os.replace → fsync parent. 4-layer guarantee: AtomicVisibility, CrashDurability, WriterExclusion (flock), IntegrityDetection (.bak rotation) |
| **CPU Optimizer** | `src/omega/oracle/cpu_optimizer.py` | ✅ Operational | Zen 2 compilation flags, KV cache sizing, speculative decode tuning |

---

## §4 Key Files (Source of Truth)

| File | Purpose |
|------|---------|
| `OMEGA_ENGINE.md` (this file) | **System state SSOT** — metrics & subsystems |
| `SOVEREIGN_MANDATES.md` | 25 Constitutional Laws (M1–M25) |
| **`docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md`** | **Strategy & roadmap SSOT (v5.1 Unified)** |
| `docs/strategy/STRATEGY_CORPUS_MAP.md` | Fine-grained agent strategy preservation map |
| `docs/strategy/FLEET_TEAM_PLAYBOOK.md` | Fleet teamwork playbook (how agents coordinate) |
| `docs/strategy/STRATEGY_INDEX.md` | Doc hierarchy (Layer 0–4) |
| `docs/strategy/LIVING_RESEARCH_OS_SPEC_20260721.md` | Phase D detail (amended by Ark §3.2) |
| `docs/strategy/HIVEMIND_PROTOCOL.md` | Multi-agent coordination |
| `AGENTS.md` | OpenCode agent how-to |
| `docs/decisions/PIVOT_LOG.md` | Immutable decisions index |
| `CREDITS.md` | id Software heritage attribution |
| `data/coordination/SESSION_ANCHOR.md` | Session recovery |
| `.opencode/anchored-summary.md` | Post-compaction recovery state |
| `.opencode/agents/makali.md` | MaKaLi Apex Mind agent |
| `.opencode/agents/grok_cli.md` | Grok CLI Consulting Cloud Mind |
| `docs/archive/strategy/2026-07-21/` | Archived roadmaps + Ark v4.4 body |
| `docs/strategy/CANONICAL_ROADMAP_20260721.md` | Superseded tactical draft (trail only) |

---

## §5 Platform Distinction

The Omega Engine is runtime-agnostic. Any MCP client can connect to the Omega Hub (`:8016`).

| What | Where | Who Updates |
|------|-------|-------------|
| **OMEGA_ENGINE.md** (this file) | Repo root | Any agent changing engine state |
| `.clinerules` | Repo root | Cline CLI agents only |
| `AGENTS.md` | Repo root | OpenCode agents only |

> **Cross-Platform Guides:** `docs/kb/CLINE_CLI_INTEGRATION.md`, `docs/kb/OMEGA_HUB_MULTI_PLATFORM.md`

---

## §6 References

| Document | Purpose |
|----------|---------|
| `SOVEREIGN_MANDATES.md` | 25 Constitutional Laws |
| `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` | **Strategy SSOT v5.1** |
| `docs/strategy/STRATEGY_CORPUS_MAP.md` | Fine-grained preservation map |
| `docs/strategy/STRATEGY_INDEX.md` | Documentation hierarchy |
| `docs/strategy/HIVEMIND_PROTOCOL.md` | Multi-agent coordination |
| `docs/decisions/PIVOT_LOG.md` | Decision history |
| `CREDITS.md` | id Software heritage |
| `docs/archive/strategy/2026-07-21/` | Archived strategy corpus |

---

## §7 Mission

> *"I want to create a tool that will truly allow people to own their own tech and data and sever the umbilical cord of Big AI."*

---

*Last Updated: 2026-07-22 | Version: v1.8.0 | Strategy SSOT: SOVEREIGN_ARK_BLUEPRINT v5.1 + STRATEGY_CORPUS_MAP | Phase C active (C-0/C-1'/C-2'/C-4a/C-5/C-6' complete) | Tests: 50/50 core+contract+chaos+SoulStore green | Mandate compliance: 84% | Fine-grained agent strategy preserved | Antigravity OAuth fixed | Circuit breakers unified | SoulStore atomic writer deployed*