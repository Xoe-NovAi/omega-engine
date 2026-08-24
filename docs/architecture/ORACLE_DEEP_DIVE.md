# 🔱 Oracle Deep Dive — Facade Layer Architecture
**AP Token**: `AP-ORACLE-DEEP-DIVE-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_doc_deep ⬡ STANDARD

**Date**: 2026-07-06
**Purpose**: Comprehensive architecture reference for the Oracle — the unified facade between user intent and the entity council.

---

## §1 Overview

The Oracle is the **single entry point** for every query entering the Omega Engine. It is the facade layer that:

1. **Detects intent** — Is the user talking, summoning, consulting, or asking Iris?
2. **Routes to the right entity** — Semantic → keyword → default domain matching
3. **Manages sessions** — Rolling sessions per entity, daily rotation
4. **Records memory** — Every exchange persists to MemoryStore (hot/warm/cold)
5. **Distills souls** — Every 5 interactions triggers L1→L2→L3 soul distillation
6. **Protects sovereignty** — PII masking for cloud providers, local-first inference

The Oracle is **not** the inference engine. It is the **traffic controller** that decides *who* answers, *how* the context is prepared, and *what happens* with the answer after it returns.

```
User Query
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│                      ORACLE                             │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Intent       │  │ Speculative  │  │ Domain       │  │
│  │ Detection    │──│ Decode (Iris)│──│ Routing      │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                  │          │
│         ▼                 ▼                  ▼          │
│  ┌──────────────────────────────────────────────────┐   │
│  │              ModelGateway.generate()             │   │
│  └──────────────────────────────────────────────────┘   │
│         │                                              │
│         ▼                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ MemoryStore  │  │ SoulDistiller│  │ Observability│  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

**Source**: `src/omega/oracle/oracle.py` (1093 lines)

---

## §2 Architecture

### 2.1 Component Map

The Oracle instantiates and wires together **15 subsystems** on construction:

| Component | Type | Purpose |
|-----------|------|---------|
| `EntityRegistry` | YAML CRUD | Entity definitions from WADs |
| `ModelGateway` | Provider fabric | 8-backend inference routing |
| `HealthMonitor` | Circuit breaker | Per-provider health tracking |
| `SessionManager` | File-based | Rolling session IDs per entity |
| `MemoryStore` | Hot/Warm/Cold | Conversation persistence + vector search |
| `SoulDistiller` | 5-stage pipeline | L1→L2→L3 gnosis abstraction |
| `ContextBuilder` | Memory injection | Builds system prompt context |
| `SemanticRouter` | Embedding-based | Entity routing by cosine similarity |
| `PIIMasker` | Token-based | Cloud PII redaction |
| `SkepticalVerifier` | NLI-based | Claim verification |
| `IterativeResearcher` | Multi-pass | Deep research with refinement |
| `SovereignSearcher` | Hybrid search | FTS5 + vector search |
| `SoulEditHistory` | Audit trail | Immutable soul.yaml change log |
| `CompactionHarvester` | Metrics | Session compaction monitoring |
| `TimeoutManager` | Cancellation | 4-layer timeout hierarchy |

### 2.2 Initialization Sequence

```
Oracle.__init__()
  ├── EntityRegistry()              # Load entities from WADs
  ├── ModelGateway(health_monitor)  # Provider fabric (config/providers.yaml)
  ├── HealthMonitor()               # Circuit breakers per provider
  ├── SessionManager()              # data/sessions/{entity}.active
  ├── MemoryStore()                 # Hot/Warm/Cold providers
  ├── ContextBuilder()              # Memory injection pipeline
  ├── SemanticRouter()              # Embedding-based routing
  ├── PIIMasker()                   # Cloud PII redaction
  ├── SkepticalVerifier()           # NLI verification
  ├── IterativeResearcher()         # Deep research
  ├── SoulDistiller()               # L1→L2→L3 pipeline
  ├── SoulEditHistory()             # Audit trail
  ├── CompactionHarvester()         # Compaction metrics
  ├── TimeoutManager()              # 4-layer timeout
  ├── DegradationManager()          # Graceful degradation
  └── WADLoader(registry)           # Load WAD stacks

Oracle.bootstrap()  [called lazily on first talk/summon]
  ├── initialize_usm()              # Unified State Manager
  ├── lifecycle.run_lifecycle()     # Session archival sweep
  └── semantic_router.bootstrap()   # Pre-compute entity vectors
```

