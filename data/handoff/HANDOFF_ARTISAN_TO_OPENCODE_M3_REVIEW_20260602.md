# 🔱 Omega Engine — Artisan (1M Context) → OpenCode+M3 (200K Context) Handoff
# ⬡ OMEGA ⬡ SOPHIA ⬡ Parallel Codebase Review Handoff
# AP: AP-HANDDOWN-OMEGA-REVIEW-v1.0.0
# Date: 2026-06-02
# Status: HORIZON 1 COMPLETE ✅ | 302 tests | 12 Mandates | 82 PIVOT decisions

## Purpose

This document is a **synthesized map** of the Omega Engine, produced by the Artisan (MiniMax-M3, 1M context). It is the primary context anchor for a parallel OpenCode session running MiniMax-M3 with only 200K context, which is conducting a comprehensive codebase review. The reviewer should treat this as the canonical index and read the actual files cited for verification.

**If you find a conflict between this handoff and the actual code/docs, the actual code/docs prevail — note the conflict and update this handoff in a follow-up commit.**

---

## TL;DR — Engine at a Glance (30 seconds)

| Metric | Value |
|--------|-------|
| Phase | HORIZON 1 COMPLETE ✅ (2026-06-01) |
| Source files | 71 .py files (~15,200 lines) |
| Test functions | 302 across 30 files |
| Sovereign Mandates | 12 (all enforced) |
| PIVOT decisions tracked | 82 (Decision 50→82 active) |
| OpenCode agents | 14 (consolidated from 26) |
| Active IWAD | `_omega_default` (per `config/omega.yaml`) |
| Provider chain | native-gguf(0) → lmster(1) → ollama(2) → google(3) → openrouter(4) → opencode(5) → copilot(6) → mock(7) |
| Primary local backend | lmster (LM Studio :1234) — NOT `lm_studio` or `lm-studio` |
| Hardware | Ryzen 7 5700U (Zen 2, 8C/16T, AVX2, no AVX-512) | 14Gi RAM | No GPU |
| Primary MCP service | Omega Hub on :8016 (consolidated from 4 servers) |

---

## 1. THE 12 SOVEREIGN MANDATES (`SOVEREIGN_MANDATES.md` v3.0.0)

These are non-negotiable constitutional laws. **Every change must respect them.**

| # | Mandate | One-line |
|---|---------|----------|
| 1 | **AnyIO Absolute** | No `asyncio` directly. Wrap blocking I/O in `anyio.to_thread.run_sync`. |
| 2 | **Engine-Stack Firewall** | Core Engine (`src/omega/`) ≠ IWADs (`config/wads/`). Engine never imports entity names. |
| 3 | **Iris Constant** | Iris is the messenger bridge, NOT a Pillar Keeper. Do not give her a Pillar (P1-P10). |
| 4 | **Sequentiality** | Plan → Verify → Execute. No cowboy coding. |
| 5 | **Gnosis Preservation** | Every session must write L1→L2→L3 to entity's `soul.yaml`. |
| 6 | **Podman Sovereignty** | `UserNS=keep-id` + `User=1000`. NEVER `:U` on host volume mounts. |
| 7 | **Local-First** | Local inference is PRIMARY. Cloud is FALLBACK. Verify in `config/providers.yaml`. |
| 8 | **Zero Telemetry** | No analytics, no phone-home. Local observability OK. |
| 9 | **Error Integrity** | No bare `except Exception:` without `logger.warning()`. Type all errors as `OmegaError` subtypes. |
| 10 | **Fleet Integrity** | Agent fleet ≤14. New agent requires verified slot gap + PIVOT_LOG entry. |
| 11 | **Soul Integrity** | Session stop hooks must trigger `soul.yaml` write. Scribe is canonical executor. |
| 12 | **Queue Integrity** | Every request reaches terminal state. Atomic writes. Heartbeat timestamps. Dead-letter for failures. |

