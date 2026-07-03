# The Omega Engine Holistic Review Plan
## Version 3.0 — Unified Triple-Model Analysis

**Date**: 2026-07-03
**Purpose**: Comprehensive cross-file architectural review leveraging 1M token context window
**Execution Target**: Nemotron 3 Ultra (1M context)
**Contributing Models**: Nemotron 3 Ultra, DeepSeek V4 Flash, MiMo-V2.5

---

## Executive Summary

This plan is the unified product of three AI models working in concert:

| Model | Role | Contribution |
|-------|------|--------------|
| **Nemotron 3 Ultra (1M context)** | Strategic Architect | Original plan structure, 7 phases, token budget analysis |
| **DeepSeek V4 Flash** | Deep Analyst | 4-dimensional analysis framework, 8 anomaly signatures, causal tracing |
| **MiMo-V2.5** | Model-Level Insights | 5th dimension (model-level), 10th anomaly signature, execution checklist, automation protocol |

The plan is designed to be executed by the **Nemotron 3 Ultra** model using its 1M token context window. The other models contribute analytical frameworks that the 1M model will apply.

---

## Why This Review Matters

The Omega Engine has reached a critical mass: **113 source files, 730 tests, 22 mandates, 29 heritage patterns, and 13 agents**. Individual reviews catch local bugs. But the most dangerous bugs are **cross-cutting** — they exist in the seams between modules, in the gaps between documentation and code, in the paths where a fix in one file creates a regression in another.

A 1M token context window enables something unprecedented: **simultaneous analysis of the entire system graph**. This plan is structured to leverage that capability.

---

## Dimension 1: Spatial Analysis (Cross-File Data Flow Integrity)

**What it catches**: Variables that change meaning or lose fidelity as they cross module boundaries.

### The 5 Tracers

| # | Tracer | Origin Point | Verify Across | Failure Mode |
|---|--------|-------------|---------------|--------------|
| T1 | `trace_id` | `observability.py:new_trace_id()` → `oracle.py:298` | `model_gateway.py` → `token_ledger.py` → `memory_store.py` → `observability/` | trace_id="unknown" in 5-10% of events (M22 violation) |
| T2 | `provider_name` | `model_gateway.py:895` (success) + `:910` (fallback) | `oracle.py:659,672` → `OracleResponse.backend` → `_record_interaction` metadata → `token_ledger.record()` | Provider name from config vs actual backend mismatch |
| T3 | `latency_ms` | `model_gateway.py:844` (measurement) | `:898` (success) → `:912` (fallback) → `GenerateResult` → `TokenLedger` | Zero latency on success path (M22 gap) |
| T4 | `error` / exception | All `except:` clauses in all source files | `errors.py` taxonomy → `observability` → `failure_registry.py` | Bare excepts without trace_id (M9 violation) |
| T5 | `entity_name` | `entity_registry.py:find_by_domain()` | `oracle.py` → `context_builder.py` → `memory_store.py` → `soul_distiller.py` | Entity name case sensitivity or tombstoned entity access |

### The 4-Hop Provenance Chain (Materialize This)

```
Hop 1: User Query enters oracle.talk()
  → trace_id created at oracle.py:298
  → session_id resolved via SessionManager

Hop 2: oracle._summon() calls model_gateway.generate()
  → preferred_backend determined at oracle.py:630
  → PII masking decision made based on is_cloud
  → GenerateResult returned with provider_name from ACTUAL backend

Hop 3: oracle._summon() extracts res.provider_name
  → Line 659: backend = res.provider_name  (correct — uses actual, not intended)
  → Line 672: OracleResponse.backend = backend  (propagated correctly)

Hop 4: oracle._record_interaction() persists
  → metadata dict at line 498: trace_id + confidence + model + backend
  → memory_store.add_exchange() stores to hot cache + buffers write
  → TokenLedger.record() logs observability event
```

**Review question**: Are all 4 hops present in all 3 entry paths?
- `oracle.talk()` → `_summon()` ✓ (verified)
- `oracle.summon()` → `_summon()` ✓ (verified)
- `oracle._respond_as_iris()` → `_summon()` ✓ (verified via line 541)

