# 🔱 Omega Engine — Oracle Stack Canonical Architecture
**AP Token**: `AP-ORACLE-RESTORE-v2.4.0` · **Status**: ACTIVE · **Last Updated**: 2026-08-28
**Supersedes**: `ORACLE_STACK_CANONICAL.md` (2026-07-01, v2.3.0)
**Companion**: `SOVEREIGN_ARK_BLUEPRINT_CANONICAL.md` · `docs/architecture/ARCHITECTURE_CANONICAL.md`

---

## §0 POST-COMPACTION RECOVERY PROTOCOL

If you are reading this, your context was just compacted. Follow these steps:

1. Read this entire document first — it restores your knowledge of the Omega repo
2. Read `AGENTS.md` for agent behavior rules
3. Read `docs/decisions/PIVOT_LOG.md` for why every decision was made
4. Read `SOVEREIGN_ARK_BLUEPRINT_CANONICAL.md` for the complete master plan
5. Read `docs/architecture/ARCHITECTURE_CANONICAL.md` for full technical architecture
6. If working on code: `src/omega/oracle/oracle.py` (main entry point)
7. Run `make test` to verify state

---

## §1 WHAT THIS REPO IS

Omega is the **community engine** — a sovereign local-first AI runtime that empowers every user to build their own entity pantheons. This repo at `~/Documents/Xoe-NovAi/omega-engine/` is the hardened, Sprint PUBLIC-DEBUT-01 evolution.

**Key differentiators**:
- **Local-first inference** (M7): native-gguf via llama-cpp-python is PRIMARY; cloud is FALLBACK
- **Zero telemetry** (M8): no external analytics, no phone-home
- **Soul integrity** (M11): L1→L2→L3 distillation per session, persisted to `proposed_lessons.yaml`
- **Entity sovereignty**: Pure YAML CRUD via EntityRegistry — no SQLAlchemy, no PostgreSQL
- **27 Sovereign Mandates** (v3.8.0): The law above all code
- **Engine-Stack Firewall** (M2): `src/omega/` (Core) never imports `config/wads/` (Stacks)

**This repo is NOT**: `omega-stack/` (33k files, Temple Grade cruft), `xna-omega/` (legacy), or any cloud-dependent stack.

---

## §2 CORE ARCHITECTURE

```
Query → Oracle.talk() → Iris speculative decode (confidence check via qwen3-1.7b)
  ├── high confidence → Iris responds directly (simple Q&A, greetings)
  └── low confidence → escalate to domain-matched entity → ModelGateway → provider fabric
```

### Key Components

| Component | Path | Responsibility |
|-----------|------|----------------|
| **Oracle** | `src/omega/oracle/oracle.py` | Intent detection + summon parsing + domain routing + Iris speculative decoder |
| **EntityRegistry** | `src/omega/oracle/entity_registry.py` | YAML-backed entity CRUD (pure Python). Auto-scaffolds sovereign workspaces on entity creation. |
| **EntityWorkspaceManager** | `src/omega/oracle/entity_workspace.py` | Creates `data/entities/<name>/` with `soul.yaml`, `knowledge/`, `workspace/` |
| **Orchestrator** | `src/omega/oracle/orchestrator.py` | Dispatches headless CLI agents (Cline, OpenCode) with soul-injected system prompts. Protected by ResourceGuard. |
| **ModelGateway** | `src/omega/oracle/model_gateway.py` | 8-backend provider fabric. **Local-first priority** per D-536. Native GGUF via `llama-cpp-python` is PRIMARY. |
| **ProviderSelector** | `src/omega/oracle/provider_selector.py` | Single router (D-536) — reads `config/providers.yaml` as SSOT |
| **Nova** | `src/omega/nova/` | FastAPI voice assistant + intent matcher, runs as Podman container ("hey Nova") |
| **Observability** | `src/omega/observability.py` | Trace IDs, event logging, fine-tuning dataset collection (JSONL export) |
| **CLI** | `src/omega/cli/oracle_cli.py` | Typer CLI (talk, summon, list-entities, add-entity, entity-info, backends, version, hardware-stats, etc.) |
| **ResourceGuard** | `src/omega/oracle/resource_guard.py` | AnyIO Semaphore(1) — one model at a time (OOM protection) |
| **CpuOptimizer** | `src/omega/oracle/cpu_optimizer.py` | Zen 2 compilation flags, KV cache sizing, speculative decode tuning, thread pool recommendations |
| **OfflineMockBackend** | `src/omega/oracle/backends/mock.py` | Deterministic responses when `OMEGA_ENV=test` |
| **ContextBuilder** | `src/omega/oracle/context_builder.py` | Memory injection pipeline for LLM system prompts |
| **SessionLifecycleManager** | `src/omega/oracle/session_lifecycle.py` | Bidirectional session lifecycle (ACTIVE→ARCHIVED→EXTERNAL→DELETED) with recall-from-external |
| **Omega Hub** | `mcp_servers/omega_hub/` | Modularized cross-CLI awareness server — 5 modules (state, background, gateway, middleware, tools). All agents post/read shared context via Hivemind protocol. |
| **Hivemind Protocol** | `docs/strategy/HIVEMIND_PROTOCOL.md` | 6 MCP tools (post_context, get_awareness, heartbeat, get_live_feed, get_workspace_lock, acknowledge) for cross-agent coordination |
| **Verity** | `verity.md` | Unified agent merging Quality (compliance audit) + Scribe (L1→L2→L3 gnosis distillation). Reports to Kali. |
| **Vector Store Adapter** | `src/omega/memory/vector_adapters.py` | `IVectorStoreAdapter` ABC with 3 implementations — `SQLiteVecAdapter` (core unified fabric), `MemoryVectorAdapter` (sovereign fallback), `QdrantAdapter` (deprecated heritage reference). **Current fabric**: 7 per-model vec0 collections + FTS5 BM25 + RRF fusion (k=60) via `HybridSearchEngine`. |
| **Memory Store** | `src/omega/memory_store.py` | Unified memory interface with FTS5, vector, and hybrid search |
| **Soul Store** | `src/omega/soul_store.py` | Atomic writer, 4-layer guarantee for soul persistence |
| **Soul Utils** | `src/omega/soul_utils.py` | Soul validation, migration, consolidation |