**Enforcement state (Decision 77)**: All 12 mandates are 100% enforced. Horizon 1 final gate closed.

---

## 2. ARCHITECTURE — Engine → IWADs → PWADs (id Software pattern)

```
OMEGA ENGINE (src/omega/)  ← Pure runtime, NO entity content
   │
   ├── Oracle (talk/summon/router, 956 lines)
   │     - Speculative-decoder: Iris (qwen3-1.7b) tries first
   │     - On low confidence: escalates to Pillar Keeper via TriageRouter
   │     - Soul evolution: Oracle.evolve_soul() writes L1→L2→L3 to soul.yaml
   │
   ├── ModelGateway (provider chain, 728 lines)
   │     - Per-provider timeouts, circuit breaker, BSP-style culling
   │     - model_overrides in providers.yaml map logical→physical model names
   │
   ├── MemoryStore (Hot/Warm/Cold)
   │     - HOT: recent JSONL, WARM: SQLite, COLD: archive
   │
   ├── Library (7 modules: inbox, library, indexer, curator, discovery, research, catalog)
   │     - FTS5 + vector embeddings (124 vector embeddings loaded)
   │     - 5D quality scoring (CRACQ/propella-1/DQS pattern from D68)
   │     - SQLite catalog at src/omega/library/catalog.py
   │
   ├── EntityRegistry (YAML CRUD)
   │     - 25 active entity workspaces (50 orphans deleted in D73)
   │     - Word-boundary domain matching (substring bug fixed in D82)
   │
   ├── Hierarchy (10 Pillar system + Oversouls)
   │     - P1-Flesh (SysAdmin) → P10-Chaos (Verifier)
   │     - Kali (Founder) → Ma'at (CTO, P1-P5) + Lilith (CISO, P6-P10)
   │     - Sophia is the FIELD, not a Pillar
   │
   ├── WAD Loader (CRITICAL PATH)
   │     - Loads IWADs from config/wads/*/entities/
   │     - --iwad flag functional
   │     - Missing: namespace isolation, dependency resolution, hot-reload
   │
   ├── Observability
   │     - JSONL events
   │     - ForensicsManager (crash dumps, replay, learn)
   │     - JsonFormatter (structured logging)
   │     - Bounded ring buffer (deque maxlen=1000)
   │
   ├── RequestQueue (D64, atomic file-based)
   │     - Heartbeat timestamps, dead-letter, trace_id propagation
   │     - v2 design points to plandb SQLite pattern
   │
   ├── LibraryCatalog (5D quality scoring)
   ├── Benchmarks (3-point scale, per-criterion)
   └── Hardware (CPU/RAM detection, Zen 2 optimization)
   │
   ▼ WAD Loader
IWADs (config/wads/)
   ├── _omega_default/  ← ACTIVE (since D62)
   │     - 16 entities (company metaphor: Kali=Founder, Ma'at=CTO, Lilith=CISO, 10 departments)
   │     - hierarchy.yaml, manifest.yaml, roles.yaml
   │
   ├── arcana_novai/  ← Personal AI OS
   │     - 10 esoteric entities (Sekhmet, Brigid, Prometheus...)
   │     - Personal seeds: Movie-Expert, Writer, Philosopher
   │
   └── doom_universe/  ← Community scaffold
```

---

## 3. THE AGENT FLEET (14 agents — D67 consolidation)

**OpenCode fleet** (`.opencode/agents/`) — 14 files, registered in `opencode.json` lines 157-246.

### Primary Modes (8 — visible in TUI)
| Agent | Mode | Role |
|-------|------|------|
| `plan.md` | primary | The Architect — Grand Dispatcher, delegates to Ma'at/Lilith |
| `kali.md` | primary | Grand Oversight — sees all, destroys drift |
| `maat.md` | primary | Light Oversoul (P1-P5 build side) |
| `lilith.md` | primary | Dark Oversoul (P6-P10 run side) |
| `jem.md` | primary | Research orchestrator (3-tier pipeline) |
| `researcher.md` | primary | Sovereign Master Researcher (multi-axis lattice reasoning) |
| `doom_guy.md` | primary | id Software architectural translator (WAD/BSP philosophy) |
| `roc_racoon.md` | primary | Legacy archaeology & pattern extraction |