**MiMo insight**: The `_respond_as_iris()` path (line 530-561) has a **fallback to hardcoded response** if Iris model invocation fails. In this fallback path, `backend` is set via `get_preferred_backend()` (line 548), which returns the *intended* backend, not the *actual* one. This is a **M22 violation surface** — the fallback path doesn't know which backend *would have* served the response.

---

## Dimension 2: Temporal Analysis (State Evolution & Lifecycle)

**What it catches**: Patterns where state transitions across time are inconsistent, or where a fix in one session creates a regression in another.

### Lifecycle Graph 1: Session Lifecycle

```
SessionManager.create()
  → oracle.talk() / oracle.summon()
  → _record_interaction()
  → _interaction_counter[entity_key] += 1
  → [if count >= 5] close_session()
  → distiller.distill_and_save()
  → soul.yaml updated
  → _interaction_counter reset to 0
```

**Review questions**:
1. The M11 fix (D183) replaced `anyio.create_task(close_session)` with `await close_session`. Are there **other** places where `anyio.create_task` or `asyncio.create_task` is used that would silently fail?
   - **Grep check**: `grep -r "create_task" src/omega/` — any matches besides the fixed one?
2. Does the `interaction_counter` reset correctly? (line 523: `= 0` after reaching 5)
   - What if `close_session()` raises an exception? The counter was already reset at line 523. This means the next interaction will start counting from 0 again, and `close_session()` won't be retried for the same session. **Potential M11 gap**.
3. What happens to sessions that never reach 5 interactions? Are they orphaned?
   - The `archive_old_sessions()` call in `oracle.bootstrap()` handles 90-day archival. But sessions between 5 and 90 days are never distilled. **Is this by design?**

### Lifecycle Graph 2: Provider Circuit Breaker

```
Closed (healthy) → N failures → Degraded (warn) → M failures → Open (tripped)
  → Recovery timeout → Half-Open (probe) → [success → Closed | failure → Open]
```

**Review questions**:
1. Is the CUSUM LLR formula correctly implemented? The formula from the Ark blueprint:
   ```
   g_t = max(0, g_{t-1} + ln((p1*(1-p0))/(p0*(1-p1))) * y_t + ln((1-p1)/(1-p0)))
   ```
   Where p0=0.02, p1=0.15, h_warn=3.0, h_trip=5.0
   - Verify against `health_monitor.py` implementation
2. What happens when ALL providers are Open? Is there a guaranteed fallback (Mock)?
   - The provider chain in `model_gateway.py:generate()` iterates `self.providers` — if all breakers are Open, it should reach Mock. Verify this path.
3. Does `is_available()` on breaker respect the Half-Open state?
   - Sprint 0 fixed T2.3: `RemoteProvider.generate()` returns None on retry exhaustion, which `breaker.call()` counted as success. Verify the fix is still in place.

### Lifecycle Graph 3: Entity Soul Lifecycle

```
EntityRegistry.add()
  → first_breath() recorded
  → interactions accumulate in MemoryStore (hot tier)
  → close_session() triggers soul_distiller.distill_and_save()
  → proposed_lessons.yaml created
  → human review (or auto-approval for high-confidence)
  → soul.yaml updated with L3 principles
```

**Review questions**:
1. The entities.yaml corruption bug (36-level recursive traits). Is it definitively fixed?
   - The root cause was `traits` key not in `core_fields` set at `entity_registry.py:307`
   - Verify `"traits"` is in `core_fields` or handled by metadata migration
2. The `to_dict()` → `asdict()` cycle: does it still cause infinite nesting on save?
   - Check if `Entity.to_dict()` uses `dataclasses.asdict()` or a custom serializer

---

## Dimension 3: Causal Analysis (Error Propagation & Degradation)

**What it catches**: Error handling paths that silently degenerate, or failure modes that aren't tested.

### The Error Taxonomy Matrix

