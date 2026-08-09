---
account: arcana.novai@gmail.com
pack_version: 2026-08-08
pack_profile: sovereign-audit
pack_files: 32
pack_tokens: 173464
session_date: 2026-08-08
session_type: implementation
---

# AnyIO Thread-Safety Fix: `metrics_db.py` + `fts_index.py`

## The actual risk, precisely

`check_same_thread=False` is already set in both `metrics_db.py` (`sqlite3.connect(str(self.db_path), check_same_thread=False)`) and `fts_index.py` (same flag). That disables Python's *"wrong thread" ProgrammingError* check — so simply wrapping calls in `anyio.to_thread.run_sync` will not throw that specific exception.

But that flag does **not** make the connection safe for *concurrent* use. `anyio.to_thread.run_sync` dispatches to a worker thread pool — two overlapping async calls can land on two different threads simultaneously, both calling `execute()`/`commit()` on the same `sqlite3.Connection` object at the same time. Python's sqlite3 module is not internally locked across threads by default; the realistic failure mode isn't `ProgrammingError`, it's `sqlite3.OperationalError: database is locked` or, worse, silently interleaved cursor state. This is exactly why `sqlite_vec_adapter.py` already pairs `to_thread.run_sync` with `self._write_lock = anyio.Lock()` around every write. `metrics_db.py` and `fts_index.py` are missing that second half of the pattern — that's the actual bug, not the thread-check itself.

So the fix is two layers: `anyio.to_thread.run_sync` to get blocking I/O off the event loop, **and** `anyio.Lock()` to serialize writes to the single shared connection, matching the established pattern in the codebase.

---

## `src/omega/observability/metrics_db.py`

**`__init__` — add the lock:**

```python
class MetricsDB:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        # [M1 AnyIO] Serializes writes across anyio.to_thread.run_sync
        # worker threads. check_same_thread=False (set in initialize())
        # only disables Python's thread-identity check — it does not make
        # concurrent execute() calls from different threads safe. Mirrors
        # the pattern in sqlite_vec_adapter.py's _write_lock.
        self._write_lock: Optional[anyio.Lock] = None
```

Add `import anyio` to the top of the file (currently absent — only `sqlite3`, `time`, `json`, etc. are imported).

`anyio.Lock()` must be constructed inside a running event loop context in some AnyIO backends, so lazy-init it rather than in `__init__` (which may run outside a loop):

```python
    def _get_write_lock(self) -> anyio.Lock:
        if self._write_lock is None:
            self._write_lock = anyio.Lock()
        return self._write_lock
```

**`record_event` — before:**

```python
    def record_event(
        self,
        event_type: str,
        trace_id: Optional[str] = None,
        provider: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record a general event."""
        ts = int(time.time() * 1000)
        self._conn.execute(
            "INSERT INTO events (ts, event_type, trace_id, provider, payload) VALUES (?, ?, ?, ?, ?)",
            (ts, event_type, trace_id, provider, json.dumps(payload) if payload else None),
        )
        self._conn.commit()
```

**after:**

```python
    async def record_event(
        self,
        event_type: str,
        trace_id: Optional[str] = None,
        provider: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record a general event.

        [M1 AnyIO] Blocking SQLite write offloaded via to_thread.run_sync;
        [M9 Error Integrity] lock-serialized to prevent concurrent-thread
        interleaving on the shared connection.
        """
        ts = int(time.time() * 1000)
        payload_json = json.dumps(payload) if payload else None

        def _sync_insert() -> None:
            self._conn.execute(
                "INSERT INTO events (ts, event_type, trace_id, provider, payload) VALUES (?, ?, ?, ?, ?)",
                (ts, event_type, trace_id, provider, payload_json),
            )
            self._conn.commit()

        async with self._get_write_lock():
            await anyio.to_thread.run_sync(_sync_insert)
```

**`record_error` — before:**