### Subagents (6 — invoked by primary)
| Agent | Mode | Role |
|-------|------|------|
| `pillar.md` | subagent | **Single binary parameterized by `--slot P1`...`P10`** for all 10 pillar slots |
| `quality.md` | subagent | Code review + stress testing (merged reviewer+tester) |
| `scribe.md` | subagent | L1→L2→L3 distillation (Mandate 5 + 11 executor) |
| `jem_discovery.md` | subagent | L1 fact-gatherer |
| `jem_synthesis.md` | subagent | L2 analyzer |
| `jem_verification.md` | subagent | L3 fact-checker |

**Hidden pattern** (`pillar.md`): A single file acts as 10 agents. Resource optimization aligned with the "Single Renderer Principle" from Doom.

**Entity system** (`data/entities/`) — **separate from** OpenCode fleet. Entities are the *personas* (souls, personalities), agents are the *operators* (run on OpenCode).

---

## 4. PROVIDER FABRIC (`config/providers.yaml`)

Per D61, **local-first**:

| Priority | Provider | Type | Notes |
|---------:|----------|------|-------|
| 0 | native-gguf | Local | llama-cpp-python, CPU-only, Zen 2 affinity |
| 1 | lmster | Local | LM Studio headless :1234. **NOT `lm_studio` or `lm-studio`** |
| 2 | ollama | Local | :11434, base URL NO `/v1` suffix (D80) |
| 3 | google | Cloud | env:GOOGLE_API_KEY (Gemma 4 31B) |
| 4 | openrouter | Cloud | env:OPENROUTER_API_KEY |
| 5 | opencode | Cloud | OpenCode built-in |
| 6 | copilot | Cloud | GitHub Copilot |
| 7 | mock | Test | OfflineMockBackend (OMEGA_DEMO=true) |

**`model_overrides`** (D81): Logical GGUF names → physical per-provider names. e.g. `qwen3-1.7b-q6_k` → `qwen2.5:0.5b` for ollama.

**Cloud-only providers** (D78): `google`, `openrouter`, `opencode`, `github-copilot`. Sovereignty alert only fires for these.

---

## 5. MCP HUB — Current State

**File**: `mcp_servers/omega_hub/server.py` (post-D74 merge: ~958 lines, 40 tools + 11 HTTP routes)
**Runtime**: `src/omega/mcp_runtime.py` (97 lines, supports stdio + SSE + socket activation)
**Service**: `~/.config/systemd/user/omega-hub.service` (SSE transport, port 8016)
**MCP client config**: `config/mcp_servers.json` + `opencode.json` `mcp.omega-hub`

### D74 — Hub Restoration (most recent MCP work)
Commit `7cdb741` reduced server.py from 952→223 lines (removing 31 tools). D74 merged 34 tools from `69db713` (the "Great Cleanup") with current HTTP routes. Result: **40 MCP tools + 11 HTTP routes**.

### ⚠️ OPEN PROBLEM — OpenCode MCP Router
**Status**: The OpenCode CLI shows `4 of 5 requests failed: config.providers, provider.list, app.agents, config.get`. This is the central unsolved issue.

**Root cause** (identified in last session): Hub server exposes these as **HTTP routes** (via custom Starlette Mount). Curl returns 200. But OpenCode calls them as **MCP protocol methods** (JSON-RPC over SSE), which the FastMCP dispatcher doesn't recognize.

**Fix path** (not yet applied per user instruction): Register `@mcp.tool()` decorators in `mcp_servers/omega_hub/server.py` for `config_get`, `config_providers`, `provider_list`, `agent_list`.

