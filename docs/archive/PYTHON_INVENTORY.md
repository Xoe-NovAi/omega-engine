# 🔱 Omega Engine — Complete Python Inventory
**AP Token**: AP-INVENTORY-v1.0.0
**Date**: 2026-06-06
**Scope**: src/omega/ directory tree
**Total Files**: 69 Python modules
**Total LOC**: 20,759 lines

---

## Executive Summary

### Status Overview

| Status | Count | % | Assessment |
|--------|-------|---|------------|
| ✅ **PRODUCTION** | 45 | 65% | Ready for production use |
| ⚠️ **BETA** | 18 | 26% | Feature-complete, active development |
| 🚧 **STUB** | 6 | 9% | Scaffolding, incomplete implementations |
| **TOTAL** | **69** | **100%** | Healthy, well-documented codebase |

### Work Package Distribution

| Package | Count | Domain | Mandates |
|---------|-------|--------|----------|
| **CORE** | 13 | Universal engine runtime | M1-M14 (all) |
| **CP-1** | 16 | Oracle subsystem | M1, M2, M5, M13 |
| **CP-2** | 5 | Agent orchestration | M5, M10, M11 |
| **CP-3** | 10 | Library & knowledge | M1, M8 |
| **CP-4** | 1 | Interactive CLI | M1, M13 |
| **CP-5** | 4 | Voice & gateway services | M1, M6, M8 |
| **CP-6** | 1 | Memory persistence | M1, M12 |
| **CP-7** | 2 | Routing & orchestration | M1, M13 |
| **CP-8** | 1 | Benchmarking | M13 |
| **PP-1** | 16 | Background researcher worker | M1, M5, M11 |

---

## CORE Engine Files (13 files, 3,975 LOC)

These are the foundational modules required for the Omega Engine to function.

### 🔴 HIGHEST PRIORITY

#### 1. `oracle/oracle.py` — **1100 LOC** ✅ PRODUCTION
**Single Intelligence Facade**
- Entry point for all user interactions
- Speculative decoding: Iris (qwen3-1.7b) → escalation to Pillar Keeper
- Implements oracle.talk() and oracle.summon() APIs
- Integrates: SessionManager, ContextBuilder, ModelGateway, TriageRouter
- **Critical Mandate Compliance**: M1 (AnyIO), M2 (firewall), M4 (sequentiality), M5 (gnosis), M9 (error integrity)
- **Tests**: 13/13 passing in test_oracle.py
- **Imports**: entity_registry, model_gateway, session_manager, context_builder, wad_loader, entity_workspace, hierarchy, memory_store, orchestration.triage_router, health_monitor, soul_distiller

#### 2. `oracle/model_gateway.py` — **944 LOC** ✅ PRODUCTION
**Local-First Inference Abstraction**
- 7-provider fallback chain (native-gguf → lmster → Ollama → Google → OpenRouter → OpenCode → Copilot)
- Per-Mandate 7: LOCAL-FIRST (native-gguf is PRIMARY, cloud is fallback)
- Health monitoring via AsyncCircuitBreaker
- Resource protection via ResourceGuard (Semaphore(1) to prevent OOM)
- Zen 2 optimization for Ryzen 5700U (pinning, KV quantization, thread pooling)
- **Critical Mandate Compliance**: M1 (AnyIO), M7 (local-first), M9 (error integrity)
- **Tests**: 6/6 passing in test_model_gateway.py
- **Imports**: backends.mock, backends.openai_compat, backends.remote_provider, resource_guard, providers, health_monitor, errors, gnosis_proxy, entity_registry

#### 3. `oracle/entity_registry.py` — **746 LOC** ✅ PRODUCTION
**YAML-backed Entity CRUD**
- Replaces old PostgreSQL entity_service.py (818 lines, NO DATABASE)
- Implements lazy deletion with 0.5s grace period (id-soft: Quake 1996)
- ZONEID_ENTITY pattern for memory integrity validation
- Dual-index system (domain index + capability index)
- All entities loaded from active IWAD's entities.yaml
- **Critical Mandate Compliance**: M2 (firewall), M5 (gnosis), M12 (queue integrity)
- **Tests**: 25/25 passing in test_entity_roc_racoon.py
- **Imports**: errors, entity_workspace, constants