---

## §3 THE ENTITY PANTHEON (Current State)

### Oversouls (Governance Layer)

| Entity | Role | Governs |
|--------|------|---------|
| **Sophia** | Akashic Record — the containing field | All entities, all sessions, all souls |
| **Kali** | Grand Oversight — Transcendent | Unifies Ma'at + Lilith, destroys drift |
| **Ma'at** | Build Oversoul — the Builder | N1-N5 (Infrastructure, Persistence, Engineering, Integration, Governance) |
| **Lilith** | Runtime Oversoul — the Runner | N6-N10 (Cognition, Context, Observability, Orchestration, Validation) |

### Specialist Agents (14 total, M10 cap)

| Entity | Domain | Status |
|--------|--------|--------|
| **Kali** | Grand Oversight / Sprint Coordinator | ACTIVE |
| **Ma'at** | Build / Justice / Persistence | ACTIVE |
| **Lilith** | Runtime / Execution | ACTIVE |
| **Sophia** | Akashic Record / Synthesis | ACTIVE |
| **Researcher** | Evidence engine / Deep research | ACTIVE |
| **Roc** | Corpus mining / Knowledge retrieval | ACTIVE |
| **Jem** | Historical research / Legacy mining | ACTIVE |
| **Verity** | Compliance audit + Gnosis distillation | ACTIVE |
| **John Carmack** | Technical audit / Engine architecture | ACTIVE |
| **Doom Guy** | Heritage vetting / ID Software patterns | ACTIVE |
| **Grokster** | Grok ecosystem / Adversarial review | ACTIVE |
| **Node** | Universal knowledge bases | ACTIVE |
| **Antigravity** | Cloud provider / OAuth fabric | ACTIVE |
| **Cline** | CLI integration / OpenCode bridge | ACTIVE |

### Iris (Voice Assistant)
- **Role**: Messenger bridge between user and entity council
- **Container**: Podman `omega-iris` (pinned CPUs 4,6)
- **NOT a Pillar Keeper** — she is the messenger bridge

---

## §4 MODEL GATEWAY — PROVIDER FABRIC (D-536)

Configured via `config/providers.yaml` (SSOT). Single router: `ProviderSelector`.

### Provider Priority Chain (Local-First)

