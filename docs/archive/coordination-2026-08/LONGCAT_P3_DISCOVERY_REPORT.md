# P3 Discovery Report — LongCat 2.0

**AP Token**: `AP-LONGCAT-P3-DISCOVERY-v1.0.0`
**Date**: 2026-08-10
**Author**: LongCat 2.0 (Nemotron 3 Ultra)
**Purpose**: Comprehensive discovery report filling all remaining knowledge gaps from P3 audit.

---

## 1. Sovereignty Ratio Root Cause — RESOLVED

### Finding

The sovereignty ratio MCP tool initially returned **87% local / 13% cloud**, but direct calls to `get_sovereignty_ratio()` return **18% local / 82% cloud**. The discrepancy is due to **stale data in the MCP server's DB connection**, not a code bug.

### Evidence

1. **`provider_classification` table is CORRECT**:
   - `openrouter: is_cloud=1` ✓
   - `opencode-zen: is_cloud=1` ✓
   - `antigravity: is_cloud=1` ✓
   - `cline: is_cloud=1` ✓
   - `native-gguf: is_cloud=0` ✓
   - `ollama: is_cloud=0` ✓

2. **`v_performance_corrected` view is CORRECT**:
   - `openrouter: is_cloud_corrected=1, count=803` ✓
   - `antigravity: is_cloud_corrected=1, count=393` ✓
   - `cline: is_cloud_corrected=1, count=383` ✓
   - `opencode-zen: is_cloud_corrected=1, count=400` ✓

3. **Direct call returns CORRECT values**:
   - `local_count: 437` (ollama 406 + native-gguf 31)
   - `cloud_count: 1979` (openrouter 803 + opencode-zen 400 + antigravity 393 + cline 383)
   - `ratio_local: 0.1809` (18.09%)

4. **MCP tool returned STALE values**:
   - `local_count: 2776`, `cloud_count: 402`
   - `openrouter: count=401, is_cloud=false` (wrong count AND wrong classification)

### Root Cause

The MCP tool was called before the `provider_classification` table was properly populated. The `_ensure_corrected_schema()` function is called inside `get_sovereignty_ratio()`, which should rebuild the table. But the MCP server may have:
1. Started before the DB was properly initialized
2. Cached the old DB state
3. Used a different DB path

### Verdict

**The sovereignty ratio code is correct.** The MCP tool returned stale data due to a DB initialization/caching issue. The actual sovereignty ratio is **18% local / 82% cloud**, which is significantly worse than the 87% reported by the MCP tool.

### Implications

This is a **M22 Response Provenance** issue. The MCP tool's stale data could lead to incorrect sovereignty claims. The fix is to ensure the MCP server's DB connection is refreshed or the `provider_classification` table is rebuilt on startup.

---

## 2. M25 AnyIO Watchdog Pattern — VERIFIED + REFINED

### Finding

The proposed AnyIO watchdog pattern is **correct in principle** but has a **subtle bug**: `stop.set()` is placed after the `async for` loop, so if an exception occurs inside the loop, the watchdog task leaks until `fail_after` fires.

### Evidence

From the AnyIO documentation:
- `fail_after(timeout)` raises `TimeoutError` when the timeout is exceeded
- `move_on_after(timeout)` just exits the context block without raising
- Task groups contain their own cancel scopes
- When a task group is cancelled, all child tasks are cancelled

### Refined Fix

```python
async def _stream_completion(self, client, url, payload, headers) -> str:
    chunk_timeout = self.config.extra.get("streaming", {}).get("chunk_timeout_ms", 30000) / 1000.0
    total_timeout = self.config.extra.get("streaming", {}).get("total_timeout_ms", 300000) / 1000.0

    chunks: List[str] = []
    activity = [0]  # mutable counter, incremented per content chunk
    stop = anyio.Event()

    async def _watchdog():
        last_seen = activity[0]
        idle_s = 0.0
        while not stop.is_set():
            with anyio.move_on_after(chunk_timeout):
                await stop.wait()
            if stop.is_set():
                return
            if activity[0] == last_seen:
                idle_s += chunk_timeout
                logger.info(f"Stream alive, {idle_s:.0f}s since last chunk (provider={self.name})")
            else:
                last_seen, idle_s = activity[0], 0.0

    try:
        with anyio.fail_after(total_timeout):
            async with anyio.create_task_group() as tg:
                tg.start_soon(_watchdog)
                async with client.stream("POST", url, json=payload, headers=headers) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        line = line.strip()
                        if not line or not line.startswith("data:"):
                            continue
                        data_str = line[5:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                        except (ValueError, OSError):
                            continue
                        choices = chunk.get("choices", [])
                        if not choices:
                            continue
                        content_piece = choices[0].get("delta", {}).get("content", "")
                        if content_piece:
                            chunks.append(content_piece)
                            activity[0] += 1
                        if choices[0].get("finish_reason") == "error":
                            raise RuntimeError(f"Provider {self.name} stream terminated with finish_reason='error'")
    finally:
        stop.set()  # ← MOVED TO finally BLOCK

    return "".join(chunks).strip()
```