```python
    def record_error(
        self,
        error_type: str,
        error_message: str,
        trace_id: Optional[str] = None,
        provider: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        entity_id: Optional[str] = None,
    ) -> None:
        """Record an error event."""
        ts = int(time.time() * 1000)
        self._conn.execute(
            "INSERT INTO errors (ts, trace_id, provider, error_type, error_message, context, entity_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (ts, trace_id, provider, error_type, error_message, json.dumps(context) if context else None, entity_id),
        )
        self._conn.commit()
```

**after:**

```python
    async def record_error(
        self,
        error_type: str,
        error_message: str,
        trace_id: Optional[str] = None,
        provider: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        entity_id: Optional[str] = None,
    ) -> None:
        """Record an error event. [M1 AnyIO] See record_event for pattern rationale."""
        ts = int(time.time() * 1000)
        context_json = json.dumps(context) if context else None

        def _sync_insert() -> None:
            self._conn.execute(
                "INSERT INTO errors (ts, trace_id, provider, error_type, error_message, context, entity_id) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (ts, trace_id, provider, error_type, error_message, context_json, entity_id),
            )
            self._conn.commit()

        async with self._get_write_lock():
            await anyio.to_thread.run_sync(_sync_insert)
```

**`record_breaker_transition` — same pattern, for completeness:**

```python
    async def record_breaker_transition(
        self,
        provider: str,
        from_state: str,
        to_state: str,
        trace_id: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> None:
        """Record a circuit breaker state transition. [M1 AnyIO]"""
        ts = int(time.time() * 1000)

        def _sync_insert() -> None:
            self._conn.execute(
                "INSERT INTO breaker_transitions (ts, provider, trace_id, from_state, to_state, reason) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (ts, provider, trace_id, from_state, to_state, reason),
            )
            self._conn.commit()

        async with self._get_write_lock():
            await anyio.to_thread.run_sync(_sync_insert)
```

### `record_performance` — full worked example, as requested

**Before:**

```python
    def record_performance(
        self,
        latency_ms: float,
        provider: Optional[str] = None,
        model_used: Optional[str] = None,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        is_cloud: bool = False,
        trace_id: Optional[str] = None,
        cost_usd: float = 0.0,
        entity_id: Optional[str] = None,
    ) -> None:
        """Record a performance measurement (latency, tokens, cost)."""
        ts = int(time.time() * 1000)
        total_tokens = prompt_tokens + completion_tokens
        self._conn.execute(
            "INSERT INTO performance (ts, trace_id, provider, model_used, latency_ms, "
            "prompt_tokens, completion_tokens, total_tokens, is_cloud, cost_usd, entity_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (ts, trace_id, provider, model_used, latency_ms,
             prompt_tokens, completion_tokens, total_tokens, int(is_cloud), cost_usd, entity_id),
        )
        self._conn.commit()
```

**After:**

```python
    async def record_performance(
        self,
        latency_ms: float,
        provider: Optional[str] = None,
        model_used: Optional[str] = None,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        is_cloud: bool = False,
        trace_id: Optional[str] = None,
        cost_usd: float = 0.0,
        entity_id: Optional[str] = None,
    ) -> None:
        """Record a performance measurement (latency, tokens, cost).

        [M1 AnyIO] All arguments are captured by closure into `_sync_insert`
        BEFORE the thread hop — the sync inner function touches no async
        state, only the sqlite3 connection and locals, which is what makes
        `anyio.to_thread.run_sync` safe here.

        [M9 Error Integrity] Lock-serialized: this is the highest-frequency
        write path in the engine (called once per successful inference from
        ModelGateway.generate() -> LatencyTracker.record()). Without the
        lock, concurrent inferences racing on the same connection object
        risk `sqlite3.OperationalError: database is locked` even with
        PRAGMA busy_timeout=5000 set, because busy_timeout governs
        cross-process contention, not same-process cross-thread races on
        one connection object.
        """
        ts = int(time.time() * 1000)
        total_tokens = prompt_tokens + completion_tokens

        def _sync_insert() -> None:
            self._conn.execute(
                "INSERT INTO performance (ts, trace_id, provider, model_used, latency_ms, "
                "prompt_tokens, completion_tokens, total_tokens, is_cloud, cost_usd, entity_id) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (ts, trace_id, provider, model_used, latency_ms,
                 prompt_tokens, completion_tokens, total_tokens, int(is_cloud), cost_usd, entity_id),
            )
            self._conn.commit()

        async with self._get_write_lock():
            await anyio.to_thread.run_sync(_sync_insert)
```