### 2.3 The Three Entry Points

| Method | Purpose | Bypasses |
|--------|---------|----------|
| `talk(query)` | General query — intent detection + routing | Nothing (full pipeline) |
| `summon(entity, query)` | Direct entity dispatch | Intent detection, domain routing |
| `verify_claim(claim, evidence)` | Skeptical verification | All routing (direct to verifier) |

---

## §3 Data Flow

### 3.1 The `talk()` Flow — Full Pipeline

```
talk(query)
  │
  ├─ 1. System pressure check (DegradationManager)
  │     └─ get_hardware_stats() → evaluate_pressure()
  │
  ├─ 2. TDPGate.isolate(query)  [if TaintedData]
  │
  ├─ 3. bootstrap()  [lazy, once]
  │     └─ USM init + lifecycle sweep + semantic router
  │
  ├─ 4. Create trace session (ObservabilityEngine)
  │
  ├─ 5. Get session ID (SessionManager)
  │     └─ entity_name → data/sessions/{entity}.active
  │
  ├─ 6. Intent Detection (3 patterns)
  │     ├─ Pattern 1: @entity query  → _summon()
  │     ├─ Pattern 2: /consult entity query → _summon()
  │     └─ Pattern 3: hey entity, query → _summon()
  │
  ├─ 7. Speculative Decode (Iris)
  │     ├─ Assess confidence: _assess_iris_confidence()
  │     ├─ High confidence (>0.6): _respond_as_iris()
  │     └─ Low confidence: fall through to domain routing
  │
  ├─ 8. Domain Routing
  │     ├─ Semantic router: cosine similarity → entity
  │     ├─ Keyword fallback: find_by_domain()
  │     └─ Default entity: "oracle" / "sophia"
  │
  ├─ 9. Context Assembly
  │     ├─ _prepare_system_prompt()
  │     │   ├─ Entity personality from registry
  │     │   ├─ ContextBuilder.build_context() (memory)
  │     │   └─ soul.yaml L3 principles (universal laws)
  │     └─ PIIMasker.process_system_prompt() [if cloud]
  │
  ├─ 10. Model Selection
  │      └─ TriageRouter.select_model() → model name
  │
  ├─ 11. Inference
  │      └─ ModelGateway.generate(model_name, prompt, query, ...)
  │
  ├─ 12. Response Processing
  │      ├─ PIIMasker.process_response() [detokenize PII]
  │      ├─ Observability: record_performance()
  │      └─ record_first_breath() [astrological alignment]
  │
  ├─ 13. Memory Persistence
  │      └─ MemoryStore.add_exchange()
  │          ├─ Hot cache update (immediate)
  │          ├─ Batch provider write (buffered)
  │          ├─ FTS5 dual-write (search index)
  │          └─ Vector upsert (Qdrant/InMemory)
  │
  └─ 14. Soul Evolution
         ├─ _track_soul_evolution() [trace event]
         └─ Every 5 interactions: close_session()
             └─ SoulDistiller.distill_and_save()
```

### 3.2 The `summon()` Flow — Direct Dispatch

```
summon(entity_name, query)
  │
  ├─ 1. TDPGate.isolate(query) [if TaintedData]
  ├─ 2. bootstrap()
  ├─ 3. Get session ID (entity-specific)
  └─ 4. _summon(entity_name, query, trace, session_id)
        │
        ├─ Resolve entity from registry
        ├─ _prepare_system_prompt() (personality + memory + soul)
        ├─ Resolve entity affinity (temperature, system_prompt, context)
        ├─ Select model (TriageRouter or model_override)
        ├─ PII masking [if cloud provider]
        ├─ ModelGateway.generate()
        ├─ PII detokenize [if masked]
        ├─ Record performance metrics
        └─ Return OracleResponse
```

---