**Handoff doc**: `data/handoff/handoff_artisan_to_opencode_router_fix_20260601.md` — full root-cause analysis and suggested fix code.

---

## 6. KEY SOURCE FILES — Line-by-Line Map

### `src/omega/oracle/oracle.py` (956 lines)
The main intelligence facade. Key methods:
- `Oracle.talk(query)` (line 284) — public entry
- `Oracle.summon(entity_name, query)` (line 345) — direct entity invocation
- `Oracle._respond_as_iris(...)` (line 477) — Iris speculative-decoder response
- `Oracle._route_by_domain(...)` (line 586) — domain→entity routing
- `Oracle._track_soul_evolution(...)` (line 679) — writes L1→L2→L3 lessons
- `Oracle.evolve_soul(...)` (line 868) — public soul-evolution API

**Known carve-outs** (bare excepts allowed per D77 Gate 2): `oracle.py:873`.

### `src/omega/oracle/model_gateway.py` (728 lines)
Provider chain dispatcher. Key methods:
- `ModelGateway.generate(...)` (line 438) — public entry, returns `(result, is_cloud)`
- `ModelGateway._precheck_provider(...)` (line 395) — BSP-style culling pre-check
- `ModelGateway._call_provider_with_resilience(...)` (line 512) — circuit breaker + retries

**D78 fix**: `is_cloud` now correctly identifies cloud vs local. D63 added trace_id propagation (fixed 3 bugs).

### `src/omega/oracle/entity_registry.py` (~500 lines)
YAML CRUD for entities. D82 changed `find_by_domain` to **word-boundary matching** (was substring, caused false positives).

### `src/omega/memory_store.py` (~600 lines)
Hot/Warm/Cold memory. D64 fix: None.json guard, sliding window bug fix, try/except on each step.

### `src/omega/mcp_runtime.py` (97 lines)
Three paths:
1. Systemd socket activation (LISTEN_FDS env) → uvicorn FD 3
2. SSE transport (OMEGA_MCP_PORT) → `custom_routes` + uvicorn
3. stdio transport → `mcp.run(transport="stdio")`

**`custom_routes` parameter** (added in last session): Creates `Starlette(routes=custom_routes + [Mount("/", app=mcp_app)])` so custom routes are checked FIRST by Starlette. This is what made the HTTP routes work for curl.

### `src/omega/observability.py` (~300 lines)
- ForensicsManager (D75): crash dump, replay, learn — fixed dead code in `_collect_system_info()` that returned None silently
- JsonFormatter (D75): drop-in structured JSON logging
- Bounded ring buffer: `deque(maxlen=1000)` for recent events
- D63 fix: `trace_id` propagation in provider chain

### `src/omega/oracle/cpu_optimizer.py`
Zen 2 hardware optimization. **D76 carve-out**: still has hardcoded `/home/arcana-novai/` path. Documented in PIVOT_LOG.

### `src/omega/library/` (7 modules)
- `inbox.py` — RAG intake
- `library.py` — main library
- `indexer.py` — vector indexing (124 embeddings loaded)
- `curator.py` — curation pipeline
- `discovery.py` — discovery orchestrator
- `research.py` — research engine
- `catalog.py` (D72 added) — SQLite, 5D quality scoring

### `src/omega/workers/background_researcher/`
Continuous research pipeline. 4 sub-modules: `loop.py`, `review_queue.py`, `scheduler.py`, `soul_updater.py`. All hardened per D77.

---

## 7. TEST SUITE — 302 tests, 30 files