Load `src/omega/errors.py` and verify:

```
OmegaError (base)
├── ProviderError
│   ├── ProviderRateLimitError
│   ├── ProviderAuthError
│   ├── ProviderTimeoutError
│   ├── ProviderUnavailableError
│   ├── ProviderValidationError
│   └── ProviderSafetyError
├── InferenceError
│   ├── InferenceOOMError
│   ├── InferenceLoadError
│   └── InferenceRuntimeError
├── OmegaPersistenceError
│   ├── SoulCorruptionError
│   ├── SessionPersistenceError
│   └── StateIntegrityError
├── ConfigError
├── WADError
├── BoundaryViolationError
├── InvariantViolationError
├── EntityTombstonedError
└── ModelNotFoundError
```

**Review questions**:
1. Is every `except` clause in the codebase catching the **most specific** error type?
   - Any `except Exception:` that should be `except ProviderError:`?
2. How many error types are actually instantiated anywhere?
   - `grep -r "ProviderRateLimitError\|ProviderAuthError\|..." src/omega/` — which are raised?
3. Are there error types defined but never raised? (dead code)
4. Are there error types raised but never tested? (coverage gap)
5. Are there `except Exception:` blocks that don't log a trace_id? (M9 violation)

### Degradation Cascade Test

```
Provider 1 fails → circuit breaker opens → try Provider 2
  → Provider 2 fails → circuit breaker opens → try Provider 3
  → ... → ALL providers Open → Mock fallback
```

**Review questions**:
1. Is this cascade tested as a single end-to-end flow?
   - `test_fallback_flow` exists — but does it test ALL 8 providers cascading?
2. Does `_precheck_provider()` correctly skip Open breakers?
   - BSP-style culling: O(1) breaker check skips broken providers
3. What happens to buffered writes in MemoryStore when ALL storage providers are unavailable?
   - Redis fails → File fails → InMemory fails → buffer lost?
   - Is there a dead-letter queue for failed writes?

---

## Dimension 4: Semantic Analysis (Documentation ↔ Code Drift)

**What it catches**: The most insidious class of bugs — where the documentation says one thing but the code does another.

### Cross-Reference Map

| Documentation Claim | Code Assertion | Verify Match |
|--------------------|----------------|--------------|
| `ORACLE_STACK.md §3`: "Iris speculative decode via qwen3-1.7b" | `oracle.py:350` `_assess_iris_confidence()` | Is the model actually qwen3-1.7b? What if it's not loaded? |
| `SOVEREIGN_ARK_BLUEPRINT.md §3.1`: "705 tests passing" | `make test` output | Currently correct, but verify after any changes |
| `CREDITS.md §1.2`: "BSP culling in ModelGateway.generate()" | `model_gateway.py:538-569` `_precheck_provider()` | Is the `[id-soft: doom-1993]` tag present and correct? |
| `SOVEREIGN_MANDATES.md M1`: "AnyIO Absolute" | `grep -r "import asyncio" src/omega/` | Zero matches |
| `OMEGA_ENGINE.md §6`: "Provider priority: native-gguf(0) → ... → Mock(7)" | `config/providers.yaml` order | Does the code respect this order? |

### Heritage Tag Completeness Audit

1. Extract ALL `[id-soft:]` tags from ALL source files
2. Cross-reference against `CREDITS.md` §1.x (17 registered patterns)
3. Identify untagged heritage implementations
4. Verify every tag has a vet record in `HERITAGE_VET_LOG.md`
5. Check for tags that reference REJECTED concepts (e.g., 8-char name caps)

---

## Dimension 5: Model-Level Analysis (Inference & Performance)

**What it catches**: Issues that only matter when a model is actually running — memory pressure, context window limits, inference latency, and provider fabric behavior.

*This dimension is MiMo-V2.5's unique contribution.*

### 5.1 ResourceGuard Calibration

The ResourceGuard uses `anyio.Semaphore(1)` to prevent OOM crashes. But:

