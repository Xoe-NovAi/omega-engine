# 🔱 ROC LEGACY MINING REPORT — omega-moderation Integration

**Date**: 2026-07-07
**Miner**: roc_racoon
**Target**: `/home/arcana-novai/Documents/Xoe-NovAi/omega-moderation/`
**Source**: `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/`

---

## §1 Circuit Breaker / Provider Failover

### What Exists

| File | Key Classes/Functions | Lines |
|------|----------------------|-------|
| `src/omega/oracle/health_monitor.py` | `AsyncCircuitBreaker`, `CircuitState` (5-state FSM: CLOSED→DEGRADED→OPEN→HALF_OPEN→UNKNOWN), `HealthMonitor` | L89-536 |
| `src/omega/oracle/model_gateway.py` | `_precheck_provider()` (BSP-style O(1) culling), `_record_provider_failure()`, `_update_active_set()` (LRU 32-entry), `_fallback_response()` | L756-868 |
| `src/omega/ingestion/pipeline.py` | `IngestionCircuitBreaker` (pybreaker wrapper), `ResilienceContext` (unified resilience stack: Sentry+Budget+Guard+Verifier) | L39-123 |
| `src/omega/oracle/provider_selector.py` | `ProviderSelector` with penalty-based scoring: PII penalty (-100 for cloud), latency penalty, stability penalty (CUSUM) | L1-93 |

### What's Reusable for omega-moderation

1. **`AsyncCircuitBreaker` (L89-230)** — The 5-state FSM with EMA latency tracking and CUSUM drift detection. Omega-moderation could wrap its ML classification backends (if they become external services) in circuit breakers. When a moderation model endpoint fails, the breaker trips and routes to a fallback (regex-only mode).

2. **`ResilienceContext` (L57-123)** — The unified pre-flight check pattern. Omega-moderation has its own `ContentPipeline` but could adopt the same pattern: Sentry probe → Budget check → Guarded extraction → Verification → Persistence.

3. **Provider Selector's penalty scoring (L62-93)** — The PII-aware routing pattern is directly applicable. Omega-moderation routes between ML models and regex fallback; the scoring pattern could weight models by latency, accuracy, and content sensitivity.

4. **`_fallback_response()` (L842-858)** — Graceful degradation messaging pattern. When all moderation backends fail, return a helpful message instead of crashing.

### What's Novel (Not in omega-moderation)
- CUSUM (Cumulative Sum) drift detection — proactive failure prediction, not just reactive threshold
- EMA (Exponential Moving Average) quality tracking — smooth health signal vs raw counts
- Sovereignty-tiered active sets — local providers always preferred over cloud

### Integration Points
- `IngestionCircuitBreaker` pattern → wrap ML model calls in omega-moderation's classification pipeline
- `ResilienceContext` → adopt for content moderation pre-flight (sentry probe before batch moderation)

---

## §2 Observability / Tracing

### What Exists

| File | Key Classes/Functions | Lines |
|------|----------------------|-------|
| `src/omega/observability/__init__.py` | `ObservabilityEngine`, `EventType` (20+ event types), `JsonFormatter`, `ForensicsManager` | L1-1342 |
| `src/omega/observability/context.py` | `get_current_trace_id()`, `set_current_trace_id()`, contextvars-based trace propagation | L1-63 |
| `src/omega/observability/token_ledger.py` | `TokenLedger.record_transaction()` — per-trace token accounting | L12-107 |
| `src/omega/observability/latency_tracker.py` | Time-series latency tracking per provider/model | L17+ |
| `src/omega/observability/metrics_db.py` | `MetricsDB` — SQLite-backed metrics storage | — |

### What's Reusable for omega-moderation

1. **`EventType` enum (L114-139)** — The event catalog is directly extensible. Omega-moderation could add:
   - `CONTENT_FLAGGED` — when content is flagged as harmful
   - `CONTENT_APPROVED` — when content passes moderation
   - `MODEL_FALLBACK` — when ML model fails and regex kicks in
   - `FALSE_POSITIVE_REPORTED` — for feedback loop

2. **`JsonFormatter` (L54-78)** — Structured JSON logging with trace_id, entity, provider, model fields. Omega-moderation should adopt this format for audit logs.

3. **`get_current_trace_id()` (L29-43)** — Contextvars-based trace propagation. Every moderation decision should carry a trace_id for forensic audit.