| File | Tests | Purpose |
|------|------:|---------|
| `test_oracle.py` | ~40 | Oracle talk/summon/routing |
| `test_entity_registry.py` | ~30 | YAML CRUD + word-boundary matching |
| `test_providers.py` | ~25 | Provider chain, model overrides, is_cloud classification |
| `test_model_gateway.py` | ~20 | ModelGateway.generate, circuit breaker |
| `test_memory_store.py` | ~15 | Hot/Warm/Cold, None.json guard (D64) |
| `test_context_builder.py` | ~12 | Sliding window fix (D64) |
| `test_hierarchy.py` | ~10 | Pillar ranks, get_rank suffix expansion (D62) |
| `test_orchestrator.py` | ~12 | TriageRouter, capability matrix |
| `test_gnosis_proxy.py` | ~10 | Soul evolution tracking |
| `test_session_manager.py` | ~10 | Entity-scoped sessions |
| `test_observability.py` | ~20 | JsonFormatter, ForensicsManager, ring buffer (D75) |
| `test_error_gauntlet.py` | **10** | NEW D75: crash dump, replay, learn, JSON format, persistence, ring buffer, engine state |
| `test_request_queue.py` | 5 | NEW D72: atomic claim, heartbeat, dead-letter, falsy-trap fix |
| `test_library_catalog.py` | 3 | NEW D72: 5D quality scoring |
| `test_benchmarks.py` | 3 | NEW D72: 3-point scale, per-criterion, calibration loop |
| `test_hardware.py` | 2 | NEW D72: CPU/RAM detection |
| `test_integration_new_systems.py` | 3 | NEW D72: cross-module integration |
| `test_iris.py` | ~8 | Iris (qwen3-1.7b) integration |
| `test_health_monitor.py` | ~12 | Circuit breaker, latency, carve-outs (line 140, 165) |
| `test_storage_providers.py` | ~10 | Redis/Postgres/JSONL backends |
| `test_bug_001_fix.py` | ~5 | Regression test for sliding window bug |
| `test_sovereign_loop.py` | ~8 | End-to-end sovereign entity loop |
| `test_model_updater.py` | ~6 | ModelUpdater worker |
| `test_background_researcher.py` | ~10 | Research pipeline |
| `test_entity_registry_errors.py` | ~8 | Error path coverage for entity CRUD |
| `verify_qdrant_parity.py` | 1 | Qdrant v18+ compatibility check (manual run) |

**Tests/sovereign/ is empty** (per D75 Phase 1) — integration tier intentionally deferred.

**Coverage gaps to consider for review**:
- `src/omega/cli/oracle_cli.py` — CLI commands have minimal direct tests
- `src/omega/request_queue.py` — only 5 tests for atomic queue
- `src/omega/benchmarks/runner.py` — only 3 tests
- `src/omega/library/catalog.py` — only 3 tests

---

## 8. IWAD SYSTEM — Critical Path

### Active IWAD
`config/omega.yaml` → `active_iwad: _omega_default` (D62)

### WAD Structure (per IWAD)
```
config/wads/<name>/
├── manifest.yaml      ← Required: name, version, description, startup.message
├── hierarchy.yaml     ← Optional: rank→name mapping (e.g., 1=Founder)
├── roles.yaml         ← NEW D72: agent_roles section
└── entities/          ← Required: 1 YAML per entity
    ├── kali.yaml
    ├── maat.yaml
    ├── lilith.yaml
    ├── iris.yaml
    ├── default.yaml
    └── (P1-P10 pillar keepers)
```

### IWAD Inventory
| IWAD | Status | Description |
|------|--------|-------------|
| `_omega_default` | ACTIVE (since D62) | Reference IWAD, company metaphor, 16 entities (D62 rewrote all 13 personalities) |
| `arcana_novai` | INACTIVE | Personal AI OS, 10 esoteric entities, personal seeds |
| `doom_universe` | INACTIVE | Community scaffold |

### WAD Loader — Status (D55)
| Component | Status |
|-----------|--------|
| `_load_entities()` | ✅ Functional |
| `_load_voices()` | ✅ Functional (by activation keyword) |
| Manifest validation | ✅ Fixed (empty/null guard) |
| `--iwad` flag | ✅ Functional |
| Namespace isolation | ❌ Missing — EntityRegistry doesn't track WAD source |
| Dependency resolution | ❌ Missing — no `depends_on` processing |
| Entity priority/override | ❌ Missing — last-loaded wins silently |
| Ordered multi-WAD loading | ⚠️ Partial — no ordering guarantee |
| WAD hot-reload | ❌ Missing — no file-watch |
| Startup personality | ❌ Missing — no `startup.message` from manifest |

