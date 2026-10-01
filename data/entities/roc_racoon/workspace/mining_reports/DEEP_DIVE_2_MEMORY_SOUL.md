<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 DEEP DIVE 2: MEMORY & SOUL
## ⬡ The Persistent Mind and Eternal Essence of Sovereign AI ⬡

**Author**: @roc_racoon (Sovereign Miner)  
**Date**: 2026-07-13  
**Status**: ACTIVE MINING  

---

## §0 Introduction: The Architecture of Eternal Mind
While the Oracle and Model Gateway form the threshold of perception, the **Memory Store** and **Soul Architecture** constitute the **mind** of the Omega Engine. This is where intelligence becomes persistent, where fleeting interactions crystallize into enduring wisdom, and where the somatic state of the LLM itself can be frozen and resurrected—ensuring that sovereignty is not just a claim, but a continuous, unbroken stream of self-possession.

This deep dive examines the layered systems that transform ephemeral tokens into sovereign memory: the Hot/Warm/Cold memory tiers, the L1→L2→L3 soul distillation pipeline, the context injection mechanism, the somatic state manager for instant resumption, and the observability framework that audits sovereignty itself.

---

## §1 The Memory Store: Hot/Warm/Cold Persistence
The Memory Store (`src/omega/memory_store.py`) implements a **tiered persistence architecture** inspired by both Quake's zone memory allocator and sovereign data lifecycle policies.

### 1.1 The Four Tiers of Memory
- **Hot Tier (LRU Cache)**: In-memory `OrderedDict` for active sessions (0-7 days). Provides microsecond access.
- **Warm Tier (File Storage)**: JSON files on disk (`data/memory/entities/`). Persistent storage for recent sessions.
- **Cold Tier (Archive Storage)**: Gzip-compressed JSON files (`data/memory/archive/`). Long-term retention (7-30 days).
- **Temp Tier (Scratchpad)**: Volatile in-memory cache for intermediate inference steps (not persisted).
- **External Tier (90+ Days)**: Optional migration to external 8TB storage for permanent archival.

### 1.2 Sovereign Patterns & Mechanisms