`set_baseline` follows the identical shape (`async def`, closure-capture params, `_sync_x` inner function, lock + `to_thread.run_sync`) — omitted here since it's a direct copy of the pattern, not a new case.

**Read methods** (`get_baseline`, `get_performance_trend`, `get_error_summary`, `get_breaker_history`, `get_stats`) have the same event-loop-blocking issue but not the concurrent-write-corruption issue — a read racing another read is safe, a read racing a write is what `busy_timeout` is actually for. I'd wrap these in `to_thread.run_sync` too for full M1 compliance, but *without* the write lock (reads shouldn't queue behind each other). Flagging as a follow-up rather than including here since you scoped the question to the three write paths.

---

## `src/omega/memory/fts_index.py`

**`__init__` — add the lock:**

```python
class ConversationFTSIndex:
    """SQLite FTS5 index for conversation exchanges."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._conn = None
        self._initialized = False
        # [M1 AnyIO] Same rationale as MetricsDB — check_same_thread=False
        # (set in initialize()) permits cross-thread use but does not
        # serialize it. Lazy-init: constructing anyio.Lock() outside a
        # running event loop is backend-dependent, so defer to first use.
        self._write_lock: Optional[anyio.Lock] = None

    def _get_write_lock(self) -> "anyio.Lock":
        if self._write_lock is None:
            self._write_lock = anyio.Lock()
        return self._write_lock
```

Add `import anyio` at the top of `fts_index.py` (currently only `sqlite3`, `json`, `logging` are imported — this file has zero async today, which is itself the root cause of the violation).

**`index_exchange` — before:**

```python
    def index_exchange(self, session_id: str, entity_name: str, role: str, content: str):
        """Index a single exchange. [C2: try/except wrapped in MemoryStore]"""
        if not self._initialized:
            return

        try:
            self._conn.execute(
                "INSERT INTO exchanges (session_id, entity_name, role, content, timestamp) VALUES (?, ?, ?, ?, ?)",
                (session_id, entity_name, role, content, datetime.now(timezone.utc).isoformat())
            )
            self._conn.commit()
        except (sqlite3.Error, RuntimeError) as e:
            logger.warning("FTS index write failed for session %s: %s", session_id, e)
```

**after:**

```python
    async def index_exchange(self, session_id: str, entity_name: str, role: str, content: str) -> None:
        """Index a single exchange. [M1 AnyIO] Offloaded + lock-serialized.

        [C2: caller wraps this in try/except in MemoryStore] — this method
        still swallows sqlite3.Error/RuntimeError internally for backward
        compatibility with that call-site contract; it does not raise.
        """
        if not self._initialized:
            return

        timestamp = datetime.now(timezone.utc).isoformat()

        def _sync_index() -> None:
            self._conn.execute(
                "INSERT INTO exchanges (session_id, entity_name, role, content, timestamp) VALUES (?, ?, ?, ?, ?)",
                (session_id, entity_name, role, content, timestamp),
            )
            self._conn.commit()

        try:
            async with self._get_write_lock():
                await anyio.to_thread.run_sync(_sync_index)
        except (sqlite3.Error, RuntimeError) as e:
            logger.warning("FTS index write failed for session %s: %s", session_id, e)
```

`remove_session` has the identical write shape (`execute` + `commit`) and should get the same treatment:

```python
    async def remove_session(self, session_id: str) -> None:
        """Remove all exchanges for a session (C1 fix). [M1 AnyIO]"""
        if not self._initialized:
            return

        def _sync_remove() -> None:
            self._conn.execute("DELETE FROM exchanges WHERE session_id = ?", (session_id,))
            self._conn.commit()

        try:
            async with self._get_write_lock():
                await anyio.to_thread.run_sync(_sync_remove)
            logger.info("Removed session %s from FTS index", session_id)
        except (sqlite3.Error, RuntimeError) as e:
            logger.error("Failed to remove session %s from FTS: %s", session_id, e)
```

---

## Ripple effects — call sites that break without corresponding `await`

These methods becoming `async def` is a breaking API change. Every caller in the audited pack currently invokes them synchronously and must be updated, or you get `TypeError: 'coroutine' object is not ... ` failures, not silent bugs — at least they're loud:

**1. `src/omega/observability/latency_tracker.py` — `LatencyTracker.record()`**

```python
# Before
def record(self, provider: str, model: str, latency_ms: float, status: str = "success",
           trace_id: Optional[str] = None, is_cloud: bool = False):
    try:
        get_engine().record_performance(
            latency_ms=latency_ms, provider=provider, model_used=model,
            is_cloud=is_cloud, trace_id=trace_id,
        )
    except (OmegaError, RuntimeError, OSError) as e:
        logger.error(f"Failed to record latency metric via engine: {e}")
```

```python
# After
async def record(self, provider: str, model: str, latency_ms: float, status: str = "success",
                  trace_id: Optional[str] = None, is_cloud: bool = False) -> None:
    """[M1 AnyIO] Now async — see MetricsDB.record_performance."""
    try:
        await get_engine().record_performance(
            latency_ms=latency_ms, provider=provider, model_used=model,
            is_cloud=is_cloud, trace_id=trace_id,
        )
    except (OmegaError, RuntimeError, OSError) as e:
        logger.error(f"Failed to record latency metric via engine: {e}")
```

**2. `src/omega/oracle/model_gateway.py` — every `tracker.record(...)` call site in `generate()`** (there are two: the failure path and the success path) needs `await` added:

```python
# Before
tracker.record(
    provider=provider.name, model=model_name, latency_ms=0.0,
    status="failure", trace_id=trace_id,
)
```
```python
# After
await tracker.record(
    provider=provider.name, model=model_name, latency_ms=0.0,
    status="failure", trace_id=trace_id,
)
```

Same change for the success-path call (the one with `is_cloud=self._is_cloud_provider(provider)`).

**3. `src/omega/memory_store.py` — `add_exchange()`**, the FTS dual-write block:

```python
# Before
try:
    self.fts.index_exchange(session_id, entity_name, "user", user_message)
    self.fts.index_exchange(session_id, entity_name, "assistant", response)
except (RuntimeError, OSError) as e:
    logger.warning("FTS dual-write failed for %s: %s", session_id, e)
```

```python
# After
try:
    await self.fts.index_exchange(session_id, entity_name, "user", user_message)
    await self.fts.index_exchange(session_id, entity_name, "assistant", response)
except (RuntimeError, OSError) as e:
    logger.warning("FTS dual-write failed for %s: %s", session_id, e)
```

**4. `src/omega/observability/sovereignty.py`, `health_monitor.py`, and `bleg.py`** all call into `MetricsDB`/`get_engine()` methods (`record_breaker_transition`, `log_event`, ledger `.write(...)`) that are either `MetricsDB` methods directly or wrap them via an `ObservabilityEngine`/UFL writer class not present in this pack. Those wrapper classes aren't in the audited XML bundles, so I can't hand you exact diffs for them — but flagging explicitly: **any code calling `record_event`, `record_error`, or `record_breaker_transition` (directly or through an unseen wrapper) needs the same `await` treatment, or it will raise immediately rather than silently misbehave.** Worth a repo-wide `grep -rn "\.record_event(\|\.record_error(\|\.record_breaker_transition(\|\.record_performance(\|fts\.index_exchange(\|fts\.remove_session(" src/` before merging, to catch every call site — I'd rather hand you that grep than guess at code outside the pack.