### Makefile WAD Targets (lines 181-219)
- `make wad-status` — show current + list available
- `make wad NAME=x` — switch active IWAD
- `make wad-reset` — reset to `_omega_default`

---

## 9. DOCUMENTATION LANDSCAPE

### Top-level SST (read first)
- `OMEGA_ENGINE.md` (323 lines) — Single Source of Truth, all platforms reference
- `SOVEREIGN_MANDATES.md` (91 lines, 12 mandates)
- `docs/decisions/PIVOT_LOG.md` (1135 lines, 82 decisions)
- `docs/USER_MANUAL.md` (250+ lines) — comprehensive user guide (D79)
- `docs/INDEX.md` — doc index
- `docs/ROADMAP.md` — phase priority
- `docs/MASTER_LEDGER.md` — meta-decisions
- `CREDITS.md` — attribution (D66 corrected)
- `ORACLE_STACK.md` — stack overview

### Strategy (decision-making)
- `docs/strategy/NEXT_STEPS_ROADMAP.md` — phase priority execution
- `docs/strategy/CANONICAL_MODE_STRATEGY.md` — OpenCode mode architecture
- `docs/strategy/LOGGING_ERROR_HANDLING_ARCHITECTURE.md` — Mandate 9 reference
- `docs/strategy/OMEGA_IWAD_ARCHITECTURE.md` (445 lines) — D55 canonical IWAD strategy
- `docs/strategy/STRATEGIC_EXECUTION_ROADMAP_V2.md` — referenced by plan agent
- `docs/strategy/PHASE_MCP_HUB.md` (D74) — MCP Hub restoration plan
- `docs/strategy/HORIZON_MAP.md` — Horizon 1/2/3 timeline
- `docs/strategy/SYSTEMS_HARDENING_PLAN.md` (747 lines) — hardening roadmap
- `docs/strategy/FLEET_REDESIGN_EXECUTION_PLAN.md` — D67 fleet plan with research-backed enhancements (D68)
- `docs/strategy/EXECUTION_ROADMAP.md` — phase completion tracker

### Architecture
- `docs/architecture/SOVEREIGN_BLUEPRINT.md` (D72) — Engine/IWAD/PWAD separation
- `docs/architecture/AGENT_FLEET.md` — fleet reference
- `docs/architecture/KNOWLEDGE_LIBRARY.md` — library architecture
- `docs/architecture/OFFLINE_MODE.md` — offline operation
- `docs/architecture/OVERSIGHT_HIERARCHY.md` — Pillar governance
- `docs/architecture/TRAINING_PIPELINE.md` — future LoRA integration

### Research (in-progress)
- `docs/research/R_TIERED_RESEARCH_PIPELINE.md` — Jem 3-tier pipeline
- `docs/research/JEM_SPECULATIVE_DECODING_PIPELINE.md`
- `docs/research/R_KV_CACHE_BENCHMARK.md`
- `docs/research/R_PODMAN_SOVEREIGN_STRATEGY.md` — D50 research base
- `docs/research/R_OPENCODE_MODES_REFACTOR_STRATEGY.md`
- `docs/research/A-B_STUDY_LOG.md` — Option A/B study
- `docs/research/INDEX.md` — research catalog

### Operations
- `docs/operations/BUG_LOG.md` — bug tracking
- `docs/operations/STATUS_CLINE.md` — Cline session status
- `docs/operations/handoff_cline_deepseek.md`