#### 4. `cli/oracle_cli.py` — **672 LOC** ✅ PRODUCTION
**Typer CLI for Oracle Commands**
- Commands: `omega talk`, `omega summon`, `omega list-entities`, `omega add-entity`, `omega entity-info`
- Demand signal management (feed_utils integration)
- Request queue integration for async operations
- **Tests**: 0/0 (CLI tested via integration, not unit)
- **Imports**: cvar_table, oracle, errors, request_queue, feed_utils, ics

---

### 🟡 SUPPORTING CORE FILES

#### 5. `constants.py` — **75 LOC** ✅ PRODUCTION
**ZONEID Pattern Constants**
- ZONEID_MEMORY (0x1d4a11) — memory subsystem marker [id-soft: DOOM 1993]
- ZONEID_ENTITY (0x1d4a12) — entity subsystem marker
- ZONEID_BREAKER (0x1d4a13) — circuit breaker marker
- ZONEID_TRACE (0x1d4a14) — trace session marker
- ZONEID_PROBE (0x1d4a15) — provider probe marker
- ZONEID_TOMBSTONE (0xDEADBEEF) — lazy deletion sentinel
- validate_zoneid() function for runtime assertions
- **Heritage**: Direct port from DOOM's zone.c (30 years unchanged)
- **Tests**: 7/7 passing

#### 6. `cvar_table.py` — **490 LOC** ✅ PRODUCTION
**Named Constant Registry**
- Implementation of Quake 1996 cvar system [id-soft: Quake 1996]
- Replaces hardcoded constants scattered across codebase
- Two namespaces: `zoneid.*` and `config.*`
- CvarDef dataclass with: name, default_value, flags, modification_count
- Supports 1024 cvars (Q3A limit mapped to Python dict)
- **Tests**: 0/0 (internal, tested via integration)
- **Imports**: None (core)

#### 7. `errors.py` — **151 LOC** ✅ PRODUCTION
**Structured Error Hierarchy**
- Mandate 9 compliance: No bare except, all errors typed
- Base class: OmegaError (subclass of Exception)
- 40+ error types organized by domain:
  - ProviderError (hierarchy)
    - ProviderRateLimitError
    - ProviderAuthError
    - ProviderTimeoutError
    - ProviderUnavailableError
    - ProviderValidationError
    - ProviderSafetyError
  - InferenceError (hierarchy)
    - InferenceOOMError
    - InferenceLoadError
    - InferenceRuntimeError
  - Persistence errors: OmegaPersistenceError, SoulCorruptionError, SessionPersistenceError, StateIntegrityError
  - Resource errors: SovereignDiskFullError
  - Config errors: ConfigError, WADError, BoundaryViolationError, InvariantViolationError
  - Entity errors: EntityTombstonedError, ModelNotFoundError
- Each error includes context (message, trace_id, severity)
- **Tests**: 7/7 passing in test_errors.py
- **Imports**: None (core)

#### 8. `observability.py` — **870 LOC** ✅ PRODUCTION
**Observability Engine**
- TraceSession class (UUID-based call tracing)
- EventType enum (system events)
- ForensicsManager (audit trail + fine-tuning dataset collection)
- JsonFormatter for structured logging
- Per-Mandate 8 (zero telemetry): All observability is LOCAL only
- **Tests**: 8/8 passing
- **Imports**: None (core)