4. **`ForensicsManager` (L144+)** — Last Gasp crash dump pattern. When moderation fails catastrophically, capture structured state snapshot.

### What's Novel (Not in omega-moderation)
- Contextvars-based trace propagation across async boundaries — zero-dependency, works with AnyIO
- ForensicsManager's "Last Gasp" pattern — crash dump with structured state capture
- TokenLedger's per-trace accounting — could track moderation cost per content piece

### Integration Points
- Import `omega.observability.context.get_current_trace_id` into moderation pipeline
- Add moderation-specific `EventType` constants to observability event catalog
- Use `JsonFormatter` pattern for moderation audit logs

---

## §3 Audit / Error Integrity (M9)

### What Exists

| File | Key Classes/Functions | Lines |
|------|----------------------|-------|
| `src/omega/errors.py` | `OmegaError` hierarchy: 20+ typed error classes, every error carries `trace_id` + `context` + `raw_error` | L1-153 |
| `src/omega/oracle/failure_registry.py` | `FailureModeRegistry` — pattern-based failure detection with severity, recovery paths, purity scoring | L1-395 |
| `src/omega/oracle/security.py` | `TDPGate` — Tainted Data Protocol, isolation markers, injection pattern sanitization | L1-143 |

### What's Reusable for omega-moderation

1. **`OmegaError` base class (L17-38)** — Every error carries `trace_id`, `context` dict, and `raw_error`. Omega-moderation should adopt this pattern:
   ```python
   class ModerationError(OmegaError):
       """Base for all moderation failures."""
   class ClassificationError(ModerationError):
       """ML model classification failed."""
   class ToxicityThresholdError(ModerationError):
       """Content exceeded toxicity threshold."""
   ```

2. **`FailureModeRegistry` (L1-395)** — Pattern-based failure detection with 5 named modes (REDIS_LOSS, LEGACY_ROT, TELEMETRY_LEAK, DUAL_IMPL, DEAD_CODE). Omega-moderation could define its own failure modes:
   - `MODEL_DEGRADATION` — ML model accuracy dropping
   - `FALSE_POSITIVE_SPIKE` — excessive false positives
   - `REGEX_LEAK` — harmful content bypassing regex fallback
   - `LATENCY_BREACH` — moderation taking too long

3. **`TDPGate` (L29-79)** — Tainted Data Protocol with isolation markers. Omega-moderation processes untrusted user content; this pattern ensures tainted data is isolated from system prompts in any LLM-based moderation.

4. **Error hierarchy pattern** — Typed errors prevent silent swallowing (M9). Omega-moderation should never use bare `except:` — always catch and convert to `ModerationError` subtypes.

### What's Novel (Not in omega-moderation)
- `FailureModeRegistry`'s purity scoring — automated code health metric
- `TDPGate`'s isolation markers — `### [EXTERNAL DATA START]` / `### [EXTERNAL DATA END]` for prompt injection prevention
- `determine_url_taint()` — URL-based trust classification (localhost=trusted, external=untrusted)

### Integration Points
- Create `omega_moderation/errors.py` with typed error hierarchy extending `OmegaError`
- Port `TDPGate` pattern for isolating user content in any LLM-based moderation calls
- Use `FailureModeRegistry` pattern for moderation-specific failure mode tracking

---

## §4 Memory Store / FTS

### What Exists

| File | Key Classes/Functions | Lines |
|------|----------------------|-------|
| `src/omega/memory_store.py` | `MemoryStore` — Hot/Warm/Cold 3-tier with LRU caching, batch persistence, tombstone grace period | L1-933 |
| `src/omega/memory/fts_index.py` | `ConversationFTSIndex` — FTS5-based full-text search | — |
| `src/omega/memory/vector_adapters.py` | `QdrantAdapter`, `MemoryVectorAdapter` (sovereign fallback) | L67+ |
| `src/omega/oracle/context_builder.py` | `ContextBuilder` — memory injection pipeline with ACON compaction, quality-weighted exchange scoring | L1-528 |
| `src/omega/oracle/selective_hydration.py` | `SelectiveHydration` — L3 principle retrieval from Qdrant | L60-371 |

### What's Reusable for omega-moderation