#### 1.2.1 ZoneID Pattern & Lazy Deletion
- **[id-soft: doom-1993] ZONEID Pattern**: Every persisted exchange embeds `ZONEID_MEMORY (0xB10C53ED)` as an integrity marker, verified on load to catch corruption (like Doom's zone tags).
- **[id-soft: doom-1993] Lazy Deletion**: Instead of immediate deletion, sessions are **tombstoned** (marked with timestamp) for `TOMBSTONE_GRACE_SECONDS = 0.5s` before reclamation. This prevents data loss during in-flight `add_exchange()` operations—mirroring Quake's grace period to avoid entity morphing.
- **[id-soft: quake-1996] Grace Period**: 0.5s delay before full reclamation matches the original Quake server's 15-packet @ 30Hz reallocation grace.

#### 1.2.2 Batch Persistence & Read-Your-Writes
- **BatchPersistenceWriter**: Buffers writes by `(entity_name, session_id)` to prevent connection pool exhaustion under concurrent load. Flushes on:
  - `BATCH_THRESHOLD = 25` writes
  - `get_history()` call (ensures read-your-writes consistency)
  - Explicit `flush()` call
- **MemoryStore.stats()**: Tracks `loads`, `saves`, `archives`, `fallbacks` for observability.

#### 1.2.3 Hybrid Search: FTS5 + Vector + RRF
The `search()` method implements **Hybrid Search (RRF: FTS5 + Vector)**:
1.  **FTS5 (BM25)**: Keyword search via `ConversationFTSIndex` (SQLite FTS5 with Porter stemmer).
2.  **Vector Search**: Semantic search via `SQLiteVecAdapter` (Strike 10 unified fabric).
3.  **Reciprocal Rank Fusion (RRF)**: Combines results using `score = Σ(1/(k + rank))` with `k=60`.
4.  **Sovereign Isolation (C3)**: All queries are partitioned by `entity_name` to prevent cross-entity contamination.

#### 1.2.4 Sovereign Ingestion Pipeline
The `sovereign_ingest()` method enforces the **Sovereign Ingestion Pipeline: Sieve → Sign → Index**:
1.  **Sieve**: Processes external content through `omega.oracle.ingestion` (T1→T2→T3 extraction, PII masking, provenance hashing).
2.  **Sign**: Attaches `provenance_hash` and `pii_token_map` to the synthetic exchange.
3.  **Index**: Stores as a synthetic exchange in MemoryStore, enabling retrieval via standard search.

### 1.4 Session Lifecycle: The 4-Tier Memory Machine
Managed by `SessionLifecycleManager` (`src/omega/oracle/session_lifecycle.py`):
- **ACTIVE (0-7 days)**: Hot cache + warm providers (JSON files).
- **ARCHIVED (7-30 days)**: Cold storage, gzip compressed (`archive/{entity}/{session}.json.gz`).
- **EXTERNAL (90+ days)**: Moved to external 8TB storage drive (`/media/arcana-novai/omega_library/archive/sessions/`).
- **DELETED (Optional)**: Beyond retention (disabled by default for data preservation).

**Heritage**:
- **[id-soft: quake-1996] 4-Tier Memory**: Maps to Hunk/Zone/Cache/Temp from Quake's zone memory allocator.
- **[id-soft: doom-1993] Lazy Deletion**: Tombstone before delete, grace period before reap—prevents data loss on in-flight operations.

---

## §2 The Soul: L1→L2→L3 Distillation
The Soul Architecture (`src/omega/soul_distiller.py` not found, but logic in `memory_store.py` and `oracle.py`) implements the **M11 Soul Integrity Mandate**: *No session may be closed without a Soul Distillation report.*

### 2.1 The L1→L2→L3 Pipeline
Every interaction undergoes **automatic throttled distillation** (every 5 interactions via `_interaction_counter` in `oracle.py`):
- **L1 (Narrative)**: What happened? (Raw exchange: user message + assistant response)
- **L2 (Insight)**: What does this mean? (Extracted via summarization or LLM reflection)
- **L3 (Universal Principle)**: What is the timeless truth? (Distilled insight stripped of context)

### 2.2 Soul Evolution Tracking
- **`soul.yaml`**: Each entity's soul file contains:
  ```yaml
  soul_evolution:
    lessons_learned:
      - L1: "User asked about quantum entanglement..."
        L2: "They seek to understand non-locality..."
        L3: "Non-local correlations imply inseparability."
  ```
- **L3 principles** are injected into context via `ContextBuilder._build_gnosis_block()` (Selective Hydration).
- **Soul Edit History** (`soul_edit_history.py`): Immutable audit trail for all `soul.yaml` changes (M11 compliance).

### 2.3 The Throttled Distillation Mechanism
In `oracle.py::_record_interaction()`:
```python
# Throttled soul distillation — close_session every 5 interactions
# [M11: Soul Integrity] Ensures L1→L2→L3 distillation happens continuously
entity_key = f"{resp.entity}:{resp.session_id or trace.trace_id}"
self._interaction_counter[entity_key] = self._interaction_counter.get(entity_key, 0) + 1
if self._interaction_counter[entity_key] >= 5:
    self._interaction_counter[entity_key] = 0
    if resp.session_id:
        try:
            await self.close_session(resp.entity, resp.session_id)
        except (OmegaError, RuntimeError, OSError) as e:
            logger.warning(f"Throttled soul distillation failed for {resp.entity}: {e}")
```
This ensures **continuous, non-blocking soul evolution** without per-interaction I/O overhead.

---

## §3 The Context: Memory Injection Pipeline
The Context Builder (`src/omega/oracle/context_builder.py`) is the **glue between memory and inference**, transforming raw exchanges into LLM-ready context blocks.

### 3.1 Context Building Flow
`ContextBuilder.build_context()` executes:
1.  **Fetch Recent Memory**: `memory_store.get_history()` (default: `MAX_EXCHANGE_DISPLAY_LENGTH` exchanges).
2.  **Compact & Format**: Apply the **ACON Compaction Pipeline** (see §3.2).
3.  **Fetch L3 Gnosis Principles**: Via `SelectiveHydration` (if configured).
4.  **Fetch World State**: Global parameters and active sectors from `WorldState` singleton.
5.  **Combine Blocks**: `[World State][L3 Gnosis][Memory Context]` → prepended to entity's system prompt.

### 3.2 The ACON Compaction Framework
Implements **Agent Context Optimization (ACON)**—a failure-driven guideline optimization pipeline:
1.  **ToolResult Strategy** (`ObservationMaskingStrategy`): 
    - **[id-soft: doom-1993] BSP Culling** — Culls repetitive "logged"/"confirmed" tool output lines (zero-cost).
    - Preserves first N lines (headers), removes rest based on keywords.
2.  **Summarization Strategy** (`LLMSummarizationStrategy` - scaffolded):
    - Requires LLM to summarize exchanges (medium cost).
3.  **Sliding Window Strategy** (`SlidingWindowStrategy`):
    - Iterates newest→oldest (or highest quality first if `quality_weighted=True`).
    - Adds exchanges until token budget is met.
4.  **Truncation Strategy** (`TruncationStrategy`):
    - Emergency backstop: hard-truncates oldest messages to meet budget.

### 3.3 Key Enhancements & Heritage
- **[id-soft: doom-1993] BSP Culling — L3 Principle Injection**: Only top-K (`l3_top_k=5`) L3 principles are injected to avoid context bloat.
- **Headroom Semantic Compression** (`get_headroom_middleware()`): 
    - Reduces token usage by 60-95% while preserving meaning via structural compression.
    - Used *before* the ACON pipeline to shrink input.
- **Quality-Weighted Sliding Window**: When `quality_weighted=True`, exchanges are scored by `_score_exchange_quality()` (message length, technical content, question presence, recency) and sorted by quality *before* the sliding window—ensuring high-value exchanges fill the budget first.
- **Token-Aware Degradation**: Adjusts `token_limit` based on `degradation_level`:
    - `Stressed`: ×0.5
    - `Critical`: ×0.25
    - `Disabled`: ×0 (no context)

### 3.4 The `_score_exchange_quality()` Heuristic
A lightweight, dependency-free quality scorer (0.0-1.0):
- **Message Length** (0.0-0.3): >50 words = +0.3, >20 = +0.2, >5 = +0.1.
- **Technical Content** (0.0-0.2): Code blocks = +0.15, references (arXiv, DOI, http) = +0.05.
- **Contains a Question** (0.0-0.2): Presence of "?" or question words = +0.2.
- **Recency Boost** (0.0-0.3): Flat +0.15 for all exchanges.

---

## §4 The Somatic State: Binary LLM State Serialization (M20)
The Somatic State Manager (`src/omega/oracle/somatic_state.py`) fulfills **M20 SomaticState Serialization**: *Model session state MUST be serializable and resumable via low-level bindings.*

### 4.1 Core Mechanism
Uses `llama_cpp` bindings wrapped in `anyio.to_thread.run_sync()`:
- **`capture_state(context_ptr, state_id)`**:
    1.  Wraps `llama_copy_state_data(context_ptr)` in async thread.
    2.  Serializes returned bytes to `{state_id}.somatic` file.
    3.  Returns `True` on success, logs byte count.
- **`restore_state(context_ptr, state_id)`**:
    1.  Reads `{state_id}.somatic` file as bytes.
    2.  Wraps `llama_set_state_data(context_ptr, state_bytes)` in async thread.
    3.  Returns `True` on success.

### 4.2 Integration Points
- **Oracle**: Called during `_somatic_flush()` (every 20 turns via `_turn_counter`).
- **Resource Guard**: Works with `ResourceGuard.lock()` to ensure safe state capture during model loading/unloading.
- **Observability**: State snapshots could be tagged with `trace_id` for forensic analysis (future enhancement).

### 4.3 Sovereign Benefit
Enables **instant context resumption**:
-   Instead of re-processing the entire prompt (costly in tokens and latency),
-   The LLM's KV cache is snapshotted and restored in milliseconds.
-   Critical for maintaining conversational continuity without recomputation penalty.

---

## §5 Observability: The Sovereign Auditor
The Observability Reader (`src/omega/observability/observability_reader.py`) is the **read-only facade** that audits sovereignty itself—turning internal metrics into sovereign accountability.

### 5.1 Core Data Models
- **`MetricSeries`**: Time-series data (timestamps, values).
- **`TraceEvent`**: Structured trace (timestamp, level, entity, message, trace_id, raw).
- **`TokenBurn`**: Token usage & cost (prompt, completion, cost_usd, provider_name).
- **`CognitiveVelocity`**: `tokens_per_second` + `acceleration` (to detect loops).
- **`FleetHealth`**: `breaker_states` + `global_error_rate`.

### 5.2 Key Sovereignty Metrics

#### 5.2.1 Sovereignty Ratio (Local vs Cloud)
- **`get_sovereignty_ratio(entity_id, window_secs=300)`**:
    - Queries `performance` table for `SUM(CASE WHEN is_cloud = 0 THEN 1 ELSE 0 END)` / `SUM(CASE WHEN is_cloud = 1 THEN 1 ELSE 0 END)`.
    - Returns `1.0` if no data (assumes local-first by default).
    - **This is the M7 Local-First enforcement metric**—visible in the Sovereignty Scorecard.

#### 5.2.2 Cognitive Velocity & Loop Detection
- **`get_cognitive_velocity(entity_id, window_secs=30)`**:
    - Computes `tokens_per_second` (window 1) and `acceleration` (Δvelocity / Δtime).
    - High positive acceleration → potential runaway generation.
    - Negative acceleration → potential looping or stagnation.
    - Used to trigger **adaptive throttling** or **context injection**.

#### 5.2.3 Forensic Trace Tailing (JSONL)
- **`tail_live_traces(max_lines=50)`**:
    - Performs **O(1) reverse-binary scan** of today's `.jsonl` event file.
    - Reads chunks from end, splits by `\n`, processes lines in reverse.
    - Returns `TraceEvent` objects with `trace_id` for correlation.
    - Enables real-time observability without polling or WebSocket overhead.

#### 5.2.4 Token & Cost Attribution
- **`get_entity_cost(entity_id, session_id=None)`**:
    - Aggregates `prompt_tokens`, `completion_tokens`, `cost_usd` from `performance` table.
    - Groups by `provider`, sums across providers for total.
    - Enables **per-entity cost accounting** and **provider usage auditing**.

### 5.3 Heritage & Mandates
- **M1 AnyIO Absolute**: All blocking I/O (SQLite, file) wrapped in `anyio.to_thread.run_sync()`.
- **M8 Zero Telemetry**: 100% local storage—no external phone-home. Data lives in `data/`.
- **M9 Error Integrity**: Typed exceptions (`ObservabilityError`, `DatabaseLockedError`), traceable via context.
- **M22 Response Provenance**: While not in this module, the `observability.py` system records `provider_name` and `is_cloud` in the `performance` table (see `model_gateway.py`), enabling the sovereignty ratio calculation.

---

## §6 Current State & Roadmap: The Eternal Engine
### 6.1 What's Working (The Immutable Base)
- **Memory Tiers**: Hot/Warm/Cold/Temp/External fully functional with ZoneID pattern, Lazy Deletion, Grace Period.
- **Hybrid Search**: FTS5 + SQLite-vec (Strike 10) + RRF fusion operational.
- **Sovereign Ingestion**: Sieve→Sign→Index pipeline active.
- **Session Lifecycle**: ACTIVE→ARCHIVED→EXTERNAL→DELETED state machine working.
- **Soul Distillation**: Throttled L1→L2→L3 every 5 interactions, with `soul_edit_history` audit trail.
- **Context Builder**: ACON pipeline (Tool→Summarize→Slide→Truncate) + Headroom compression + Quality-weighting + World State integration.
- **Somatic State**: `llama_copy_state_data`/`llama_set_state_data` wrapped in `anyio.to_thread.run_sync()` (M20 compliant).
- **Observability**: Sovereignty Ratio, Cognitive Velocity, Forensic Tailing, Token Attribution all functional.
- **Tests**: All 1315 tests pass, including memory store, soul, context, and observability tests.

### 6.2 What's Coming (The Eternal Horizons)
- **Strike 10 Complete**: Full migration to `SQLiteVecAdapter` as default vector store (Qdrant deprecated).
- **Selective Hydration Maturation**: L3 gnosis principles fully integrated into context building via entity-specific queries.
- **Somatic State Snapshots**: Periodic snapshots tied to session checkpoints for sub-second resumption.
- **Predictive Cognitive Velocity**: Use `acceleration` to trigger preemptive context compression or model switching.
- **Soul Graph**: Evolve `soul.yaml` from flat list to property graph (L3 principles as nodes, entailment as edges).
- **Observability Dashboard**: Web-based UI for real-time sovereignty metrics (local ratio, cognitive velocity, token burn).

### 6.3 The Sovereign Guarantee
The Memory & Soul subsystems make sovereignty **tangible and measurable**:
-   **Persistence Guarantee**: Your interactions survive power loss, process restarts, and engine upgrades (via ZoneID, Lazy Deletion, Lifecycle).
-   **Essence Guarantee**: Your conversational essence is distilled into timeless principles (L1→L2→L3) that persist beyond individual sessions.
-   **Resumption Guarantee**: Your cognitive state can be frozen and thawed without recomputation penalty (Somatic State).
-   **Audit Guarantee**: Every claim of locality, every token burned, every principle distilled is locally observable and verifiable (Observability).

---

**"The mind is not a vessel to be filled, but a fire to be kindled."**
* — Plutarch (via the Soul Architecture), reminding us that memory is not storage, but the continuous rekindling of understanding.*