| Priority | Provider | Type | Status |
|----------|----------|------|--------|
| 0 | **native-gguf** | LOCAL | PRIMARY — llama-cpp-python, Zen 2 optimized |
| 1 | **lmster** | LOCAL | LM Studio headless server (:1234) |
| 2 | **ollama** | LOCAL | Lightweight local fallback (:11434) |
| 3 | **antigravity** | CLOUD | OAuth pool — primary cloud |
| 4 | **google / google-compat** | CLOUD | Gemma 4 31B (unlimited, 262K context) |
| 5 | **openrouter** | CLOUD | 300+ models |
| 6 | **opencode-zen** | CLOUD | OpenCode built-in |
| 7 | **cline** | CLOUD | OpenCode bridge |
| 8 | **anthropic** | CLOUD | Claude Haiku, GPT-4.1, GPT-4o, GPT-5-mini |
| 9 | **xai** | CLOUD | API |
| — | **mock** | TEST | Last resort, `OMEGA_ENV=test` only |

**Routing when local saturated**: Antigravity → Google → OCZ → OpenRouter · single breaker per provider (C-6′ HealthMonitor factory).

**Model specs**: `config/models.yaml` (SINGLE SOURCE OF TRUTH) with loading strategies: `always` | `warm` | `on_demand_5min` | `on_demand_10min`. Context windows: 4K-16K (sized to use case, not model max).

---

## §5 MEMORY & VECTOR ARCHITECTURE

### Vector Store Adapter Pattern
```
IVectorStoreAdapter (ABC)
├── SQLiteVecAdapter     ← CORE (sqlite-vec unified fabric)
├── MemoryVectorAdapter  ← SOVEREIGN FALLBACK (no external deps)
└── QdrantAdapter        ← DEPRECATED (heritage reference only)
```

### Current Fabric
- **7 per-model vec0 collections** (one per active model)
- **FTS5 BM25** for keyword search
- **RRF fusion (k=60)** via `HybridSearchEngine` in `src/omega/memory/hybrid_search.py`
- **SQLite-vec** as primary vector backend (no external Qdrant required for core)

### Memory Store (`src/omega/memory_store.py`)
- Unified interface for FTS5, vector, and hybrid search
- `HybridSearchEngine` with RRF re-ranking
- Per-entity memory isolation via `data/entities/<name>/memory/`

### Soul Persistence (`src/omega/soul_store.py`)
- Atomic writer with 4-layer guarantee
- `proposed_lessons.yaml` → `approved_lessons.yaml` promotion via `scripts/promote_soul_lessons.py`
- L1→L2→L3 distillation per session (M11)

---

## §6 INFRASTRUCTURE — PODMAN CONTAINERS

| Container | Image | Purpose | Limit | CPUs |
|-----------|-------|---------|-------|------|
| redis | redis:7-alpine | Session/cache | 256M | none |
| **qdrant** | qdrant/qdrant | **Optional WAD adapter** (not core) | 6G | 4 cores (80%) |
| postgres | pgvector-pg17 | SQL persistence | 512M | none |
| caddy | caddy:alpine | Reverse proxy | 64M | none |
| iris | omega-iris | Voice assistant container | 512M | pinned 4,6 |

All containers run rootless (user 1000) using Sovereign Permission Protocol (UserNS=keep-id + User=1000).

**Qdrant Status**: Deployed as optional WAD adapter only. Core engine uses `SQLiteVecAdapter`. Qdrant implements `IVectorStoreAdapter` for stacks opting into external vector infrastructure. Migration strategy: adapter swap with config toggle (`config/jit_rag.yaml`), not wholesale replacement.

---

## §7 HARDWARE TARGET (Ryzen 7 5700U)

| Spec | Value |
|------|-------|
| CPU | AMD Ryzen 7 5700U (Zen 2, 8C/16T, AVX2, FMA3) |
| L1 Cache | 64KB/core (32KB Data + 32KB Instruction) |
| L2 Cache | 512KB/core |
| L3 Cache | 8MB shared **Victim Cache** (evictions only, no mirroring) |
| RAM | 14Gi total (~2Gi overhead → ~12Gi for AI) |
| GPU | None (integrated only) |
| Disk | /dev/nvme0n1p3 omega_library (110G, 17G free) |
| Podman Storage | /media/arcana-novai/omega_library/podman-storage/ |
| Models | /media/arcana-novai/omega_library/models/gguf/ |
| TDP | 15W (thermal throttling is primary constraint for concurrent models) |

**Critical constraints**:
- No AVX-512
- L3 is victim cache, not inclusive
- 15W TDP limits concurrent model loading
- `MALLOC_ARENA_MAX=2` + `MALLOC_MMAP_THRESHOLD_=65536` required for pymalloc arena fragmentation

---