1. **`MemoryStore` 3-tier pattern (L88-108)** — Hot (in-memory LRU) → Warm (file) → Cold (Qdrant vector). Omega-moderation could use this for:
   - **Hot**: Recent moderation decisions (last 1000) in memory for fast false-positive checks
   - **Warm**: Full moderation history on disk for batch analysis
   - **Cold**: Vector-indexed moderation decisions for semantic similarity search (finding similar past flagged content)

2. **`ContextBuilder._score_exchange_quality()` (L182-229)** — Lightweight quality scorer using 4 signals: message length, technical content, question presence, recency. Omega-moderation could score content quality to prioritize review queue.

3. **`ConversationFTSIndex`** — FTS5 full-text search. Omega-moderation could index flagged content for keyword-based search (finding all content matching a slur pattern without re-scanning).

4. **Batch persistence pattern (L102-108)** — Buffer writes and flush on threshold/read/explicit-call. Omega-moderation should batch moderation results to avoid per-content I/O overhead.

### What's Novel (Not in omega-moderation)
- Tombstone grace period (0.5s) — prevents hot-slot reuse during in-flight operations
- Quality-weighted exchange scoring — prioritizes substantive content over chitchat
- Selective Hydration — L3 principle injection into context (could inject moderation guidelines)

### Integration Points
- `MemoryStore` → store moderation decisions with trace_id for audit trail
- `FTSIndex` → index flagged content for pattern-based search
- `ContextBuilder` scoring → adapt for content priority scoring in moderation queue

---

## §5 Privacy / PII

### What Exists

| File | Key Classes/Functions | Lines |
|------|----------------------|-------|
| `src/omega/oracle/pii_masker.py` | `PIIMasker` — 18 PII types, regex + pii-shield detection, tokenize/detokenize, provider-aware bypass | L1-468 |
| `src/omega/oracle/provider_selector.py` | PII-aware routing: -100 penalty for cloud providers when PII detected | L73-77 |
| `src/omega/oracle/security.py` | `TDPGate.sanitize()` — prompt injection pattern removal | L61-79 |
| `src/omega/ingestion/pipeline.py` | Sovereign Filter: PII masking before cloud model calls | L245-249 |
| `src/omega/oracle/dpo_logger.py` | PII masking before DPO record persistence | L284-300 |

### What's Reusable for omega-moderation

1. **`PIIMasker` class (L97-468)** — This is the most directly reusable component. Omega-moderation processes user content that may contain PII. The pattern:
   - `detect()` → find PII instances
   - `tokenize()` → replace with reversible placeholders `[EMAIL_1]`
   - `[process content]` → moderate the tokenized version
   - `detokenize()` → restore original PII in output

