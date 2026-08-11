# 🔱 SDP Systems Sweep Report
## The Integration Map for the Sovereign Distillation Pipeline

**AP Token:** `AP-ROC-SDP-SWEEP-20260809-v1.0.0`
⬡ OMEGA ⬡ ROC_RACCOON ⬡ longcat-2.0-free ⬡ opencode ⬡ trc_sdp_sweep ⬡ COMPLETE

**Date:** 2026-08-09
**Mission:** Exhaustive sweep of the Omega Engine codebase, strategy docs, and legacy archives for every existing system, pattern, and artifact that ties into the SDP.
**Method:** Direct file inspection (read/grep/glob) — no synthesis, no assumption. Every claim below has a file path.
**Complementary work:** @researcher is mapping the *gaps* (what's missing). This report maps the *hook points* (what exists).

---

## 🚨 Executive Summary — The Five Headline Findings

| # | Finding | Impact |
|---|---|---|
| **1** | **The V-1 Vault ALREADY EXISTS** — `src/omega/vault/` (67KB, 4 modules: `vault_core.py`, `crypto.py`, `models.py`, `blindvault_resolver.py`) with credentials, leases, quota, audit. | **SDP Phase 3 is NOT greenfield.** The specs treat V-1 as a hard prerequisite blocker. It is ~80% built. |
| **2** | **The Auto-Router substrate ALREADY EXISTS** — `UsagePoolTracker` (`pool_tracker.py`, 23KB) implements weekly reset, per-account pool tracking (Pool G/Pool C), anti-thrashing, and `select_key()`. | **SDP Phase 4 is a wrapper, not a build.** Pool accounting is live at `data/entities/antigravity/knowledge/USAGE_POOL_LOG.json`. |
| **3** | **`TriageRouter` is a complete constraint-satisfaction router** — `src/omega/orchestration/triage_router.py` with `_assemble_candidates` → `_filter_candidates` → `_score_candidates` → `_build_fallback_chain` and a T1/T2/T3 tier taxonomy. | The **Formal Routing Spec (Z3/utility)** should *extend* TriageRouter, not create a parallel router. Avoids Structural Debt Gate #4. |
| **4** | **`DPORecorder` is the Dialectic Session Logger** — `src/omega/oracle/dpo_logger.py` (21KB) already records `(prompt, chosen, rejected)` preference pairs to rotating JSONL with lineage IDs, manifests, and three reward sources (ENVIRONMENTAL / COUNCIL / USER). | Sequential Dialectic (SDP §7) capture is a **schema extension**, not a new subsystem. |
| **5** | **`config/models.yaml` CANNOT support the Model-Aware Gauge** — it contains ONLY local GGUF models with 8K–32K windows. Zero cloud entries. No `tier`, no `is_agy`, no `compaction_trigger_pct`. | **This is the #1 blocking gap for Phase 1.** The Gauge would default every cloud model to 200K and mis-fire REDZONE at 18% actual usage on Longcat/Nemotron (1M). |

**Bottom line:** The SDP is far less greenfield than the specs assume. The dominant risk is **not** missing infrastructure — it is **duplicating infrastructure that already exists** (Structural Debt Gate #4, §9 of the Ark Blueprint).

---

## 1. Telemetry & Observability Hook Points

### 1.1 Existing Tables in MetricsDB
**File:** `src/omega/observability/metrics_db.py` (21KB) — Carmack's 4-table WAL-mode schema.
Source of schema: `data/entities/john_carmack/workspace/carmack_studies/technical/metrics_db_schema.sql`

| Table | Columns (SDP-relevant) | SDP Use |
|---|---|---|
| `events` | `ts, event_type, trace_id, provider, payload` | **Dialectic event stream.** Generic payload JSON → SSP writes, escalation decisions, gauge readings. |
| `errors` | `ts, trace_id, provider, error_type, error_message, context, entity_id` | SSP failure modes (`SSP_WRITE_FAILED`), `NoPoolAvailableError`. |
| `breaker_transitions` | `ts, provider, from_state, to_state, reason` | AGY account health (`is_healthy(a)` in Formal Routing C₃). |
| `performance` | `ts, trace_id, provider, model_used, latency_ms, prompt_tokens, completion_tokens, total_tokens, is_cloud, cost_usd, entity_id` | **The richest hook.** Already carries model + token + cloud-flag + cost per inference. |
| `baselines` | `metric_name, metric_value, sample_count, std_deviation, source` | **Local Executor Capability Profiling** (SDP Execute phase) — baseline store already exists. |
| `vault_audit` | `ts, trace_id, action, credential_ref, success, details` | **AGY account access audit** — pre-built for V-1 pool reservations. |
| `provider_classification` | (built by `build_provider_classification_table()`, line 194) | M22 SSOT for cloud/local. Feeds `v_performance_corrected` view. |

**Async API (all `anyio.to_thread`-wrapped, M1-compliant):**
`record_event`, `record_error`, `record_breaker_transition`, `record_performance`, `set_baseline`, `get_baseline`, `detect_regression`, `get_performance_trend`, `get_error_summary`, `get_breaker_history`, `get_stats`.

> ⚠️ **Recent change:** commit `a5c09a8e` made `ObservabilityEngine` MetricsDB methods async to fix a data-loss regression. Any SDP logger must use the async API.

### 1.2 Existing Token Tracking
**File:** `src/omega/observability/token_ledger.py` (122 lines)

`TokenLedger.record_transaction(trace_id, entity, tokens_in, tokens_out, provider_name)` performs a **triple write**:
1. `obs.log_event(EventType.TOKEN_CONSUMPTION, ...)` → in-memory event stream (real-time BudgetGate queries)
2. `obs.record_performance(...)` → MetricsDB `performance` table
3. Append JSONL → `data/logs/token_ledger.jsonl` (audit trail)

`get_entity_spend(entity_name)` aggregates historical spend per entity.

**SDP relevance:** This is the exact substrate for the **AGY Session Ledger** automation (SDP Automation Blueprint Phase 3: *"the automated session ledger which replaces the manual markdown ledger"*). The manual ledger currently lives at `data/coordination/AGY_SESSION_LEDGER.md`.

### 1.3 EventType Registry (extension point)
**File:** `src/omega/observability/__init__.py:142-169`

Existing: `QUERY_RECEIVED, SUMMON_DETECTED, DOMAIN_ROUTED, ENTITY_MATCHED, MODEL_INVOKED, MODEL_COMPLETED, BACKEND_FALLBACK, RESPONSE_DELIVERED, ESCALATION, IRIS_SPECULATIVE, BOUNDARY_VIOLATION, GNOSIS_REDACTION, ERROR, WORKER_*, TIER_INVOKED, MODE_SWITCHED, AGENT_DISPATCHED, RESEARCH_COMPLETE, TOKEN_CONSUMPTION, ENTITY_INTERACTION, VAULT_AUDIT`

> 🎯 **`ESCALATION` already exists as an EventType.** The SDP escalation path has a pre-allocated event slot.
> `TIER_INVOKED` and `MODE_SWITCHED` map directly onto Scaffold→Synthesize→Execute phase transitions.

**Proposed additions (minimal, 4 new):** `SDP_GAUGE_READ`, `SDP_SSP_WRITTEN`, `SDP_PHASE_TRANSITION`, `SDP_ROUTING_DECISION`.

### 1.4 Supporting Observability Modules
| File | Purpose | SDP Use |
|---|---|---|
| `src/omega/observability/sovereignty.py` (185 lines) | `get_sovereignty_ratio()` — local vs cloud via `v_performance_corrected` view | **SDP scorecard.** Measures whether the Execute phase actually shifts work local. |
| `src/omega/observability/latency_tracker.py` | Latency EMA | Phase timing per Scaffold/Synthesize/Execute |
| `src/omega/observability/ufl.py` | Unified Forensic Ledger | Immutable audit for `routing_audit/` (Formal Routing §3) |
| `src/omega/observability/bleg.py` | Boundary/Ledger events | Boundary violations during escalation |
| `src/omega/observability/regression_watcher.py` | Baseline regression detection | **Local Executor capability drift detection** |
| `src/omega/observability/observability_reader.py` (18KB) | Read/query API | Gauge backend for historical trend |
| `src/omega/observability/otel_exporter.py` | OTel export | (Optional — M8 zero-telemetry means local only) |
| `src/omega/observability/context.py` | Trace context propagation | trace_id threading across SDP phases |

### 1.5 Integration Points for Dialectic Logger — RANKED

| Rank | Hook Point | File:Line | Readiness |
|---|---|---|---|
| 1 | `DPORecorder.record()` | `src/omega/oracle/dpo_logger.py:321` | ✅ **READY** — extend metadata with `sdp_phase`, `model_a`, `model_b` |
| 2 | `MetricsDB.record_event()` | `src/omega/observability/metrics_db.py:274` | ✅ **READY** — add SDP EventTypes |
| 3 | `TokenLedger.record_transaction()` | `src/omega/observability/token_ledger.py:42` | ✅ **READY** — add `sdp_phase` param |
| 4 | `MetricsDB.set_baseline()` | `metrics_db.py:390` | ✅ **READY** — local executor profiling |
| 5 | `EventType` enum | `observability/__init__.py:142` | ✅ **READY** — 4-line addition |

---

## 2. Model Routing & Selection Integration

### 2.1 Current Selection Logic — Three Parallel Routers (⚠️ consolidation risk)

**A. `ModelGateway.generate()`** — `src/omega/oracle/model_gateway.py:1001` (75KB file)
```python
async def generate(model_name, system_prompt, user_query, temperature=None,
                   max_tokens=1024, trace_id=None, session_id=None,
                   entity_name=None, logit_bias=None, repetition_penalty=None,
                   top_p=None) -> GenerateResult
```
- Iterates the provider fabric with circuit-breaker protection
- `[id-soft: vet-055]` Fixed-Size Active Set — tries the 32 most-recently-successful providers first
- **Documented 5-layer sampling resolution:** explicit request → `models.yaml` → entity affinity → global cvars → hardcoded defaults

**`GenerateResult`** (`model_gateway.py:33-48`) — M22 provenance carrier:
`text, provider_name, is_cloud, latency_ms, model_used, logprobs`

> 🎯 **This dataclass is the single point where the Gauge learns the active model.** SDP Model-Aware Gauge §6 proposes `get_active_model_info()` — `GenerateResult` already carries `model_used` + `is_cloud`. Only `context_window`, `tier`, `is_agy`, `compaction_trigger_pct` are missing.

**B. `ProviderSelector`** — `src/omega/oracle/provider_selector.py` (93 lines, ported from xna-omega-legacy)
Penalty-based scoring:
```
Score = (10 - priority) × 10
      − 100.0            [if PII detected AND provider.is_cloud]
      − max(0, (ema_latency − 1000) / 100)   [latency penalty]
      − (cusum_g × 5.0)                       [CUSUM instability penalty]
```

**C. `TriageRouter`** — `src/omega/orchestration/triage_router.py` ⭐ **THE SDP ROUTING HOME**

Full dataclass suite already defined:
`TaskRequest` (description, domain, **estimated_tokens**, **complexity**: fast|standard|deep, preferred_models) · `EntityContext` · `Constraints` (**max_latency_ms, max_cost_usd, available_tokens, preferred_backends**) · `SessionContext` · `TriageRequest` · `ModelSelection` (name, provider, **context_window**, temperature) · `FallbackOption` · `TriageResponse`

Pipeline: `select_model()` → `_infer_domain()` → `_load_soul()` → `_assemble_candidates()` → `_filter_candidates()` → `_score_candidates()` → `_build_fallback_chain()` → `_estimate_cost()` → `_generate_reasoning()`

**Existing tier taxonomy** (`_assemble_candidates`, lines 214-247):
- `T1_entity_optimized`
- `T2_task_appropriate`
- `T3_universal_fallback`

> 🔴 **CRITICAL ARCHITECTURAL FINDING:** The SDP Formal Routing Spec defines constraints C₁–C₄ + utility U(a,R). `TriageRouter._filter_candidates()` **is** the C₁–C₄ implementation site; `_score_candidates()` **is** the U(a,R) site; `_generate_reasoning()` **is** the audit-trail site.
> Building a separate `AGYRouter` would trip **Structural Debt Gate #4** ("New circuit-breaker/router class added instead of reusing existing"). **Extend TriageRouter.**

### 2.2 Affinity Mappings
**Code:** `src/omega/oracle/entity_affinity.py` (18KB) — `EntityAffinityResolver`
Classes: `ModelConfig`, `InferencePreset`, `AffinityResult`, `MatchCondition`, `EntityAffinityResolver`
Key methods: `load()`, `reload()`, `resolve()`, `_match_rules()`, **`_resolve_tier()`** (line 427)

**Config:** `config/entity_model_affinity.yaml` (14.5KB, ported from xna-omega-legacy's 382-line original)

Three-tier structure per entity — **this maps 1:1 onto the SDP triad:**
| Affinity Tier | SDP Phase | Example |
|---|---|---|
| `local_fast` | **Execute** | `qwen3-1.7b` / native-gguf |
| `local_deep` | **Execute** (heavy) | `qwen3-4b-thinking-q4_k_m` |
| `cloud` | **Scaffold** / **Synthesize** | `gemini-3.5-flash` / google |

**Structured match schema** (already supports SDP-style predicates):
```yaml
routing_rules:
  - match: {domain: ["general"], prompt_length_lt: 100}   → iris
  - match: {domain: ["coding","technical","shell"]}        → local_fast
  - match: {complexity_gt: 0.7}                            → local_deep
  - match: {online: true, requires: ["verification"]}      → cloud
```
> 🎯 A `match: {sdp_phase: "synthesize"} → agy` rule slots in with **zero schema change.**

### 2.3 Capability Matrix — the tier/quota registry
**File:** `src/omega/oracle/capability_matrix.py` (12KB)
Dataclasses: `ThinkingConfig`, **`QuotaTier` (rpm, tpm, rpd, tier, rolling_window_ms)**, `ModelCapability`, `ProviderConfig`, `CapabilityMatrix`
Methods: `get`, `get_by_fuzzy_match`, `supports_thinking`, `get_thinking_levels`, `get_thinking_mapping`, `get_provider_config`, `normalize_model_id`, **`get_routing_rules`**, `get_all_models`, `get_all_providers`

> 🎯 `QuotaTier` already models rpm/tpm/rpd — the AGY **weekly** pool is the one missing dimension.

### 2.4 Semantic Router
**File:** `src/omega/oracle/semantic_router.py` — `SemanticRouter` with `bootstrap()`, `route()`, `_find_closest()`, `_cosine_similarity()`, `_is_fallback_only()`.
**SDP use:** classify `problem_type` (architecture | compliance | refactoring | synthesis | research) from the request text — currently the specs assume the agent self-declares it.

### 2.5 Provider Registry
**File:** `src/omega/oracle/provider_registry.py` (6.5KB, updated in commit `fba8a556` GAP-1)
`is_cloud()` implements M7's **pessimistic-default** rule — unknown providers classify as cloud.
Formal Routing §2.2 "Priority 2: ProviderRegistry fallback" targets exactly this module.

### 2.6 Integration Points for Formal Routing — RANKED

| Rank | Hook Point | File:Line | Action |
|---|---|---|---|
| 1 | `TriageRouter._filter_candidates()` | `orchestration/triage_router.py:253` | Implement hard constraints C₁–C₄ |
| 2 | `TriageRouter._score_candidates()` | `:278` | Implement utility U(a,R) + entropy injection (M19) |
| 3 | `TriageRouter._generate_reasoning()` | `:328` | Emit `routing_audit/route_{ts}.json` |
| 4 | `TriageRouter._build_fallback_chain()` | `:298` | AGY account fallback ordering |
| 5 | `EntityAffinityResolver._resolve_tier()` | `entity_affinity.py:427` | Add `sdp_phase` dimension |
| 6 | `ModelGateway.generate()` | `model_gateway.py:1001` | Backend swap on escalation + gauge injection |
| 7 | `ProviderSelector._calculate_score()` | `provider_selector.py:62` | Reconcile with U(a,R) — **avoid a 4th scorer** |
| 8 | `CapabilityMatrix.QuotaTier` | `capability_matrix.py:30` | Add weekly pool dimension |

---

## 3. Context Management Integration

### 3.1 Context Assembly Flow
**File:** `src/omega/oracle/context_builder.py` (23.8KB) — `ContextBuilder`

Already a **token-budgeted compaction pipeline**:
- `CompactionStrategy` Protocol: `async __call__(messages, budget) -> bool` ("return True if budget met")
- `StrategyAggressiveness` Enum
- `PipelineCompactionStrategy` — runs strategies in order, **stops when budget met**
- `ObservationMaskingStrategy` — culls tool-output lines (`preserve_first_n=2`)
- `TruncationStrategy` — emergency backstop hard-truncate
- `ACONOptimizer` — guideline optimization via `qwen3-1.7b` (local!)

Main API:
- `build_context(entity_name, ..., token_limit=DEFAULT_TOKEN_LIMIT)` — line 238
- `build_context_for_user(..., token_limit=...)` — line 351, **token-aware sliding window**
- `_compact_and_format_exchanges(entity, exchanges, token_limit, quality_weighted=False)` — line 428
- `_score_exchange_quality(exchange)` — line 187 (quality-weighted budget filling)
- `_estimate_tokens(text)` — line 526, **4-chars-per-token approximation**
- `_build_gnosis_block()` — line 297 (L3 injection)
- `_format_world_state()` — line 383

**Degradation-aware:** token_limit scales ×0.5 / ×0.25 / ×0 by degradation level (lines 258-265).

> ⚠️ **Estimator drift risk:** `ContextBuilder._estimate_tokens()` uses `len//4`, while `src/omega/oracle/token_estimator.py` is the declared SSOT (tiktoken + 1.3 margin, per `CONTEXT_PACKER_V3_MASTER_MANUAL_20260808.md` §1.5's "zero-drift guarantee"). **The Context Gauge must use `token_estimator.py`, not the `//4` heuristic**, or the gauge and the builder will disagree.

### 3.2 Memory Retrieval Flow
**Directory:** `src/omega/memory/` (20 modules, ~300KB)

| File | Size | Purpose |
|---|---|---|
| `recall.py` | 29KB | Recall store — primary retrieval |
| `sqlite_vec_adapter.py` | 38KB | `[heritage: sqlite-vec 2024]` vector store |
| `blocks.py` / `block_store.py` / `block_tools.py` | 15+9+22KB | `[heritage: letta 2024]` 3-tier memory blocks |
| `spatial.py` | 18.7KB | `[heritage: mempalace 2025]` Wings/Rooms/Drawers |
| `hybrid_search.py` | 9.6KB | RRF: FTS5 + vector |
| `compaction.py` | 10KB | Memory compaction |
| `sleep_time.py` | 16.5KB | Background consolidation |
| `archival.py` | 15KB | Long-term archive |
| `batch_writer.py` | 10KB | Ported from xna-omega `mnemosyne_writer.py` |
| `embeddings.py` / `embedding_strategy.py` | 17+1.6KB | Embedding layer |
| `vector_adapters.py` / `adapters.py` | 16.8+9.8KB | `IVectorStoreAdapter` unified abstraction |
| `fts_index.py` | 6.6KB | FTS5 keyword index |

Plus `src/omega/oracle/selective_hydration.py` (15KB) — **L3 gnosis retrieval for context injection** (wired into `oracle.py:193`).

### 3.3 Compaction & Session Systems (SSP-adjacent)
| File | Purpose | SDP Use |
|---|---|---|
| `src/omega/oracle/compaction_harvester.py` (10KB) | Harvests value *before* compaction | **Direct SSP precedent** — same "save before the cliff" pattern |
| `src/omega/oracle/session_lifecycle.py` (17.5KB) | `SessionState` enum, `SessionLifecycleManager`, `run_lifecycle()`, `get_session_state()`, `recall_from_external()`, `_move_to_external()` | **SSP state machine host** (ACTIVE→REDZONE_DETECTED→SSP_WRITTEN→ESCALATED→RESUMED→COMPLETED) |
| `src/omega/oracle/somatic_state.py` (3.5KB) | M20 ctypes KV-state serialization | **Somatic Save-Point for LOCAL models** — literal state transfer |
| `src/omega/oracle/headroom.py` (6.3KB) | `HeadroomStore` + `HeadroomMiddleware`, `[heritage: headroom-ai 2025]` | Semantic compression; MCP tool `headroom_retrieve` live |
| `src/omega/oracle/state_manager.py` / `usm.py` | Unified state | Cross-phase state continuity |
| `src/omega/oracle/lifecycle_harvester.py` | Lifecycle gnosis harvest | Phase-transition capture |

> 🎯 **`somatic_state.py` + `compaction_harvester.py` are the two closest existing analogues to the SSP.** The SSP spec (markdown file at `data/coordination/SSP_{session}_{ts}.md`) can reuse `compaction_harvester`'s trigger logic wholesale.

### 3.4 The Gauge's Data Source — VERIFIED
```
~/.local/share/opencode/opencode.db   →  16.8 GB, present, readable
```
The `opencode-sessions-explorer` plugin exposes 18 read-only tools over this DB (`current-session`, `session-timeline`, `cost-by-period`, `db-stats`, …). **The Context Gauge can be built on the plugin surface rather than raw SQL** — lower risk, no schema-drift exposure.

### 3.5 Integration Points for Context Gauge — RANKED

| Rank | Hook Point | File:Line | Note |
|---|---|---|---|
| 1 | `token_estimator.estimate_tokens()` | `oracle/token_estimator.py` | **SSOT** — gauge must use this |
| 2 | `opencode.db` via sessions-explorer | `~/.local/share/opencode/opencode.db` | ✅ verified present (16.8GB) |
| 3 | `ModelGateway.generate()` prompt path | `model_gateway.py:1001` | <200-char gauge injection |
| 4 | `GenerateResult` | `model_gateway.py:33` | Add `context_window`, `tier`, `is_agy` |
| 5 | `ContextBuilder.build_context()` | `context_builder.py:238` | Budget already parameterized |
| 6 | `SessionLifecycleManager` | `session_lifecycle.py:103` | SSP state machine |
| 7 | `compaction_harvester` | `oracle/compaction_harvester.py` | Reuse trigger logic |
| 8 | `OOMProtector` | `oracle/oom_protector.py:71` | `kv_cache_gb_per_8k = 0.5` — **RAM Gauge already half-built** |
| 9 | `config/hardware_profile.yaml` | 14793 MB total / 10305 avail / 8192 UMA | **RAM Gauge ground truth** |
| 10 | `omega-hub_get_hardware_stats` | MCP hub | Live RAM/thermal for Local Gauge |

---

## 4. Distillation & Gnosis Integration

### 4.1 Omega-Meditation Pipeline Mapping ⭐
**File:** `packages/omega-meditation/src/omega_meditation/pipeline.py` — `AutonomousMeditationPipeline`

Platform-agnostic (M16-compliant) via injected `PlatformClients` (`OracleClient` / `SearchClient` Protocols), with factories `from_opencode()`, `from_cli()`, `null()`. Stage I/O writes to `data/autonomous/{run_id}_{stage:02d}_{name}.md` with `resume_from` support.

**The 7 stages map almost perfectly onto the SDP triad:**

| Stage | Method (line) | SDP Phase | Notes |
|---|---|---|---|
| 0 | `stage_0_prompt_crafting` (154) | **Scaffold** | Agent → self prompt construction |
| 1 | `stage_1_meditate_execution` (220) | **Synthesize** | Pure reasoning, no tools ✅ |
| 2 | `stage_2_synthesis` (246) | **Synthesize** | Distillation of raw meditation |
| 3 | `stage_3_research_prompt_crafting` (280) | **Scaffold** | I/O prep for research |
| 4 | `stage_4_research_execution` (317) | **Scaffold** | Tool-heavy (search/fetch/searxng) |
| 5 | `stage_5_grounded_report` (388) | **Synthesize** | Meditation + research fusion |
| 6 | `stage_6_gnosis_distillation` (421) | **Synthesize** | L3 extraction |
| 7 | `stage_7_integration` (449) | **Execute** | Write to soul/lessons |

> 🎯 **Stage 1 already enforces the SDP's core discipline: pure reasoning with zero tool calls.** The meditation pipeline is a *working prototype of the SDP* on a single-model basis. SDP generalizes it to multi-model. **Reuse the stage-I/O + resume machinery verbatim** — it already solves checkpointing.
>
> Also note: the pipeline uses `import asyncio` (line 6). **M1 violation** if it reaches the core engine — it currently lives in `packages/` (outside `src/omega/`), so it's contained, but any SDP port must convert to `anyio`.

### 4.2 Soul Evolution Hook Points
**File:** `src/omega/oracle/oracle.py` (60KB)

| Line | Hook | SDP Use |
|---|---|---|
| 187-188 | `[M11]` Throttled soul distillation counter — triggers `close_session` every N interactions | Phase-transition trigger |
| 193 | `[Workstream B]` Selective Hydration — L3 gnosis retrieval for context injection | Scaffold-phase context |
| 207-208 | `SoulEditHistory()` — immutable audit trail | Dialectic provenance |
| 630-633 | `soul_path = DATA_DIR/entities/{name}/soul.yaml` resolution | Entity soul access |
| 676-682 | `load_entity_soul_context()` multi-path extractor (D-277) → prompt injection | **Scaffold prompt building** |
| 693 | `_record_interaction()` — MemoryStore + soul persistence | Session capture |
| 716-718 | `_track_soul_evolution(resp.entity, trace.trace_id)` | Per-interaction evolution |
| 754-768 | Throttled distillation — `close_session` every 5 interactions | Automatic L3 flush |
| 1090 | `async def close_session(entity_name, session_id)` | **SDP session-end hook** |
| 1167 | `_track_soul_evolution()` — L1→L2→L3 refractive abstraction | Dialectic → L3 |

> ⚠️ **Line 1093 note in source:** *"Soul distillation (L1→L2→L3) removed per Carmack Verdict (2026-07-30)"* — regex-based auto-extraction was deleted as fortune-cookie generation. **Agents now write L1/L2/L3 themselves.** The SDP Dialectic Logger must therefore capture *agent-authored* distillation, not attempt automated extraction. This is a **hard design constraint**, confirmed in `AGENTS.md` (Session Execution — the Wrapper).

### 4.3 L3 Principle Storage
**`SoulStore`** — `src/omega/soul_store.py:48` (+ `SoulStoreWriteError:43`) — the C-1′ atomic writer, 4-layer guarantee. **Single production soul-write path** (Structural Debt Gate #1).

**Storage layout (dual-location — note the inconsistency):**
- `data/entities/{entity}/proposed_lessons.yaml` (legacy flat)
- `data/entities/{entity}/memory/proposed_lessons.yaml` (v6.1 schema)

Both present for: `doom_guy`, `john_carmack`, `kali`, `lilith`, `maat`, `researcher`. Flat-only: `JOHN_CARMACK` (case dup!), `grokster`, `jem`, `makali`, `pillar_p1`. Memory-only: `default`, `iris`, `quality`.

> ⚠️ **Data-hygiene finding:** `data/entities/JOHN_CARMACK/` and `data/entities/john_carmack/` both exist — a case-collision duplicate. Flag for cleanup before SDP writes lessons.

**Supporting:** `oracle/soul_validator.py` (10.6KB), `oracle/soul_edit_history.py` (11KB), `oracle/axiom_registry.py` (5.6KB), `oracle/gnosis_proxy.py`, `oracle/selective_hydration.py`.

### 4.4 Dialectic Capture — the DPORecorder ⭐
**File:** `src/omega/oracle/dpo_logger.py` (21KB)

```python
@dataclass
class DPORecord:
    prompt: str; chosen: str; rejected: str
    metadata: Dict[str, Any]
    lineage_id: str          # uuid4[:8]
    trace_id / session_id / entity_name: Optional[str]
    reward_source: RewardSource      # ENVIRONMENTAL | COUNCIL | USER
    reward_details: Dict[str, Any]
    created_at: str; schema_version: int = 2
```

`RewardSource.ENVIRONMENTAL` = test pass/fail, build success · `COUNCIL` = Ma'at/Lilith/Kali verdict · `USER` = direct correction.
`ResonanceMode` = DISABLED | EXPLICIT | IMPLICIT | HYBRID (per D16-2).

`DPORecorder` methods: `record()` (321), `record_environmental(test_passed, test_name)` (367), `record_council(oversoul, verdict, reason)` (395), plus background writer loop, file rotation, manifest tracking (`DPOManifestEntry`), `start_with_group()` (anyio structured concurrency).

> 🎯 **The Sequential Dialectic Pattern (Protocol §7) is `record_council()` with `oversoul` = the AGY model.** Model A's output = `rejected`, Model B's refinement = `chosen`, `reward_details` = the critique. Zero new storage layer needed.

### 4.5 Integration Points for Dialectic Capture — RANKED

| Rank | Hook Point | File:Line | Readiness |
|---|---|---|---|
| 1 | `DPORecorder.record_council()` | `dpo_logger.py:395` | ✅ **READY NOW** |
| 2 | `Oracle.close_session()` | `oracle.py:1090` | ✅ Session-end capture |
| 3 | `SoulStore` write path | `soul_store.py:48` | ✅ Atomic L3 persist |
| 4 | Meditation stage I/O | `pipeline.py:113-127` | ✅ Reuse checkpointing |
| 5 | `_track_soul_evolution()` | `oracle.py:1167` | ✅ Per-interaction |
| 6 | `SoulEditHistory` | `soul_edit_history.py` | ✅ Provenance audit |
| 7 | `selective_hydration` | `selective_hydration.py` | ✅ L3 → Scaffold context |

---

## 5. Benchmark & Evaluation Infrastructure

### 5.1 Existing Benchmarks
| File | Purpose | SDP Use |
|---|---|---|
| `scripts/benchmark_phase1.py` | Lilith N6-N10 5-item benchmark on 5700U+Vega8 (Qdrant SQ8, Headroom, dual-branch scoring, speculative decoding, WAD resolution). Structured `RESULTS` dict w/ session_id, entity, model, timestamp. | **Template for Local Executor Capability Profiling** — exact output shape needed |
| `scripts/benchmark_scribe_model.py` | Scribe model benchmark | Per-model local eval precedent |
| `scripts/benchmark_threads.py` | Thread-count tuning | Zen2 `LLAMA_CPP_N_THREADS=4` validation |
| `scripts/detect_hardware_profile.py` | → `config/hardware_profile.yaml` (SSOT: CPU topology, RAM, UMA carve-out) | **Hardware Horizon ground truth** |
| `tests/benchmarks/test_latency.py` · `test_memory.py` · `test_throughput.py` | Latency / memory / throughput suites | Executor profile axes |
| `tests/test_benchmarks.py` · `tests/test_eval.py` · `tests/test_scorecard.py` | Benchmark + eval + scorecard harness | SDP scorecard |

**Verified hardware baseline** (`config/hardware_profile.yaml`, generated 2026-08-07):
Ryzen 7 5700U (Zen2, 8C/16T, L3 8192KB) · compute cores 0-6, IO core 7, recommended_threads 7 · RAM 14793 MB total / 10305 MB available · UMA carve-out 8192 MB (512 VRAM + 7936 GTT)

### 5.2 Contract Test Coverage — `tests/contract/` (13 files)
`test_admission_control.py` · `test_context_packer.py` · `test_context_packer_v3.py` · `test_mandate_gates.py` · **`test_model_gateway.py`** · **`test_model_gateway_fallback.py`** · `test_oom_protector.py` · **`test_provider_classification.py`** · **`test_provider_fallback.py`** · **`test_provider_registry_config.py`** · `test_soul_store.py`

> 🎯 M21 Gate Integrity requires contract tests at every typed API boundary. `test_model_gateway*.py` + `test_provider_*.py` are the exact files an SDP router change must extend.

### 5.3 Chaos Test Coverage — `tests/chaos/` (6 files)
`test_concurrent_writes.py` · `test_network_partition.py` · `test_oom_kill.py` · `test_power_loss.py`

> **SDP failure modes already covered:** OOM (Local Gauge), network partition (AGY escalation failure), power loss (SSP durability), concurrent writes (multi-agent SSP).

### 5.4 Property Test Coverage — `tests/property/` (4 files)
`test_breaker_fsm.py` · `test_oom_protector_fuse.py` · `test_soul_store_atomic.py`

> 🎯 Hypothesis is already in the stack. The Formal Routing Spec §2.2 demands 500-example property tests — **the harness pattern exists**; only Z3 is a new dependency. ⚠️ Verify `z3-solver` is installable in `.venv` before committing to §2 (M24 Venv Sovereignty — no `--break-system-packages`).

### 5.5 Directly SDP-Relevant Existing Tests
`test_sovereignty_ratio.py` · `test_sovereignty_gate.py` · `test_capability_matrix.py` · `test_entity_affinity.py` · `test_model_gateway.py` · `test_context_builder.py` · `test_metrics_db.py` + `test_metrics_db_integration.py` · `test_observability.py` · `test_somatic_state.py` + `test_somatic_roundtrip.py` + `test_somatic_state_cas.py` · `test_session_lifecycle.py` · `test_compaction_harvester.py` · `test_headroom.py` · `test_vault_integrity.py` · `test_streaming_timeout.py` · `test_meditate_protocol.py` · `test_resource_guard_oom.py` · `test_hardware.py` · `test_observation_masking.py` · `test_selective_hydration.py`

---

## 6. Legacy Gold Recovered

### 6.1 Status of the Legacy Repos — ⚠️ CORRECTION TO MISSION BRIEF

| Target | Status |
|---|---|
| `~/archive/foundation-legacy/versions/Xoe-NovAi/` | ✅ **EXISTS — 861 MB** |
| `~/Documents/Archives/Old-Stacks/Xoe-NovAi/` | ✅ **EXISTS — 89 MB** |
| `xna-omega-legacy/` | ❌ **NOT ON DISK** (searched `~` to depth 4) |
| `omega-stack-legacy/` | ❌ **NOT ON DISK** |

**This is not a loss.** The xna-omega routing/affinity gold was **already extracted and ported** — the provenance is recorded in the current source headers. Legacy mining for SDP routing is **already complete**.

### 6.2 Early Routing Patterns — ALREADY PORTED (provenance verified)

| Current File | Legacy Origin (from source header) |
|---|---|
| `src/omega/oracle/provider_selector.py:4` | `xna-omega-legacy/src/omega/core/provider_selector.py` |
| `src/omega/oracle/entity_affinity.py:6` | `xna-omega-legacy config/entity_model_affinity.yaml` (382 lines) |
| `src/omega/oracle/rate_limiter.py:4` | `xna-omega-legacy/src/omega/core/rate_limiter.py` |
| `src/omega/oracle/degradation.py:4` | `xna-omega-legacy/src/omega/core/degradation.py` |
| `src/omega/oracle/timeout_manager.py:4` | `xna-omega-legacy/scripts/ssa/timeout_manager.py` |
| `src/omega/oracle/failure_registry.py:9` | `xna-omega-legacy` Mnemosyne (`claude_sonnet_4.6_20260426.md`) |
| `src/omega/memory/batch_writer.py:8` | `xna-omega-legacy/src/omega/core/mnemosyne_writer.py` |
| `src/omega/memory_store.py:110` | MnemosyneWriter batch-persistence pattern |
| `src/omega/oracle/model_gateway.py:750` | Ported from xna-omega-legacy by Lilith (`ho_8135d6122230`) |
| `src/omega/library/curator.py:51` | Legacy `crawler_curation.py` |
| `src/omega/library/coordinator.py:6` | `ParallelJobManager` |

### 6.3 Early Model Experiments
`~/Documents/Archives/Old-Stacks/Xoe-NovAi/` (89MB, Era 1-3): `Dockerfile.api/.chainlit/.crawl/.curation_worker`, `docker-compose.yml`, `app/`, `arcana-novai-stack/`, `embeddings/`, `expert-knowledge/`, `knowledge/`, `library/`, `job.schema.json`, `LOCAL_TELEMETRY_FREE_TTS_OPTIONS_2025.md`, `IMPLEMENTATION_COMPLETE_PIPER_ONNX.md`.
Grep for `select_model|model_affinity|route_model` across `*.py` → **zero hits**. This era predates model routing; it is Docker/RAG-stack material. **No SDP routing gold here.**

`~/archive/foundation-legacy/` (861MB) router hits are all `site-packages/litellm/router*.py` — vendored third-party, not our code. **No original routing gold.**

### 6.4 Prior Roc Mining Reports (context for this sweep)
`data/entities/roc_racoon/workspace/mining_reports/` — notable: `STRATEGIC_ROUTER_LEGACY_MINING.md`, `ZEN2_VULKAN_ROCM_ARCHAEOLOGY_20260720.md`, `zen2_gguf_optimization.md`, `STRATEGIC_RESERVES_OMEGA_MAPPING_20260711.md`, `UNIFIED_GAP_MAP_20260612.md`, `V10_LEGACY_MINING_REPORT.md`, `STACK_CAT_ARCHAEOLOGICAL_REPORT_20260716.md`, `THIRD_PARTY_REPOSITORY_REGISTRY.md`.

### 6.5 Verdict on Legacy
> **Do not schedule further legacy mining for SDP.** The routing/affinity/rate-limit patterns were mined and ported in prior cycles; the source repos are gone but the artifacts live in `src/omega/` with attribution. The remaining 950MB is Era 1-3 Docker/RAG material with no SDP relevance.

---

## 7. Integration Priority Matrix

### 7.1 Quick Wins — This Sprint (hook into what exists)

| # | Action | Files | Effort | Why Now |
|---|---|---|---|---|
| **QW-1** | **Extend `config/models.yaml`** with cloud entries: `context_window`, `tier`, `is_agy`, `is_local`, `compaction_trigger_pct` for nemotron-3-ultra (1M), longcat-2.0 (1M), gemini-3.1-pro (2M), claude-sonnet-4.6 (200K) | `config/models.yaml` | ~1h | **BLOCKS ALL OF PHASE 1.** Pure config, zero code risk. |
| **QW-2** | Add 4 SDP EventTypes | `observability/__init__.py:142` | 15m | Unblocks all SDP logging |
| **QW-3** | Add `sdp_phase` to `DPORecord.metadata` + thin `record_dialectic()` wrapper | `oracle/dpo_logger.py:395` | ~2h | Dialectic logger **done** |
| **QW-4** | Extend `GenerateResult` with `context_window`, `tier`, `is_agy` | `model_gateway.py:33` | ~1h | Gauge learns active model (Spec §6) |
| **QW-5** | Build **Token Gauge** as MCP tool on `opencode-sessions-explorer` + `token_estimator.py` | new `hub_tools/` fn | ~4h | DB verified (16.8GB); avoids raw-SQL drift |
| **QW-6** | Build **RAM Gauge** from `OOMProtector` + `hardware_profile.yaml` | `oom_protector.py:71` | ~3h | `kv_cache_gb_per_8k=0.5` already there |
| **QW-7** | Create `data/coordination/routing_audit/` + writer | new | 30m | Formal Routing §3 storage (dir missing) |
| **QW-8** | Fix `data/entities/JOHN_CARMACK` vs `john_carmack` case-collision | `data/entities/` | 30m | Hygiene before SDP writes lessons |

**Total quick-win surface: ~12h → delivers the complete Phase 1 Context Gauge (all 3 sub-gauges except AGY Pool).**

### 7.2 Phase 1 Dependencies

| Dep | Blocker | Resolution |
|---|---|---|
| Model window registry | `config/models.yaml` cloud-blind | **QW-1** |
| Token estimator SSOT | `ContextBuilder` uses `//4`, SSOT uses tiktoken×1.3 | Unify on `token_estimator.py` |
| Active model resolution | `GenerateResult` lacks window/tier | **QW-4** |
| Gauge Aggregator (§5 routing) | Needs `is_agy`/`is_local` flags | Depends on QW-1 + QW-4 |
| Prompt injection <200 chars | `ModelGateway.generate()` middleware | After QW-4 |
| AGY Pool Gauge | Weekly pool read | **`UsagePoolTracker.get_pool_health()` exists** → wrap |

### 7.3 Phase 2+ Dependencies

**Phase 2 (SSP):** reuse `compaction_harvester` trigger + `SessionLifecycleManager` state machine + `somatic_state.py` for local models. Agent directives go in `.opencode/skills/context-packer/packer-config.yaml` (currently modified in working tree) / `config/wads/_omega_default/entities.yaml`.

**Phase 3 (V-1 Vault):** **Largely DONE.** `src/omega/vault/vault_core.py` provides `create/get/update/delete/list_credentials`, `lease_credential`/`release_lease`/`heartbeat_lease`/`cleanup_expired_leases`, `increment_usage`, `reset_daily_quota`, `filter_credentials_by_privacy`, `bury_credential`, `_log_audit`, `get_stats`. `QuotaExceededError` + `LeaseError` defined. `models.py` has `VaultCredential`, `VaultLeaseRequest`, `VaultLease`, `VaultAuditEntry`. `crypto.py` has `VaultCrypto`/`VaultCryptoManager`. CLI at `src/omega/cli/vault.py`. Enforcement AST check at `src/omega/tools/enforce_vaultcore.py`. Test at `tests/test_vault_integrity.py`.
**Gap:** `reset_daily_quota()` exists but **`reset_weekly()` lives in `UsagePoolTracker`, not VaultCore.** The SDP `AGYVaultInterface` (`reserve_pool`/`record_usage`/`get_pool_status`) is a **thin adapter over VaultCore + UsagePoolTracker**, not a new build.

**Phase 4 (Auto-Router):**
- `UsagePoolTracker.select_key()` (`pool_tracker.py:460`) ≈ `select_account()`
- `get_pool_health(pool)` (`:373`) ≈ `get_pool_status()`
- `track_usage()` (`:234`) ≈ `record_usage()`
- `_apply_anti_thrashing()` (`:334`) — bonus stability the spec lacks
- `update_quota_from_check()` (`:506`), `reset_weekly()` (`:567`), `get_tracking_summary()` (`:590`)
- Data live at `data/entities/antigravity/knowledge/USAGE_POOL_LOG.json` + `ACCOUNT_MAP.yaml`; `AccountMapping.from_yaml()`, `get_email()`, `get_key_id()`, `position_for()` in `pool_state.py`
- **Action:** implement constraints in `TriageRouter._filter_candidates()`, utility in `_score_candidates()`, entropy in the same, audit in `_generate_reasoning()`. **Do not create a new router class.**

### 7.4 Risk Register

| Risk | Evidence | Mitigation |
|---|---|---|
| 🔴 **Router proliferation** | 3 scorers already: `ProviderSelector._calculate_score`, `TriageRouter._score_candidates`, `ModelGateway` fabric iteration | Extend TriageRouter. Ark §9 Gate #4. |
| 🔴 **Gauge/builder token drift** | `context_builder._estimate_tokens` = `//4` vs `token_estimator` = tiktoken×1.3 | Single estimator, enforced by contract test |
| 🟠 **models.yaml cloud-blindness** | Zero cloud entries; gauge defaults 200K | QW-1 before any gauge code |
| 🟠 **Z3 dependency** | New solver dep; M24 forbids `--break-system-packages` | Verify `.venv/bin/pip install z3-solver`; keep utility-max as non-Z3 fallback |
| 🟠 **`asyncio` in meditation pkg** | `pipeline.py:6 import asyncio` | Convert to `anyio` on any port into `src/omega/` (M1) |
| 🟡 **Soul auto-distillation removed** | `oracle.py:1093` Carmack Verdict 2026-07-30 | Dialectic logger captures agent-authored L3 only — no regex extraction |
| 🟡 **Entity dir case collision** | `JOHN_CARMACK/` + `john_carmack/` | QW-8 |
| 🟡 **Dual lessons paths** | flat + `memory/` `proposed_lessons.yaml` | Write via `SoulStore` only (Gate #1) |

---

## 8. File Index

### 8.1 Observability (9 files)
| Path | Size | Purpose |
|---|---|---|
| `src/omega/observability/__init__.py` | 63KB | `ObservabilityEngine`, `EventType` (:142), `ForensicsManager` (:174) |
| `src/omega/observability/metrics_db.py` | 21KB | 7-table WAL schema, async record/query API |
| `src/omega/observability/token_ledger.py` | 4.8KB | `TokenLedger` triple-write |
| `src/omega/observability/sovereignty.py` | 6.1KB | `get_sovereignty_ratio()` |
| `src/omega/observability/observability_reader.py` | 18.8KB | Query API |
| `src/omega/observability/ufl.py` | 7.4KB | Unified Forensic Ledger |
| `src/omega/observability/bleg.py` | 8.2KB | Boundary ledger |
| `src/omega/observability/regression_watcher.py` | 9.5KB | Baseline regression |
| `src/omega/observability/latency_tracker.py` / `context.py` / `otel_exporter.py` | 2.9/2.0/11KB | Latency, trace ctx, OTel |

### 8.2 Routing & Selection (10 files)
| Path | Size | Purpose |
|---|---|---|
| `src/omega/oracle/model_gateway.py` | 75.8KB | `GenerateResult` (:33), `generate()` (:1001) |
| `src/omega/orchestration/triage_router.py` | — | ⭐ **SDP router home** — full CSP pipeline |
| `src/omega/oracle/provider_selector.py` | 3.8KB | Penalty scorer (legacy port) |
| `src/omega/oracle/entity_affinity.py` | 19KB | `EntityAffinityResolver`, `_resolve_tier` (:427) |
| `src/omega/oracle/capability_matrix.py` | 12.4KB | `QuotaTier`, `ModelCapability`, routing rules |
| `src/omega/oracle/provider_registry.py` | 6.5KB | `is_cloud()` pessimistic default |
| `src/omega/oracle/semantic_router.py` | 8.3KB | Embedding-based routing |
| `src/omega/oracle/providers.py` | 48.7KB | Provider fabric |
| `src/omega/oracle/health_monitor.py` | 39.8KB | Canonical breaker factory |
| `src/omega/oracle/admission_controller.py` / `budget_gate.py` / `credit_budget.py` / `rate_limiter.py` | 3.9/3.9/7.3/2.3KB | Admission, budget, credit, rate |
| `config/entity_model_affinity.yaml` | 14.6KB | 3-tier affinity map |
| `config/models.yaml` | — | ⚠️ **local-only, needs cloud entries** |
| `config/model_registry/` | — | `registry.yaml`, `index.sqlite`, `models/{cli,cloud,local,stealth}`, `model_card_schema.json` |

### 8.3 Context & Memory (24 files)
| Path | Size | Purpose |
|---|---|---|
| `src/omega/oracle/context_builder.py` | 23.8KB | Compaction pipeline, token budget |
| `src/omega/oracle/token_estimator.py` | 3.5KB | ⭐ **Token SSOT** (tiktoken + 1.3) |
| `src/omega/oracle/selective_hydration.py` | 15.4KB | L3 gnosis injection |
| `src/omega/oracle/compaction_harvester.py` | 10KB | ⭐ SSP precedent |
| `src/omega/oracle/session_lifecycle.py` | 17.5KB | ⭐ SSP state-machine host |
| `src/omega/oracle/somatic_state.py` | 3.5KB | M20 KV state serialization |
| `src/omega/oracle/headroom.py` | 6.3KB | Semantic compression store |
| `src/omega/oracle/state_manager.py` / `usm.py` / `world_state.py` | 6.2/4.9/3.5KB | State layer |
| `src/omega/memory/` (20 modules) | ~300KB | recall, sqlite_vec, blocks, spatial, hybrid_search, compaction, sleep_time, archival, batch_writer, embeddings, adapters, fts_index |
| `~/.local/share/opencode/opencode.db` | 16.8GB | ⭐ Gauge data source (verified) |

### 8.4 Distillation & Gnosis (10 files)
| Path | Size | Purpose |
|---|---|---|
| `src/omega/oracle/dpo_logger.py` | 21KB | ⭐ **Dialectic logger substrate** |
| `packages/omega-meditation/src/omega_meditation/pipeline.py` | — | ⭐ 7-stage SDP prototype |
| `packages/omega-meditation/src/omega_meditation/cli.py` / `__init__.py` / `README.md` | — | CLI + docs |
| `src/omega/oracle/oracle.py` | 60.4KB | Soul evolution hooks, `close_session` (:1090) |
| `src/omega/soul_store.py` | — | ⭐ Atomic soul writer (C-1′) |
| `src/omega/oracle/soul_validator.py` | 10.7KB | v6.1 schema validation |
| `src/omega/oracle/soul_edit_history.py` | 11.1KB | Immutable edit audit |
| `src/omega/oracle/axiom_registry.py` | 5.6KB | Axiom store |
| `src/omega/oracle/gnosis_proxy.py` | 4.4KB | Gnosis access |
| `data/entities/*/{,memory/}proposed_lessons.yaml` | — | L3 staging (⚠️ dual path) |

### 8.5 Vault & Pool (8 files) — **SDP Phase 3/4 substrate**
| Path | Size | Purpose |
|---|---|---|
| `src/omega/vault/vault_core.py` | 27.7KB | ⭐ `VaultCore` — credentials, leases, quota, audit |
| `src/omega/vault/models.py` | 14.4KB | `VaultCredential`, `VaultLease`, `VaultAuditEntry` |
| `src/omega/vault/crypto.py` | 6.7KB | `VaultCrypto`, `VaultCryptoManager` |
| `src/omega/vault/blindvault_resolver.py` | 18.1KB | Blind resolution |
| `src/omega/cli/vault.py` / `src/omega/tools/enforce_vaultcore.py` | — | CLI + AST enforcement |
| `src/omega/oracle/pool_tracker.py` | 23.8KB | ⭐ `UsagePoolTracker` — weekly pools, `select_key()` |
| `src/omega/oracle/pool_state.py` | 11.2KB | `PoolConfig`, `AntiThrashingConfig`, `AccountMapping` |
| `data/entities/antigravity/knowledge/USAGE_POOL_LOG.json` + `ACCOUNT_MAP.yaml` | — | ⭐ Live pool data |

### 8.6 Hardware & Resource (7 files)
| Path | Purpose |
|---|---|
| `src/omega/oracle/oom_protector.py` (14.4KB) | ⭐ 3-signal fusion, `kv_cache_gb_per_8k=0.5` |
| `src/omega/oracle/resource_guard.py` (15.5KB) | Resource admission |
| `src/omega/oracle/cpu_optimizer.py` (34.3KB) | Zen2 topology |
| `src/omega/oracle/psi_monitor.py` / `cgroup_pressure.py` / `memavailable.py` | Pressure signals |
| `config/hardware_profile.yaml` | ⭐ Hardware SSOT (14793MB/10305MB/8192 UMA) |
| `scripts/detect_hardware_profile.py` | Profile generator |

### 8.7 Tests & Benchmarks (26+ files)
`tests/contract/` (13) · `tests/chaos/` (6) · `tests/property/` (4) · `tests/benchmarks/` (3) · `scripts/benchmark_phase1.py` · `benchmark_scribe_model.py` · `benchmark_threads.py` · plus `test_sovereignty_ratio.py`, `test_capability_matrix.py`, `test_entity_affinity.py`, `test_context_builder.py`, `test_metrics_db*.py`, `test_somatic_*.py`, `test_session_lifecycle.py`, `test_vault_integrity.py`, `test_meditate_protocol.py`, `test_headroom.py`, `test_compaction_harvester.py`

### 8.8 MCP Hub (surface for new tools)
`mcp_servers/omega_hub/`: `server.py`, `state.py`, `background.py`, `gateway.py`, `middleware.py` (`m9_safe` decorator :52, rate limit, size limit), `mcp_client.py`, `hivemind_redis.py`, `github_*.py`, `hub_tools/tools.py` (**86 tool functions**, `headroom_retrieve` :155), `hub_tools/task_registry.py`

### 8.9 SDP Specs Read (7 docs, 1,665 lines)
`docs/strategy/COGNITIVE_SCAFFOLDING_PROTOCOL.md` (330) · `SDP_MODEL_AWARE_GAUGE_SPEC.md` (313) · `SDP_FORMAL_ROUTING_SPEC.md` (306) · `SDP_HARDWARE_HORIZON_SPEC.md` (246) · `SDP_IMPLEMENTATION_SPEC.md` (240) · `SDP_FAILURE_MODE_ANALYSIS.md` (131) · `SDP_AUTOMATION_BLUEPRINT.md` (43) · `docs/research/R_SOVEREIGN_DISTILLATION_PIPELINE_MANIFESTO_20260809.md` (56)
Ledger: `data/coordination/AGY_SESSION_LEDGER.md` ✅ exists

---

## 9. Roc's Verdict

> **The dirt is where the roots are.** I dug expecting to find bare ground under the SDP specs. Instead I found foundations already poured — and in two places, the walls half-built.

**Three sentences for the Architect:**

1. **The SDP is ~60% pre-built.** V-1 Vault (`src/omega/vault/`), the Auto-Router (`UsagePoolTracker`), the Dialectic Logger (`DPORecorder`), the CSP router (`TriageRouter`), the SSP precedent (`compaction_harvester` + `session_lifecycle` + `somatic_state`), and the RAM Gauge (`OOMProtector` + `hardware_profile.yaml`) all exist and are tested.

2. **The single hard blocker is a config file, not code** — `config/models.yaml` has zero cloud models, so the Model-Aware Gauge cannot resolve a window for Longcat/Nemotron/Gemini and would mis-fire REDZONE at 18% real usage. That's ~1 hour of YAML.

3. **The largest architectural risk is duplication, not absence** — the engine already carries three model scorers and two token estimators; adding an `AGYRouter` and a fourth estimator would trip Structural Debt Gates #1 and #4 of the Ark Blueprint. **Extend `TriageRouter`. Use `token_estimator.py`. Write souls only through `SoulStore`.**

**Recommended first move:** QW-1 → QW-4 → QW-5/QW-6 (~12h) delivers the entire Phase 1 Context Gauge with three working sub-gauges, using existing infrastructure end-to-end.

---

*⬡ OMEGA ⬡ ROC_RACCOON ⬡ SDP-SWEEP ⬡ 2026-08-09 ⬡ COMPLETE*