## §8 TEST SUITE

All tests in `tests/`. Run with `make test` or `OMEGA_ENV=test PYTHONPATH=src python3 -m pytest tests/`.

**Current state (2026-08-28)**: 162 test files, ~1,887 test functions. Full suite requires CI resources (OOM risk on 14Gi dev box).

Key test modules:
- `tests/contract/` — Contract tests for mandates (M21, M20, etc.)
- `tests/oracle/` — Oracle, entity, provider tests
- `tests/memory/` — Memory store, adapters, hybrid search
- `tests/hivemind/` — Hivemind protocol tests
- `tests/security/` — Security/taint tests
- `tests/benchmarks/` — Performance benchmarks

---

## §9 SESSION HEADER FORMAT (Required)

All agent outputs MUST include:
```
⬡ OMEGA ⬡ {entity} ⬡ {model} ⬡ {channel} ⬡ {trace} ⬡ {phase}
```

Generated via `src/omega/ics.py` → `ics_render()` (single source of truth).

---

## §10 ANYIO COMPLIANCE (M1)

- **Critical runtime paths** (inference, resource guard, async file I/O, process spawning) are fully AnyIO-compliant.
- **Bootstrap/initialisation** still uses synchronous I/O (`Path.glob()`, `open()`). Acceptable for now but should be migrated to async (`anyio.Path`, `to_thread.run_sync`) for hot-reload scenarios.
- **Aiosqlite warning**: ensure DB connections are closed before the event loop ends to avoid `RuntimeError: Event loop is closed`.
- **M1 Gate**: `make check-m1-anyio` — `rg 'import asyncio|from asyncio' src/omega/ --type py --glob '!*test*' --glob '!*governance*' --glob '!*tty_agent*'`

---

## §11 CRITICAL RULES (Non-Negotiable)

1. **Do NOT** add sphere-port routing (Temple Grade was Path A, rejected)
2. **Do NOT** make entities require PostgreSQL — YAML only (M2)
3. **Iris is a container**, NOT a Pillar Keeper — she is the messenger bridge
4. **The 10 Pillars are mythic foundation**, NOT runtime enforcement
5. **All async code must use AnyIO** (not asyncio) — M1
6. **No telemetry. Zero. None.** — M8
7. **This repo is at** `~/Documents/Xoe-NovAi/omega-engine/` — NOT xna-omega, NOT omega-stack
8. **The 10 Pillar Keepers are DEFAULT TEMPLATE** — users customize freely
9. **Primary inference backend is local-first**: native-gguf via llama-cpp-python is PRIMARY. Cloud is FALLBACK. Always. See Mandate 7.
10. **Always use the venv** (`.venv/`) or podman for package management — NEVER `--break-system-packages` (M24)
11. **M20-M22** (SomaticState, Gate Integrity, Response Provenance) are ratified — see `SOVEREIGN_MANDATES.md`
12. **Engine-Stack Firewall** (M2): `src/omega/` (Core) never imports `config/wads/` (Stacks)
13. **M23 Failure Integrity**: No soft-failures; broken tools → STOP, report
14. **M27 Tracking Integrity**: State follows 5-Tier Tracking Architecture

---

## §12 LEGACY MINING COMPLETE (2026-05-31)

All 5 legacy areas explored and documented:

| Area | Status | Key Finding |
|------|--------|-------------|
| **Grok Exports** | ✅ | MASTER_NAVIGATION_INDEX.md, 10 Pillars genesis, 8 accounts (~414 MB) |
| **OpenCode Integration** | ✅ | MCP server architecture, CLI config strategy |
| **Personas + Model Configs** | ✅ | Complete Model-Persona Affinity Map — Size-hierarchy philosophy |
| **ANAi/XNAi Blueprints** | ✅ | Chainlit UI (Era 1-2), 5 design patterns, Circuit Breaker, Voice Interface |
| **Old Stacks** | ✅ | Complete 4-service architecture, system prompts, persona files |

**Documentation**:
- `docs/legacy/LEGACY_MASTER_SYNTHESIS.md` — Timeline, Model-Persona Affinity Map, Design Patterns
- `docs/legacy/LEGACY_ASSET_CATALOG.md` — Full inventory of recovered assets
- `docs/legacy/LEGACY_INDEX.md` — Gateway to the legacy archive

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ x-preview-f-free ⬡ opencode ⬡ trc_audit ⬡ ORACLE-STACK-CANONICAL-v2.4.0*