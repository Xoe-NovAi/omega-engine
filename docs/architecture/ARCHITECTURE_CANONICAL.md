# 🔱 Omega Engine — Master Technical Architecture
**AP Token**: `AP-ARCH-CANONICAL-v1.0.0` · **Status**: ACTIVE · **Last Updated**: 2026-08-28
**Companion**: `ORACLE_STACK_CANONICAL.md` · `SOVEREIGN_ARK_BLUEPRINT_CANONICAL.md` · `docs/architecture/MODULE_BOUNDARIES.md` · `docs/architecture/PERFORMANCE_ARCHITECTURE.md`

---

## §1 SYSTEM OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        OMEGA ENGINE ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────┐  │
│  │   CLI /      │    │   Oracle     │    │  Model       │    │ Provider │  │
│  │   API        │───▶│   Core       │───▶│  Gateway     │───▶│  Fabric  │  │
│  └──────────────┘    └──────┬───────┘    └──────┬───────┘    └──────────┘  │
│                             │                   │                           │
│                    ┌────────┴────────┐          │                           │
│                    ▼                 ▼          ▼                           │
│            ┌───────────────┐  ┌─────────────┐  ┌─────────────────────┐     │
│            │ Entity        │  │ Memory      │  │ Observability       │     │
│            │ Registry      │  │ Store       │  │ (Trace IDs, Events) │     │
│            └───────────────┘  └──────┬──────┘  └─────────────────────┘     │
│                                     │                                      │
│                    ┌────────────────┼────────────────┐                    │
│                    ▼                ▼                ▼                    │
│            ┌───────────────┐  ┌─────────────┐  ┌─────────────┐           │
│            │ Vector Store  │  │ FTS5 BM25   │  │ Hybrid      │           │
│            │ (sqlite-vec)  │  │ (keyword)   │  │ Search (RRF)│           │
│            └───────────────┘  └─────────────┘  └─────────────┘           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Core Principles
1. **Local-First** (M7): Native GGUF via llama-cpp-python is PRIMARY; cloud is FALLBACK
2. **Zero Telemetry** (M8): No external analytics, no phone-home
3. **Engine-Stack Firewall** (M2): `src/omega/` (Core) never imports `config/wads/` (Stacks)
4. **Soul Integrity** (M11): L1→L2→L3 distillation per session
5. **AnyIO Compliance** (M1): All async code uses AnyIO, not asyncio
6. **Failure Integrity** (M23): No soft-failures; broken tools → STOP, report

---

## §2 MODULE ARCHITECTURE

### 2.1 Core Modules (`src/omega/`)

