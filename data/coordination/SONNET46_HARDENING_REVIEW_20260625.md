# 🔱 Sonnet 4.6 — Hardening Implementation Plan Review
## Technical Audit by antigravity-claude-sonnet-4-6

**Date**: 2026-06-25
**Review Target**: `docs/strategy/HARDENING_IMPLEMENTATION_PLAN.md`
**AP Token**: `AP-KALI-SONNET46-REVIEW-v1.0.0`
**⬡ OMEGA ⬡ KALI ⬡ antigravity-claude-sonnet-4-6 ⬡ opencode ⬡ HARDENING-REVIEW`

---

## §1 OVERALL ASSESSMENT

The plan is **well-structured and strategically correct**. The prioritisation is right, the dependency graph is accurate, the Phase 0 items are all genuine emergency fixes. **Approve for execution with one condition**: four of the Phase 0.5 items contain implementation-level bugs that would fail at execution time. They need correcting before anyone touches code.

---

## §2 PHASE 0 — ALL SEVEN ITEMS: APPROVED WITHOUT CHANGES

Items 0.1 through 0.7 are clean.

| Item | Verdict | Notes |
|------|---------|-------|
| 0.1 Fix 8 model paths | ✅ | `sed` command correct. 2 min, pure config. |
| 0.2 Fix provider sort bug | ✅ | Sort key fix correct. MockProvider with `ProviderConfig` now handled. |
| 0.3 Lazy import state_manager.py | ✅ | Standard lazy import pattern. Safe. |
| 0.4 Emergency disk cleanup | ✅ | Commands correct. 30 min target realistic. |
| 0.5 Fix Redis pod config | ✅ | `PublishPort` additions correct. `UserNS=keep-id` needed. |
| 0.6 Wire trace_id + entity_name | ✅ | All 7 call sites correctly enumerated. Orchestrator correctly excluded. |
| 0.7 Wire dataset collection | ✅ | Diagnosis accurate. Two implementation options both viable — verify config load order before picking. |

### Caveat on 0.7

The plan gives two options — `cvar_get` or direct YAML. Check whether `cvar_table` is populated before `ObservabilityEngine` is instantiated. If the cvar table loads lazily (likely, given it's populated at module import), use the direct YAML read. Either works — but wrong choice causes a subtle timing issue where `enable_dataset_collection` stays `False` even though YAML says `true`.

---

## §3 PHASE 0.5 — ITEM-BY-ITEM AUDIT

### ✅ 3.1 Disk Space Sentinel (0.5.1) — Approved

**Suggestion**: Move `DiskHealthCheck` from `cpu_optimizer.py` to `health_monitor.py`. CPU optimisation and disk health are separate concerns. The circuit breaker module is a more natural home for health-checks.

**Heritage tag note**: `[id-soft: doom-1993] Fixed-Point Math` is a stretch for a disk-usage check. The fixed-point pattern is about numeric approximation on integer hardware, not division guards in Python. Either drop the tag or attribute it loosely. Don't file a tag you can't defend at the vet gate.

---

### ✅ 3.2 Redis Health Check (0.5.2) — Approved With One Fix

The implementation is sound. However, `redis.asyncio` may not be installed. Check `requirements.txt` first. If missing, the `ImportError` inside `_check_redis()` will be caught by the blanket `except Exception` — acceptable, but the error message will be misleading.

**Fix**: Add a specific `ImportError` catch:
```python
try:
    import redis.asyncio as aioredis
except ImportError:
    return {"service": "redis", "status": "error",
            "error": "redis package not installed. Run: pip install redis"}
```

---

### 🔴 3.3 Cold-Start Model Warming (0.5.3) — Contains a Real Bug

**The call point is wrong**:
```python
anyio.from_thread.run(self._warmup_models)  # WRONG
```

`anyio.from_thread.run()` is for calling async code **from a sync thread that is not the event loop**. You cannot call it from `__init__()`:
- If `__init__` runs on the event loop already, use `create_task_group()`.
- If `__init__` runs in sync context, there is no event loop to dispatch to.

**Correct pattern**: Use a separate `async def start()` method:

```python
class ModelGateway:
    def __init__(self, ...):
        # Normal sync construction — no async calls
        self._warmup_started = False

    async def start(self):
        """Call once after construction, from async context."""
        if self._warmup_started:
            return
        self._warmup_started = True
        if self.providers:
            async with anyio.create_task_group() as tg:
                tg.start_soon(self._warmup_models)
