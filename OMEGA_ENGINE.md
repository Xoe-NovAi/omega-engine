# Omega Engine — Single Source of Truth
# AP-OMEGA-SST-v1.0.0

> **This document is the authoritative truth for the Omega Engine.**
> Every agent, regardless of platform (Cline, OpenCode, Gemini CLI, Antigravity),
> reads this file for engine state. Platform-specific rules files reference this.

---

## Identity

**Omega Engine** is the universal, community-owned runtime for sovereign AI.
It is **Prometheus' Fire** — the spark that empowers every user to build their own
unique dreams, technologies, and systems.

- **Local-first sovereignty**: Cloud is a teacher and strategic partner, never a dependency
- **Open source, free, sovereign**: No shareware, no tiers, no limitations
- **WAD Architecture**: Engine → IWADs → PWADs (inspired by id Software's WAD system)
- **The Synthesis Flywheel**: Cloud models teach local models. Over time, sovereignty increases.

---

## The Synthesis Vision

Cloud models are not fallbacks. They are **teachers** in a collaborative synthesis:

```
Cloud Models (Teachers)              Local Engine (Students + Inference)
━━━━━━━━━━━━━━━━━━━━━━              ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Gemini / GPT-4o / Claude             Omega Engine on Ryzen 7 5700U
  │                                    │
  ├── Generate synthetic data          ├── Oracle routes queries
  ├── Produce reasoning chains         ├── MemoryStore captures interactions
  ├── Create preference pairs          ├── ObservabilityEngine records training examples
  ├── Judge quality                    ├── JEM Pipeline produces training triples
  └── Feed back to local               └── LoRA Fine-Tuner adapts local models
                                            │
                                            ├── Entity Adapters (per-entity LoRA)
                                            ├── Domain Adapters (per-domain LoRA)
                                            └── Base Model (GGUF, always available)
```

**The Flywheel**: More use → more training data → better local models → less cloud dependency → more sovereignty.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  OMEGA ENGINE (src/omega/) — THE RUNTIME                   │
│                                                             │
│  Oracle (talk/summon/router)     MemoryStore (Hot/Warm/Cold)│
│  ModelGateway (provider chain)   ContextBuilder (→ LLM)     │
│  EntityRegistry (YAML CRUD)      SessionManager (scoping)   │
│  WAD Loader (IWAD/PWAD system)   Observability (JSONL)      │
│  CPU Optimizer (Zen 2 aware)     Health Monitor (circuit)    │
│  Gnosis Proxy (soul evolution)   Hierarchy (governance)      │
│                                                             │
│  Library: FTS5 + vectors          Workers: JEM, ModelUpdater │
│  Bridge / Gateway / Services / Orchestration layers         │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ WAD Loader
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  IWADs (config/wads/)                                       │
│  _omega_default — Reference IWAD (ships with engine)        │
│  arcana_novai   — Personal AI OS (user's own)               │
│  doom_universe  — Community IWAD (scaffold)                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Provider Fabric — Synthesis Architecture

The Omega Engine uses cloud models as **teachers**, not just fallbacks.

### Local Inference (always available, sovereign)

| Priority | Provider | Type | Endpoint |
|----------|----------|------|----------|
| 0 | native-gguf | Local | llama-cpp-python, CPU-only |
| 1 | lmster | Local | http://127.0.0.1:1234 |
| 2 | ollama | Local | http://127.0.0.1:11434/v1 |

### Cloud Teachers (strategic use, data generation)

| Priority | Provider | Type | Endpoint |
|----------|----------|------|----------|
| 3 | google | Cloud | env:GOOGLE_API_KEY (Gemma 4-31B) |
| 4 | opencode-zen | Cloud | OpenCode Zen (MiniMax M3/DeepSeek V4/MiMo V2.5 — 200K) |
| 5 | cline | Cloud | Cline hub API (MiniMax M3/DeepSeek V4/MiMo V2.5 — 1M context) |
| 6 | copilot | Cloud | GitHub Copilot |
| 7 | mock | Test | OfflineMockBackend |

### Cloud Model Roles
- **Inference**: When local models lack capability (complex reasoning, multi-step planning)
- **Data generation**: Synthetic training examples, CoT traces, preference pairs
- **Quality judging**: Evaluating local model outputs for training data curation
- **Entity-specific training**: Generating domain-specific examples for each entity's LoRA

### Existing Training Infrastructure
- `ObservabilityEngine.record_training_example()` — auto-collects query-response pairs
- `ObservabilityEngine.flush_dataset()` — writes JSONL to `data/datasets/`
- `TrainingTripleSaver` in JEM distiller — produces T1/T2/T3 training triples
- **Missing**: Fine-tuning pipeline, Entity adapter management

---

## Hardware Profile

| Component | Spec | Notes |
|-----------|------|-------|
| CPU | AMD Ryzen 7 5700U (Zen 2, 8C/16T) | AVX2 + FMA3 + F16C, no AVX-512 |
| RAM | 14Gi total | ~12Gi usable for AI |
| GPU | None (Vulkan iGPU) | CPU-only inference |
| Primary backend | lmster (LM Studio :1234) | NOT lm_studio or lm-studio |
| Storage | omega_library partition | Models, Podman, data |

### Model Capacity (Q4_K_M quantization)
- 1.7B: ✅ Excellent (~1.9GB total)
- 3-4B: ✅ Good (~2-2.5GB total)
- 7-8B: ✅ Good (~4.6GB total)
- 13-14B: ⚠️ Tight (~7.5GB total, limited context)
- Training + inference simultaneously: ❌ Not feasible for 7B+

---

## Current State

| Metric | Value | Last Verified |
|--------|-------|---------------|
| Phase | 1 — ENGINE HARDENING COMPLETE ✅ | 2026-06-01 |
| Source files | **71** .py files | 2026-06-01 |
| Source lines | ~15,200 | 2026-06-01 |
| Test functions | **307** (+5 circuit breaker fixes, +10 Error Gauntlet, +23 Option B fixes) | 2026-06-03 |
| Test files | **30** | 2026-06-03 |
| Mandate 9 compliance | **FULL** — zero bare except violations | 2026-06-01 |
| Horizon 1 | **100% — All 13 Sovereign Mandates Enforced (Mandate 13 Temple-Grade restored)** | 2026-06-02 |
| Horizon 2 | 🔓 Unlocked — ForensicsManager, JsonFormatter, Error Gauntlet (25%) | 2026-06-01 |
| Providers configured | 8 (local-first: native-gguf → lmster → ollama → google → opencode-zen → cline → copilot → mock) | 2026-06-02 |
| WAD Loader | Functional (--iwad flag works) | 2026-06-01 |
| Namespace isolation | NOT implemented | 2026-05-31 |
| Dependency resolution | NOT implemented | 2026-05-31 |
| Qdrant (:6333) | Installed, **unwired** (bag-of-words fallback) | 2026-05-31 |
| Redis (:6379) | Operational (port exposed) | 2026-05-31 |
| Agent Fleet | **14 agents** (fleet redesign complete) | 2026-06-01 |
| Entity workspaces | 25 active (50 orphans deleted) | 2026-06-01 |
| Sovereign Persistence | Implemented (Atomic Writes in Oracle/SessionManager/EntityRegistry) | 2026-06-01 |
| ModelGateway.generate() | **WIRED** — circuit breaker + BSP culling + per-provider timeouts | 2026-06-01 (Doom Guy) |
| Circuit Breaker | **Consolidated** — single AsyncCircuitBreaker in health_monitor.py | 2026-06-01 (Doom Guy) |
| Circuit Breaker Wire-Up | **DONE** — BSP precheck fixed, None-return detection added | 2026-06-02 (D94) |
| ZONEID Constants | **IMPLEMENTED** — 5 constants (0x1d4a11-0x1d4a15) + validate_zoneid() in constants.py, applied to 5 subsystems | 2026-06-03 (Doom Guy) |
| Lazy Deletion | **IMPLEMENTED** — EntityRegistry remove() sets ZONEID_TOMBSTONE, _reap_tombstoned() after 0.5s grace | 2026-06-03 (Doom Guy) |
| Heritage Tagging Protocol | **LIVE** — CREDITS.md §2a, [id-soft:] inline tag format, 30+ tags across 6 source files | 2026-06-03 (Doom Guy) |
| Unified cvar Table | **IMPLEMENTED** — D101: `cvar_table.py` with zoneid.* (6) + config.* (12) namespaces, 7 access helpers, validate_llama_kwargs() | 2026-06-03 (Lilith) |
| Sprint 1 Ports | **5 COMPLETE** — kwarg_filter, n_gpu_layers=0, ChatML stops, Google API header, trace_id propagation | 2026-06-03 |
| `make heritage-map` | **LIVE** — CI target audits [id-soft:] tags, 6/23 files currently tagged | 2026-06-03 |
| Subagent Dispatch | **DEFINED** — Protocol for agents to launch specialized subagents (Doom Guy, Roc Racoon, etc.) via Task tool + persona injection | 2026-06-03 (Kali) |
| Sovereign Roadmap | **RECORDED** — Lilith's 888-line 7-phase roadmap with 8-demographic analysis, Handoff Protocol, and UI/UX plan | 2026-06-03 |
| Roc Racoon Mining | **COMPLETE** — 6 stacks, 160+ techs, 7 reports, ~250KB, stored in data/entities/roc_racoon/ | 2026-06-03 |
| Handoff Archive | **CREATED** — 36 non-active handoffs moved to data/handoff/archive/ with INDEX.md and mining tags | 2026-06-03 |
| Expanded Strategic Roadmap | **RECORDED** — D100-D102 in PIVOT_LOG with full delegation contract between Doom Guy and Dev Session | 2026-06-03 |
| Sovereign Mandates | **13 (12 original + Mandate 13 Temple-Grade)** | 2026-06-02 |
| PIVOT decisions | **102 (D1-D102 tracked)** | 2026-06-03 |
| Horizon 1.5 (Bridge Phase) | **DEFINED — 4 sprints, F→A→B→C→E→D execution** | 2026-06-02 |
| Role Mappings | `config/wads/_omega_default/roles.yaml` created | 2026-06-01 |
| Request Queue | `src/omega/request_queue.py` — atomic queue with heartbeat/dead-letter | 2026-06-01 |
| Library Catalog | `src/omega/library/catalog.py` — SQLite, 5D quality scoring | 2026-06-01 |
| Benchmark Runner | `src/omega/benchmarks/runner.py` — 3-point scale, per-criterion scoring | 2026-06-01 |
| Iris (:8080) | Operational | 2026-05-31 |
| SearXNG (:8017) | **Operational** — JSON search verified, 14 engines active | 2026-06-02 (D83) |
| Ollama | **Running** — qwen2.5:0.5b model, real inference working | 2026-06-01 |
| Entity Routing | **Fixed** — word-boundary matching, capability matrix populated | 2026-06-01 |
| User Manual | **Updated** — model configuration docs, provider setup, entity management | 2026-06-01 |
| Search MCP Fleet | **5 wired** — Tavily, Firecrawl, Exa, Jina, SearXNG (via `~/.config/opencode/mcp_servers.json`) | 2026-06-02 (D84) |
| Model Reference Library | **R100 created** — TIER 0-3, 7-metric pattern from legacy | 2026-06-02 (D85) |
| MiniMax M3 Context | **200K (OpenCode Zen free tier)**, 1M only via Cline/Artisan (D86) | 2026-06-02 (D86) |
| rag-v1/ | **ERADICATED** + `make audit-no-rag-v1` (4/4 GREEN) | 2026-06-02 (D87) |

---

## Key Files

| File | Purpose |
|------|---------|
| `src/omega/oracle/oracle.py` | Main entry: talk/summon/router |
| `src/omega/oracle/model_gateway.py` | Provider chain inference |
| `src/omega/oracle/entity_registry.py` | YAML CRUD for entities |
| `src/omega/oracle/wad_loader.py` | WAD system loader (CRITICAL PATH) |
| `src/omega/oracle/context_builder.py` | Memory → LLM injection |
| `src/omega/oracle/session_manager.py` | Entity-scoped sessions |
| `src/omega/oracle/cpu_optimizer.py` | Zen 2 hardware optimization |
| `src/omega/oracle/health_monitor.py` | Circuit breaker + latency |
| `src/omega/oracle/gnosis_proxy.py` | Soul evolution tracking |
| `src/omega/memory_store.py` | Hot/Warm/Cold memory |
| `src/omega/observability.py` | JSONL events + training data + ForensicsManager + JsonFormatter |
| `src/omega/request_queue.py` | Offline request queue (atomic, heartbeat, dead-letter) |
| `src/omega/library/catalog.py` | SQLite document catalog with 5D quality scoring |
| `src/omega/benchmarks/runner.py` | LLM benchmark runner with 3-point scale |
| `src/omega/constants.py` | ZONEID magic constants + validate_zoneid() + ZONEID_TABLE (re-export from cvar_table) |
| `src/omega/cvar_table.py` | Unified named-constant registry — zoneid.* + config.* namespaces + CvarDef + 7 access helpers |
| `src/omega/oracle/subagent_dispatcher.py` | HandoffPacket + Agent Capability Registry + dispatch() — subagent launch protocol |
| `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` | Full protocol spec for launching specialized agents as subagents |
| `src/omega/library/` | FTS5 + vector library (7 modules) |
| `src/omega/workers/` | Background researcher, model updater |
| `mcp_servers/omega_hub/server.py` | Agent bus (40 MCP tools + 11 HTTP routes) |
| `config/wads/_omega_default/` | Reference IWAD |
| `config/wads/arcana_novai/` | Personal IWAD |
| `config/providers.yaml` | Provider fabric config |
| `config/models.yaml` | Model specs |
| `config/omega.yaml` | Core engine config |

---

## Sovereign Mandates

1. **AnyIO Absolute**: No `asyncio`. Use AnyIO. Wrap blocking I/O in `anyio.to_thread.run_sync`.
2. **Engine-Stack Firewall**: Absolute separation between Core Engine (`src/omega/`) and IWAD/PWAD Content (`config/wads/`).
3. **Iris Constant**: Iris is the messenger bridge, NOT a Pillar Keeper.
4. **Sequentiality**: Plan → Verify → Execute. No cowboy coding.
5. **Gnosis Preservation**: Distill session insights into L1 → L2 → L3 abstractions.
6. **Podman Sovereignty**: All Quadlets use `UserNS=keep-id` + `User=1000`.
7. **Local-First**: Local inference is PRIMARY. Cloud is FALLBACK.
8. **Zero Telemetry**: No telemetry. Zero. None. Ever.
9. **Error Integrity**: All errors MUST be typed, traceable, and testable. No silent swallowing.

See `SOVEREIGN_MANDATES.md` for full details (13 mandates).

---

## Phase Priority Queue

### ✅ DONE — Agent Fleet & Entity Cleanup
- [x] Phase A: 26→14 agent consolidation, redesign 9 agents, create quality/pillar
- [x] Phase B: Delete 67 orphan entity directories, create 13 new workspaces (plus 50 more during Option A)
- [x] Update `opencode.json` to 14-agent registry

### ✅ DONE — Offline Request Queue
- [x] Phase C: `src/omega/request_queue.py` — file-based queue with atomic claim/heartbeat/dead-letter
- [x] CLI commands: `queue-status`, `process-queue`, `review-pending`, `queue-prune`
- [ ] v2 design doc referencing plandb SQLite patterns for Horizon 2

### ✅ DONE — Knowledge Library
- [x] Phase D: `src/omega/library/catalog.py` — SQLite-backed multi-dimensional catalog
- [x] 10 domain subdirectories under `data/library/documents/`
- [x] CLI commands: `library curate`, `library status`, `library search`

### ✅ DONE — Model Tiers & Benchmarking
- [x] Phase E: `agent_roles` section in `config/models.yaml`
- [x] Benchmark runner with per-criterion scoring, calibration loop, position randomization
- [x] CLI commands: `bench run`, `bench compare`, `bench rank`, `bench list`

### ✅ DONE — Option B (Mandate 9 Violations)
- [x] Fix 23 bare `except Exception:` without logging (10 files)
- [x] Fix falsy-trap in openai_compat.py:102 (`timeout or 15.0`)
- [x] Fix hardcoded paths in greek.py + cpu_optimizer.py
- [x] Fix direct `asyncio` import in observability.py:235
- [x] All violations now have `logger.warning()` before silent fallback

### ✅ DONE — MCP Hub Restoration (40 Tools)
- [x] Restored 40 MCP tools from git history (`69db713` merged with current HTTP routes)
- [x] Background task lifecycle via daemon thread
- [x] Verified all 6 gates (health, routes, agents, config, SSE, tools)
- [x] Restarted systemd service

### P1 — WAD System Hardening
- [x] `--iwad` flag implemented
- [x] Council Restoration (Pillars + Oversouls)
- [x] Sovereign Persistence (Atomic Writes in 3 modules)
- [x] Sprint 0+1 Complete — missing agents created, stubs filled, Blueprint aligned
- [ ] Namespace isolation: WAD source tracked in EntityRegistry
- [ ] Dependency resolution: wads declare `depends_on`
- [ ] Entity priority: later-loaded overrides earlier for same pillar
- [ ] Manifest validation + edge cases

### P1 — Provider Fabric
- [x] Provider chain ordered correctly (local-first)
- [x] CPU Optimizer integrated
- [x] ModelGateway.generate() method added (with per-provider timeouts)
- [x] Circuit Breaker consolidation (2→1) and wiring into generate() — D94 fixed BSP precheck + None detection
- [x] BSP-style provider culling (_precheck_provider() by provider.name) — D94
- [ ] Qdrant hybrid search wiring (fastembed BGE-base-en-v1.5)
- [ ] Redis pub/sub for cross-agent communication

### ✅ DONE — Horizon 2: Observability & Forensics
- [x] ForensicsManager — crash dump creation, recovery, replay, learn (10 tests)
- [x] Structured JSON logging — JsonFormatter + setup_json_logging()
- [x] Error Gauntlet — 10 scenarios (crash dump, replay, learn, engine state, persistence, ring buffer, JSON format)
- [x] Fixed structural bug in `_collect_system_info()` (dead code, returned None)
- [x] Fixed `asyncio` → `sniffio` in `_detect_anyio_backend()` (Mandate 1)
- [x] Fixed `deque` slicing bug in `recent_events()` (was masking TypeError)

### ✅ DONE — Sprint 1: cvar Table + Priority Ports + Subagent Dispatch Protocol
- [x] `src/omega/cvar_table.py` — unified named-constant registry with zoneid.* (6) + config.* (12) namespaces
- [x] `constants.py` — re-export layer for backward compatibility
- [x] 7 access helpers: cvar_get, cvar_set, cvar_namespace, cvar_modification_count, cvar_by_subsystem, cvar_list, cvar_summary
- [x] Port 1.1: `validate_llama_kwargs()` — kwarg whitelist for llama-cpp
- [x] Port 1.2: `n_gpu_layers=0` — cvar default for CPU-only
- [x] Port 1.3: ChatML stop tokens — wired into Ollama + Locallmster providers
- [x] Port 1.4: Google API key header — documented in cvar table
- [x] Port 1.5: Atomic trace_id — NativeGGUFProvider logs trace_id
- [x] `make heritage-map` — CI target audits [id-soft:] tags
- [x] Subagent Dispatch Protocol: `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` + `src/omega/oracle/subagent_dispatcher.py`
- [x] Handoff Archive: 36 non-active handoffs → `data/handoff/archive/` with INDEX.md and mining tags
- [x] Expanded Roadmap: D100-D102 recorded, delegation contract between Doom Guy and Dev Session
- [x] Commit: `3048e91`, tests: 307/307, Temple-Grade: 7/11 GREEN

### P1 — Subagent Dispatch Protocol
- [ ] HandoffPacket dataclass — typed schema for agent-to-agent task delegation
- [ ] Agent Capability Registry — what each of the 14 agents can do
- [ ] Standardized Task tool prompt format for persona injection
- [ ] `dispatch_subagent()` — build prompts from HandoffPacket
- [ ] Archive: processed handoffs → `data/handoff/archive/`

### P1 — Handoff Protocol (Link P9)
- [ ] Redis Pub/Sub handoff bus (reuse existing redis container at port 6379)
- [ ] Link P9 runtime module — agent presence, task queue, heartbeat
- [ ] CLI commands: `omega handoff send`, `omega handoff list`, `omega handoff status`
- [ ] JSON archive system — `data/handoffs/archive/{packet_id}.json`
- [ ] MCP Hub resurrection — read running config, serve agent state

### P3 — Synthesis Pipeline
- [ ] Entity LoRA adapter management
- [ ] CPU fine-tuning integration (LLaMA-Factory or PEFT)
- [ ] Cloud → training data pipeline
- [ ] A/B testing for new adapters

### P4 — Reference IWAD Content
- [ ] Rewrite `config/wads/_omega_default/entities.yaml`
- [ ] Create 10 pillar entity YAMLs
- [ ] Verify `omega talk "hello"` works

---

## Engine vs. Platform Distinction

| What | Where | Who Updates |
|------|-------|-------------|
| **OMEGA_ENGINE.md** (this file) | Repo root | Any agent changing engine state |
| `.clinerules` | Repo root | Cline agents only |
| `AGENTS.md` | Repo root | OpenCode agents only |
| `GEMINI.md` | Repo root | Gemini CLI only |
| Omega Hub (`:8016`) | Live service | Runtime state |

**The rule**: If it describes WHAT the engine is → this file.
If it describes HOW to use the engine from Platform X → that platform's rules file.

---

## Key Supporting Documents

| Document | Purpose | Status |
|----------|---------|--------|
| `SOVEREIGN_MANDATES.md` | 12 constitutional laws (non-negotiable) | Updated 2026-06-01 — v3.1.0, Twelve Laws |
| `data/handoff/HANDOFF_FLEET_REDESIGN_G4.md` | Fleet Redesign & Systems Hardening — Gemma 4 31B execution handoff | NEW 2026-06-01 — 2,000+ lines, 8 phases |
| `docs/strategy/LOGGING_ERROR_HANDLING_ARCHITECTURE.md` | Error taxonomy, handling standards, recovery matrix | NEW 2026-05-31 |
| `tests/test_error_gauntlet.py` | 10 Error Gauntlet scenarios (crash dump, replay, learn, JSON format) |
| `docs/architecture/SOVEREIGN_BLUEPRINT.md` | Engine/IWAD/PWAD separation strategy | v1.0.0 — authored by Doom Guy |
| `docs/operations/BUG_LOG.md` | Bug tracking (3 open, 1 resolved) | Updated 2026-05-31 |
| `data/handoff/HANDOFF_GEMMA_SPRINT0_1.md` | Sprint 0+1 execution (Foundation Repair + Alignment) **COMPLETE** | 668 lines, executed 2026-06-01 |
| `data/handoff/HANDOFF_DOOM_GUY_CIRCUIT_BREAKER.md` | Circuit breaker consolidation + BSP provider culling | NEW 2026-06-01 — awaiting Doom Guy |
| `data/handoff/handoff_cline_to_opencode_artisan_20260531.md` | OpenCode builder task queue (8 tasks P0-P3) | 2026-05-31 |
| `docs/strategy/SYSTEMS_HARDENING_PLAN.md` | Agent/MCP/workflow hardening roadmap (747 lines) | Existing |
| `docs/strategy/NEXT_STEPS_ROADMAP.md` | Phase priority execution plan | Existing |

---

*Last Updated: 2026-06-03 | Author: KALI/DOOM_GUY — Sprint 1 complete (cvar_table + 5 ports + heritage-map) + Subagent Dispatch Protocol defined*
*This document is the Single Source of Truth. All platforms reference it.*
*Changes: cvar_table.py live (276 lines, 18 entries, 7 helpers), constants.py re-export, providers wired, make heritage-map CI, Subagent Dispatch Protocol defined, 8 handoffs archived for Roc Racoon mining.*
