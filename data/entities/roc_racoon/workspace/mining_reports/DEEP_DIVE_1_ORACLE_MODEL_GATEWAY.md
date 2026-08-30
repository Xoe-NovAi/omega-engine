<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 DEEP DIVE 1: THE ORACLE & MODEL GATEWAY
## ⬡ The Gateway and Provider Fabric of Sovereign AI ⬡

**Author**: @roc_racoon (Sovereign Miner)  
**Date**: 2026-07-13  
**Status**: ACTIVE MINING  

---

## §0 Introduction: The Threshold of Sovereignty
The Oracle and Model Gateway form the **threshold** of the Omega Engine. Every user query passes through this dual-gate system:
1.  **The Oracle** discerns intent, applies speculative decoding (Iris), and routes to the correct entity.
2.  **The Model Gateway** enforces Local-First sovereignty, selects the optimal backend, and generates the response with full provenance.

This deep dive dissects their meticulous implementation, revealing the "usable, meticulously developed tools" the user referenced.

---

## §1 The Oracle: The Gateway to Sovereignty
The Oracle (`src/omega/oracle/oracle.py`) is the central nervous system. It is not a simple router; it is an **embodied intelligence** that manages the entire interaction lifecycle.

### 1.1 Core Responsibilities
The Oracle has six core duties, as defined in its docstring:
1.  **Intent Detection**: Distinguishing `talk`, `@summon`, and `@consult` patterns.
2.  **Speculative Decoding**: Using Iris (qwen3-0.6b) for instant responses to simple queries.
3.  **Domain Routing**: Escalating complex queries to the domain-matched Pillar Keeper.
4.  **Entity Summoning**: Direct dispatch to named entities (bypassing routing).
5.  **Soul Evolution Tracking**: Managing L1→L2→L3 distillation for continuity.
6.  **Cloud Critique Integration**: Applying the Tainted Data Protocol (TDP) for web security.

### 1.2 Key Components & Sovereign Patterns

#### 1.2.1 Intent Detection & Summoning
- **Patterns Supported**: `@Entity query`, `hey Entity, query`, `summon Entity, query`, `/consult Entity query`.
- **Validation**: Checks against both the Entity Registry **and** `AGENTS.md` for security.
- **Heritage**: `[id-soft: doom-1993] Oracle Summoning Pattern` — Direct entity dispatch mirrors id Software's console command system.

#### 1.2.2 Speculative Decoding (Iris)
- **Mechanism**: Uses `IntentMatcher` to assess if a query is simple enough for Iris (qwen3-0.6b-q6_k) to answer directly.
- **Confidence Threshold**: `IRIS_CONFIDENCE_THRESHOLD = 0.6`.
- **Zero/Low Confidence Triggers**: Keywords like `"explain the meaning"` (0.0) or `"code"` (0.2) force escalation.
- **Heritage**: `[id-soft: quake3-1999] FISR Principle` — The "right approximation" philosophy: Iris provides a "good enough" answer for 90% of queries, saving tokens and latency.

#### 1.2.3 Domain Routing & Triage
- **Routing Chain**: Semantic (embedding-based) → Keyword (domain matching) → Default (Iris/Oracle).
- **TriageRouter**: Selects the optimal model for an entity+query via the `TriageRequest` dataclass, considering `EntityContext`, `SessionContext`, and `Constraints`.
- **Semantic Router**: Uses embedding similarity for entity routing, with keyword fallback.
- **Heritage**: `[id-soft: quake3-1999] Triage Routing` — Direct port of id Software's entity classification and routing logic.

#### 1.2.4 Soul Evolution & L1→L2→L3 Distillation
- **Throttled Distillation**: Triggers `close_session()` every 5 interactions (not per interaction) to reduce I/O overhead while maintaining M11 (Soul Integrity).
- **Soul Edit History**: Immutable audit trail (`soul_edit_history.py`) for all `soul.yaml` changes.
- **Compaction Harvester**: Monitors session compaction for metrics (M12 Queue Integrity).