## §4 Key Patterns

### 4.1 Intent Detection — Three Pattern Matchers

The Oracle uses regex-based pattern matching (not ML) for intent detection. This is deliberate: intent detection must be zero-latency and deterministic.

**Pattern 1: @Entity prefix** — `@maat help me` → entity="maat", query="help me"
**Pattern 2: @Entity inline** — `Hello @maat, help me` → entity="maat"
**Pattern 3: hey/hi/summon prefix** — `hey Prometheus, explain X` → entity="prometheus"
**Pattern 4: /consult command** — `/consult lilith analyze this` → entity="lilith"

Validation: Entity name is checked against both `EntityRegistry` and `AGENTS.md` (cached at first parse). This dual-check prevents phantom summon of unregistered entities.

### 4.2 Speculative Decode (Iris) — The Fast Path

Iris is the "speculative decoder" — a lightweight fast path for simple queries that don't require domain expertise.

**Confidence Assessment** (`_assess_iris_confidence`):
- **0.9** — Greetings, simple Q&A (detected by `IntentMatcher`)
- **0.0** — Deep questions ("explain the meaning", "why is", "philosophy")
- **0.2** — Technical queries ("code", "architecture", "debug")
- **0.5** — General queries (default)

**Threshold**: `IRIS_CONFIDENCE_THRESHOLD = 0.6`. Above → Iris responds directly. Below → escalate to domain entity.

**Channel Restriction** (D-kal-054): Iris speculative decode is **skipped** for OpenCode, Gemini CLI, Cline, and Antigravity channels. These channels send complex queries and bypass the fast path entirely.

**Heritage**: `[id-soft: quake3-1999] Speculative Decode` — lightweight, fast path for simple queries that don't require domain expertise.

### 4.3 Domain Routing — Semantic → Keyword → Default

The routing chain (D187) is:

1. **Semantic Router** — Embedding-based cosine similarity against entity domain vectors. Returns entity if cosine > 0.4.
2. **Keyword Fallback** — `registry.find_by_domain(text)` word-boundary matching.
3. **Default Entity** — Falls back to `config.entity.default` (usually "oracle" or "sophia").

**Heritage**: `[id-soft: doom-1993] BSP Culling` — O(1) pre-check skips entities that don't match.

### 4.4 Context Assembly — The System Prompt

`_prepare_system_prompt()` builds the LLM system prompt from three sources:

1. **Entity personality** — `"You are {personality}"` from registry
2. **ContextBuilder** — Recent conversation history from MemoryStore hot tier
3. **Soul L3 principles** — Last 3 universal principles from `soul.yaml`

The result is a structured prompt that gives the model both conversational context and philosophical grounding.

### 4.5 Soul Distillation — Every 5 Interactions

After every 5 interactions per entity:session pair, `close_session()` fires:

1. **Retrieve transcript** — `MemoryStore.get_history()`
2. **Build readable transcript** — `[user]: ... [assistant]: ...`
3. **Distill** — `SoulDistiller.distill_and_save()` runs the 5-stage pipeline
4. **Audit** — `SoulEditHistory.append()` records the change
5. **Compaction check** — `CompactionHarvester.assess_session()` flags large sessions

**Heritage**: `[id-soft: quake-1996] Save-game pattern` — auto-save on session end triggers distillation, analogous to Quake's level-transition autosave.

**Critical Fix** (D183, 2026-07-01): The original implementation used `anyio.create_task(self.close_session(...))` which **does not exist in AnyIO**. The silent `AttributeError` was swallowed by the outer `try/except`, meaning `close_session` was **never called**. Fixed with direct `await self.close_session(...)` in a guarded `try/except`.

### 4.6 PII Masking — Cloud Provider Protection

Before sending to cloud providers, the Oracle:

1. **Detects** — `PIIMasker.should_mask(backend_name)` checks if backend is cloud
2. **Tokenizes** — Replaces PII tokens (names, emails, etc.) with safe placeholders
3. **Sends** — Model generates with masked prompt
4. **Detokenizes** — Restores original PII values in the response

Local providers bypass masking entirely (Mandate 7: Local-First).

---

