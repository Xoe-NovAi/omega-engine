# P8 Observability — Strategic Review: Epoch I Phase 1 Readiness
**Agent**: P8 (WatchTower — Observability & Tracing)
**Date**: 2026-06-25
**Scope**: Full audit of trace_id propagation, dataset collection, entity_name flow, and M22 compliance
**Status**: 🔴 NO-GO — 7 of 8 call sites missing trace_id propagation

---

## Executive Summary

The Omega Engine's observability system has strong *infrastructure* (ObservabilityEngine, TraceSession, GenerateResult with provider_name) but **critical gaps in propagation**. The trace_id created at oracle.py entry is **not forwarded** to `model_gateway.generate()` in 7 of 8 call sites, creating broken trace chains that make forensic debugging impossible and M22 Response Provenance claims unverifiable at the inference boundary.

**Verdict**: NO-GO for Epoch I Phase 1 until trace_id propagation is fixed across all call sites.

---

## §1 Call Site Audit — `model_gateway.generate()` Invocations

### 1.1 Complete Inventory (8 External Call Sites)

| # | File | Line | Function | trace_id Passed? | entity_name Passed? | Severity |
|---|------|------|----------|-------------------|---------------------|----------|
| 1 | `oracle.py` | 599 | `_summon_direct()` | ❌ **NO** | ❌ NO | 🔴 CRITICAL |
| 2 | `oracle.py` | 671 | `_route_by_domain()` | ❌ **NO** | ❌ NO | 🔴 CRITICAL |
| 3 | `iterative_research.py` | 64 | gap analysis | ❌ **NO** | ❌ NO | 🟡 HIGH |
| 4 | `iterative_research.py` | 143 | synthesis | ❌ **NO** | ❌ NO | 🟡 HIGH |
| 5 | `iterative_research.py` | 159 | claim extraction | ❌ **NO** | ❌ NO | 🟡 HIGH |
| 6 | `skeptical_verifier.py` | 130 | NLI check | ❌ **NO** | ❌ NO | 🟡 HIGH |
| 7 | `skeptical_verifier.py` | 171 | contradiction resolution | ❌ **NO** | ❌ NO | 🟡 HIGH |
| 8 | `orchestrator.py` | 94 | sensing | ✅ **YES** (`task_id`) | ❌ NO | 🟢 PASS (partial) |

**Score**: 1/8 pass trace_id (12.5%). **7 call sites create orphan traces.**

### 1.2 Root Cause Analysis

The `model_gateway.generate()` signature accepts `trace_id` as an optional parameter:

```python
async def generate(
    self, model_name: str, system_prompt: str, user_query: str,
    temperature: float = 0.7, max_tokens: int = 1024, trace_id: Optional[str] = None,
    session_id: Optional[str] = None, entity_name: Optional[str] = None
) -> 'GenerateResult':
```