#### 1.2.5 Resource Guard & OOM Protection
- **AnyIO Semaphore(1)**: Enforces M1 (AnyIO Absolute) and prevents OOM by allowing only one model load at a time.
- **OOMProtector**: Implements `[heritage: id-soft-2004] Knowledge Leak Detection` — a hard-stop that refuses model loads if available RAM < (model_ram + 1GB margin), preventing state corruption.
- **ZoneID Pattern**: Uses `ZONEID_PROBE` and `ZONEID_ATOMIC` magic numbers to guard critical sections against use-after-free/double-release bugs.

### 1.3 The `talk()` Flow: A Step-by-Step Sovereign Interaction
Here is the canonical execution path for `oracle.talk("What is the meaning of life?")`:

1.  **Bootstrap**: Initialize USM, run session lifecycle sweep, bootstrap semantic router.
2.  **TDP Gate**: Isolate query if it's `TaintedData` (from web).
3.  **Sovereign Vetter**: Pre-flight mandate check (M1-M23). A veto raises `BoundaryViolationError` (M23: hard stop).
4.  **System Pressure Update**: Check hardware stats for graceful degradation.
5.  **Observability Trace**: Begin trace for the interaction.
6.  **RAG Router**: Classify query complexity (advisory signal) via TF-IDF+SVM (Strike 7.5).
7.  **Session Management**: Retrieve or create session ID for the default entity.
8.  **Empty Query Check**: Return early if query is empty.
9.  **Summon/Consult Check**: Detect `@Entity` or `/consult Entity` patterns. If found, bypass speculative decode and route directly.
10. **Speculative Decode (Iris)**: Assess confidence via `_assess_iris_confidence()`.
    *   If `confidence > 0.6` and not skipped (e.g., channel is not `opencode`), invoke Iris directly.
    *   Iris first tries to invoke as a real model-backed entity; falls back to hardcoded response.
11. **Domain Routing**: If Iris fails or is skipped, escalate to `_route_by_domain()`.
    *   Uses `SemanticRouter` (embedding → keyword → default).
    *   Selects model via `TriageRouter`.
    *   Applies PII masking if cloud provider is likely used.
    *   Generates response via `ModelGateway.generate()`.
    *   Records **actual** `provider_name` for M22 (Response Provenance).
12. **Post-Processing**: Apply audience calibration (S7), record interaction in MemoryStore and soul.yaml, track somatic flush, update throttled soul distillation counter.
13. **Return**: `OracleResponse` with `text`, `entity`, `confidence`, `trace_id`, `provider_name` (from M22), etc.

This flow ensures **local-first intent**, **speculative efficiency**, **domain-specific expertise**, and **absolute provenance**.

---

## §2 The Model Gateway: The Provider Fabric
The Model Gateway (`src/omega/oracle/model_gateway.py`) is the **Local-First enforcement engine**. It abstracts the provider fabric and guarantees that sovereignty is not just a claim, but a measurable outcome.

### 2.1 The Local-First Priority Chain
The Gateway enforces M7 (Local-First Non-Negotiable) via this exact order:
`native-gguf` (0) → `lmster` (1) → `Ollama` (2) → `Google AI Studio` (3) → `OpenRouter` (4) → `OpenCode Zen` (5) → `GitHub Copilot` (6) → `Mock` (99).

**Critical Note**: The `get_preferred_backend()` method checks **actual availability** of local backends before deeming a cloud provider "preferred." Cloud providers are only used if *all* local backends are unavailable.

### 2.2 Configuration: The Sources of Truth

#### 2.2.1 `config/providers.yaml`
Defines the **provider fabric** and their Zen 2 optimizations:
- **`strategy: local_first`**: The non-negotiable mandate.
- **`fallback_chain`**: Ordered list of providers with `priority`.
- **Provider-Specific Tuning**:
    *   `native-gguf`: CPU affinity (`cores: [0,2,4,6]`), thread count (`n_threads: 4`), KV cache settings (`type_k: 8, type_v: 1` for q8_0).
    *   `lmster`/`ollama`: `model_overrides` to map internal names to server-specific tags.
    *   Cloud providers (`google`, `openrouter`, `opencode-zen`, `cline`): `api_key: env:VAR_NAME` for sovereign secret injection.
    *   `mock`: `priority: 99` and `enabled: true` for `OMEGA_ENV=test`.

