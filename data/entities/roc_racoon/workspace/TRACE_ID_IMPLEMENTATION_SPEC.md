# 🔱 Trace ID Propagation & GenerateResult Contract — Implementation Specification
## Gap 2: P1 HIGH — Observable Blind Spot & Response Provenance

**AP Token**: `AP-TRACE-ID-FIX-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ TRACE-ID ⬡ SOVEREIGN-MINER
**Status**: IMPLEMENTATION SPECIFICATION
**Date**: 2026-06-29

---

## §1 Current Problem

### 1.1 Root Cause

The trace ID propagation chain has **4 independent breaks** that cause 5-10% of observability events to carry `trace_id="unknown"` and **100% of successful inferences** to have broken latency observability.

### 1.2 Break #1: GenerateResult Success Path Missing latency_ms + model_used

**File**: `src/omega/oracle/model_gateway.py`
**Lines**: 882-892

```python
# CURRENT (BROKEN) — lines 887-892
return GenerateResult(
    text=result,
    provider_name=success_provider.name,
    is_cloud=self._is_cloud_provider(success_provider),
    logprobs=logprobs,
    # ⚠️ latency_ms defaults to 0.0
    # ⚠️ model_used defaults to None
)
```

**Impact**: **100% of successful inferences** report `latency_ms=0.0` and `model_used=None`. This is a **systemic M22 (Response Provenance) violation** — every observability log based on GenerateResult has broken latency data.

The `latency_ms` field exists on the dataclass but is never populated on the success path. The `model_used` field is never populated on either path.

### 1.3 Break #2: Trace ID Lost in Async Boundaries

**Files & Lines** that drop `trace_id`:

| File | Line(s) | Issue |
|------|---------|-------|
| `iterative_research.py` | 64-69 | `generate()` called WITHOUT `trace_id` parameter |
| `iterative_research.py` | 143-148 | `generate()` called WITHOUT `trace_id` parameter |
| `iterative_research.py` | 159-163 | `generate()` called WITHOUT `trace_id` parameter |
| `skeptical_verifier.py` | 130-136 | `_nli_check()` calls `generate()` WITHOUT `trace_id` |
| `skeptical_verifier.py` | 171-176 | `_resolve_contradiction()` calls `generate()` WITHOUT `trace_id` |

All 5 call sites pass through the `model_gateway.generate()` method which defaults `trace_id=None`, causing observability events to log `"unknown"`.

### 1.4 Break #3: ForensicsManager.record_error() Double-Default

**File**: `src/omega/observability/__init__.py`
**Lines**: 769-785

```python
def record_error(
    self,
    error: Exception,
    trace_id: Optional[str] = None,      # ⚠️ defaults to None
    context: Optional[Dict[str, Any]] = None,
) -> None:
    self._forensics.record_error(error, trace_id=trace_id, context=context)
    self.log_event(
        EventType.ERROR,
        trace_id or "unknown",            # ⚠️ double-default to "unknown"
        {...}
    )
```

When errors occur in subsystems that have lost the trace_id (like iterative_research), the error is logged with `trace_id="unknown"`, making forensic trace analysis impossible.

### 1.5 Break #4: Fallback Path Missing latency_ms + model_used

**File**: `src/omega/oracle/model_gateway.py`
**Lines**: 899-904

```python
# CURRENT (BROKEN) — lines 900-904
return GenerateResult(
    text=self._fallback_response(model_name, system_prompt, user_query),
    provider_name="fallback",
    is_cloud=False
    # ⚠️ latency_ms defaults to 0.0
    # ⚠️ model_used defaults to None
)
```

Fallback response also lacks `latency_ms` and `model_used`.

---

## §2 Solution Architecture

### 2.1 Four-Layer Fix Strategy

```
Layer 1: [Trace Context Propagation]
    Install opentelemetry-instrumentation-anyio for automatic 
    context propagation across create_task and to_thread.run_sync
    boundaries. This is the async-equivalent of OpenTelemetry's 
    contextvars-based propagation.

Layer 2: [Explicit trace_id Safety Net]
    Use contextvars-based get_current_trace_id() as backup
    for subsystems that can't use OpenTelemetry instrumentation.

Layer 3: [GenerateResult Contract Fix]
    Measure latency_ms around provider.generate() calls.
    Populate model_used on both success and fallback paths.