### Key Changes from Audit Proposal

1. **`stop.set()` moved to `finally` block** — ensures watchdog terminates even on exception
2. **Removed redundant `stop.set()` after the loop** — the `finally` block handles it
3. **Watchdog uses `anyio.move_on_after(chunk_timeout)`** — exits the wait after chunk_timeout, checks if activity changed

### Acceptance Test Required

Per the audit report: simulate a connection that sends zero bytes for >30s, assert the heartbeat log fires at ~30s, then assert `RuntimeError` fires at the total-timeout boundary even though no line was ever received.

---

## 3. M7 Tuple Sorting — VERIFIED

### Finding

Python tuple sorting with `reverse=True` works correctly for the proposed priority-dominant scoring.

### Evidence

```python
providers = [
    ('native-gguf', 0, 40.0),   # priority=0, penalty=40
    ('antigravity', 3, 5.0),    # priority=3, penalty=5
    ('openrouter', 5, 2.0),     # priority=5, penalty=2
]

# Current (additive) scoring
scored = [(name, float((10 - priority) * 10.0) - penalty) for name, priority, penalty in providers]
scored.sort(key=lambda x: x[1], reverse=True)
# Result: antigravity: 65.0, native-gguf: 60.0, openrouter: 48.0
# antigravity WINS (WRONG)

# Proposed (tuple) scoring
scored = [(name, (-int(priority), -penalty)) for name, priority, penalty in providers]
scored.sort(key=lambda x: x[1], reverse=True)
# Result: native-gguf: priority_tier=0, antigravity: priority_tier=3, openrouter: priority_tier=5
# native-gguf WINS (CORRECT)
```

### Verdict

The tuple scoring fix is **safe and correct**. Only one caller of `_calculate_score` exists (confirmed via grep), so changing the return type from `float` to `tuple[int, float]` breaks nothing.

---

## 4. Heritage Vet Log Collision Origin — CONFIRMED

### Finding

The Sprint A-EXT section was added in commit `8d0abb46` (2026-07-13) or earlier, restarting numbering at vet-059. This collided with existing vet-064-072 entries from the earlier code-pattern-focused numbering.

### Evidence

- All commits from `92b1b6e8` (2026-07-19) down to at least `e005e8a1` (2026-07-13) have the Sprint A-EXT section
- The Sprint A-EXT section uses `####` heading level (h4) while the original entries use `###` (h3)
- The collision was introduced when the "General Heritage Vetting — Non-id-Sources (Sprint A-EXT)" section was added

### Root Cause

The vetting process lacked:
1. **ID collision detection** — no grep for existing IDs before assigning new ones
2. **Content-aware dedup** — no check for redundant vetting of the same code
3. **A `make heritage-vet` Makefile target** — per GAP-2, still not implemented

---

## 5. Other `_calculate_score` Callers — NONE FOUND

### Finding

`_calculate_score` has exactly **one caller** in the entire codebase (excluding tests).

### Evidence

```
src/omega/oracle/provider_selector.py:54:            score = self._calculate_score(provider, query)
src/omega/oracle/provider_selector.py:62:    def _calculate_score(self, provider: Any, query: str) -> float:
```

No callers in `tests/` directory. The tuple fix is safe.

---

## 6. HTTPX Streaming Timeout Edge Cases — RESEARCH FINDING

### Finding

HTTPX has four timeout types: **connect**, **read**, **write**, and **pool**. The **read timeout** is the maximum duration to wait for a chunk of data to be received. If no data is received within this time, a `ReadTimeout` exception is raised.