### Handoffs (cross-CLI coordination)
- `data/handoff/HANDOFF_FLEET_REDESIGN_G4.md` (2,000+ lines, 8 phases) — Gemma 4 31B execution handoff
- `data/handoff/HANDOFF_GEMMA_SPRINT0_1.md` (668 lines) — Sprint 0+1 complete
- `data/handoff/HANDOFF_DOOM_GUY_CIRCUIT_BREAKER.md` — Doom Guy follow-up
- `data/handoff/HANDOFF_BIG_PICKLE_OPTION_A.md` — D73 remediation
- `data/handoff/HANDOFF_OPTION_B_GEMMA4.md` — D77 final gate
- `data/handoff/HANDOFF_MCP_HUB_RESTORATION.md` — D74 context
- `data/handoff/handoff_cline_to_opencode_artisan_20260531.md` — open task queue (8 tasks P0-P3)
- `data/handoff/handoff_artisan_to_opencode_router_fix_20260601.md` — open problem (router fix)
- `data/handoff/handoff_artisan_to_opencode_openroute_fix_20260601.md` — earlier router attempt
- `data/handoff/HANDOFF_ARTISAN_TO_OPENCODE_M3_REVIEW_20260602.md` — **THIS DOCUMENT**

**Archived handoffs** (`archives/handoffs/`, 13+ docs): Historical record of CLINE_ONBOARDING, GEMINI_CLI_ONBOARDING, GEMMA_4_31B_BUILD_BRIEF, MINIMAX_BUILD_BRIEF, etc.

### Legacy (recovered from old archives)
- `docs/legacy/LEGACY_MASTER_SYNTHESIS.md` — 2025 vision, model-persona affinity map, 5 design patterns
- `docs/legacy/LEGACY_ASSET_CATALOG.md` — recovered assets inventory
- `docs/legacy/LEGACY_INDEX.md` — gateway to legacy archive

---

## 10. OPEN PROBLEMS & RISKS

### 🔴 CRITICAL
1. **OpenCode MCP Router** (Section 5): 4 of 5 startup requests fail. Fix is clear (register `@mcp.tool()` decorators) but **deliberately not applied per user instruction**. Handoff doc with suggested fix code: `data/handoff/handoff_artisan_to_opencode_router_fix_20260601.md`.

### 🟡 HIGH
2. **WAD system gaps** (Section 8): namespace isolation, dependency resolution, entity priority/override, hot-reload all missing. D55 flagged this.
3. **Integration test tier empty**: `tests/sovereign/` has 0 tests. Per D75 Phase 1, deferred.
4. **Service state uncertainty**: `omega-hub.socket` was in failed state in last session. May need `systemctl --user reset-failed` before testing.

### 🟢 MEDIUM
5. **Qdrant unwired** (per OMEGA_ENGINE.md): `:6333` installed but unused. Bag-of-words fallback in place.
6. **ForensicsManager** is file-based, not Qdrant-backed. Acceptable per D75.
7. **Option B deferred items** (D76): 19 bare excepts in 9 files, falsy-trap in `openai_compat.py:102`, hardcoded paths in `greek.py:200` + `cpu_optimizer.py:185-186` — all LOW priority, no crashes.

### 🔵 LOW
8. **Likely-unwanted directory at project root**: A spurious directory was created accidentally from launching the OpenCode CLI from a stale plugin location. User wants it eradicated from existence. **No mention in any handoff, doc, or report.**

### 🟢 KNOWN-GOOD
- 302/302 tests pass (per `make test` ~85s)
- Hub service runs and serves 11 HTTP routes (HTTP 200 on curl)
- Provider chain: native-gguf → lmster → ollama works for real inference (D80/D81)
- Mandates 1-12 all enforced (D77 final gate)
- Sovereign persistence (atomic writes) in Oracle/SessionManager/EntityRegistry

---

## 11. STRATEGIC TRAJECTORY