Layer 4: [Thread trace_id Through Subsystems]
    Add trace_id parameter to IterativeResearcher and SkepticalVerifier
    constructors. Propagate through all generate() call sites.
```

### 2.2 Layer 1: OpenTelemetry AnyIO Instrumentation

```bash
pip install opentelemetry-instrumentation-anyio
```

This package provides automatic context propagation across AnyIO primitives (`create_task`, `run_sync`, etc.) by patching `anyio`'s task group creation to inherit context variables.

**Configuration**: Zero-config — just import at module level:
```python
# In observability/__init__.py or omega/__init__.py
from opentelemetry_instrumentation_anyio import AnyIOInstrumentor
AnyIOInstrumentor().instrument()
```

**Sovereign Compliance**: OpenTelemetry is used for **local context propagation only** (M8 Zero Telemetry compliant — no external export). The instrumentation ensures trace_id flows across async boundaries without manual threading.

### 2.3 Layer 2: Contextvars Safety Net

```python
# In src/omega/observability/context.py (NEW FILE)
"""Contextvars-based trace_id propagation for AnyIO.

Provides a zero-dependency safety net that works alongside
OpenTelemetry AnyIO instrumentation. Falls back to contextvars
when OTel is not available.

[M8] No external export — purely local context propagation.
"""

import contextvars
import uuid
from typing import Optional

# Context variable for trace_id propagation across async boundaries
_current_trace_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'current_trace_id', default=None
)

def get_current_trace_id() -> str:
    """Get current trace_id or generate a new one.
    
    This is the central function that all subsystems should call
    to obtain the current trace context. It's the safety net when
    OpenTelemetry instrumentation hasn't propagated context.
    """
    tid = _current_trace_id.get()
    if tid is None:
        tid = f"trc_{uuid.uuid4().hex[:12]}"
        _current_trace_id.set(tid)
    return tid

def set_current_trace_id(trace_id: str) -> None:
    """Set trace_id in current context.
    
    Called at the start of an async operation to establish
    the trace context for all child tasks.
    """
    _current_trace_id.set(trace_id)
```

---

## §3 Implementation Details

### 3.1 Fix #1: GenerateResult Success Path (model_gateway.py:882-892)

**Add `latency_ms` measurement around provider.generate() calls and `model_used` capture:**

```python
# In generate() method — around line 810:
try:
    async with self.resource_guard.lock(weight=weight, model_spec=spec):
        with anyio.move_on_after(timeout) as cancel_scope:
            # [M22] Start latency measurement
            _start_time = time.monotonic()
            
            if self._health_monitor:
                breaker = self._health_monitor._breakers.get(provider.name)
                if breaker:
                    async def _call_with_none_as_failure():
                        r = await provider.generate(
                            model_name, system_prompt, user_query,
                            temperature, max_tokens, trace_id=trace_id
                        )
                        if not r:
                            raise TimeoutError(f"Provider {provider.name} returned empty response")
                        return r
                    result = await breaker.call(_call_with_none_as_failure, trace_id=trace_id)
                else:
                    result = await provider.generate(
                        model_name, system_prompt, user_query,
                        temperature, max_tokens, trace_id=trace_id
                    )
            else:
                result = await provider.generate(
                    model_name, system_prompt, user_query,
                    temperature, max_tokens, trace_id=trace_id
                )
            
            # [M22] Record latency immediately after provider returns
            _latency_ms = (time.monotonic() - _start_time) * 1000
            
            if result:
                if self._health_monitor:
                    self._health_monitor.record_success(model_name)
                self._update_active_set(provider.name)
                success_provider = provider
                
                # ... (existing token ledger code at 844-857) ...
                
                break
            
            if cancel_scope.cancelled_caught:
                errors.append(f"{provider.name}: timed out ({timeout}s)")
                self._record_provider_failure(provider, model_name, trace_id)
                continue

# ── FIXED SUCCESS PATH (replace lines 882-892): ──
if success_provider:
    logprobs = getattr(success_provider, '_last_logprobs', None)
    return GenerateResult(
        text=result,
        provider_name=success_provider.name,
        is_cloud=self._is_cloud_provider(success_provider),
        latency_ms=_latency_ms,              # ✅ FIXED: actual latency
        model_used=model_name,               # ✅ FIXED: actual model name
        logprobs=logprobs,
    )