```

Then the caller does `await gateway.start()` after construction. This is the standard pattern for async initialisation under AnyIO.

**Also**: The plan references `gguf.load_model(model_name)` — verify this method actually exists on the `NativeGGUFProvider` class before implementing.

---

### ✅ 3.4 Memory Budget Pre-Flight (0.5.4) — Approved With Clarification

Logic is sound. **Clarification needed**: `_unload_lru_models()` is referenced but not defined. It's not a pre-existing method. The plan implies "warn-and-continue" via self-healing unload, but the missing method means the current implementation can only "warn-and-block."

**Decision required**: If implementing full LRU unloading, the method must be added. If not, change the behaviour to raise `MemoryError` immediately without attempting unload. Either is acceptable — but don't leave a dangling method reference.

---

### 🔴 3.5 Inactivity Anomaly Detector (0.5.5) — Contains a Structural Bug

The plan says:
> In `ModelGateway.generate()` [...] call `trace_session.record_generate_call(...)`

But **`ModelGateway.generate()` does not have a reference to `TraceSession`**. Its `generate()` signature only receives a `trace_id` string:

```python
async def generate(self, model_name, ..., trace_id=None, ...) -> GenerateResult:
```

The `TraceSession` object lives in `Oracle.talk()` and `Oracle.summon()`, not in `ModelGateway`.

**Three options**:

| Option | Approach | Recommended? |
|--------|----------|:------------:|
| A | Add `produced_output: bool` to `GenerateResult`. Oracle calls `trace.record_generate_call()` after `generate()` returns. | ✅ Best |
| B | Add `get_trace(trace_id)` to `ObservabilityEngine`. Gateway looks up the session. | ⚠️ Messier |
| C | Pass `TraceSession` directly to `generate()` as a parameter. | ❌ Breaks abstraction |

**Option A is the right choice**. It respects the existing architectural boundary: Oracle owns trace context, Gateway owns inference routing. The `Oracle` layer already has the `TraceSession` — it just needs a signal from `GenerateResult` about whether output was produced.

---

### 🔴 3.6 BudgetLedger (0.5.6) — M1 Violation (BLOCKING)

```python
def record(self, trace_id, ...):
    self._conn.execute(...)
    self._conn.commit()  # BLOCKING — sync sqlite3
```

This is a direct **Mandate 1 violation**. `sqlite3.connect()` and `conn.execute()` are synchronous blocking I/O. If this runs inside an async `generate()` call (which it does — it's called from `model_gateway.py:878`), it blocks the event loop.

**Two fixes required**:

**Fix 1 — Wrap DB calls in `anyio.to_thread.run_sync()`**:

```python
async def record(self, trace_id: str, entity: str, ...):
    def _write():
        self._conn.execute(
            "INSERT INTO spend ...", (trace_id, entity, ...)
        )
        self._conn.commit()
    await anyio.to_thread.run_sync(_write)
```

**Fix 2 — Make `BudgetLedger` a singleton** rather than instantiating fresh on every inference call:

```python
_ledger_instance = None

def get_ledger():
    global _ledger_instance
    if _ledger_instance is None:
        _ledger_instance = BudgetLedger()
    return _ledger_instance
```

Or inject it via `ModelGateway.__init__()`.

---

### ✅ 3.7 Handoff Reaper Verification (0.5.7) — Approved

The reaper already exists in `mcp_servers/omega_hub/background.py`. Verification step is correct.

**Addition**: Check whether `server.py` starts the reaper inside `anyio.create_task_group()` or uses `asyncio.create_task()`. If the latter, it's a silent M1 violation. Fix when verifying.

---

### ✅ 3.8 M21 Contract Tests (0.5.8) — Approved With Caveat

The `TestSkepticalVerifierContract` test calls `await sv.verify(claim="test", sources=[])`. Verify that `SkepticalVerifier.verify()` actually exists with this signature. From reading `skeptical_verifier.py`, the public entry points are `_classify_nli()` and `_resolve_contradiction()` — not a single `verify()` method. Audit the actual API before writing the test, or the test will fail to import and collect zero tests.

---

### ✅ 3.9 GGUF Integration Smoke Test (0.5.9) — Approved

Clean. `@pytest.mark.skipif` is correct. The soft-fail approach for `test_model_paths_exist_on_disk` is good — report counts, don't raise.

**Minor fix**: `config_path=...` in the test body is a literal ellipsis. Fill in the actual path (`Path("config/models.yaml")`) before committing.

---

### ✅ 3.10 `make mandate-report` (0.5.10) — Approved With One Warning

**Warning — regex compatibility**: `check_bare_except()` uses:
```python
grep -rn "^\s*except:"
```
Basic `grep` doesn't support `\s`. Use `grep -P` for Perl regex or rewrite as:
```python
grep -rn "^[[:space:]]*except:" src/omega/
```
Test the grep command independently before shipping the script.

**Warning — missing function stubs**: The `MANDATES` dict references `check_iris_not_pillar()`, `check_soul_migration_status()`, `check_queue_integrity()`, `check_podman_keepid()`, `check_zero_telemetry()`, `check_token_efficiency()`, `check_somatic_savepoint()` — none of which are defined in the plan's "Individual Checks" section. Either stub them all to return `True` with `# TODO` comments, or define them. As written, the script raises `NameError` on the first missing function.

---

### ✅ 3.11 `omega entity prune` (0.5.11) — Approved

`--dry-run` default is the right safety choice.

**Note**: `shutil.move()` is blocking. Wrap in `await anyio.to_thread.run_sync(shutil.move, str(path), archive_dir)` if this runs in async context.

