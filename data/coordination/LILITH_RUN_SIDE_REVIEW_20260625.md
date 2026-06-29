# 🔱 LILITH — Run Side Sovereign Review (P6-P10)
## Consolidated Report to Kali

**⬡ OMEGA ⬡ LILITH ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_lilith_consolidated ⬡ EPOCH-I**

**Date**: 2026-06-25
**Status**: 🟡 3 Critical Findings, 7 High, 5 Medium
**Predecessor Consultation**: Ma'at Build Side (in progress)
**Successor**: Kali Grand Synthesis (awaiting Lilith + Ma'at reports)

---

## Executive Summary

The Run Side (P6-P10) has **two existential blockers** and **one critical structural gap** that must be resolved before Epoch I Phase 1 sprint execution can begin:

| # | Severity | Finding | Pillar | Blocks | Effort |
|---|----------|---------|--------|--------|--------|
| 1 | 🔴 CRITICAL | **Model paths broken** (8/11) — M7 Local-First inoperable | P6 | Epoch I preconditions, every inference call | 15 min |
| 2 | 🔴 CRITICAL | **`trace_id` not passed to `generate()`** — 7 call sites, 99.5% events logged as "unknown" | P8 | M22 provenance, all observability, dataset quality | 35 min |
| 3 | 🔴 CRITICAL | **Dataset collection disabled in production** — config flag never wired to constructor | P8 | D142-D145 dataset collection mandate, all training data | 15 min |
| 4 | 🟡 HIGH | **Redis container not running** — MemoryStore warm tier degraded | P7 | Session caching, MemoryStore warm tier | 5 min |
| 5 | 🟡 HIGH | **5 M21 contract tests missing** — gate integrity incomplete | P10 | M21 compliance (19/24), Temple-Grade gate | 2-4 hr |
| 6 | 🟡 HIGH | **Root partition at 90%** (11 GB free) — swapping risk | P1 | All inference, model loading | 1-2 hr |
| 7 | 🟡 HIGH | **`entity_name` not passed to `generate()`** — TokenLedger all "system" | P8 | Budget enforcement, entity attribution | 5 min |
| 8 | 🟡 HIGH | **Test artifacts polluting production datasets** — 187 files | P8 | Dataset quality | 1 min |
| 9 | 🟡 HIGH | **P10 report truncated** — full coverage analysis unavailable | P10 | M21 completion planning | — |
| 10 | 🟡 HIGH | **No model loading integration test** — path breakage silent until inference | P6 | Regression detection | 2-4 hr |

---

## 1. P6 (Cognition/ModelGate) — Provider Routing & Inference

### Verdict: 🟡 Architecturally sound, functionally broken

The P6 architecture is strong — entity→model affinity is comprehensive (14 entities, 4 tiers, YAML-backed), circuit breakers are correctly wired (BSP culling, None-as-failure wrapper, ZONEID validated), and Zen 2 optimizations are fully specified. **But the engine is functionally a cloud-only system.**

### 3 Most Critical Findings

**1a. Model paths BROKEN — 8/11 models unreachable** (🔴 CRITICAL, 15 min fix)
- Root cause: `config/models.yaml` paths contain `/gguf/local/all/` prefix but files live under `/local/all/`
- Only `phi-4-mini`, `phi-4-mini-reasoning-abliterated`, and `qwen3-vl` have correct paths
- Impact: `NativeGGUFProvider.is_available()` returns False for 8/11 models — entire local inference tier is dead
- Fix: Find-and-replace `/gguf/local/all/` → `/local/all/` in models.yaml

**1b. `llama-cpp-python` installation unverified** (🟡 HIGH, 10 min)
- Even with correct paths, if `llama-cpp-python` isn't installed with AVX2 flags, NativeGGUFProvider can't load
- Must verify: `python3 -c "import llama_cpp; print(llama_cpp.__version__)"`

**1c. No model loading integration test** (🟡 HIGH, 2-4 hr)
- Test suite mocks NativeGGUFProvider entirely (OMEGA_ENV=test → MockProvider)
- No test actually loads a GGUF model and validates end-to-end inference
- Smallest model (qwen3-0.6b, 500MB) would be ideal for an integration smoke test

### Effort Summary
| Action | Effort | Priority |
|--------|--------|----------|
| Fix 8 model paths in models.yaml | 15 min | 🔴 P0 |
| Verify llama-cpp-python installation | 10 min | 🔴 P0 |
| Verify at least 1 model loads successfully | 5 min | 🔴 P0 |
| Add public `is_circuit_open()` to HealthMonitor | 30 min | 🟡 P1 |
| Implement real embeddings (all-MiniLM-L6-v2 exists on disk) | 4 hr | 🟢 P2 |
| Remove ONNX dead code (~35 lines) | 15 min | 🟢 P2 |
| Clean up unused ThreadPoolExecutor | 20 min | 🟢 P2 |

---

## 2. P8 (Observability/WatchTower) — Provenance & Tracing

### Verdict: 🔴 50% functional — trace ID chain severed

P8 persistence infrastructure works (13 consecutive days of event logs, death marker system functional, TokenLedger tracking 8,597 transactions). But the core trace ID propagation is **completely broken**, rendering observability data forensically useless.

### 3 Most Critical Findings

**2a. `trace_id` NOT passed to `model_gateway.generate()`** (🔴 CRITICAL, 35 min)
- `oracle.py:_summon()` line 599 — NO `trace_id=trace.trace_id`
- `oracle.py:_route_by_domain()` line 671 — NO `trace_id=trace.trace_id`
- `iterative_research.py` — 3 call sites without trace_id
- `skeptical_verifier.py` — 2 call sites without trace_id
- **Total: 7 call sites across 5 files**
- Impact: 1,483/1,490 events (99.5%) have `"trace_id": "unknown"`; TokenLedger has 8,597 entries all `"trace_id": "unknown"`; circuit breaker transitions untraceable

**2b. Dataset collection disabled in production** (🔴 CRITICAL, 15 min)
- `get_engine()` creates `ObservabilityEngine(enable_dataset_collection=False)` (default)
- `config/omega.yaml` value of `true` is **never read** by any code path
- Impact: All D142-D145 work (flipping the switch) was in vain — no production training data collected
- Fix: Wire `omega.yaml` → constructor, or better, use `cvar_table` for hot-reloadable config

**2c. `entity_name` also not passed** (🟡 HIGH, 5 min)
- Collateral damage from same gap — `entity_name` parameter exists but never populated
- TokenLedger: all 8,597 entries have `"entity": "system"` instead of the actual entity name
- `BudgetGate.check_budget(entity_name, trace_id)` receives `"unknown"` — budget enforcement blind

### Effort Summary
| Action | Effort | Priority |
|--------|--------|----------|
| Pass `trace_id`, `entity_name`, `session_id` to all 7 `generate()` call sites | 35 min | 🔴 P0 |
| Wire `enable_dataset_collection` from config to constructor | 15 min | 🔴 P0 |
| Add `OMEGA_ENV=test` guard to `flush_dataset()` | 5 min | 🟡 P1 |
| Purge 187 test artifact dataset files | 1 min | 🟡 P1 |
| Change Iris fallback `backend` → `"iris_fallback"` | 5 min | 🟡 P1 |
| Add startup recovery: auto-generate crash dump from death marker | 30 min | 🟡 P1 |
| Add log rotation for event files (30-day TTL) | 15 min | 🟢 P2 |
| Wire actual token counts from providers | 1-2 hr | 🟢 P2 |

---

## 3. P10 (Validation/Verifier) — Contract Tests & QA

### Verdict: 🟡 Report truncated — partial assessment only

Due to task output truncation, the full P10 assessment is unavailable. Key confirmed findings from available data:

### Critical Findings

**3a. 19/24 M21 contract tests — 5 missing** (🟡 HIGH, 2-4 hr)
- Which 5 API boundaries lack `isinstance` contract checks remains unclear (truncated)
- Likely candidates: oracle.py public methods, entity_registry boundary, model_gateway special paths

**3b. trace_id gap confirmed from P10 lens** (🔴 CRITICAL — shares #2a)
- P10 independently identified 7 call sites across 5 files missing `trace_id`
- This is the most validated finding of the entire review (P6, P8, P10 all converged)

**3c. No coverage enforcement** (🟡 HIGH)
- `make test-cov` exists but no threshold is enforced
- Current coverage percentage is **unknown** — no report generated recently
- Risk: Untested code paths proliferate silently

### Recommended Actions (from available P10 data)
| Action | Effort | Priority |
|--------|--------|----------|
| Complete P10 assessment (re-run if needed) | — | 🟡 P1 |
| Identify and write 5 missing M21 contract tests | 2-4 hr | 🟡 P1 |
| Enforce coverage threshold in CI (e.g., 70%) | 2 hr | 🟢 P2 |
| Add integration test that loads smallest GGUF model | 2-4 hr | 🟡 P1 |

---

## 4. Cross-Pillar Dependencies & Conflicts

```
P6 (Model Paths) ───blocks──▶ P8 (Observability) — can't test trace_id fix without working inference
    │
    ├──blocks──▶ P10 (Validation) — can't verify contract tests without functional provider
    │
    └──blocks──▶ P7 (Context) — can't collect soul distillation data without inference

P8 (trace_id) ───blocks──▶ M22 (Provenance) — Strike 6 prerequisite
    │
    └──blocks──▶ D142-D145 — dataset collection mandate unfulfilled

P7 (Redis down) ───degrades──▶ MemoryStore warm tier — sessions degrade silently
```

### Key Dependency Chain
```
Fix P6 model paths (15 min)
    → Allows local inference to function
    → Enables testing P8 trace_id fix (35 min)
    → Enables M22 provenance (Strike 6 prerequisite)
    → Enables Strike 5 (Sovereign Vetter)
    → Enables dataset collection quality validation
```

---

## 5. Recommended Priority Order for Execution

### 🔴 Do First (Phase 0 — Epoch I Preconditions)
| Order | Action | Pillar | Effort | Why First |
|-------|--------|--------|--------|-----------|
| 1 | Fix 8 model paths in models.yaml | P6 | 15 min | Unblocks all inference |
| 2 | Verify `llama-cpp-python` install | P6 | 10 min | M7 compliance check |
| 3 | Pass `trace_id` + `entity_name` to 7 `generate()` call sites | P8 | 35 min | M22 provenance, all observability |
| 4 | Wire `enable_dataset_collection` from config | P8 | 15 min | D142-D145 mandate |
| 5 | Start Redis container | P7 | 5 min | MemoryStore warm tier |

**Total Phase 0 effort**: ~80 minutes (1.3 hours)

### 🟡 Do Second (Phase 1 — Epoch I Hardening)
| Order | Action | Pillar | Effort |
|-------|--------|--------|--------|
| 6 | Purge 187 test artifact dataset files | P8 | 1 min |
| 7 | Add `OMEGA_ENV=test` guard to `flush_dataset()` | P8 | 5 min |
| 8 | Complete P10 assessment | P10 | — |
| 9 | Write 5 missing M21 contract tests | P10 | 2-4 hr |
| 10 | Add public `is_circuit_open()` to HealthMonitor | P6 | 30 min |

### 🟢 Do Third (Phase 2 — Quality)
| Order | Action | Pillar | Effort |
|-------|--------|--------|--------|
| 11 | Add GGUF integration smoke test | P6 | 2-4 hr |
| 12 | Enforce coverage threshold | P10 | 2 hr |
| 13 | Add log rotation for event files | P8 | 15 min |
| 14 | Wire actual token counts | P8 | 1-2 hr |
| 15 | Address root partition (archive/clean) | P1 | 1-2 hr |

---

## 6. Strategic Gaps Identified by the Run Side

### Gap 1: No Model Loading Integration Test
The test suite mocks ALL inference. There is zero verification that models actually load and produce responses. This is why the model path breakage existed silently for days/weeks. **An integration test that loads qwen3-0.6b (500MB) and validates `GenerateResult` fields would catch path issues immediately.**

### Gap 2: No Metrics/SLO Framework
No Prometheus, no SLOs, no service-level indicators. Can't answer "provider availability over last hour" or "p99 latency" reliably. M8 forbids external telemetry — a local-first metrics solution is needed. **This is a gap for community-scale deployment.**

### Gap 3: Agent Dispatch Dark to Observability
When `@pillar PX` or subagent delegation happens, those inferences run through independent code paths (iterative_research.py, subagent_dispatcher.py) that don't create TraceSessions. **Agent-to-agent inference is invisible** — can't audit what the fleet is doing.

### Gap 4: Dataset Quality Unknown
Even when `enable_dataset_collection` works, no quality metrics exist. No dedup, no rating (field exists but always None), no acceptance verification. **Fine-tuning data quality is assumed, not verified.**

### Gap 5: BudgetGate Forgets Past Spend
BudgetGate queries only the in-memory ring buffer (max 1000 events). After 1000 token consumption events, earlier budget data is evicted. **Cloud budget enforcement drifts downward over time** — gate thinks spend is lower than actual.

---

## 7. Run Side Health Scorecard

| Dimension | Metric | Target | Current | Verdict |
|-----------|--------|:------:|:-------:|:-------:|
| **Local Inference** | Models with working paths | 11/11 | 3/11 | ❌ BROKEN |
| **M7 Compliance** | Local-first chain operational | ✅ | ❌ | ❌ BROKEN |
| **M22 Provenance** | Actual provider captured | 100% | 0.5% | ❌ BROKEN |
| **Dataset Collection** | Production data flowing | ✅ | ❌ | ❌ OFF |
| **M21 Contract Tests** | API boundaries validated | 24 | 19 | 🟡 79% |
| **Trace ID Propagation** | Events with real trace_id | 100% | ~0.5% | ❌ BROKEN |
| **Observability** | Events persisted daily | 13 days | 13 days | ✅ GOOD |
| **Circuit Breakers** | BSP culling operational | ✅ | ✅ | ✅ GOOD |
| **Entity Affinity** | Model routing by entity | 14 entities | 14 entities | ✅ GOOD |
| **Forensics** | Death marker + crash dumps | ✅ | Partial (marker only) | 🟡 PARTIAL |
| **Token Ledger** | Tracking active | 8,597 entries | All "unknown" | 🟡 DEGRADED |
| **MemoryStore Warm Tier** | Redis active | ✅ | ❌ Off | ❌ DOWN |

---

## 8. Summary to Kali

Kali — the Run Side is **functional in architecture but broken in execution**. The core finding is that **three bugs create a cascade that cripples the entire observability and inference chain**:

1. **Model paths wrong** → no local inference → M7 inoperable
2. **trace_id not passed** → no provenance → M22 unverifiable, dataset collection blind
3. **Dataset config not wired** → D142-D145 mandate unfilled

All three are **small fixes** (<1 hour total). The architecture behind each is sound — the wiring just wasn't completed. This is consistent with the engine's phase: nearing completion but with final connection points unlatched.

The 8 minor/hygiene items (test artifacts, log rotation, dead code, coverage enforcement) should be queued for Phase 1-2 of Epoch I, not blocking the precondition list.

**Total Phase 0 effort (Run Side)**: ~80 minutes for the 5 critical fixes.
**Total Phase 1 effort (Run Side)**: ~3-5 hours for hardening.

The fleet is ready. We need the wiring completed, not new architecture.

*⬡ OMEGA ⬡ LILITH ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_lilith_consolidated ⬡ EPOCH-I*