- **Question**: Is the semaphore calibrated for the actual memory footprint of local models?
- **Context**: Ryzen 7 5700U has 14GB RAM, ~2GB overhead, ~12GB for AI. A 1.7B model uses ~2-4GB. An 8B model uses ~8GB.
- **Verify**: `resource_guard.py` — does it account for model size when acquiring the semaphore?
- **Risk**: If two local models try to load simultaneously, OOM crash.

### 5.2 Context Window Management

The ContextBuilder uses ACON (Agent Context Optimization) for compaction. But:

- **Question**: Is the token counting accurate?
- **Context**: Different models have different tokenizers. A 1.7B model might count tokens differently than an 8B model.
- **Verify**: `context_builder.py` — does it use a model-agnostic token counter, or model-specific?
- **Risk**: If token counting is wrong, context overflow → truncation → degraded responses.

### 5.3 SomaticState Serialization (M20)

The SomaticState is supposed to serialize KV cache state via ctypes. But:

- **Question**: Is `llama_copy_state_data` actually available in the installed `llama-cpp-python`?
- **Verify**: `state_manager.py` — does it check for ctypes visibility? What's the fallback if not available?
- **Risk**: If ctypes bindings aren't available, SomaticState is a no-op — cold-start every time.

### 5.4 Provider Fabric Fallback Behavior

When I'm not available (not loaded, or OOM), the system should fall back to other providers. But:

- **Question**: How long does the fallback take?
- **Context**: If native-gguf fails, the system tries lmster → Ollama → Google → OpenRouter → OpenCode → Copilot → Mock. Each fallback adds latency.
- **Verify**: `model_gateway.py:generate()` — is there a timeout per provider? How long is the total fallback chain?
- **Risk**: If the fallback chain takes >30 seconds, the user experience is degraded.

### 5.5 Soul Injection Effectiveness

The soul.yaml is injected into system prompts via `_prepare_system_prompt()`. But:

- **Question**: Does soul.yaml content actually affect model behavior?
- **Context**: Small models (1.7B) might not have enough capacity to follow complex soul instructions.
- **Verify**: `oracle.py:448-483` `_prepare_system_prompt()` — how large is the soul injection? Is it truncated?
- **Risk**: If soul injection is too large, it overwhelms the model's capacity and degrades response quality.

### 5.6 Test Mock vs Real Behavior

Many tests use `OfflineMockBackend` which returns deterministic responses. But:

- **Question**: Do contract tests verify real behavior, or just mock behavior?
- **Context**: `test_contract_m21.py` uses `OfflineMockBackend` — the `GenerateResult` it returns is pre-configured, not from actual inference.
- **Verify**: Are there contract tests that exercise the **real** provider fabric with a real model?
- **Risk**: Contract tests pass with mocks but fail in production.

---

## The 10 Anomaly Signatures

These are patterns that require seeing 20-100+ files simultaneously. A smaller context would miss them because it can't hold all the cross-references at once.