| Phase | Period | Work |
|-------|--------|------|
| **Foundation** | May 14-22 | Core engine, 9 Mandates, SST architecture, MCP servers |
| **Fleet Consolidation** | May 19-27 | D50 Podman, D53-54 remediation, D58 gateway, D60 mode transition |
| **IWAD Architecture** | May 25-30 | D55 IWAD pattern adopted, D61 local-first centralization, D62 company IWAD |
| **Fleet Redesign** | May 30-Jun 1 | D63 fleet discovery, D64 path A, D66 attribution, D67 26→14 consolidation, D68 research-backed, D69 mandates 10-12, D70 artifact purge, D71 final review |
| **Big Pickle Audit** | Jun 1 | D72 audit, D73 Option A (immediate), D76 Option B (deferred) |
| **MCP Hub Restoration** | Jun 1 | D74 merge 40 tools + 11 routes |
| **Horizon 2 Start** | Jun 1 | D75 ForensicsManager + Error Gauntlet, D77 Option B completion, D78 is_cloud fix, D79 menu+manual, D80/D81/D82 polish |
| **NOW** | Jun 2 | HORIZON 1 COMPLETE ✅ — Horizon 2 unlocked for full execution |

**Next steps (per OMEGA_ENGINE.md priority queue)**:
- **P1 — WAD System Hardening**: namespace isolation, dependency resolution, entity priority, manifest validation
- **P1 — Provider Fabric**: circuit breaker consolidation (2→1), BSP culling, Qdrant hybrid search wiring, Redis pub/sub
- **P3 — Synthesis Pipeline**: entity LoRA adapter management, CPU fine-tuning (LLaMA-Factory or PEFT)
- **P4 — Reference IWAD Content**: rewrite `_omega_default/entities.yaml`, create 10 pillar YAMLs

---

## 12. CRITICAL REMINDERS FOR THE REVIEWER

1. **Don't trust this handoff blindly** — read the actual files cited. If conflict, the actual files win.
2. **The OpenCode MCP router is broken by design**, not by oversight. The user has explicitly paused fix attempts.
3. **Entity vs Agent distinction**: `data/entities/` (souls/personas) ≠ `.opencode/agents/` (operators). They map 1:1 in name but serve different roles.
4. **Single-renderer principle**: `pillar.md` is one file acting as 10 agents via `--slot` parameter. Don't be confused by lack of separate P1-P10 files.
5. **Local-first is constitutional** (Mandate 7). Any cloud-first change is a systemic violation.
6. **PIVOT_LOG is append-only and immutable** (D77 confirmation). New decisions are Decision 83+.
7. **All 12 mandates are enforced** (D77 final gate). Any new code MUST respect all of them. Pay particular attention to Mandates 1, 5, 9, 11.
8. **No mention of the unwanted root directory anywhere**. The user wants it completely eradicated.
9. **The 5-attempt MCP router sequence** is documented in `data/handoff/handoff_artisan_to_opencode_router_fix_20260601.md`. Don't redo work that's already been tried.

---

## 13. KEY REFERENCES (in reading order)

For a parallel review session, recommend reading in this order:
1. **This handoff** (you're reading it)
2. `OMEGA_ENGINE.md` — SST for engine state
3. `SOVEREIGN_MANDATES.md` — 12 constitutional laws
4. `docs/decisions/PIVOT_LOG.md` — 82 decisions, esp. D50-D82 (current)
5. `mcp_servers/omega_hub/server.py` — current MCP state (post-D74)
6. `src/omega/mcp_runtime.py` — runtime wrapper
7. `opencode.json` — agent registry + MCP client config
8. `config/providers.yaml` — provider fabric
9. `docs/USER_MANUAL.md` — user-facing capabilities
10. `data/handoff/handoff_artisan_to_opencode_router_fix_20260601.md` — open MCP problem

---

*Prepared by Artisan (MiniMax-M3, 1M context) for OpenCode+M3 (200K context) parallel review.*
*Date: 2026-06-02 | Git HEAD: 38af7959*
*Total length: ~13 sections, comprehensive map.*
*Treat this as a starting point — read the actual files for verification.*