| Module | Purpose | Key Files |
|--------|---------|-----------|
| **oracle/** | Core inference & routing | `oracle.py`, `entity_registry.py`, `model_gateway.py`, `provider_selector.py`, `provider_registry.py`, `orchestrator.py`, `context_builder.py`, `resource_guard.py`, `cpu_optimizer.py` |
| **memory/** | Vector + FTS + Hybrid search | `vector_adapters.py`, `sqlite_vec_adapter.py`, `hybrid_search.py`, `fts_index.py`, `embeddings.py`, `blocks.py` |
| **memory_store.py** | Unified memory interface | FTS5, vector, hybrid search, per-entity isolation |
| **soul_store.py** | Soul persistence | Atomic writer, 4-layer guarantee |
| **soul_utils.py** | Soul validation/migration | Schema validation, migration, consolidation |
| **cli/** | Typer CLI | `oracle_cli.py` (main), `youtube_cli.py`, `bundle.py`, `local_queue.py`, `vault.py`, `soul_stage.py` |
| **observability/** | Trace IDs, events, datasets | `observability.py` |
| **ics.py** | Session header rendering | Single source of truth for `⬡ OMEGA ⬡` headers |
| **cvar_table.py** | Configuration variables | Runtime tunables |
| **config/loader.py** | Config loading | `config/providers.yaml`, `config/models.yaml` SSOT |
| **audit/** | Mandate compliance | `mandate_auditor.py`, `firewall_checker.py`, `memory_firewall_auditor.py` |
| **ingestion/** | Knowledge ingestion | Pipeline, sources, extractors, verifier, worker |
| **workers/** | Background workers | `youtube_worker.py` |
| **model_registry/** | Model metadata | `registry.py`, `providers.py`, `models.py` |
| **council/** | Multi-agent coordination | `coordinator.py`, `execution_mode.py`, `failure_layer.py` |
| **orchestration/** | Task orchestration | `orchestrator.py` (legacy), `subagent_dispatcher.py` |
| **hub.py** | Omega Hub client | Hivemind protocol client |
| **mcp_runtime.py** | MCP server runtime | Tool registration, transport |
| **monitoring/** | Hardware monitoring | `HardwareMonitor` (psutil-based) |
| **security/** | Taint tracking | `taint.py` |
| **privacy/** | PII masking | `kernel.py`, `cpe_scorer.py` |
| **eval/** | Evaluation framework | `runner.py`, `calibrate.py`, `check.py` |
| **research/** | Research pipeline | `sediment.py`, `hivemind_bridge.py`, `sandbox.py` |
| **agents/** | Agent runtime | `tty_agent.py` |
| **gateway/** | A2A bridge | `a2a_bridge.py`, `a2a_auth.py` |
| **orchestrator/** | Legacy orchestrator | (being consolidated) |
| **state/** | State management | `state_manager.py` |
| **skills/** | Skill system | Skill loading/execution |
| **tools/** | Tool registry | Tool definitions |
| **teachers/** | Teacher pipeline | Distillation, training |
| **training/** | Training pipeline | DPO, RLHF preparation |
| **rag/** | RAG pipeline | Retrieval-augmented generation |
| **search/** | Search infrastructure | `search_router.py`, `search_cache.py` |
| **request_queue.py** | Request queuing | Async request queue |
| **errors.py** | Error types | `OmegaError` hierarchy |

### 2.2 Stack Modules (`config/wads/`) — M2 Firewall

| Stack | Purpose | Isolation |
|-------|---------|-----------|
| `_omega_default` | Default engine config | Core-only |
| `arcana_novai` | Arcana-NovAi WAD | User pantheon |
| `ingestion` | Ingestion stack config | Stack-only |
| `omega_research` | Research stack config | Stack-only |

**M2 Rule**: `src/omega/` (Core) **never** imports from `config/wads/` (Stacks). Stacks import from Core.

---

## §3 DATA FLOW

### 3.1 Query Flow
```
User Query
    │
    ▼
CLI (oracle_cli.py) ──▶ _inject_vault_to_env() (decrypts keys.json.enc → os.environ)
    │
    ▼
Oracle.talk(query)
    │
    ├──▶ Intent Detection (Oracle._detect_intent)
    │
    ├──▶ Summon Parsing (Oracle._parse_summon)
    │
    ├──▶ Domain Routing (Oracle._route_to_entity)
    │       │
    │       ▼
    │  EntityRegistry.get(entity) → Entity config (model, temperature, personality)
    │
    ├──▶ Iris Speculative Decode (confidence check via qwen3-1.7b)
    │       │
    │       ├── High confidence → Iris responds directly
    │       └── Low confidence → Escalate to domain-matched entity
    │
    ▼
ModelGateway.route(request)
    │
    ├──▶ ProviderSelector.select() → reads config/providers.yaml (SSOT)
    │
    ├──▶ ResourceGuard.acquire() → AnyIO Semaphore(1) — one model at a time
    │
    ├──▶ Provider.call() → native-gguf / lmster / ollama / antigravity / etc.
    │
    ▼
Response → ContextBuilder.inject_memory() → MemoryStore.hybrid_search()
    │
    ▼
OracleResponse(entity, model, text, trace_id, slots, cost_warning)
    │
    ▼
CLI → _display_response() → ics_render() → Session Header + Output
```

### 3.2 Memory Flow
```
Entity Interaction
    │
    ▼
ContextBuilder.build_context(entity, query)
    │
    ├──▶ MemoryStore.hybrid_search(query, entity) → RRF fusion (k=60)
    │       ├── FTS5 BM25 (keyword)
    │       └── Vector (sqlite-vec, per-model collections)
    │
    ├──▶ SoulStore.load_soul(entity) → approved_lessons.yaml
    │
    ├──▶ EntityWorkspace.get_knowledge(entity) → knowledge/ files
    │
    ▼
Injected into system prompt → LLM
    │
    ▼
Response → SoulStore.propose_lesson(entity, L1/L2/L3) → proposed_lessons.yaml
    │
    ▼
scripts/promote_soul_lessons.py → approved_lessons.yaml (vetted)
```

---

## §4 ENTITY SYSTEM

### 4.1 Entity Registry (`src/omega/oracle/entity_registry.py`)
- Pure YAML CRUD — no SQLAlchemy, no PostgreSQL
- Source of truth: active IWAD's `entities.yaml` (e.g., `config/wads/arcana_novai/entities.yaml`)
- Auto-scaffolds sovereign workspaces on entity creation:
  ```
  data/entities/<name>/
  ├── soul.yaml              # Entity identity + config
  ├── proposed_lessons.yaml  # L1→L2→L3 distillation (staging)
  ├── approved_lessons.yaml  # Vetted lessons (hydrated)
  ├── knowledge/             # Domain knowledge files
  └── workspace/             # Working files
  ```

### 4.2 Entity Config Schema (`soul.yaml`)
```yaml
name: entity_name
slots: [slot1, slot2]           # Governance slots (M10)
domains: [domain1, domain2]     # Affinity routing domains
model: qwen3-1.7b               # Preferred model
temperature: 0.7
personality: "System prompt..."
container: null                 # Podman container if voice
```

### 4.3 Governance Slots (M10)
- 14 slots max (M10 cap)
- Current: Kali, Ma'at, Lilith, Sophia, Researcher, Roc, Jem, Verity, John Carmack, Doom Guy, Grokster, Node, Antigravity, Cline
- Slot = role, not agent — can be reassigned by Architect

---

## §5 PROVIDER FABRIC (D-536)

### 5.1 Single Router: ProviderSelector
- Reads `config/providers.yaml` as SSOT
- Priority chain: native-gguf (0) → lmster (1) → ollama (2) → antigravity (3) → google (4) → openrouter (5) → opencode-zen (6) → cline (7) → anthropic (8) → xai (9)
- Local-first: priorities 0-2 are LOCAL; 3-9 are CLOUD

### 5.2 Provider Interface
```python
class BaseProvider:
    async def complete(self, request: CompletionRequest) → CompletionResponse
    async def stream(self, request: CompletionRequest) → AsyncIterator[Chunk]
    def health_check(self) → HealthStatus
    def get_models(self) → List[ModelSpec]
```

### 5.3 Circuit Breakers (C-6′)
- Single `HealthMonitor` factory per provider
- 5/7 legacy breakers deprecated; 2 unmigrated (P-5 ticket)

---

## §6 MEMORY ARCHITECTURE

### 6.1 Vector Store Adapter Pattern
```
IVectorStoreAdapter (ABC in src/omega/memory/vector_adapters.py)
├── SQLiteVecAdapter     ← CORE (sqlite-vec unified fabric)
├── MemoryVectorAdapter  ← SOVEREIGN FALLBACK (no external deps)
└── QdrantAdapter        ← DEPRECATED (heritage reference only)
```

### 6.2 Current Fabric
- **7 per-model vec0 collections** (one per active model)
- **FTS5 BM25** for keyword search (sqlite3 FTS5)
- **RRF fusion (k=60)** via `HybridSearchEngine` in `src/omega/memory/hybrid_search.py`

### 6.3 Memory Store (`src/omega/memory_store.py`)
- Unified interface for FTS5, vector, and hybrid search
- Per-entity memory isolation via `data/entities/<name>/memory/`
- `HybridSearchEngine` with RRF re-ranking

---

## §7 OBSERVABILITY & TRACING

### 7.1 Trace IDs
- Every interaction generates UUID `trace_id`
- Passed through entire call chain: CLI → Oracle → ModelGateway → Provider → Memory
- Logged to `data/observability/events.jsonl`

### 7.2 Event Log
```json
{
  "trace_id": "uuid",
  "timestamp": "ISO8601",
  "entity": "kali",
  "model": "qwen3-1.7b",
  "confidence": 0.92,
  "provider": "native-gguf",
  "latency_ms": 1450,
  "tokens": {"input": 1200, "output": 340}
}
```

### 7.3 Fine-Tuning Dataset
- Optional JSONL export keyed by `trace_id`
- Enables local model improvement without cloud

---

## §8 INFRASTRUCTURE

### 8.1 Podman Containers (Rootless, UserNS=keep-id)
| Container | Image | Purpose | Limit | CPUs |
|-----------|-------|---------|-------|------|
| redis | redis:7-alpine | Session/cache | 256M | none |
| qdrant | qdrant/qdrant | Optional WAD adapter | 6G | 4 cores (80%) |
| postgres | pgvector-pg17 | SQL persistence | 512M | none |
| caddy | caddy:alpine | Reverse proxy | 64M | none |
| iris | omega-iris | Voice assistant | 512M | pinned 4,6 |

### 8.2 Hardware Target (Ryzen 7 5700U)
- CPU: Zen 2, 8C/16T, AVX2, FMA3, **NO AVX-512**
- L1: 64KB/core, L2: 512KB/core, L3: 8MB **Victim Cache**
- RAM: 14Gi (~12Gi for AI)
- TDP: 15W (thermal throttling primary constraint)
- `MALLOC_ARENA_MAX=2` + `MALLOC_MMAP_THRESHOLD_=65536` for pymalloc

---

## §9 SECURITY & COMPLIANCE

### 9.1 Mandates Enforcement
- **M1 AnyIO**: `make check-m1-anyio` — no `import asyncio` in `src/omega/`
- **M8 Zero Telemetry**: `make check-m8-zero-telemetry` — no segment/posthog/datadog imports
- **M9 Error Integrity**: `make check-m9-error-integrity` — no bare `except:`
- **M14 Heritage**: `scripts/heritage_vet.sh` — all `[id-soft:]` tags vetted ≥7/10
- **M23 Failure Integrity**: `scripts/m23_gate.py` — ratchet baseline `config/m23_baseline.txt`
- **M27 Tracking**: `scripts/validate_tracking_state.py` — 5-Tier architecture

### 9.2 Vault (Excluded from Debut — D-565)
- `src/omega/vault/` — Argon2id + age encryption
- `data/vault/keys.json.enc` — Encrypted credentials
- `_inject_vault_to_env()` in CLI decrypts at process edge only
- **Post-debut**: Delete or replace with 100-line `secrets.py` env adapter

---

## §10 TEST ARCHITECTURE

### 10.1 Test Organization
```
tests/
├── contract/           # Mandate contract tests (M20, M21, etc.)
├── oracle/             # Oracle, entity, provider tests
├── memory/             # Memory store, adapters, hybrid search
├── hivemind/           # Hivemind protocol tests
├── security/           # Security/taint tests
├── benchmarks/         # Performance benchmarks
├── property/           # Property-based tests
├── chaos/              # Chaos engineering
├── mcp/                # MCP transport tests
└── integration/        # E2E integration tests
```

### 10.2 Key Contract Tests
- `tests/contract/test_soul_lessons.py` — M11 Soul Integrity
- `tests/contract/test_provider_classification.py` — D-536 SSOT
- `tests/contract/test_contract_m21.py` — M21 Gate Integrity
- `tests/test_somatic_roundtrip.py` — M20 SomaticState
- `tests/test_streaming_timeout.py` — M25 Streaming Resilience

---

## §11 CRITICAL RULES SUMMARY

| Rule | Mandate | Enforcement |
|------|---------|-------------|
| No `import asyncio` in `src/omega/` | M1 | `make check-m1-anyio` |
| Core never imports Stacks | M2 | `scripts/check_mandate_compliance.py` |
| No telemetry SDKs | M8 | `make check-m8-zero-telemetry` |
| No bare `except:` | M9 | `make check-m9-error-integrity` |
| Local-first provider chain | M7 | `config/providers.yaml` SSOT |
| Soul L1→L2→L3 per session | M11 | `scripts/promote_soul_lessons.py` |
| No soft-failures | M23 | `scripts/m23_gate.py` |
| 27 mandates v3.8.0 | All | `SOVEREIGN_MANDATES.md` |

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ x-preview-f-free ⬡ opencode ⬡ trc_audit ⬡ ARCHITECTURE-CANONICAL-v1.0.0*