<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 DOOM GUY TIER 2 — Circuit Breaker Consolidation
# ⬡ OMEGA ⬡ DOOM_GUY ⬡ doom_guy.md ⬡ Gemma 4 31B ⬡ SPRINT-DOOM
# Date: 2026-06-02 | Synthesized by Opus 4.6 from 3-model audit chain
# Replaces: PROMPT_OPENCODE_DOOM_GUY_SPRINT_INIT_20260602.md (corrected)

---

## 0. MISSION SUMMARY & RULES OF ENGAGEMENT

You are executing a focused architectural pass on the Omega Engine's provider resilience layer. 

**Wait for Dev Sprint 0**: You must wait for the `OPENCODE_DEV_LIVE_FEED.md` to post `[C1] DONE` before starting Task D1. 
*Recovery Pattern*: If Dev session posts `[C1] FAILED` or 4 hours pass with no update, begin Task D2 (Consolidation) anyway — it does not depend on C1. Only D1 depends on C1.

### CRITICAL RULES
1. Run `make test` after EVERY file edit. **All 302 tests must pass.** (Baseline is 302, not 276).
2. Use AnyIO, never asyncio.
3. Never use bare `except:` — always catch specific exceptions or add `logger.warning()`.
4. All new error types MUST inherit from `OmegaError` in `src/omega/errors.py`.
5. **READ BEFORE CODING**: The `generate()` and `_precheck_provider()` methods in `model_gateway.py` (lines 395-510) already contain 80+ lines of implementation. Do NOT blindly copy-paste greenfield snippets from older handoffs. Integrate cleanly into the existing logic.

### ASSETS & FACTS
- `circuit_breaker.py` — **ALREADY DELETED** in a prior session. Do not try to delete it again or look for it.
- `src/omega/oracle/health_monitor.py` (440 lines) — The surviving breaker implementation.
- `src/omega/oracle/model_gateway.py` (729 lines) — `generate()` is at line 438.
- `src/omega/oracle/backends/remote_provider.py` (246 lines) — Contains primitive breaker logic to remove.

---

## TASKS — EXECUTE IN ORDER

| # | Task | File(s) | Risk |
|---|------|---------|------|
| **D2** | Consolidate Breakers | `remote_provider.py` | LOW |
| **D3** | Trace ID Propagation | `health_monitor.py` | LOW |
| **D4** | BSP Culling Fix | `model_gateway.py` | MEDIUM |
| **D5** | Exhaustion Trip Fix | `remote_provider.py` | HIGH |
| **D1** | Wire into `generate()` | `model_gateway.py` | HIGH |

---

### D2 — Consolidate Breakers (Clean up `remote_provider.py`)

**What**: `remote_provider.py` has its own primitive `consecutive_failures` breaker that overlaps with `HealthMonitor`. We only want one breaker system.

**Action**:
1. In `src/omega/oracle/backends/remote_provider.py`: Remove `consecutive_failures` from `ProviderMetrics` (line 43).
2. Remove the health degradation logic that checks `consecutive_failures > 0` (lines 100-101).
3. Remove all increments/resets of `consecutive_failures` in `generate()` (lines 172, 190, 212).
4. Remove it from `get_status()` output (line 225).

**Verification**: `make test` must pass.

---

### D3 — Trace ID Propagation (Mandate 9 Fix)

**What**: `AsyncCircuitBreaker` in `health_monitor.py` tries to log state transitions to the observability engine (lines 130-141, 154-166). However, the `except Exception:` blocks silently pass, violating Mandate 9 (Error Integrity).

**Action**:
1. In `src/omega/oracle/health_monitor.py`: Update the `except Exception:` blocks in `_on_success` and `_on_failure` to log the error.

```python
# health_monitor.py ~line 141
except Exception as e:
    logger.debug(f"Failed to log circuit state transition: {e}")
```

**Verification**: `make test` must pass.

---

### D4 — BSP Culling Fix (Provider vs Model Name Bug)