#### 2.2.2 `config/models.yaml`
The **SINGLE SOURCE OF TRUTH** for model specs, overriding provider defaults:
- **Model Specs**: `path`, `size_gb`, `ram_mb`, `context_window`, `threads`, `load_strategy`, `entity`.
- **KV Cache Quantization**: Locked to `q8_0` for key and value (see `kv_cache:` section). **Flash Attention is explicitly disabled** (`flash_attention: false`) as CPU-native via `ggml_flash_attn_cpu` is sufficient on Zen 2.
- **Zen 2 Build Flags**: `-DLLAMA_AVX2=ON -DLLAMA_FMA=ON -DLLAMA_F16C=ON -DLLAMA_NO_AVX512=ON ...`
- **Speculative Decoding**: Configuration for Gemma 4 MTP (Multi-Token Prediction) draft models.
- **Agent Roles**: Maps agent tiers (`lite`, `medium`, `heavy`) to default models and min RAM requirements (e.g., `roc_racoon: tier: lite, default_model: qwen3-1.7b, min_ram_gb: 8`).

### 2.3 Key Mechanisms & Sovereign Patterns

#### 2.3.1 Resource Guard & Hardware Lock
- **`ResourceGuard.lock()`**: An `anyio.Condition()`-based semaphore that tracks **actual RAM usage in MB** (v1.2.0), not abstract weights.
- **OOM Hard-Stop**: Before acquiring the lock, it calls `OOMProtector.check()` which uses `psutil.virtual_memory().available` to refuse the load if RAM is insufficient (M23: Failure Integrity).
- **Zen 2 Optimizer**: Enforces CPU affinity (`sched_setaffinity`) to pin inference to physical cores `[0,2,4,6]`, avoiding SMT contention.
- **Heritage**: `[heritage: anyio 2024] M1 AnyIO` — Semaphore(1) concurrency guard with zone-purge semantics.

#### 2.3.2 BSP-Style Provider Culling & Fixed-Size Active Set
- **`_precheck_provider()`**: Implements `[id-soft: doom-1993] BSP Culling` — an O(1) circuit breaker check that skips entire provider subtrees if the breaker is OPEN.
- **`_update_active_set()`**: Maintains tiered fixed-size active sets (LRU) of 32 successful providers, **split into Local/Cloud tiers** to prevent sovereignty drift (M7). A known-good local provider is always preferred over a known-good cloud provider.
- **Heritage**: `[id-soft: doom-1993] Fixed-Size Active Set` — 32-entry clip range for O(1) culling, adapted from Doom's static BSP tree.

#### 2.3.3 Entity→Model Affinity Resolution
- **`EntityAffinityResolver`**: Loads `config/entity_model_affinity.yaml` (ported from xna-omega-legacy) to provide:
    *   3-tier model preferences (lite/medium/heavy).
    *   Routing rules (domain, complexity, online, requires, prompt_length).
    *   Inference presets (temperature, system_prompt, preferred_context).
