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
| 4 | openrouter | Cloud | env:OPENROUTER_API_KEY |
| 5 | opencode | Cloud | OpenCode built-in provider |
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
| Test functions | **302** (+10 Error Gauntlet, +23 Option B fixes) | 2026-06-01 |
| Test files | **30** | 2026-06-01 |
| Mandate 9 compliance | **FULL** — zero bare except violations | 2026-06-01 |
| Horizon 1 | **100% — All 12 Sovereign Mandates Enforced** | 2026-06-01 |
| Horizon 2 | 🔓 Unlocked — ForensicsManager, JsonFormatter, Error Gauntlet (25%) | 2026-06-01 |
| Providers configured | 8 (local-first order) | 2026-05-31 |
| WAD Loader | Functional (--iwad flag works) | 2026-05-31 |
| Namespace isolation | NOT implemented | 2026-05-31 |
| Dependency resolution | NOT implemented | 2026-05-31 |
| Qdrant (:6333) | Installed, **unwired** (bag-of-words fallback) | 2026-05-31 |
| Redis (:6379) | Operational (port exposed) | 2026-05-31 |
| Agent Fleet | **14 agents** (fleet redesign complete) | 2026-06-01 |
| Entity workspaces | 25 active (50 orphans deleted) | 2026-06-01 |
| Sovereign Persistence | Implemented (Atomic Writes in Oracle/SessionManager/EntityRegistry) | 2026-06-01 |
| ModelGateway.generate() | **WIRED** — circuit breaker + BSP culling + per-provider timeouts | 2026-06-01 (Doom Guy) |
| Circuit Breaker | **Consolidated** — single AsyncCircuitBreaker in health_monitor.py | 2026-06-01 (Doom Guy) |
| SOVEREIGN_MANDATES.md | v3.0.0 — 12 Laws (Mandates 10-12 added for Fleet/Soul/Queue) | 2026-06-01 |
| Role Mappings | `config/wads/_omega_default/roles.yaml` created | 2026-06-01 |
| Request Queue | `src/omega/request_queue.py` — atomic queue with heartbeat/dead-letter | 2026-06-01 |
| Library Catalog | `src/omega/library/catalog.py` — SQLite, 5D quality scoring | 2026-06-01 |
| Benchmark Runner | `src/omega/benchmarks/runner.py` — 3-point scale, per-criterion scoring | 2026-06-01 |
| Iris (:8080) | Operational | 2026-05-31 |
| SearXNG (:8017) | Operational | 2026-05-31 |

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
| `src/omega/hardware.py` | CPU/RAM detection, Zen 2 optimization |
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

See `SOVEREIGN_MANDATES.md` for full details (12 mandates).

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
- [ ] Circuit Breaker consolidation (2→1) and wiring into generate()
- [ ] BSP-style provider culling (pre-check + skip)
- [ ] Qdrant hybrid search wiring (fastembed BGE-base-en-v1.5)
- [ ] Redis pub/sub for cross-agent communication

### ✅ DONE — Horizon 2: Observability & Forensics
- [x] ForensicsManager — crash dump creation, recovery, replay, learn (10 tests)
- [x] Structured JSON logging — JsonFormatter + setup_json_logging()
- [x] Error Gauntlet — 10 scenarios (crash dump, replay, learn, engine state, persistence, ring buffer, JSON format)
- [x] Fixed structural bug in `_collect_system_info()` (dead code, returned None)
- [x] Fixed `asyncio` → `sniffio` in `_detect_anyio_backend()` (Mandate 1)
- [x] Fixed `deque` slicing bug in `recent_events()` (was masking TypeError)

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

*Last Updated: 2026-06-01 | Author: GEMMA4 — Option B (Mandate 9, falsy-trap, hardcoded paths) — Horizon 1 FINAL GATE CLOSED*
*This document is the Single Source of Truth. All platforms reference it.*