2. **`PII_PATTERNS` dict (L68-93)** — 18 PII type patterns (EMAIL, PHONE, SSN, CREDIT_CARD, API_KEY, AWS_KEY, IP_ADDRESS, etc.). Omega-moderation could use these to:
   - Detect PII in user content before moderation (PII shouldn't trigger toxicity flags)
   - Redact PII from moderation audit logs
   - Separate PII detection from content moderation (two different concerns)

3. **Provider-aware bypass (L387-403)** — `should_mask()` checks if provider is local (bypass) or cloud (mask). Omega-moderation could use the same pattern: if running local ML model, skip PII masking; if sending to cloud API, mask first.

4. **`validate_safe_input()` (L153-168)** — Whitelist validation for inputs. Omega-moderation could use this as a first-pass gate before expensive ML classification.

5. **`sanitize_id()` (L172-184)** — Path traversal prevention. Omega-moderation should sanitize content IDs to prevent injection.

### What's Novel (Not in omega-moderation)
- Reversible tokenization (tokenize→process→detokenize) — preserves referential integrity
- 18-type PII pattern library — comprehensive, regex-based, zero deps
- Provider-aware masking — only mask when data leaves the machine

### Integration Points
- Import `PIIMasker` into omega-moderation for PII detection before content analysis
- Use `PII_PATTERNS` to separate PII detection from toxicity detection (PII ≠ harmful)
- Adopt `validate_safe_input()` as first-pass input gate

---

## §6 Entity Registry / YAML Config

### What Exists

| File | Key Classes/Functions | Lines |
|------|----------------------|-------|
| `src/omega/oracle/entity_registry.py` | `EntityRegistry` — YAML-backed CRUD, 3-tier resolution (name→slot→role), Shadow-Stacking layers, Lazy Deletion with grace period | L1-866 |
| `src/omega/oracle/entity_workspace.py` | `EntityWorkspaceManager` — scaffold `data/entities/<name>/` with `soul.yaml`, `knowledge/`, `workspace/` | L413+ |
| `config/wads/` | WAD-based entity definitions (IWAD/GWAD separation) | — |

### What's Reusable for omega-moderation

1. **`EntityRegistry` YAML pattern (L208-866)** — Pure YAML CRUD, no database. Omega-moderation could store moderation configuration (thresholds, rules, model configs) in YAML files managed by a similar registry pattern.

2. **`Entity` dataclass (L90-206)** — Engine Zone vs Game Zone separation. Omega-moderation could adopt:
   - **Engine Zone**: Moderation rules, thresholds, model configs (structural, read-only for game logic)
   - **Game Zone**: Custom rules, entity-specific overrides (freely modifiable)

3. **`write_soul_file()` (L48-63)** — Atomic rename pattern under permission guard. Omega-moderation should use this for writing moderation audit logs (atomic writes prevent corruption).

4. **`with_soul_lock()` (L65-80)** — Advisory file locking via `fcntl`. Omega-moderation needs this for concurrent moderation of the same content from multiple agents.

5. **Lazy Deletion (L601-653)** — Tombstone + grace period + reap pattern. Omega-moderation could use this for soft-deleting moderation rules (keep audit trail, prevent accidental permanent deletion).

### What's Novel (Not in omega-moderation)
- Shadow-Stacking (layered entity projection by priority) — WAD overrides without mutation
- ZoneID Pattern — magic constants validated on get() to catch stale references
- High-Bit Trick — flag encoding using bit 31 for system entities

### Integration Points
- YAML config pattern → store moderation rules/thresholds in `config/moderation/`
- Atomic rename pattern → safe writes for moderation audit logs
- Advisory locking → concurrent moderation coordination

---

## §7 Soul Architecture / Lessons (M11)

### What Exists

| File | Key Classes/Functions | Lines |
|------|----------------------|-------|
| `src/omega/oracle/soul_distiller.py` | `SoulDistiller`, `SessionClassifier`, `DistillationEntry` (L1→L2→L3), 5-stage pipeline | L1-689 |
| `src/omega/oracle/soul_history.py` | `SoulHistoryManager` — immutable audit trail for soul.yaml changes | L1-97 |
| `src/omega/oracle/selective_hydration.py` | `SelectiveHydration`, `L3Principle` — Qdrant-backed principle retrieval | L60-371 |
| `src/omega/cli/soul_stage.py` | `SoulStageApp` — TUI for staging soul proposals before commit | L1-114 |

### What's Reusable for omega-moderation

1. **L1→L2→L3 abstraction pipeline (L40-66)** — The distillation pattern:
   - **L1 (Narrative)**: "What happened?" — raw moderation events
   - **L2 (Insight)**: "What does this mean?" — patterns in flagged content
   - **L3 (Principle)**: "What is the timeless truth?" — universal moderation rules
   
   Omega-moderation could use this to evolve its rules over time:
   - L1: "User X posted content with slur Y at time Z"
   - L2: "Slur Y appears in 73% of flagged content targeting group G"
   - L3: "Content targeting group G with specific slurs should be auto-flagged"

2. **`SessionClassifier` (L93-150)** — Conservative classifier that returns "routine" for trivial sessions. Omega-moderation could classify content as "routine" (known patterns) vs "novel" (needs deeper analysis) to optimize processing.

3. **`QualityScore` (L82-90)** — 5-factor quality scoring: relevance, novelty, actionability, completeness, accuracy. Omega-moderation could score moderation decisions on these axes.

4. **`SoulHistoryManager`** — Immutable audit trail. Omega-moderation MUST have an immutable audit trail of all moderation decisions for compliance.

5. **`SoulStageApp`** — Staging area before committing changes. Omega-moderation could stage rule changes for review before deploying.

### What's Novel (Not in omega-moderation)
- 5-stage distillation pipeline (Classify→Extract→Score→Distill→Stage)
- Conservative classification — reject trivial sessions to avoid noise
- Staging area pattern — proposed_lessons.yaml before soul.yaml

### Integration Points
- L1→L2→L3 pipeline → evolve moderation rules from accumulated decisions
- SessionClassifier → triage content as routine vs novel
- SoulHistoryManager → immutable moderation decision audit trail

---

## §8 Skeptical Verifier / Cognitive Integrity (M17)

### What Exists

| File | Key Classes/Functions | Lines |
|------|----------------------|-------|
| `src/omega/oracle/skeptical_verifier.py` | `SkepticalVerifier` — NLI-based Two-Source Rule, ENTAIL/CONTRADICT/NEUTRAL classification, contradiction resolution | L1-191 |
| `src/omega/oracle/failure_registry.py` | `FailureModeRegistry` — 5 named failure modes, pattern-based detection, purity scoring | L1-395 |
| `src/omega/oracle/iterative_research.py` | Iterative research loops with skeptical verification | L13+ |

### What's Reusable for omega-moderation

1. **Two-Source Rule (L86-114)** — The core verification pattern:
   - Check for contradictions first (CONTRADICTED wins)
   - Require ≥2 independent entailments for VERIFIED
   - Default to UNVERIFIED if insufficient evidence
   
   Omega-moderation could use this for **content verification**:
   - Is this content actually harmful? (require ≥2 signals)
   - Is this a false positive? (check for contradicting evidence)
   - Default to UNVERIFIED (let human review) if uncertain

2. **NLI Check (L116-152)** — Natural Language Inference classifier. Omega-moderation could use NLI to:
   - Determine if content matches a known harmful pattern (ENTAIL)
   - Determine if content contradicts a safe pattern (CONTRADICT)
   - Classify borderline content as NEUTRAL (needs human review)

3. **Contradiction Resolution (L154-191)** — When evidence conflicts, use recency + authority + divergence analysis. Omega-moderation could use this when:
   - ML model says harmful, regex says safe (resolve divergence)
   - Multiple moderation signals disagree

4. **`FailureModeRegistry` pattern (L1-395)** — Named failure modes with detection patterns. Omega-moderation should define its own failure modes:
   - `MODEL_DRIFT` — ML model accuracy degrading over time
   - `PATTERN_LEAK` — Known harmful patterns bypassing detection
   - `OVER_CENSORSHIP` — False positive rate exceeding threshold
   - `LATENCY_SPIKE` — Moderation taking too long

### What's Novel (Not in omega-moderation)
- NLI-based verification — deterministic verification from probabilistic generation
- Two-Source Rule — formal epistemological standard (≥2 independent sources)
- Purity scoring — automated code health metric from failure mode findings

### Integration Points
- Two-Source Rule → content verification (require ≥2 moderation signals)
- NLI Check → classify content relationship to known harmful patterns
- FailureModeRegistry → track moderation-specific failure modes

---

## §9 Summary: Top Integration Priorities

### Priority 1: Direct Port (No Modification)
| Component | Source | Target |
|-----------|--------|--------|
| `PIIMasker` | `pii_masker.py` | omega-moderation content preprocessing |
| `OmegaError` hierarchy | `errors.py` | omega-moderation error types |
| `get_current_trace_id()` | `observability/context.py` | moderation audit trail |
| `JsonFormatter` | `observability/__init__.py` | moderation structured logging |

### Priority 2: Pattern Adoption (Adapt to Moderation Domain)
| Pattern | Source | Adaptation |
|---------|--------|------------|
| Circuit Breaker (5-state FSM) | `health_monitor.py` | Wrap ML model backends |
| Two-Source Rule | `skeptical_verifier.py` | Content verification (≥2 signals) |
| L1→L2→L3 Distillation | `soul_distiller.py` | Evolve moderation rules from decisions |
| ResilienceContext | `ingestion/pipeline.py` | Pre-flight checks for batch moderation |
| TDPGate isolation markers | `security.py` | Isolate user content in LLM moderation |

### Priority 3: Structural Patterns
| Pattern | Source | Use Case |
|---------|--------|----------|
| YAML config (no DB) | `entity_registry.py` | Moderation rules/config storage |
| Atomic rename writes | `entity_registry.py` | Safe audit log writes |
| Advisory file locking | `entity_registry.py` | Concurrent moderation coordination |
| Lazy Deletion + Grace Period | `entity_registry.py` | Soft-delete moderation rules |
| 3-tier memory (Hot/Warm/Cold) | `memory_store.py` | Moderation decision storage |
| FTS5 indexing | `memory/fts_index.py` | Flagged content search |

---

*Report generated by roc_racoon — Sovereign Miner & Ideas Guy*
*All file paths verified against omega-engine repo as of 2026-07-07*