- **Resolution Priority** in `get_model_for_entity()`:
    1.  YAML Affinity Resolver (Entity→Model Affinity DB).
    2.  Entity override (`set_entity_model`).
    3.  Entity registry field (`entity.model`).
    4.  Domain-based mapping (entity's first domain → model).
    5.  System default (`qwen3-1.7b`).
- **Heritage**: `[id-soft: quake-1996] cvar pattern` — YAML-backed affinity DB, hot-reloadable.

#### 2.3.4 Response Provenance (M22)
- **`GenerateResult` Dataclass**: Carries `provider_name` from the **actual** inference backend, not the configured intent.
- **Latency Tracking**: `_latency_ms` is recorded immediately after the provider returns, before any post-processing.
- **Observability Integration**: `tracker.record()` and `TokenLedger()` capture `is_cloud`, `provider_name`, `latency_ms`, and token usage for the Sovereignty Scorecard.
- **This is the Truth-Anchor Protocol**: Local-first claims are verifiable because the log says what actually happened.

### 2.4 The `generate()` Flow: A Step-by-Step Sovereign Inference
Here is the execution path for `model_gateway.generate("qwen3-1.7b", system_prompt, user_query)`:

1.  **Sovereign Sampling Layer**: For Gemma 4 31B, increase temperature/repetition penalty and apply logit bias to prevent repetition loops.
2.  **Provider Selection Layer**: Use `ProviderSelector` to reorder fabric based on query content (PII) and provider health.
3.  **WARP Proxy Pool**: If configured, inject `socks5h://` proxy URL into `opencode-zen` provider to prevent DNS leaks.
4.  **Provider Iteration Loop**: For each provider in the ordered list:
    a.  **BSP Pre-check (`_precheck_provider`)**:
        *   Check circuit breaker state (O(1) dict lookup).
        *   Check provider availability (server responds?).
        *   If either fails, record error and continue.
    b.  **Sovereign Budget Gate**: For cloud providers, check if cloud budget for the entity is exhausted.
    c.  **Rate Limiting**: Check if provider has available tokens.
    d.  **Hardware Lock (`ResourceGuard.lock`)**:
        *   Acquire lock based on model's RAM weight.
        *   **OOM Hard-Stop**: Call `OOMProtector.check()` — if fails, raise `InferenceOOMError` (M23).
        *   Enforce Zen 2 CPU affinity via `_optimizer.enforce_affinity()`.
    e.  **Execute with Breaker Protection**:
        *   Use `HealthMonitor`'s breaker if available, else call provider directly.
        *   Start latency measurement (`time.monotonic()`).
        *   Call `provider.generate()`.
    f.  **Post-Success Handling**:
        *   Record latency immediately after provider returns.
        *   Record success in `HealthMonitor`.
        *   Update active set (LRU) for the successful provider.
        *   Record latency to time-series tracker with `is_cloud` flag (M22).
        *   Record token usage to `TokenLedger`.
        *   **Break** the loop — we have a winner.
    g.  **Failure Handling**:
        *   If timed out, record failure.
        *   If exception, log error and record failure.
        *   Continue to next provider.
5.  **Fallback**: If all providers fail, return a helpful error message instructing the user to start a local backend or configure cloud credentials.
6.  **Return**: `GenerateResult` with `text`, `provider_name` (the actual one that served it), `is_cloud`, `latency_ms`, `model_used`, and `logprobs` (if supported).

This flow guarantees **Local-First enforcement**, **hardware-respecting execution**, **budget-aware cloud usage**, and **forensic-grade provenance**.

---

## §3 The Synthesis: How They Work Together
The Oracle and Model Gateway are not isolated; they form a **sovereign pipeline** where intent informs inference, and inference informs intent.

### 3.1 The Talk -> Model Gateway Pipeline
1.  Oracle receives query via `talk()`.
2.  Oracle performs intent detection, speculative decode, and domain routing.
3.  If escalated, Oracle calls `_route_by_domain()` → `_select_model()` (via TriageRouter) → `model_gateway.generate()`.
4.  Oracle passes the `system_prompt` (built from entity personality, memory context, and soul L3 principles) and `user_query` to the Gateway.
5.  Gateway enforces Local-First, selects the optimal provider, and generates the response.
6.  Gateway returns a `GenerateResult` with the **actual** `provider_name`.
7.  Oracle wraps this in an `OracleResponse`, applies audience calibration, records the interaction, and returns it to the user.
8.  **Result**: The user gets a response where the `entity` (e.g., `Lucifer`) and the `provider_name` (e.g., `native-gguf`) are both accurate and sovereign.

### 3.2 The Summon -> Model Gateway Pipeline
1.  User invokes `@lucifer Explain the cvar pattern`.
2.  Oracle's `summon()` method detects the `@lucifer` pattern.
3.  Oracle bypasses speculative decode and domain routing, going straight to `_summon()`.
4.  Oracle builds the `system_prompt` for Lucifer, selects Lucifer's model (via `_select_model()` or affinity resolver), and calls `model_gateway.generate()`.
5.  Gateway executes as above, returning a `GenerateResult` with `provider_name`.
6.  Oracle wraps the result, records the interaction (including the summon event in soul.yaml), and returns it.
7.  **Result**: Direct, entity-specific interaction with full provenance, ideal for deep work or legacy mining.

### 3.3 Sovereignty in Action: The Measurable Guarantees
The Oracle/Model Gateway duo makes sovereignty **tangible**:
- **Local-First Enforcement (M7)**: The Gateway's `get_preferred_backend()` and provider iteration loop ensure local is tried first. The Sovereignty Scorecard tracks the ratio.
- **Response Provenance (M22)**: The `GenerateResult.provider_name` field is the bedrock of observability. If the log says "local" but the response came from cloud, sovereignty is a lie — this cannot happen.
- **Zero Telemetry (M8)**: No external phone-home. All observability (traces, events, metrics) is stored locally in `data/`.
- **Error Integrity (M9)**: Bare `except:` is forbidden. All errors are typed (`OmegaError` subtypes), traceable (`trace_id`), and testable.
- **Temple-Grade (M13)**: Every code path in these modules is covered by contract tests (`isinstance(result, ExpectedType)`) and must pass `make temple-grade`.

---

## §4 Current State & Roadmap: The Gateway to Tomorrow
### 4.1 What's Working (The Locked-In Sovereign Base)
- **KV Cache Quantization**: **LOCKED: q8_0 on CPU (Zen 2)** — No Flash Attention/GPU required. Research complete.
- **Local-First Chain**: Fully wired and tested (native-gguf → lmster → Ollama → Cloud).
- **Response Provenance (M22)**: `provider_name` + `latency_ms` wired.
- **Resource Guard**: OOM hard-stop, AnyIO Semaphore(1), ZoneID Pattern active.
- **Affinity Resolution**: Entity→Model Affinity DB (`entity_model_affinity.yaml`) loaded and used.
- **BSP Culling & Active Set**: Functional, preventing wasted effort on broken providers.
- **Tests**: All 1315 tests pass, including provider fabric and Oracle-specific tests.

### 4.2 What's Coming (The Next Gateways to Sovereignty)
- **Sovereign WAD Protocol (SWP) Strike 11**: The Oracle and Gateway will evolve to interact with **Lumps** (ILump) via the **SovereignBus** (AnyIO channels). The WAD Loader will become a topological DAG loader for PWADs.
- **Unified Vector Abstraction (IVectorStoreAdapter)**: Strike 10 in progress — migrating from Qdrant to `SQLiteVecAdapter` as the default, unifying the vector store behind an interface.
- **Adaptive RAG (Strike 3)**: TF-IDF+SVM router (`src/omega/rag/router.py`) will be integrated into the Oracle's routing chain for query complexity-based model selection.
- **Sovereign Export Bundle (Strike 1)**: The `.omega` ZIP+JSON format will allow users to export their entity's `soul.yaml`, knowledge, and sessions as a sovereign asset.
- **Redis Streams Hivemind (Strike 8.5)**: Will replace file-based Hivemind for task-critical coordination, allowing the Oracle to scale its coordination without I/O bottlenecks.

### 4.3 The Sovereign Promise
The Oracle and Model Gateway are not just code; they are the **enforcement of the Sovereign Mandates**. Every line:
-   Wraps blocking I/O in `anyio.to_thread.run_sync()` (M1).
-   Respects the Engine-Stack Firewall (M2).
-   Tries local backends first (M7).
-   Records the actual provider that served the response (M22).
-   Refuses to load a model if it would OOM the system (M23).
-   Is covered by a contract test that validates its return type (M21).

They are the **guarantors** that the Omega Engine remains a **universal, community-owned runtime for sovereign AI** — a runtime where the user is not a product, but the proprietor.

---

**"The right approximation for the problem is better than the exact solution you can't afford."**
* — The FISR Principle, guiding the Oracle's speculative decode and the Gateway's KV cache quantization.*