However, callers in `oracle.py` do not pass it. The `trace` object is available in both `_summon_direct()` and `_route_by_domain()` (it's a parameter), but the `trace.trace_id` is never forwarded to `model_gateway.generate()`.

**oracle.py:599** (the primary summon path):
```python
res = await self.model_gateway.generate(
    model_name=model_name,
    system_prompt=effective_system_prompt,
    user_query=query,
    temperature=effective_temperature,
    max_tokens=effective_max_tokens,
    # ← trace_id MISSING
)
```

**oracle.py:671** (the domain-routed path):
```python
res = await self.model_gateway.generate(
    model_name=model_name,
    system_prompt=system_prompt,
    user_query=text,
    temperature=entity.temperature,
    max_tokens=1024,
    # ← trace_id MISSING
)
```

The `trace.trace_id` is used elsewhere in these functions (e.g., `trace.record()`, `OracleResponse(trace_id=trace.trace_id)`) but is never forwarded to the inference boundary.

---

## §2 Dataset Collection Status

### 2.1 Configuration

| Source | Value | Status |
|--------|-------|--------|
| `config/omega.yaml` §observability | `enable_dataset_collection: true` | ✅ ENABLED |
| `ObservabilityEngine.__init__` default | `enable_dataset_collection: bool = False` | ⚠️ DEFAULT OFF |
| `ObservabilityEngine._collect_dataset` gate | `if not self.enable_dataset_collection: return` | ⏸️ GATED |

### 2.2 Assessment

The config declares `enable_dataset_collection: true`, but the `ObservabilityEngine` constructor defaults to `False`. The actual behavior depends on whether the config value is loaded and passed to the constructor at engine startup.

**Risk**: If the engine instantiation path does not read `config/observability/enable_dataset_collection` and pass it to `ObservabilityEngine(enable_dataset_collection=True)`, dataset collection is silently disabled despite the config.

**Recommendation**: Verify the engine bootstrap path loads this config. Add a startup log line confirming dataset collection status.

---

## §3 Entity Name Propagation

### 3.1 Current State

The `model_gateway.generate()` accepts `entity_name` as an optional parameter (used for BudgetGate cloud cost tracking). However:

- **oracle.py:599** (`_summon_direct`): Does NOT pass `entity_name` — the entity is available (`entity.name`) but not forwarded
- **oracle.py:671** (`_route_by_domain`): Does NOT pass `entity_name` — same issue
- **orchestrator.py:94**: Does NOT pass `entity_name`
- **iterative_research.py**: Does NOT pass `entity_name`
- **skeptical_verifier.py**: Does NOT pass `entity_name`

**Score**: 0/8 pass entity_name (0%).

**Impact**: BudgetGate cloud cost tracking cannot attribute spending to specific entities. The `entity_name` parameter exists in the API but is never used by callers.

---

## §4 M22 Response Provenance Compliance

### 4.1 What M22 Requires

> "All observability logs MUST record the actual provider that generated a response, not the configured intent."
> — SOVEREIGN_MANDATES.md §22

### 4.2 What's Implemented

| Component | Status | Evidence |
|-----------|--------|----------|
| `GenerateResult.provider_name` field | ✅ PRESENT | `model_gateway.py:45` — populated from `success_provider.name` |
| `GenerateResult.is_cloud` field | ✅ PRESENT | `model_gateway.py:46` — populated from `_is_cloud_provider()` |
| `oracle.py` reads `res.provider_name` | ✅ PRESENT | Lines 608, 680: `backend = res.provider_name` |
| `trace.record()` logs backend | ✅ PRESENT | Line 636: `backend=backend` |
| Provider name at inference boundary | ✅ PRESENT | `model_gateway.py:911`: `provider_name=success_provider.name` |

### 4.3 M22 Compliance Verdict

**M22 is COMPLIANT** at the `GenerateResult` level — the actual provider name is captured from the provider that served the response, not from the configuration intent. The `GenerateResult` dataclass carries `provider_name` from `success_provider.name` (the actual provider), and `oracle.py` reads it correctly.

**However**, the broken trace chain (§1) means forensic logs cannot reconstruct *which trace* produced *which provider response*. The provenance data exists per-interaction but is not linkable across the full call chain.

---

## §5 Gap Analysis — What's Missing

### 5.1 Critical Gaps (Must-Fix Before Epoch I)

| Gap | Impact | Fix Effort | Owner |
|-----|--------|------------|-------|
| **trace_id not passed to model_gateway.generate()** from oracle.py (2 sites) | Broken forensic chain for all summon/route queries | 5 min (add `trace_id=trace.trace_id` parameter) | P3 Engineering |
| **trace_id not passed** from iterative_research.py (3 sites) | Research traces are orphaned | 5 min (need to accept trace_id in IterativeResearcher) | P3 Engineering |
| **trace_id not passed** from skeptical_verifier.py (2 sites) | Verification traces are orphaned | 5 min (need to accept trace_id in SkepticalVerifier) | P3 Engineering |
| **entity_name not passed** from any oracle.py call site | BudgetGate cannot track per-entity cloud spend | 5 min (add `entity_name=entity.name`) | P3 Engineering |

### 5.2 Moderate Gaps (Should-Fix Before Epoch I)

| Gap | Impact | Fix Effort | Owner |
|-----|--------|------------|-------|
| Dataset collection config not verified in bootstrap path | Silent data collection failure | 15 min (add startup log + test) | P1 Infrastructure |
| `latency_ms` not populated in GenerateResult | Cannot track inference latency per provider | 30 min (measure at provider.generate call) | P3 Engineering |
| No trace_id in BudgetGate calls from oracle.py | Budget decisions not traceable | 5 min | P3 Engineering |

### 5.3 Nice-to-Have (Can Defer)

| Gap | Impact | Fix Effort |
|-----|--------|------------|
| Token ledger integration with trace_id | Token cost per trace | 1 hr |
| Cross-session trace correlation (parent_trace_id) | Multi-turn research trace trees | 2 hr |

---

## §6 Recommended Fix — The Trace Propagation Patch

The minimal fix for the 7 broken call sites:

### oracle.py — _summon_direct() (line 599)

```python
# BEFORE:
res = await self.model_gateway.generate(
    model_name=model_name,
    system_prompt=effective_system_prompt,
    user_query=query,
    temperature=effective_temperature,
    max_tokens=effective_max_tokens,
)

# AFTER:
res = await self.model_gateway.generate(
    model_name=model_name,
    system_prompt=effective_system_prompt,
    user_query=query,
    temperature=effective_temperature,
    max_tokens=effective_max_tokens,
    trace_id=trace.trace_id,
    entity_name=entity.name,
)
```

### oracle.py — _route_by_domain() (line 671)

```python
# BEFORE:
res = await self.model_gateway.generate(
    model_name=model_name,
    system_prompt=system_prompt,
    user_query=text,
    temperature=entity.temperature,
    max_tokens=1024,
)

# AFTER:
res = await self.model_gateway.generate(
    model_name=model_name,
    system_prompt=system_prompt,
    user_query=text,
    temperature=entity.temperature,
    max_tokens=1024,
    trace_id=trace.trace_id,
    entity_name=entity.name,
)
```

### iterative_research.py & skeptical_verifier.py

These need `trace_id` threaded through their constructors or method signatures from the oracle layer.

---

## §7 GO / NO-GO Recommendation

### 🔴 NO-GO for Epoch I Phase 1

**Rationale**:

1. **M22 is partially violated**: While `GenerateResult.provider_name` captures the actual provider, the broken trace chain means forensic logs cannot reconstruct *which trace* produced *which provider response*. M22 requires "record the actual provider" — but without trace_id, the record is unlinkable.

2. **7/8 call sites are orphan traces**: Any inference error, fallback, or performance issue in the primary oracle paths (summon, domain-route) produces logs with no trace_id, making debugging impossible.

3. **BudgetGate is blind**: Entity-level cloud cost tracking cannot work because entity_name is never forwarded.

4. **Dataset collection is unverified**: The config says `true` but the bootstrap path is not verified.

**Gate Criteria** (must pass all for GO):

| Gate | Criterion | Current | Status |
|------|-----------|---------|--------|
| G1 | All oracle.py generate() calls pass trace_id | 0/2 | ❌ FAIL |
| G2 | All iterative_research generate() calls pass trace_id | 0/3 | ❌ FAIL |
| G3 | All skeptical_verifier generate() calls pass trace_id | 0/2 | ❌ FAIL |
| G4 | GenerateResult.provider_name populated from actual provider | Yes | ✅ PASS |
| G5 | Dataset collection config verified in bootstrap | Unknown | ⏸️ UNVERIFIED |
| G6 | entity_name forwarded to BudgetGate | 0/8 | ❌ FAIL |

**Estimated fix effort**: 30 minutes for all critical gaps. The patches are mechanical (adding keyword arguments to existing function calls).

---

## §8 Recommendation to Kali

> **P8 WatchTower recommends a 30-minute remediation sprint before Epoch I Phase 1 begins.**
>
> The fix is mechanical: add `trace_id=trace.trace_id` and `entity_name=entity.name` to 7 call sites in `oracle.py`, `iterative_research.py`, and `skeptical_verifier.py`. Verify dataset collection bootstrap. Then re-run this audit.
>
> The observability *infrastructure* is strong. The *propagation* is broken. Fix the plumbing, and the system delivers on its M22 promise.

---

*P8 WatchTower — Observability & Tracing*
*Review completed: 2026-06-25*