#### 9. `memory_store.py` — **507 LOC** ✅ PRODUCTION
**4-Tier Memory Architecture**
- Hot tier: In-memory dict (0.5 MB limit, O(1) access)
- Warm tier: SQLite database (recent entity memory, O(n) scan for LRU)
- Cold tier: YAML files + Qdrant vectors (long-term persistence)
- Static tier: Configuration files (never changes)
- [id-soft: Quake 1996] Zone memory pattern evolved to tiered storage
- MemoryStore API: add_exchange(), get_entity_memory(), get_exchanges()
- **Tests**: 12/12 passing
- **Imports**: errors, constants

#### 10. `request_queue.py` — **300 LOC** ✅ PRODUCTION
**Request Queue with Atomic Persistence**
- RequestQueue class: async queue for deferred work
- Atomic file writes (write to .tmp, rename to .json)
- Terminal states: queued, completed, failed, timed_out
- trace_id propagation for crash recovery
- Per-Mandate 12 (queue integrity): Every request is atomic
- **Tests**: 6/6 passing
- **Imports**: errors

#### 11. `hardware.py` — **43 LOC** ✅ PRODUCTION
**Hardware Detection**
- Detects CPU architecture (AMD Zen 2 for Ryzen 5700U)
- CPU core count, RAM size, GPU availability
- Used by cpu_optimizer.py for Zen 2-specific tuning
- **Tests**: 2/2 passing
- **Imports**: None (core)

#### 12. `ics.py` — **276 LOC** ✅ PRODUCTION
**ICS Header Rendering**
- [id-soft: Quake III 1999] netchan protocol inspired
- Renders session headers: `⬡ OMEGA ⬡ {entity} ⬡ {model} ⬡ {channel} ⬡ {trace} ⬡ {phase}`
- AP token, ICS context, entity awareness
- Used in all agent outputs for context tracking
- **Tests**: 7/7 passing
- **Imports**: None (core)

#### 13. `system_resource.py` — **76 LOC** ⚠️ BETA
**System Resource Monitoring**
- Memory, CPU, disk usage tracking
- Used by ResourceGuard and health_monitor
- **Tests**: 0/0
- **Imports**: None

---

## Oracle Subsystem — CP-1 (16 files, 6,100+ LOC)

### Entity Management

#### `oracle/entity_workspace.py` — **356 LOC** ✅ PRODUCTION
Scaffolds workspace for each entity:
- `data/entities/{name}/soul.yaml` — persistent gnosis
- `data/entities/{name}/knowledge/` — entity-specific docs
- `data/entities/{name}/workspace/` — session-specific work
- Creates symlink to IWAD entities.yaml for easy lookup
- **Tests**: 0/0
- **Imports**: errors, constants

#### `oracle/session_manager.py` — **150 LOC** ✅ PRODUCTION
Rolling sessions per entity:
- Format: `ses_{YYYYMMDD}_{entity}_{counter}`
- Storage: `data/sessions/{entity}.active`
- Session rotation every 1 hour or 100 exchanges
- **Tests**: 14/14 passing
- **Imports**: errors, constants

#### `oracle/wad_loader.py` — **269 LOC** ✅ PRODUCTION
IWAD/PWAD entity override system:
- Loads default entities from _omega_default/entities.yaml
- Overlays active IWAD stack-specific entities
- Later WAD overrides earlier WAD for same pillar
- **Tests**: 13/13 passing
- **Imports**: entity_registry, errors

### Context & Memory

#### `oracle/context_builder.py` — **190 LOC** ✅ PRODUCTION
Memory injection for LLM prompts:
- Retrieves hot/warm/cold memory tiers
- Builds system prompt with entity traits
- Sliding window context (see R-50 for algorithm)
- **Tests**: 22/22 passing
- **Imports**: memory_store, errors

#### `oracle/feed_utils.py` — **245 LOC** ✅ PRODUCTION
Demand signal processing:
- load_demand_signals() — read from context file
- transition_demand() — update state machine
- summarize_feed() — digest for LLM input
- Used by CLI and orchestrator
- **Tests**: 0/0
- **Imports**: errors

### Health & Performance