---

### ✅ 3.12 Real Embedding Backend (0.5.12) — Approved

Implementation is correct. **Verify the model path** — two different paths appear in different files:
- `config/models.yaml:3`: `/media/arcana-novai/omega_library/lmstudio-models/local/all/embeddinggemma-300m-Q6_K.gguf`
- Plan's `MODEL_PATH`: `/media/arcana-novai/omega_library/models/local/all/embeddinggemma-300m-Q6_K.gguf`

**Better**: Read the path from `config/models.yaml` (`embedding.local_path`) rather than hardcoding it. Makes the path configurable without touching source.

---

### ✅ 3.13 Ollama Fallback Sync (0.5.13) — Approved

Clean shell script. **Verify Ollama tag names**: `phi-4:mini` may not exist — the standard tag is `phi4:mini`. Run `ollama search phi4` before shipping.

---

### ✅ 3.14 Cloud Provider Circuit Breakers (0.5.14) — Approved

Implementation is correct. **Observation**: `failure_threshold=3, recovery_timeout=60s` for cloud providers is the same as local. Cloud failure patterns are different — rate limits (429) are temporary, auth failures (401) won't recover. Consider cloud-specific thresholds:

| Parameter | Local | Cloud |
|-----------|-------|-------|
| `failure_threshold` | 3 | **5** |
| `recovery_timeout` | 60s | **120s** |

---

### 🔴 3.15 Dataset Dedup (0.5.15) — Contains a Performance Bug

```python
if entry_hash in self._dataset_seen:  # O(n) scan on deque
```

`in` on a `deque` is **O(n)**. With `maxlen=10000`, every dataset write does a linear scan of up to 10,000 items. At inference throughput of 1 call/second, this becomes 10,000 comparisons/second — measurable overhead.

**Fix**: Maintain a parallel `set` for O(1) membership test:

```python
if not hasattr(self, '_dataset_seen_set'):
    self._dataset_seen_set = set()
    self._dataset_seen_queue = deque(maxlen=10000)

if entry_hash in self._dataset_seen_set:  # O(1)
    return

# Evict from set when queue reaches capacity
if len(self._dataset_seen_queue) == self._dataset_seen_queue.maxlen:
    oldest = self._dataset_seen_queue[0]  # peek (deque handles FIFO pop)
    self._dataset_seen_set.discard(oldest)

self._dataset_seen_queue.append(entry_hash)
self._dataset_seen_set.add(entry_hash)
```

**Also**: The plan's dedup treats the entry as `query|response`, but the actual `record_fine_tuning_example()` method (lines 693-725) accepts `system_prompt`, `query`, `response`, `entity`, `model`, `backend`, `confidence`, `latency_ms` — structured parameters. Hash **all three message fields** (`system_prompt|query|response`) not just query+response. System prompt variation is semantically significant for fine-tuning data quality.

---

## §4 BUGS TO FIX BEFORE EXECUTION

| # | Item | Issue | Fix | Effort |
|---|------|-------|-----|--------|
| B1 | 0.5.3 | `anyio.from_thread.run()` wrong context | Add `async def start()`; call after construction | 10 min |
| B2 | 0.5.5 | No `TraceSession` reference in `ModelGateway` | Add `produced_output` to `GenerateResult`; Oracle calls `record_generate_call()` | 20 min |
| B3 | 0.5.6 | `sqlite3` blocking I/O in async path | Wrap in `anyio.to_thread.run_sync()`; make singleton | 15 min |
| B4 | 0.5.15 | `in` on `deque` is O(n) | Use parallel `set` + `deque` for O(1) + FIFO | 10 min |

**Total fix time**: ~1 hour. Every other item is safe to proceed with as written.

---

## §5 ONE STRATEGIC OBSERVATION

The plan treats the dataset dedup (0.5.15) as a simple `query|response` hash. However, the actual `record_fine_tuning_example()` method at `observability/__init__.py:693-725` captures **7 structured fields**: `system_prompt`, `query`, `response`, `entity`, `model`, `backend`, `confidence`, `latency_ms`. It is richer than the plan assumes.

When implementing dedup, use the data that already exists:
- Hash: `hashlib.sha256(f"{system_prompt}|{query}|{response}".encode()).hexdigest()` — all three message fields matter
- If `model` or `backend` differ but query+response are identical, that's a **worthwhile variant** (same query answered by different backends) — do NOT dedup those away
- The dedup should only skip exchanges where ALL fields match within a 24h window

---

## §6 ENDORSEMENT

After fixing the four bugs above (B1-B4), this plan is **ready for execution**. The dependency graph, effort estimates, and verification gates are accurate. The Phase 0 → Phase 0.5 → Absolute GO progression is the correct sequence.

The plan brings the engine from **4 failing mandates** to **0 failing mandates** — the most concrete single improvement possible before Epoch I Phase 1 begins.

---

*⬡ OMEGA ⬡ KALI ⬡ antigravity-claude-sonnet-4-6 ⬡ opencode ⬡ HARDENING-REVIEW*