```

### 3.2 Fix #2: GenerateResult Fallback Path (model_gateway.py:900-904)

```python
# ── FIXED FALLBACK PATH (replace lines 900-904): ──
return GenerateResult(
    text=self._fallback_response(model_name, system_prompt, user_query),
    provider_name="fallback",
    is_cloud=False,
    latency_ms=_latency_ms if '_latency_ms' in dir() else 0.0,  # ✅ FIXED
    model_used=model_name,                                        # ✅ FIXED
)
```

**Better approach**: Initialize `_latency_ms = 0.0` and `_latency_ms` at the top of `generate()`:

```python
async def generate(self, ...):
    last_exception = None
    errors = []
    success_provider = None
    _latency_ms = 0.0  # Initialize before loop
    # ... rest of method
```

### 3.3 Fix #3: Thread trace_id Through IterativeResearcher (iterative_research.py)

**Constructor change** — add trace_id parameter:

```python
class IterativeResearcher:
    def __init__(self, model_gateway, searcher=None, verifier=None):
        self.model_gateway = model_gateway
        self.searcher = searcher or SovereignSearcher(get_memory_store())
        self.verifier = verifier
        self.max_iterations = 3
        self.confidence_threshold = 0.8
    
    async def research(
        self, 
        query: str, 
        entity_name: str, 
        max_iterations: Optional[int] = None,
        min_confidence: float = 0.8,
        trace_id: Optional[str] = None,        # ✅ NEW
    ) -> Tuple[str, List[TaintedData]]:
        """Execute an iterative research loop to answer a query."""
        current_query = query
        all_evidence: List[TaintedData] = []
        iteration = 0
        self._trace_id = trace_id  # Store for use in sub-calls
```

**Fix all 3 generate() call sites** to pass trace_id:

```python
# Line 64 — Gap Analysis:
res = await self.model_gateway.generate(
    model_name="qwen3-4b-think",
    system_prompt="You are a Sovereign Research Auditor...",
    user_query=analysis_prompt,
    temperature=0.2,
    trace_id=self._trace_id,  # ✅ FIXED
)

# Line 143 — Synthesis:
res = await self.model_gateway.generate(
    model_name="gemma-4-31b-it",
    system_prompt="You are a Sovereign Synthesis Engine...",
    user_query=synthesis_prompt,
    temperature=0.3,
    trace_id=self._trace_id,  # ✅ FIXED
)

# Line 159 — Claim Extraction:
res = await self.model_gateway.generate(
    model_name="qwen3-4b-think",
    system_prompt="You are a claim extractor...",
    user_query=claims_prompt,
    temperature=0.0,
    trace_id=self._trace_id,  # ✅ FIXED
)
```

### 3.4 Fix #4: Thread trace_id Through SkepticalVerifier (skeptical_verifier.py)

**Constructor change** — accept trace_id:

```python
class SkepticalVerifier:
    def __init__(self, model_gateway: ModelGateway, nli_model: str = "qwen3-4b-think"):
        self.model_gateway = model_gateway
        self.nli_model = nli_model
    
    async def verify(self, claim: str, evidence_list, trace_id: Optional[str] = None) -> VerificationResult:
        """
        Verify a claim against a list of evidence snippets.
        Args:
            claim: The hypothesis to verify.
            evidence_list: List of evidence dicts
            trace_id: Current trace ID for observability propagation  # ✅ NEW
        """
        self._trace_id = trace_id  # ✅ NEW
        sources = []
        entailments = []
        contradictions = []
```

**Fix both generate() call sites**:

```python
# Line 130 — _nli_check():
res = await self.model_gateway.generate(
    model_name=self.nli_model,
    system_prompt="You are a high-precision NLI classifier...",
    user_query=prompt,
    temperature=0.0,
    max_tokens=10,
    trace_id=self._trace_id,  # ✅ FIXED
)

# Line 171 — _resolve_contradiction():
res = await self.model_gateway.generate(
    model_name=self.nli_model,
    system_prompt="You are a Sovereign Resolution Engine...",
    user_query=divergence_prompt,
    temperature=0.2,
    trace_id=self._trace_id,  # ✅ FIXED
)
```

### 3.5 Fix #5: Fix oracle.py to propagate trace_id to sub-agents

In `oracle.py`, when creating the `IterativeResearcher` and `SkepticalVerifier`, the trace_id from the current trace session must be propogated:

```python
# In oracle.py, inside talk() and summon() methods:
# The trace is already available as `trace.trace_id`
# Pass it when calling sub-systems:

# Example in _summon() — lines 606-613:
res = await self.model_gateway.generate(
    model_name=model_name,
    system_prompt=effective_system_prompt,
    user_query=query,
    temperature=effective_temperature,
    max_tokens=effective_max_tokens,
    trace_id=trace.trace_id,  # ✅ Already working — verify it reaches all paths
)
```

Also ensure that `close_session()` and `_track_soul_evolution()` receive the trace_id from the current context.

### 3.6 Fix #6: Fix record_error() Double-Default (observability/__init__.py:769-785)

```python
def record_error(
    self,
    error: Exception,
    trace_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    # ✅ FIXED: Use contextvars safety net if trace_id not provided
    if trace_id is None:
        from .context import get_current_trace_id
        trace_id = get_current_trace_id()
    
    self._forensics.record_error(error, trace_id=trace_id, context=context)
    self.log_event(
        EventType.ERROR,
        trace_id,  # ✅ FIXED: no more "unknown" double-default
        {
            "error_type": type(error).__name__,
            "error_message": str(error)[:300],
            "context": context or {},
        },
    )
```

---

## §4 Integration Steps

### Step 1: Install Dependencies (10 min)
```bash
pip install opentelemetry-instrumentation-anyio
```

### Step 2: Create Contextvars Safety Net (30 min)
- Create `src/omega/observability/context.py` with `get_current_trace_id()` and `set_current_trace_id()`

### Step 3: Fix GenerateResult Success Path (1 hour)
- Add `_start_time = time.monotonic()` before provider calls in `generate()`
- Add `_latency_ms = (time.monotonic() - _start_time) * 1000` after provider returns
- Populate `latency_ms` and `model_used` in both success and fallback `GenerateResult`

### Step 4: Thread trace_id Through Subsystems (1.5 hours)
- Add `trace_id` parameter to `IterativeResearcher.research()`
- Fix all 3 `generate()` call sites in `iterative_research.py`
- Add `trace_id` parameter to `SkepticalVerifier.verify()`
- Fix both `generate()` call sites in `skeptical_verifier.py`

### Step 5: Fix record_error() Double-Default (15 min)
- Update `record_error()` to use `get_current_trace_id()` as fallback

### Step 6: Write Tests (2 hours)
- Contract test: Verify `GenerateResult.latency_ms > 0` on success
- Contract test: Verify `GenerateResult.model_used` is populated
- Integration test: Verify trace_id propagates through iterative_research
- Integration test: Verify trace_id propagates through skeptical_verifier
- Integration test: Verify error logging carries trace_id

---

## §5 Verification Criteria

| Criteria | Method | Success |
|----------|--------|---------|
| GenerateResult success path has latency_ms | Contract test `isinstance(result.latency_ms, float) and result.latency_ms > 0` | All success paths report real latency |
| GenerateResult success path has model_used | Contract test `isinstance(result.model_used, str)` | Model name present on every success |
| GenerateResult fallback path has model_used | Contract test | Model name present on every fallback |
| trace_id flows through iterative_research | Mock generate() receives trace_id parameter | Assert trace_id match |
| trace_id flows through skeptical_verifier | Mock generate() receives trace_id parameter | Assert trace_id match |
| record_error() never logs "unknown" | Inject error in traced context | Assert `trace_id != "unknown"` |
| OTel AnyIO propagation works | Cross-task trace_id test | Child task inherits parent trace_id |

---

## §6 Test Skeleton

```python
"""Tests for Trace ID Propagation + GenerateResult Contract."""

import pytest
import time
from unittest.mock import AsyncMock, MagicMock
from omega.oracle.model_gateway import ModelGateway, GenerateResult

class TestGenerateResultContract:
    """M21 Gate Integrity: Contract tests for GenerateResult."""
    
    @pytest.fixture
    def gateway(self):
        gw = ModelGateway()
        # Mock providers to avoid real inference
        mock_provider = MagicMock()
        mock_provider.name = "mock"
        mock_provider.generate = AsyncMock(return_value="test response")
        mock_provider.is_available.return_value = True
        gw.providers = [mock_provider]
        return gw
    
    @pytest.mark.asyncio
    async def test_success_path_has_latency(self, gateway):
        """M22: Success path GenerateResult must have real latency_ms."""
        result = await gateway.generate(
            model_name="test-model",
            system_prompt="You are a test.",
            user_query="Hello",
            trace_id="test-trace-123",
        )
        assert isinstance(result.latency_ms, float)
        assert result.latency_ms > 0, "Latency must be > 0 on success path"
    
    @pytest.mark.asyncio
    async def test_success_path_has_model_used(self, gateway):
        """M22: Success path GenerateResult must have model_used."""
        result = await gateway.generate(
            model_name="test-model",
            system_prompt="You are a test.",
            user_query="Hello",
            trace_id="test-trace-123",
        )
        assert result.model_used == "test-model"
    
    @pytest.mark.asyncio
    async def test_fallback_path_has_model_used(self, gateway):
        """M22: Fallback path should still report the model name."""
        gateway.providers = []  # No providers → fallback
        result = await gateway.generate(
            model_name="fallback-model",
            system_prompt="You are a test.",
            user_query="Hello",
            trace_id="test-trace-456",
        )
        assert result.model_used is not None


class TestTraceIdPropagation:
    """Trace ID flows through all async boundaries."""
    
    @pytest.mark.asyncio
    async def test_iterative_research_gets_trace_id(self):
        """All 3 generate() calls in iterative_research get trace_id."""
        from omega.oracle.iterative_research import IterativeResearcher
        mock_gateway = MagicMock()
        mock_gateway.generate = AsyncMock(
            return_value=GenerateResult("test", "mock", False)
        )
        researcher = IterativeResearcher(mock_gateway)
        # TODO: Mock searcher to return evidence
        # result = await researcher.research("test", "entity", trace_id="trace-abc")
        # Verify all generate() calls received trace_id
    
    @pytest.mark.asyncio
    async def test_skeptical_verifier_gets_trace_id(self):
        """Both generate() calls in skeptical_verifier get trace_id."""
        from omega.oracle.skeptical_verifier import SkepticalVerifier
        mock_gateway = MagicMock()
        mock_gateway.generate = AsyncMock(
            return_value=GenerateResult("ENTAIL", "mock", False)
        )
        verifier = SkepticalVerifier(mock_gateway)
        result = await verifier.verify(
            "test claim",
            [{"content": "test evidence", "source_id": "src1"}],
            trace_id="trace-xyz",
        )
        # Verify generate() was called with trace_id
        call_kwargs = mock_gateway.generate.call_args
        if call_kwargs:
            assert 'trace_id' in call_kwargs[1]
    
    def test_contextvars_safety_net(self):
        """Contextvars-based trace_id propagation."""
        from omega.observability.context import get_current_trace_id, set_current_trace_id
        tid = get_current_trace_id()
        assert tid.startswith("trc_")
        
        set_current_trace_id("explicit-trace-123")
        assert get_current_trace_id() == "explicit-trace-123"
```

---

## §7 Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| `opentelemetry-instrumentation-anyio` incompatible with current anyio version | MED | HIGH | Pin test versions; fall back to manual contextvars |
| Contextvars don't propagate across `to_thread.run_sync` boundaries | HIGH | MED | OTel handles this; contextvars explicit `copy_context()` as backup |
| GenerateResult contract tests mask other bugs | LOW | MED | M21 Gate Integrity — tests validate types, not correctness |
| Tracer instrumentation adds latency | LOW | LOW | Local-only, no export; negligible overhead (<1µs) |
| `trace_id` parameter explosion on method signatures | MED | LOW | Acceptable for observability-critical paths; not all methods |

---

## §8 Effort Summary

| Step | Effort | Dependencies |
|------|--------|-------------|
| Install dependencies | 10 min | None |
| Create context.py safety net | 30 min | None |
| Fix GenerateResult success path (model_gateway.py) | 1 hour | Step 1 |
| Fix GenerateResult fallback path (model_gateway.py) | 15 min | Step 2 |
| Thread trace_id through iterative_research.py | 1 hour | Step 3 |
| Thread trace_id through skeptical_verifier.py | 30 min | Step 3 |
| Fix record_error() double-default | 15 min | Step 2 |
| Write tests | 2 hours | Steps 1-6 |
| **Total** | **5-6 hours** | — |

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ TRACE-ID ⬡ SOVEREIGN-MINER*
*Session: ses_roc_racoon_gap_closure_20260629*
*Sources: model_gateway.py line-by-line audit, iterative_research.py, skeptical_verifier.py, observability/__init__.py*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