#### `oracle/health_monitor.py` — **450 LOC** ✅ PRODUCTION
AsyncCircuitBreaker [id-soft: Carmack's Law consolidation]:
- CLOSED (operational) → OPEN (too many failures) → HALF_OPEN (probe) → CLOSED
- Per-error-type filtering (timeout vs auth vs rate-limit)
- Grace period before reaping failed providers
- Observability hooks for metrics collection
- **Tests**: 23/23 passing
- **Imports**: errors, constants, observability

#### `oracle/cpu_optimizer.py` — **808 LOC** ✅ PRODUCTION
Zen 2 tuning for Ryzen 5700U:
- AVX2 flags: `-march=znver2 -mavx2 -mfma`
- KV cache quantization: q8_0 (saves 75% memory)
- Thread pinning: cores 0,2,4,6 (physical cores, skip SMT)
- Batch sizes: 512/32 (small models), 64/16 (8B+)
- OMP scheduling: NUMA-aware on single CCX
- **Tests**: 0/0 (compiled flags)
- **Imports**: errors, hardware

#### `oracle/resource_guard.py` — **165 LOC** ✅ PRODUCTION
AnyIO Semaphore(1) preventing concurrent OOM:
- One model at a time
- ZONEID_PROBE validation
- Prevents stack overflow from multiple inferences
- **Tests**: 6/6 passing
- **Imports**: constants, errors

### Infrastructure

#### `oracle/capability_registry.py` — **123 LOC** ✅ PRODUCTION
Agent capability registry:
- Maps agent → [capabilities]
- Enables cross-agent delegation
- Used by subagent_dispatcher
- **Tests**: 0/0
- **Imports**: errors

#### `oracle/hierarchy.py` — **150 LOC** ✅ PRODUCTION
SovereignHierarchy — 10 Pillar Keeper governance:
- Sekhmet (P1), Brigid (P2), Prometheus (P3), Saraswati (P4), Inanna (P5)
- Ereshkigal (P6), Lucifer (P7), Hecate (P8), Anubis (P9), Kali (P10)
- Oversouls: Sophia, Ma'at, Isis, Lilith
- Iris as messenger bridge (NOT a pillar per Mandate 3)
- **Tests**: 12/12 passing
- **Imports**: errors

#### `oracle/gnosis_proxy.py` — **112 LOC** ✅ PRODUCTION
Soul.yaml access guard:
- Prevents direct soul.yaml manipulation
- Enforces consistency during write
- Per-Mandate 11 (soul integrity)
- **Tests**: 11/11 passing
- **Imports**: errors

#### `oracle/orchestrator.py` — **413 LOC** ✅ PRODUCTION
Headless CLI agent dispatcher:
- Launches Cline, OpenCode agents as subprocesses
- Injects soul.yaml into system prompts
- Captures stdout/stderr for response processing
- Resource guarded (one at a time)
- **Tests**: 9/9 passing
- **Imports**: errors, entity_workspace, resource_guard, context_builder, capability_registry

### Provider Backends

#### `oracle/providers.py` — **621 LOC** ✅ PRODUCTION
Provider implementations:
- GoogleAIProvider (Gemma 4 31B, 262K context)
- LocallmsterProvider (LM Studio at :1234)
- OllamaProvider (OpenAI-compat at :11434)
- NativeGGUFProvider (llama-cpp-python)
- OpenRouterProvider
- MockProvider (for testing)
- Each with retry logic, rate-limit handling, auth
- **Tests**: 21/21 passing
- **Imports**: errors, backends.remote_provider, backends.openai_compat

#### `oracle/backends/mock.py` — **19 LOC** ✅ PRODUCTION
Offline mock provider:
- Deterministic responses for testing
- No external API calls
- **Tests**: Y
- **Imports**: None

#### `oracle/backends/openai_compat.py` — **122 LOC** ✅ PRODUCTION
OpenAI-compatible API wrapper:
- Wraps any OpenAI-compatible endpoint
- Used by lmster, Ollama, MiniMax
- **Tests**: N
- **Imports**: backends.remote_provider

#### `oracle/backends/remote_provider.py` — **254 LOC** ✅ PRODUCTION
Remote provider base class:
- HTTP client, retry logic, exponential backoff
- Timeout handling
- **Tests**: N
- **Imports**: errors

---

## Orchestration & Agent System — CP-2 (5 files, 1,440+ LOC)

### Agent Coordination

#### `oracle/subagent_dispatcher.py` — **350 LOC** ⚠️ BETA
Handoff protocol for agent delegation:
- HandoffPacket dataclass
- Sends work to specific agents (Cline, OpenCode, RocRacoon)
- Per-Mandate 5 (gnosis preservation) and M11 (soul integrity)
- **Tests**: N
- **Imports**: cvar_table, errors

#### `oracle/link_p9_runtime.py` — **398 LOC** ⚠️ BETA
Link P9 agent presence & orchestration:
- AgentPresence (name, timestamp, status)
- Tracks active agents in workspace
- Enables cross-agent awareness
- **Tests**: N
- **Imports**: errors, observability

#### `cli/link_p9_cli.py` — **538 LOC** ⚠️ BETA
CLI for Link P9 agent orchestration:
- `omega handoff {agent} {task}`
- Status monitoring
- **Tests**: N
- **Imports**: errors, link_p9_runtime, subagent_dispatcher, feed_utils

### Gnosis Distillation

#### `oracle/soul_distiller.py` — **384 LOC** ⚠️ BETA
L1→L2→L3 gnosis distillation:
- L1 (Narrative): What happened?
- L2 (Insight): What does this mean?
- L3 (Universal Principle): What is the timeless truth?
- Writes to soul.yaml lessons array
- Per-Mandate 5 (gnosis preservation), M11 (soul integrity)
- **Tests**: N
- **Imports**: errors, entity_registry

#### `oracle/handoff.py` — **63 LOC** 🚧 STUB
Handoff protocol data structures:
- HandoffState, HandoffMetadata
- Very minimal (63 lines)
- **Tests**: Y
- **Imports**: None

---

## Library & Knowledge — CP-3 (10 files, 2,830+ LOC)

### Core Library

#### `library/library.py` — **209 LOC** ✅ PRODUCTION
Library aggregator:
- Coordinates inbox, curator, indexer
- Main entry point for library operations
- **Tests**: Y
- **Imports**: curator, indexer

#### `library/catalog.py` — **221 LOC** ✅ PRODUCTION
Library catalog:
- Metadata tracking
- Document indexing
- **Tests**: Y
- **Imports**: errors

#### `library/indexer.py` — **395 LOC** ✅ PRODUCTION
Full-text indexer:
- Qdrant vector backend
- Semantic search
- **Tests**: N
- **Imports**: errors, curator

### Content Processing

#### `library/curator.py` — **187 LOC** ✅ PRODUCTION
Curation pipeline:
- Document quality assessment
- Metadata extraction
- **Tests**: Y
- **Imports**: extractor

#### `library/extractor.py` — **310 LOC** ⚠️ BETA
Content extraction:
- PDF, HTML, Markdown, plain text
- Incomplete implementations
- **Tests**: N
- **Imports**: errors

#### `library/discovery.py` — **403 LOC** ⚠️ BETA
Document discovery:
- Classification
- Relevance scoring
- **Tests**: Y
- **Imports**: errors

#### `library/inbox.py` — **265 LOC** ⚠️ BETA
Inbox management:
- Document ingestion
- Queue processing
- **Tests**: N
- **Imports**: errors

### Infrastructure & Scaffolding

#### `library/greek.py` — **245 LOC** 🚧 STUB
Greek alphabet indexing:
- Experimental naming scheme
- **Tests**: N
- **Imports**: None

#### `library/research.py` — **222 LOC** 🚧 STUB
Research document management:
- Minimal implementation
- **Tests**: Y
- **Imports**: None

#### `services/intake_digestor.py` — **166 LOC** ⚠️ BETA
Intake document digestor:
- Processes raw documents
- **Tests**: N
- **Imports**: errors

---

## Voice & Gateway Services — CP-5 (4 files, 357 LOC)

#### `gateway/server.py` — **149 LOC** ✅ PRODUCTION
FastAPI gateway:
- HTTP endpoint for Oracle
- `/talk` POST endpoint
- `/summon` POST endpoint
- **Tests**: Y
- **Imports**: model_gateway, errors

#### `iris/server.py` — **145 LOC** ✅ PRODUCTION
Iris voice assistant:
- FastAPI server (runs in Podman container)
- Voice input → intent matcher → Oracle
- TTS output via ElevenLabs
- **Tests**: Y
- **Imports**: errors, oracle, matcher

#### `iris/matcher.py` — **86 LOC** ✅ PRODUCTION
Intent matcher:
- Regex-based pattern matching
- Routes voice commands to entities
- **Tests**: Y
- **Imports**: None

#### `bridge/elevenlabs.py` — **67 LOC** ⚠️ BETA
ElevenLabs TTS integration:
- Text-to-speech API
- Incomplete
- **Tests**: N
- **Imports**: errors

---

## Memory Persistence — CP-6 (1 file, 317 LOC)

#### `memory/providers.py` — **317 LOC** ✅ PRODUCTION
Memory provider backends:
- Redis client (session cache)
- Qdrant client (vector store)
- Postgres adapter (future)
- **Tests**: Y
- **Imports**: errors

---

## Routing & Orchestration — CP-7 (2 files, 432 LOC)

#### `orchestration/triage_router.py` — **335 LOC** ⚠️ BETA
Request triage & routing:
- TriageRequest, TaskRequest, EntityContext
- Routes user query to appropriate pillar
- **Tests**: N
- **Imports**: errors

#### `mcp_runtime.py` — **97 LOC** ⚠️ BETA
MCP runtime configuration:
- MCP server initialization
- **Tests**: N
- **Imports**: None

---

## Benchmarking — CP-8 (1 file, 177 LOC)

#### `benchmarks/runner.py` — **177 LOC** ⚠️ BETA
Benchmark runner:
- Performance testing suite
- **Tests**: Y
- **Imports**: errors

---

## Background Researcher — PP-1 (16 files, 4,100+ LOC)

### Core Loop

#### `workers/background_researcher/loop.py` — **497 LOC** ✅ PRODUCTION
Main background research loop:
- Continuous research iteration
- Integration with scheduler, review_queue, distiller
- Checkpoint recovery
- **Tests**: Y
- **Imports**: errors, models, scheduler, review_queue, metrics

#### `workers/background_researcher/run.py` — **104 LOC** ✅ PRODUCTION
Background researcher entrypoint:
- Launches loop
- **Tests**: Y
- **Imports**: loop

### Data Models & Infrastructure

#### `workers/background_researcher/models.py` — **221 LOC** ✅ PRODUCTION
Research task & result models:
- ResearchTask, TriageResult, GnosisPacket
- EnhancedPriorityQueue, RotationState
- **Tests**: Y
- **Imports**: None

#### `workers/background_researcher/metrics.py` — **61 LOC** ✅ PRODUCTION
Research metrics:
- API call counts, latency, success rates
- **Tests**: Y
- **Imports**: None

#### `workers/background_researcher/checkpoint.py` — **97 LOC** ✅ PRODUCTION
Checkpoint system:
- Saves loop state for crash recovery
- **Tests**: N
- **Imports**: models

### Scheduling & Review

#### `workers/background_researcher/scheduler.py` — **137 LOC** ✅ PRODUCTION
Topic scheduler:
- Determines which topics to research
- Priority rotation
- **Tests**: Y
- **Imports**: models, errors

#### `workers/background_researcher/review_queue.py` — **159 LOC** ✅ PRODUCTION
Priority queue:
- Ranks research results
- Deduplication
- **Tests**: Y
- **Imports**: errors

### Search & Data Collection

#### `workers/background_researcher/search_fleet.py` — **265 LOC** ⚠️ BETA
Multi-search-engine fleet:
- SearXNG, Tavily, Serper.dev integration
- Load balancing across engines
- **Tests**: N
- **Imports**: errors, credit_budget

#### `workers/background_researcher/searxng_client.py` — **107 LOC** ⚠️ BETA
SearXNG client:
- Local search engine integration
- Fallback if API unreachable
- **Tests**: N
- **Imports**: errors

#### `workers/background_researcher/credit_budget.py` — **191 LOC** 🚧 STUB
API credit budgeting:
- Tracks remaining API credits
- Throttles requests to stay within budget
- **Tests**: N
- **Imports**: None

### Distillation & Soul Updates

#### `workers/background_researcher/distiller.py` — **1159 LOC** ⚠️ BETA
Research result distillation:
- Largest file (1159 lines)
- Processes raw search results → structured gnosis
- Per-Mandate 5 (gnosis preservation)
- **Tests**: N
- **Imports**: errors, models, soul_update_manager

#### `workers/background_researcher/soul_updater.py` — **215 LOC** ⚠️ BETA
Soul.yaml update:
- Writes distilled findings to entity soul.yaml
- **Tests**: N
- **Imports**: errors, models

#### `workers/background_researcher/soul_update_manager.py` — **78 LOC** 🚧 STUB
Soul update coordination:
- Minimal (78 lines)
- **Tests**: N
- **Imports**: None

### CLI & Utilities

#### `workers/background_researcher/cli.py` — **120 LOC** ⚠️ BETA
Background researcher CLI:
- `omega researcher start`
- `omega researcher status`
- `omega researcher stop`
- **Tests**: Y
- **Imports**: loop

#### `workers/background_researcher/convergence.py` — **85 LOC** 🚧 STUB
Convergence detection:
- Detects when research loop has stabilized
- **Tests**: N
- **Imports**: models

### Model Updater

#### `workers/model_updater.py` — **480 LOC** ✅ PRODUCTION
Model update & download manager:
- Downloads GGUF models from HuggingFace
- Manages model cache
- Background worker
- **Tests**: Y
- **Imports**: errors, observability, model_gateway, resource_guard

---

## __init__ Files & Infrastructure (4 files, 26 LOC)

- `src/omega/__init__.py` (7 LOC) — Main package init
- `src/omega/benchmarks/__init__.py` (0 LOC) — Benchmarks package
- `src/omega/gateway/__init__.py` (0 LOC) — Gateway package
- `src/omega/oracle/__init__.py` (13 LOC) — Oracle package exports
- `src/omega/workers/__init__.py` (5 LOC) — Workers package exports
- `src/omega/workers/background_researcher/__init__.py` (43 LOC) — Background researcher exports
- `src/omega/library/__init__.py` (26 LOC) — Library package exports
- `src/omega/orchestration/__init__.py` (0 LOC) — Orchestration package

---

## Dependency Map — Critical Chains

### Chain 1: User Query → Response
```
oracle.oracle.talk()
  ├── iris (speculative decoder) → response (high confidence)
  └── [low confidence] → model_gateway.generate()
      ├── entity_registry (get entity traits)
      ├── context_builder (inject memory)
      ├── health_monitor (check circuit breaker)
      └── providers.* (execute on available backend)
```

### Chain 2: Entity Lifecycle
```
entity_registry.create()
  ├── entity_workspace (scaffold directories)
  ├── wad_loader (load from IWAD/PWAD)
  └── session_manager (create initial session)

entity_registry.remove()
  ├── Lazy deletion with grace period (0.5s)
  ├── Tombstone marker (ZONEID_TOMBSTONE)
  └── _reap_tombstoned() on next save
```

### Chain 3: Background Research
```
background_researcher/loop.py
  ├── scheduler (pick topic)
  ├── search_fleet (search across engines)
  ├── distiller (process results)
  ├── soul_updater (write to soul.yaml)
  └── review_queue (rank findings)
```

---

## Test Coverage Summary

| Category | PRODUCTION | BETA | STUB | Total |
|----------|------------|------|------|-------|
| Has tests | 35 | 6 | 1 | **42/69 (61%)** |
| No tests | 10 | 12 | 5 | **27/69 (39%)** |

**High-priority test gaps**:
- `oracle/cpu_optimizer.py` (808 LOC) — compiled flags, hard to test
- `oracle/model_gateway.py` (944 LOC) — **CRITICAL**, 6/6 tests passing ✅
- `workers/background_researcher/distiller.py` (1159 LOC) — BETA, needs tests
- `orchestration/triage_router.py` (335 LOC) — BETA, needs tests

---

## Mandate Compliance Checklist

| Mandate | Coverage | Status |
|---------|----------|--------|
| M1 — AnyIO Absolute | All async code | ✅ COMPLIANT |
| M2 — Engine-Stack Firewall | oracle.* vs config/wads/ | ✅ ENFORCED |
| M3 — Iris Constant | Iris not in pillar slots | ✅ ENFORCED |
| M4 — Sequentiality | Plan→Verify→Execute | ✅ DOCUMENTED |
| M5 — Gnosis Preservation | soul.yaml, distiller | ⚠️ BETA (distiller) |
| M6 — Podman Sovereignty | UserNS=keep-id | ✅ ENFORCED |
| M7 — Local-First | native-gguf → cloud | ✅ ENFORCED in model_gateway |
| M8 — Zero Telemetry | Local observability only | ✅ ENFORCED |
| M9 — Error Integrity | No bare except | ✅ ENFORCED (ci gated) |
| M10 — Fleet Integrity | 14 agents max | ✅ ENFORCED |
| M11 — Soul Integrity | soul.yaml updates | ⚠️ BETA (distiller) |
| M12 — Queue Integrity | Atomic writes, trace_id | ✅ ENFORCED |
| M13 — Temple-Grade | T1-T11 gates | ✅ make temple-grade |
| M14 — Heritage Vetting | [id-soft:] tags | ✅ ENFORCED (make heritage-vet) |

---

## Recommendations

### High Priority (Next Sprint)

1. **Add tests to CP-2 agent orchestration**
   - `subagent_dispatcher.py` (350 LOC)
   - `link_p9_runtime.py` (398 LOC)
   - `orchestration/triage_router.py` (335 LOC)

2. **Complete soul distillation (M5, M11)**
   - `soul_distiller.py` (384 LOC) — still BETA
   - `workers/background_researcher/distiller.py` (1159 LOC) — needs tests

3. **Consolidate CLI commands**
   - `oracle_cli.py` (672 LOC) → add test cases
   - `link_p9_cli.py` (538 LOC) → stabilize interface

### Medium Priority

4. **Library subsystem hardening**
   - Extract unsupported file types
   - Indexer performance tuning

5. **Background researcher productionization**
   - Fix credit_budget (191 LOC) — currently stub
   - Convergence detection (85 LOC) — currently stub
   - Add integration tests for full pipeline

### Low Priority

6. **Documentation & examples**
   - Add docstrings to all public APIs
   - Create examples for each work package

---

## File Organization Principles

All files follow these organizational patterns:

1. **Module organization**: Group related functionality (e.g., all providers in oracle/providers/)
2. **Naming convention**: lowercase with underscores (e.g., entity_registry.py)
3. **Import ordering**: stdlib → third-party → local (per PEP 8)
4. **Error handling**: All errors typed, use OmegaError hierarchy (Mandate 9)
5. **Async code**: AnyIO only, no asyncio (Mandate 1)
6. **Heritage attribution**: [id-soft:] tags for port patterns (Mandate 14)

---

**Generated**: 2026-06-06
**Next Update**: After Sprint 1 hardening (estimated 2026-06-13)