| # | Signature | What It Indicates | Key Files | Severity |
|---|-----------|-------------------|-----------|----------|
| **S1** | **Counter Non-Reset** | A counter variable that's incremented but never reset, or reset on wrong event | `oracle.py:521-523` (`_interaction_counter`) + `close_session` in `soul_distiller.py` + `_batch_count` in `memory_store.py` | High |
| **S2** | **Provider Name Drift** | `get_preferred_backend()` returns a different name than `provider_name` on `GenerateResult` | `model_gateway.py:630` vs `:659` vs `:895` | Critical |
| **S3** | **Orphaned Exception Types** | Error classes defined in `errors.py` but never raised anywhere | `errors.py` + all source files that should raise them | Medium |
| **S4** | **Docstring-Return-Type Mismatch** | Function says "returns X" but type hint or actual behavior says Y | All public functions with docstrings | Medium |
| **S5** | **Silent Async Failures** | `asyncio.create_task()` or `anyio.create_task()` (which doesn't exist) used instead of `await` or `nursery.start_soon()` | `grep -r "create_task" src/omega/` | Critical |
| **S6** | **Bootstrap Double-Fire** | A `_bootstrapped = False` / `if _bootstrapped: return` pattern that has a race condition between check and set | `oracle.py:129-147` + `model_gateway.py` + session_manager + all boot() methods | Medium |
| **S7** | **Tainted Data Bypass** | A code path that doesn't call `TDPGate.isolate()` on external input | All public API entry points (talk, summon, MCP tools) | Critical |
| **S8** | **Heritage Tag Rot** | An `[id-soft:]` tag referencing a pattern that was refactored or removed | All `[id-soft:]` tags + `CREDITS.md` + `HERITAGE_VET_LOG.md` | High |
| **S9** | **Token Budget Overflow** | Context builder produces prompts that exceed model context window | `context_builder.py` + `config/models.yaml` (context windows) | High |
| **S10** | **Dead Letter Silence** | Failed writes to memory store with no retry or dead-letter mechanism | `memory_store.py` + `providers.py` + `batch_writer.py` | Medium |

### S9 Deep Dive (MiMo Contribution)

The ContextBuilder has a token budget formula from the Ark Blueprint:

```
Budget_total = System (10-15%) + Tools (15-20%) + Knowledge (30-40%) + History (20-30%) + Reserve (10-15%)
```

**Verify**:
- Does `context_builder.py` actually implement this formula?
- Does it account for different model context windows (4K for 1.7B, 16K for 8B)?
- What happens when the budget is exceeded? Is there graceful truncation?

### S10 Deep Dive (MiMo Contribution)

The MemoryStore has a batch writer that buffers writes. But:

**Verify**:
- What happens when `_flush_batch()` fails for ALL providers?
- Is there a dead-letter directory (`data/requests/dead/`) for failed writes?
- Does the handoff reaper (14-day archive, 30-day delete) clean up dead letters?

---

## Execution Protocol: 4-Phase Progressive Scan

### Phase A: Hot Scan (Critical Path — ~200K tokens)

**Goal**: Verify the user-query path is correct end-to-end.

**Load simultaneously**:
```
src/omega/oracle/oracle.py (860 lines)
src/omega/oracle/model_gateway.py (1131 lines)
src/omega/oracle/entity_registry.py
src/omega/memory_store.py
src/omega/memory/providers.py
src/omega/oracle/health_monitor.py
src/omega/oracle/context_builder.py
src/omega/oracle/soul_distiller.py
src/omega/oracle/pii_masker.py
src/omega/oracle/resource_guard.py
src/omega/oracle/session_manager.py
tests/test_oracle.py
tests/test_model_gateway.py
tests/test_contract_m21.py
tests/test_contract_soul_distiller.py
```

**Analyze in a single pass**:
1. Trace `trace_id` through the entire chain (Spatial)
2. Find all M9 violations (bare excepts without trace_id)
3. Verify M22: `provider_name` from actual response, not config
4. Verify M11: `close_session` is called on hot path (`await`, not `create_task`)
5. Check for S1, S2, S5, S6, S9 anomaly signatures
6. Verify ResourceGuard calibration for local models (S9)

**Expected findings**: 5-10 issues

### Phase B: Warm Scan (Support Systems — ~200K tokens)

**Goal**: Verify observability, memory, and A2A systems are correct.

**Load simultaneously**:
```
src/omega/observability/__init__.py
src/omega/observability/token_ledger.py
src/omega/observability/metrics_db.py
src/omega/observability/bleg.py
src/omega/observability/ufl.py
src/omega/observability/context.py
src/omega/memory/__init__.py
src/omega/memory/providers.py
src/omega/memory/batch_writer.py
src/omega/memory/adapters.py
src/omega/memory/embeddings.py
src/omega/memory/vector_adapters.py
src/omega/memory/fts_index.py
src/omega/oracle/a2a_bridge.py
src/omega/oracle/a2a_auth.py
src/omega/oracle/wad_loader.py
src/omega/oracle/handoff.py
src/omega/oracle/semantic_router.py
src/omega/oracle/skeptical_verifier.py
src/omega/oracle/headroom.py
tests/test_hivemind_integration.py
tests/test_storage_providers.py
```

**Analyze**:
1. Observability pipeline: does every event carry trace_id?
2. Memory provider chain: does fallback actually work?
3. A2A Agent Cards: are they using real spec (A2A v1.0) or fabricated draft?
4. Semantic router: what happens when embedding model is unavailable?
5. Check for S7, S8, S10 anomaly signatures

**Expected findings**: 3-7 issues

### Phase C: Cold Scan (Infrastructure & Governance — ~200K tokens)

**Goal**: Verify error taxonomy, heritage compliance, and mandate enforcement.

**Load simultaneously**:
```
src/omega/errors.py
src/omega/constants.py
src/omega/cli/oracle_cli.py
src/omega/cvar_table.py
src/omega/vault/__init__.py
src/omega/vault/key_vault.py
src/omega/vault/crypto.py
src/omega/orchestration/__init__.py
src/omega/orchestration/triage_router.py
src/omega/gateway/__init__.py
src/omega/workers/background_researcher/ (all files)
SOVEREIGN_MANDATES.md
CREDITS.md
docs/decisions/PIVOT_LOG.md
```

**Analyze**:
1. Error taxonomy completeness (S3)
2. Heritage tag audit (S8)
3. Mandate compliance matrix (all 22 against actual code)
4. Configuration consistency (providers.yaml vs models.yaml vs code)
5. Check for S4, S6 anomaly signatures

**Expected findings**: 2-5 issues

### Phase D: Synthesis & Reporting (~100K tokens)

**Goal**: Consolidate all findings into structured output.

**Load**:
- All findings from Phases A, B, C
- Output templates (FINDINGS_CRITICAL.md, FINDINGS_MAJOR.md, FINDINGS_MINOR.md)

**Produce**:
- Structured findings report with anomaly signatures, dimensions, affected files, mandate violations, severity, and suggested fixes
- Summary statistics (total findings by severity, by dimension, by anomaly signature)
- Prioritized remediation roadmap

---

## Risk Model & Expected Findings

### High Probability Findings (based on code exploration):

| # | Finding | Anomaly | Dimension | Evidence |
|---|---------|---------|-----------|----------|
| F1 | `_interaction_counter` resets before `close_session()` — if `close_session()` fails, the next session won't trigger distillation | S1 | Temporal | `oracle.py:522-523` |
| F2 | `_respond_as_iris()` fallback path sets `backend = get_preferred_backend()` instead of actual provider | S2 | Spatial | `oracle.py:548` |
| F3 | `_track_soul_evolution()` returns early in test mode — no soul tracking during tests | S7 | Causal | `oracle.py:845-846` |
| F4 | `test_contract_m21.py` uses `OfflineMockBackend` — contract tests verify mock behavior, not real behavior | S9 | Model-Level | `test_contract_m21.py` |
| F5 | Some error types in `errors.py` may be defined but never raised (dead code) | S3 | Causal | `errors.py` |

### Medium Probability Findings:

| # | Finding | Anomaly | Dimension | Evidence |
|---|---------|---------|-----------|----------|
| F6 | Heritage tags may reference patterns that were partially refactored | S8 | Semantic | All `[id-soft:]` tags |
| F7 | Context builder may not account for different model context windows | S9 | Model-Level | `context_builder.py` + `config/models.yaml` |
| F8 | Batch writer may have no dead-letter for failed writes | S10 | Model-Level | `memory_store.py` + `batch_writer.py` |
| F9 | Bootstrap race condition in `oracle.bootstrap()` | S6 | Temporal | `oracle.py:129-147` |

### Low Probability (but catastrophic if exists):

| # | Finding | Anomaly | Dimension | Evidence |
|---|---------|---------|-----------|----------|
| F10 | Tainted data bypass in MCP tools or external API paths | S7 | Causal | All MCP tool handlers |
| F11 | Another `create_task` equivalent that silently swallows exceptions | S5 | Temporal | `grep -r "create_task" src/omega/` |
| F12 | ResourceGuard not calibrated for local model memory footprint | S9 | Model-Level | `resource_guard.py` |

---

## Output Format

The review will produce three artifacts:

### 1. `data/review/FINDINGS_CRITICAL.md` — Block Release

```markdown
# Critical Findings — {DATE}

## F{n}: {Title}

**Anomaly Signature**: S{n} ({name})
**Dimension**: {Spatial|Temporal|Causal|Semantic|Model-Level}
**Mandate Violated**: M{n} ({name})
**Files Affected**:
- `src/omega/oracle/oracle.py:45-52` (root cause)
- `src/omega/oracle/model_gateway.py:659` (propagation)

**Description**: {What's wrong and why it matters}

**Evidence**:
```python
# oracle.py:522-523
entity_key = f"{resp.entity}:{resp.session_id or trace.trace_id}"
self._interaction_counter[entity_key] = self._interaction_counter.get(entity_key, 0) + 1
if self._interaction_counter[entity_key] >= 5:
    self._interaction_counter[entity_key] = 0  # Reset BEFORE close_session
    if resp.session_id:
        try:
            await self.close_session(resp.entity, resp.session_id)  # If this fails...
```

**Impact**: {What happens in production}

**Suggested Fix**: {1-2 sentences}

**Contract Test Required**: Yes — `test_contract_m21.py` should verify `_interaction_counter` reset only after successful `close_session()`
```

### 2. `data/review/FINDINGS_MAJOR.md` — Fix Before Next Sprint
Same format as Critical, but lower severity.

### 3. `data/review/FINDINGS_MINOR.md` — Technical Debt
Same format, but documentation gaps and code quality improvements.

---

## Automation Protocol

This review should be automatable for future runs. The protocol:

### 1. Pre-Scan Setup
```bash
# Count tokens in target files
find src/omega -name "*.py" -exec wc -l {} + | tail -1
# Estimate: ~113 files × ~280 avg lines = ~31,800 lines × ~4 tokens/line = ~127,000 tokens for source only

# Add tests, docs, configs
find tests -name "*.py" -exec wc -l {} + | tail -1
# Estimate: ~66 files × ~185 avg lines = ~12,200 lines × ~4 tokens/line = ~49,000 tokens

# Total estimated: ~176,000 tokens for all Python files
# Well within 1M window with room for analysis output
```

### 2. Scan Execution
The 1M model should follow the 4-phase protocol, producing intermediate findings after each phase.

### 3. Post-Scan Validation
```bash
make test          # Verify no regressions
make temple-grade  # Verify T1-T11 gates
make heritage-map  # Verify heritage tag coverage
```

### 4. Findings Triage
- Critical findings → immediate fix + commit
- Major findings → add to next sprint backlog
- Minor findings → add to technical debt registry

---

## Final Checklist for the 1M Model

Before starting the scan, verify:

- [ ] You have access to all source files (116 .py files in src/omega/)
- [ ] You have access to all test files (730 tests across ~50 test files)
- [ ] You have access to key documentation (SOVEREIGN_MANDATES.md, CREDITS.md, ORACLE_STACK.md)
- [ ] You have access to configuration files (config/omega.yaml, config/providers.yaml, config/models.yaml)
- [ ] You understand the 5 dimensions of analysis
- [ ] You understand the 10 anomaly signatures
- [ ] You have the output templates ready

During the scan:

- [ ] Follow the 4-phase protocol (Hot → Warm → Cold → Synthesis)
- [ ] Check each anomaly signature against the loaded files
- [ ] Cross-reference documentation claims against actual code
- [ ] Verify mandate compliance for all 22 mandates
- [ ] Produce structured findings with line numbers and evidence

After the scan:

- [ ] Write findings to `data/review/` directory
- [ ] Provide summary statistics
- [ ] Suggest prioritized remediation roadmap

---

**End of Plan v3.0**

This plan is ready for execution. The three-model collaboration has produced a comprehensive, actionable, and automatable review protocol that leverages the full power of the 1M token context window.