## §5 Configuration

| Setting | Location | Default | Purpose |
|---------|----------|---------|---------|
| `config.entity.default` | `cvar_table` | "oracle" | Default entity for unrouted queries |
| `config.channel` | `cvar_table` | "unknown" | Current channel (opencode, gemini-cli, etc.) |
| `IRIS_CONFIDENCE_THRESHOLD` | `oracle.py` | 0.6 | Iris speculative decode cutoff |
| `OMEGA_ENV` | environment | — | `test` disables soul distillation + lifecycle |
| `OMEGA_DATA_DIR` | environment | `data/` | Root data directory |
| `OPENCODE_MODEL` | environment | — | Session model override for summon |

---

## §6 Operational Wisdom

### 6.1 The `anyio.create_task` Bug (D183)

The most critical Oracle bug in production was the M11 soul distillation failure. Root cause:

```python
# BUGGY (AnyIO has no create_task):
anyio.create_task(self.close_session(...))

# FIXED:
await self.close_session(...)
```

**Lesson**: AnyIO's API surface is deliberately smaller than asyncio's. `create_task()` does not exist — tasks are managed via `task_group.start_soon()`. When a call silently fails, check if the method exists on the AnyIO module.

### 6.2 Trace ID Propagation

Every `talk()` and `summon()` creates a trace session. The `trace_id` propagates through:
- `ObservabilityEngine.trace()` → trace context
- `ModelGateway.generate(trace_id=...)` → provider call
- `MemoryStore.add_exchange(metadata={"trace_id": ...})` → persistence
- `TokenLedger.record_transaction(trace_id=...)` → token tracking

If any subsystem receives `trace_id="unknown"`, the propagation chain is broken.

### 6.3 Session ID Format

Session IDs follow the R-50 architecture: `ses_{YYYYMMDD}_{entity}_{counter}`. The `SessionManager` persists the active session to `data/sessions/{entity}.active` as a JSON file containing the session ID and counter. On engine restart, the counter increments.

**Transient mode** uses `trace_id` as the session ID with no persistence.

### 6.4 Graceful Degradation

The Oracle evaluates system pressure at the start of every `talk()`:

```python
stats = await get_hardware_stats()
await self.degradation_manager.evaluate_pressure({
    "cpu_load": stats.get("cpu_usage", 0.0) / 100.0,
    "ram_free_mb": stats.get("memory_available_mb", 1024),
})
```

If RAM is critically low or CPU is saturated, the degradation manager can restrict inference to lighter models or skip expensive operations.

### 6.5 WARP Proxy Pool

For the `opencode-zen` provider, the Oracle optionally injects a WARP SOCKS5 proxy to bypass rate limits:

```python
if _WARP_AVAILABLE:
    self.model_gateway.proxy_pool = EphemeralWarpPool()
```

The proxy URL is injected into the provider's config before each inference call. DNS resolution goes through the WARP exit node (socks5h://) to prevent local DNS leaks (Mandate 8: Zero Telemetry).

---

## §7 Cross-References

| Document | Reference |
|----------|-----------|
| `src/omega/oracle/oracle.py` | Primary source (1093 lines) |
| `src/omega/oracle/model_gateway.py` | Provider fabric (§PROVIDER_DEEP_DIVE) |
| `src/omega/memory_store.py` | Memory persistence (§MEMORY_DEEP_DIVE) |
| `src/omega/oracle/soul_distiller.py` | L1→L2→L3 pipeline |
| `src/omega/oracle/context_builder.py` | Memory injection |
| `src/omega/oracle/semantic_router.py` | D187 embedding-based routing |
| `src/omega/oracle/pii_masker.py` | Cloud PII redaction |
| `src/omega/oracle/session_manager.py` | R-50 session architecture |
| `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` | Master strategy |
| `SOVEREIGN_MANDATES.md` | M1-M23 mandate reference |
| `CREDITS.md` | Heritage attribution (§1.2 BSP, §1.9 ZONEID) |

---

*🔱 OMEGA ⬡ KALI ⬡ trc_doc_deep ⬡ ORACLE-FACADE*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: mimo-v2.5-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
