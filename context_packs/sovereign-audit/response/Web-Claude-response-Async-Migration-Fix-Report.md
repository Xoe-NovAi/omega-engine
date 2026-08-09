---
account: arcana.novai@gmail.com
pack_version: 2026-08-08
pack_profile: sovereign-audit
pack_files: 32
pack_tokens: 173464
session_date: 2026-08-08
session_type: verification
---

# Async Migration Fix Report

**Scope caveat, stated once up front:** the XML pack is full-file dumps with no line numbers, so I cannot cite literal line numbers without fabricating them — that would violate the "don't hallucinate" rule and isn't worth the false precision. Every call site below is anchored to its exact enclosing method/function (unambiguous within each file), and I give you a grep command at the end to convert those into real line numbers against your actual working tree. I also could not inspect files outside these 8 bundles (`provider_selector.py`, `budget_gate.py`, `token_ledger.py`, `usm.py`, the UFL writer, `ObservabilityEngine`) — those are flagged separately as unverified, not silently assumed clean.

## Summary

| Metric | Count |
|---|---|
| Total call sites found (in-pack, verified) | **12** |
| Call sites already correctly using `await` | **0** |
| Call sites needing fix | **12** |
| Cascading functions requiring `async def` conversion | **1** (`ModelGateway._record_provider_failure`) |
| Additional out-of-pack risks flagged (not counted above) | 5 |

Two of the 12 are not simple "add `await`" fixes — they're **double-async-wrap bugs**: code that was already correctly written as `await anyio.to_thread.run_sync(self.fts.X, ...)` for the *old synchronous* `X()`, which now silently wraps a coroutine instead of a blocking call. `to_thread.run_sync` returns the un-awaited coroutine object as its result and nothing ever raises. These are the most dangerous ones in the list — they look correct on read-through.

---

## Critical Fixes (Data Loss)