**What**: In `model_gateway.py:404`, `_precheck_provider` does `if not self._health_monitor.is_available(model_name):`. But the HealthMonitor expects a model name and does a dict lookup. The `_precheck_provider` logic is iterating over *providers*, not models. This can cause valid fallbacks to be skipped.

**Action**:
1. In `src/omega/oracle/model_gateway.py`: Update `_precheck_provider` to check the breaker explicitly using `provider.name`, since we are testing if the *provider's circuit* is open.

```python
# model_gateway.py:404
if self._health_monitor:
    breaker = self._health_monitor._breakers.get(provider.name)
    if breaker and not breaker.is_available:
        return False
```

**Verification**: `make test` must pass.

---

### D5 — Exhaustion Trip Fix (The Silent `None` Bug)

**What**: In `src/omega/oracle/backends/remote_provider.py:207-208`, if all retries fail, `generate()` logs an error and returns `None`. 
**The Bug**: Because it doesn't *raise* an exception, the `AsyncCircuitBreaker` in `model_gateway.py` thinks the call was a SUCCESS and records a success, meaning the circuit breaker **never trips** for cloud providers.

**Action**:
1. In `src/omega/errors.py`: Add `ProviderExhaustedError(OmegaError)`.
2. In `remote_provider.py:207`: Instead of returning `None`, raise `ProviderExhaustedError`.

```python
# remote_provider.py:207
logger.error(f"Provider {self.name} exhausted all retries. Last error: {last_error}")
from omega.errors import ProviderExhaustedError
raise ProviderExhaustedError(f"Provider {self.name} exhausted retries. Last error: {last_error}")
```

**Verification**: `make test` must pass. You may need to update tests if they expect `None` from `RemoteProvider.generate()`.

---

### D1 — Wire Breaker into `generate()` (The Capstone)

**WAIT FOR DEV SPRINT C1 COMPLETION BEFORE STARTING THIS.**

**What**: `model_gateway.py`'s `generate()` (line 438) uses a timeout but lacks proper `AsyncCircuitBreaker.call()` wrapping.

**Action**:
1. Refactor `generate()` to wrap the `provider.generate` call inside `breaker.call()`, exactly as described in the original DOOM_GUY handoff, but **integrate cleanly with the existing code** (which already has timeouts and tracing).

```python
# model_gateway.py:464
if self._health_monitor:
    breaker = self._health_monitor._breakers.get(provider.name)
    if breaker:
        result = await breaker.call(
            provider.generate, model_name, system_prompt,
            user_query, temperature, max_tokens,
            trace_id=trace_id
        )
    else:
        # ... fallback to direct call
```
**Note**: The current code actually *has* this structure around line 464, but ensure it catches `CircuitOpenError` explicitly (line 493) and handles `ProviderExhaustedError` cleanly.

**Verification**: `make test` must pass.

---

## DELIVERY PROTOCOL

After each task lands, emit a handoff fragment:

```markdown
## [TASK-ID] — [STATUS] — [TIMESTAMP]
**File(s)**: [absolute paths]
**Diff stat**: +X -Y
**Test result**: N/302 passing in T seconds
**Mandate check**: M1✓ M2✓ M9✓ M13✓
**PIVOT_LOG entry**: D[N] [title]
```

Write each to `data/handoff/DOOM_GUY_RETURN_[TASK-ID]_[TIMESTAMP].md`.
Append a 1-line summary to `data/handoff/DOOM_GUY_LIVE_FEED.md`.

## SUCCESS CRITERIA

Sprint is complete when ALL of:
- [ ] `make test` passes 302/302 tests
- [ ] `make temple-grade` exits 0
- [ ] All handoff return files written
- [ ] `data/handoff/DOOM_GUY_LIVE_FEED.md` has one line per task completed

Then emit `[SPRINT-DOOM] COMPLETE [TIMESTAMP]` to the live feed.

**PIVOT_LOG entries required:** Log D94-D98 for tasks D2-D5 + D1 respectively.

---

⬡ OMEGA ⬡ DOOM_GUY ⬡ doom_guy.md ⬡ SPRINT-DOOM ⬡ BEGIN WITH D2

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: doom_guy.md | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