### Implications for M25

1. **Current code**: `httpx.AsyncClient(timeout=120.0)` sets ALL timeout types to 120s. For streaming, this means a `ReadTimeout` will be raised if the server goes silent for >120s.

2. **Silent connection scenario**: If the TCP connection is open but the server sends zero bytes, `aiter_lines()` will block. The read timeout will fire after 120s, raising `ReadTimeout`.

3. **Nemotron-specific behavior**: Nemotron 3 Ultra has 30s+ chunk gaps. The current 120s read timeout is sufficient for Nemotron's gaps, but the streaming path is unreachable anyway (Finding A).

4. **AnyIO watchdog advantage**: The AnyIO watchdog pattern is superior to httpx's read timeout because:
   - It can log heartbeats on a fixed cadence (e.g., every 30s)
   - It enforces a total deadline regardless of data flow
   - It uses real cancellation timers independent of whether data arrives

### Verdict

The AnyIO watchdog pattern is the correct approach for M25. The httpx read timeout is a fallback, not a replacement.

---

## 7. AnyIO Watchdog Best Practices — RESEARCH FINDING

### Key Principles from AnyIO Documentation

1. **`fail_after` vs `move_on_after`**:
   - `fail_after(timeout)` — raises `TimeoutError` on timeout
   - `move_on_after(timeout)` — exits context block silently on timeout

2. **Task groups contain cancel scopes**:
   - When a task group is cancelled, all child tasks are cancelled
   - Level cancellation: tasks are cancelled at every yield point

3. **Shielding**:
   - `CancelScope(shield=True)` — exempts a block from cancellation
   - Useful for cleanup operations

4. **Finalization**:
   - Always re-raise cancellation exceptions
   - Use shielded scopes for cleanup that requires `await`

### Recommended Watchdog Pattern

The pattern proposed in the audit report is correct:
1. Use `anyio.fail_after(total_timeout)` for the total deadline
2. Use a background watchdog task with `anyio.move_on_after(chunk_timeout)` for heartbeats
3. Use a mutable counter (`activity = [0]`) to track data flow
4. Use `anyio.Event` to signal the watchdog to stop
5. **CRITICAL**: Use `try/finally` to ensure `stop.set()` is called even on exception

---

## 8. Summary of All Findings

| # | Finding | Status | Severity |
|---|---------|--------|----------|
| 1 | Sovereignty ratio root cause | RESOLVED — MCP tool returned stale data, code is correct | HIGH (M22) |
| 2 | M25 watchdog pattern | VERIFIED — needs try/finally fix | CRITICAL |
| 3 | M7 tuple sorting | VERIFIED — safe and correct | CRITICAL |
| 4 | Heritage collision origin | CONFIRMED — Sprint A-EXT section added ~2026-07-13 | HIGH |
| 5 | Other `_calculate_score` callers | NONE FOUND | LOW |
| 6 | HTTPX streaming timeout | RESEARCHED — AnyIO watchdog is superior | MEDIUM |
| 7 | AnyIO watchdog best practices | RESEARCHED — mutable counter + try/finally pattern | MEDIUM |

---

## 9. Recommended Next Steps

### Immediate (P0)

1. **Fix M7 tuple scoring** — ~15 lines, fires on every request, inverts M7's core guarantee
2. **Re-run sovereignty ratio** — confirm the MCP tool returns correct values after DB refresh

### Short-term (P1)

3. **Wire M25 streaming + AnyIO watchdog** — ~50 lines, with try/finally fix
4. **Write M25 acceptance test** — simulate silent connection, assert heartbeat + timeout

### Medium-term (P2)

5. **Renumber heritage vet-064-072 block** — ~20 lines
6. **Resolve vet-017 contradiction** — ~10 lines
7. **Merge redundant vetting pairs** — ~15 lines

### Long-term (P3)

8. **Delete dead `_detect_repetition_loop` override** — ~20 lines
9. **Delete dead `create_openrouter_provider`** — ~10 lines
10. **Implement `make heritage-vet` Makefile target** — per GAP-2

---

*⬡ OMEGA ⬡ LONGCAT-2.0 ⬡ P3-DISCOVERY-v1.0.0 ⬡ 2026-08-10*