### 1. `src/omega/observability/latency_tracker.py` — `LatencyTracker.record()`
**Call**:
```python
def record(self, provider: str, model: str, latency_ms: float, status: str = "success", trace_id: Optional[str] = None, is_cloud: bool = False):
    try:
        get_engine().record_performance(
            latency_ms=latency_ms, provider=provider, model_used=model,
            is_cloud=is_cloud, trace_id=trace_id
        )
    except (OmegaError, RuntimeError, OSError) as e:
        logger.error(f"Failed to record latency metric via engine: {e}")
```
**Fix**:
```python
async def record(self, provider: str, model: str, latency_ms: float, status: str = "success", trace_id: Optional[str] = None, is_cloud: bool = False) -> None:
    try:
        await get_engine().record_performance(
            latency_ms=latency_ms, provider=provider, model_used=model,
            is_cloud=is_cloud, trace_id=trace_id
        )
    except (OmegaError, RuntimeError, OSError) as e:
        logger.error(f"Failed to record latency metric via engine: {e}")
```
**Cascades**: Method itself was already listed as migrated to `async def` per your report. Every caller of `tracker.record(...)` (items #2, #3 below) must now be awaited — that's the actual production regression.

---

### 2. `src/omega/oracle/model_gateway.py` — `ModelGateway.generate()`, success path
**Call**:
```python
tracker.record(
    provider=provider.name,
    model=model_name,
    latency_ms=_latency_ms,
    status="success",
    trace_id=trace_id,
    is_cloud=self._is_cloud_provider(provider),
)
```
**Fix**:
```python
await tracker.record(
    provider=provider.name,
    model=model_name,
    latency_ms=_latency_ms,
    status="success",
    trace_id=trace_id,
    is_cloud=self._is_cloud_provider(provider),
)
```
**Cascades**: No — `generate()` is already `async def`.

---

### 3. `src/omega/oracle/model_gateway.py` — `ModelGateway._record_provider_failure()`
**Call**:
```python
def _record_provider_failure(self, provider, model_name: str, trace_id: Optional[str] = None):
    """Record provider failure with HealthMonitor and observability."""
    if self._health_monitor:
        self._health_monitor.record_failure(model_name)

    # Record failure in latency tracker (latency is 0 or estimated)
    tracker.record(
        provider=provider.name,
        model=model_name,
        latency_ms=0.0,
        status="failure",
        trace_id=trace_id
    )
    ...
```
**Fix**:
```python
async def _record_provider_failure(self, provider, model_name: str, trace_id: Optional[str] = None) -> None:
    """Record provider failure with HealthMonitor and observability."""
    if self._health_monitor:
        self._health_monitor.record_failure(model_name)

    # Record failure in latency tracker (latency is 0 or estimated)
    await tracker.record(
        provider=provider.name,
        model=model_name,
        latency_ms=0.0,
        status="failure",
        trace_id=trace_id
    )
    ...
```
**Cascades**: **Yes.** This method was previously `def` (sync). Converting it to `async def` requires every call site to add `await` — that's items #4, #5, #6 below. This is the one true "cascading function" in the pack. Note also the `get_engine().log_event(...)` call further down in the same method's `try` block — flagged separately below (out-of-pack-scope, `log_event` not in your migrated list, but same class family).

---

### 4. `src/omega/oracle/model_gateway.py` — `generate()`, cancel-scope timeout path
**Call**:
```python
if cancel_scope.cancelled_caught:
    errors.append(f"{provider.name}: timed out ({timeout}s)")
    self._record_provider_failure(provider, model_name, trace_id)
    continue
```
**Fix**:
```python
if cancel_scope.cancelled_caught:
    errors.append(f"{provider.name}: timed out ({timeout}s)")
    await self._record_provider_failure(provider, model_name, trace_id)
    continue
```
**Cascades**: No further cascade — direct consumer of the fix in #3, already inside `async def generate()`.

---

### 5. `src/omega/oracle/model_gateway.py` — `generate()`, `TimeoutError` except block
**Call**:
```python
except TimeoutError as e:
    errors.append(f"{provider.name}: {e}")
    self._record_provider_failure(provider, model_name, trace_id)
    continue
```
**Fix**:
```python
except TimeoutError as e:
    errors.append(f"{provider.name}: {e}")
    await self._record_provider_failure(provider, model_name, trace_id)
    continue
```
**Cascades**: No further cascade.

---

### 6. `src/omega/oracle/model_gateway.py` — `generate()`, generic `Exception` except block
**Call**:
```python
except Exception as e:
    last_exception = e
    logger.error(
        "ModelGateway.generate: unexpected error from provider=%s trace=%s err=%s",
        provider.name, trace_id, str(e), exc_info=True
    )
    errors.append(f"{provider.name}: {e}")
    self._record_provider_failure(provider, model_name, trace_id)
    continue
```
**Fix**:
```python
except Exception as e:
    last_exception = e
    logger.error(
        "ModelGateway.generate: unexpected error from provider=%s trace=%s err=%s",
        provider.name, trace_id, str(e), exc_info=True
    )
    errors.append(f"{provider.name}: {e}")
    await self._record_provider_failure(provider, model_name, trace_id)
    continue
```
**Cascades**: No further cascade.

---

### 7. `src/omega/oracle/health_monitor.py` — `AsyncCircuitBreaker._on_success()`
**Call**:
```python
if trace_id and old_state != self.state:
    try:
        from omega.observability import get_engine, EventType
        engine = get_engine()
        engine.log_event(
            EventType.BACKEND_FALLBACK, trace_id,
            {"provider": self.name, "event": "circuit_closed",
             "from": old_state.value, "to": self.state.value}
        )
        engine.record_breaker_transition(
            provider=self.name, from_state=old_state.value,
            to_state=self.state.value, trace_id=trace_id,
            reason="success_recovery",
        )
    except (OmegaError, RuntimeError, OSError) as e:
        logger.warning(f"Circuit closed event failed — observability unavailable: {e}")
        pass
```
**Fix**:
```python
if trace_id and old_state != self.state:
    try:
        from omega.observability import get_engine, EventType
        engine = get_engine()
        engine.log_event(
            EventType.BACKEND_FALLBACK, trace_id,
            {"provider": self.name, "event": "circuit_closed",
             "from": old_state.value, "to": self.state.value}
        )
        await engine.record_breaker_transition(
            provider=self.name, from_state=old_state.value,
            to_state=self.state.value, trace_id=trace_id,
            reason="success_recovery",
        )
    except (OmegaError, RuntimeError, OSError) as e:
        logger.warning(f"Circuit closed event failed — observability unavailable: {e}")
        pass
```
**Cascades**: No — `_on_success` is already `async def`. Note `engine.log_event(...)` on the line above is *not* fixed here — it's not one of your 14 listed migrated methods, flagged separately below.

---

### 8. `src/omega/oracle/health_monitor.py` — `AsyncCircuitBreaker._on_failure()`
**Call**:
```python
if trace_id and old_state != self.state:
    try:
        from omega.observability import get_engine, EventType
        engine = get_engine()
        engine.log_event(
            EventType.BACKEND_FALLBACK, trace_id,
            {"provider": self.name, "event": "circuit_opened",
             "from": old_state.value, "to": self.state.value,
             "failure_count": self.failure_count, "cusum": self.cusum_g}
        )
        engine.record_breaker_transition(
            provider=self.name, from_state=old_state.value,
            to_state=self.state.value, trace_id=trace_id,
            reason=f"failures={self.failure_count},cusum={self.cusum_g:.2f}",
        )
    except (OmegaError, RuntimeError, OSError) as e:
        logger.warning(f"Circuit opened event failed — observability unavailable: {e}")
        pass
```
**Fix**:
```python
        await engine.record_breaker_transition(
            provider=self.name, from_state=old_state.value,
            to_state=self.state.value, trace_id=trace_id,
            reason=f"failures={self.failure_count},cusum={self.cusum_g:.2f}",
        )
```
**Cascades**: No — `_on_failure` is already `async def`.

---

### 9. `src/omega/memory_store.py` — `MemoryStore.add_exchange()`, user turn
**Call**:
```python
try:
    self.fts.index_exchange(session_id, entity_name, "user", user_message)
    self.fts.index_exchange(session_id, entity_name, "assistant", response)
except (RuntimeError, OSError) as e:
    logger.warning("FTS dual-write failed for %s: %s", session_id, e)
```
**Fix**:
```python
try:
    await self.fts.index_exchange(session_id, entity_name, "user", user_message)
    await self.fts.index_exchange(session_id, entity_name, "assistant", response)
except (RuntimeError, OSError) as e:
    logger.warning("FTS dual-write failed for %s: %s", session_id, e)
```
**Cascades**: No — `add_exchange` is already `async def`. **Both** user (#9) and assistant (#10) calls sit in the same try block; fix together.

### 10. Same location — assistant turn
Covered in the single fix above.

---

### 11. `src/omega/memory_store.py` — `MemoryStore.search_fts()` — **double-wrap bug, not a missing await**
**Call**:
```python
async def search_fts(
    self,
    query: str,
    entity_name: str,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    if not query.strip():
        return []

    return await anyio.to_thread.run_sync(
        self.fts.search, query, entity_name, limit
    )
```
This was correctly written for the **old** synchronous `fts.search()`. Now that `search()` is `async def`, `anyio.to_thread.run_sync(self.fts.search, ...)` runs `self.fts.search(query, entity_name, limit)` in a worker thread — which does not execute the query, it just instantiates and returns a coroutine object almost instantly. `to_thread.run_sync` hands that coroutine object back as its "result." `search_fts()` then returns a **coroutine object, not a result list**, to its caller.

**Blast radius, traced in-pack**: `MemoryStore.search()` calls `fts_results = await self.search_fts(...)`, then does `enumerate(fts_results)` — iterating a coroutine object raises `TypeError: 'coroutine' object is not iterable`. This is loud (crashes hybrid search), not silent — but it's the exact same root cause class as #12, and it's the one that will page someone the moment hybrid search is exercised.

**Fix**:
```python
async def search_fts(
    self,
    query: str,
    entity_name: str,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    if not query.strip():
        return []

    return await self.fts.search(query, entity_name, limit)
```
**Cascades**: No — `search_fts` is already `async def`, its caller (`MemoryStore.search()`) already `await`s it correctly. The fix is entirely local: delete the `to_thread.run_sync` wrapper, call `fts.search` directly with `await`.

---

### 12. `src/omega/memory_store.py` — `MemoryStore.archive_session()` — **double-wrap bug, silent (this is your worst one)**
**Call**:
```python
# [Horizon 2: MiMo] FTS5 Cleanup (C1 fix)
try:
    await anyio.to_thread.run_sync(self.fts.remove_session, session_id)
except (RuntimeError, OSError) as e:
    logger.warning("FTS cleanup failed for %s: %s", session_id, e)
```
Same double-wrap as #11, but here it's genuinely silent. `anyio.to_thread.run_sync(self.fts.remove_session, session_id)` constructs the coroutine, returns it as the thread-pool result, and the outer `await` on `to_thread.run_sync(...)` completes successfully — no exception, nothing for the `except` clause to catch. Python's garbage collector will eventually print `RuntimeWarning: coroutine 'ConversationFTSIndex.remove_session' was never awaited` to stderr, but nothing surfaces in application logs and the function returns normally. **The `DELETE FROM exchanges WHERE session_id = ?` never runs.** Archived sessions keep their FTS index entries permanently — stale, searchable content for sessions the rest of the system believes are archived. This is the textbook "no exception, no warning, just silent data loss" case you described in the bug report.

**Fix**:
```python
try:
    await self.fts.remove_session(session_id)
except (RuntimeError, OSError) as e:
    logger.warning("FTS cleanup failed for %s: %s", session_id, e)
```
**Cascades**: No — `archive_session` is already `async def`.

---

## Needs Verification — Outside Pack Scope (not counted in the 12 above)

I'm listing these because your instruction was "be exhaustive" and "the cost of missing one is silent data loss" — I'd rather hand you a checklist than let these hide because they're technically outside the 8 files I can read.

1. **`src/omega/oracle/health_monitor.py` — `AsyncCircuitBreaker.record_429()`**: calls `engine.log_event(...)` (sync call site, method itself is `def`, not `async def`). `log_event` is not in your list of 14 migrated methods, but it's on the same `ObservabilityEngine`/`get_engine()` object as `record_breaker_transition` — if `log_event` internally delegates to `MetricsDB.record_event` (plausible, same family), this is unverified and possibly broken the same way. `ObservabilityEngine` isn't in the pack. **Check this file.**

2. **`src/omega/observability/bleg.py` — `BLEGMiddleware.inspect()`**: calls `self._ledger.write(...)` where `self._ledger = get_ufl_writer()`. Neither `get_ufl_writer` nor the UFL writer class are in the pack. `inspect()` is itself a synchronous `def` (called directly after an `httpx` response, per its own docstring), so even if `.write()` needs awaiting, this method's whole call contract would need redesign, not just an `await` added. **Check this file and its caller contract.**

3. **`src/omega/observability/latency_tracker.py` — `LatencyTracker.get_recent_stats()`**: bypasses the migrated API entirely — it does `metrics_db._conn.execute(...)` directly on the raw connection, synchronously, with no `to_thread.run_sync` and no lock. Not a "missing await on a migrated method" bug, but it's a **new post-migration risk**: if `record_performance()` now holds `MetricsDB._write_lock` during a write (per the earlier hotfix), a concurrent call to `get_recent_stats()` reads `._conn` without that lock and without thread-offload — worst case it blocks the event loop and/or races the writer thread on the same connection object. **Should get the same `to_thread.run_sync` treatment even though it's not one of your 14 named methods.**

4. **`MetricsDB.get_baseline`, `set_baseline`, `get_performance_trend`, `get_error_summary`, `get_breaker_history`, `get_stats`**: I found **zero call sites** for any of these six in the 8 XML bundles. They're presumably called from a CLI, dashboard, or `omega-hub` diagnostics endpoint not included in this pack (`make health`, `omega-hub_get_system_stats`, etc. are referenced by name in `AGENTS.md` but their implementations aren't in the audited files).

5. **`ConversationFTSIndex.count()`**: zero call sites found in-pack. Likely diagnostics/CLI code outside the pack.

Items 4 and 5 are not "confirmed clean" — they're "not found," which is a different and weaker claim. Run the grep below across the full repo to close this gap.

---

## Verification Command

```bash
# Pass 1 (requires GNU grep -P / PCRE support): flags call sites of the
# migrated methods that do NOT have "await " immediately before the dot.
# Excludes the method definitions themselves (the `def name(` lines).
grep -rn -P --include="*.py" \
  '(?<!await )\.(record_event|record_error|record_breaker_transition|record_performance|set_baseline|get_baseline|get_performance_trend|get_error_summary|get_breaker_history|get_stats|index_exchange|remove_session|count)\(' \
  src/ mcp_servers/ scripts/ 2>/dev/null \
  | grep -vE '^\S+:\d+:\s*(async )?def (record_event|record_error|record_breaker_transition|record_performance|set_baseline|get_baseline|get_performance_trend|get_error_summary|get_breaker_history|get_stats|index_exchange|remove_session|count)\('

# Pass 2 (portable fallback if grep -P unavailable, e.g. macOS/BSD grep):
# broader, requires manual eyeballing of every hit for "await" nearby.
grep -rn --include="*.py" -E \
  '\.(record_event|record_error|record_breaker_transition|record_performance|set_baseline|get_baseline|get_performance_trend|get_error_summary|get_breaker_history|get_stats|index_exchange|remove_session|count)\(' \
  src/ mcp_servers/ scripts/ 2>/dev/null | grep -v 'await'

# Pass 3: specifically hunt for the double-wrap bug pattern (the two
# most dangerous cases in this report, #11 and #12) — any remaining
# to_thread.run_sync wrapping one of the now-async FTS/MetricsDB methods.
grep -rn --include="*.py" -E \
  'to_thread\.run_sync\(\s*(self\.)?(fts\.)?(index_exchange|search|remove_session|count|record_event|record_error|record_breaker_transition|record_performance|set_baseline|get_baseline|get_performance_trend|get_error_summary|get_breaker_history|get_stats)' \
  src/ mcp_servers/ scripts/ 2>/dev/null
```

Pass 1 is your primary signal. Pass 2 is the fallback for grep implementations without `-P`, but every hit needs a human look since it can't distinguish `await` on the line above a multi-line call. Pass 3 is the one that would have caught #11 and #12 specifically — it exists because "already uses `to_thread.run_sync`" is not proof of correctness once the wrapped method itself goes async, and that's the pattern most likely to recur if anyone converts another sync method to async later without checking existing callers.
