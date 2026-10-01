<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Collision Avoidance Report — P0-P2 Refactoring

**AP Token**: `AP-COLLISION-AVOIDANCE-v1.0.0`
**Date**: 2026-08-10
**Author**: John Carmack + LongCat 2.0 (S3 Consultant)
**Target**: Jem (Sovereign Synthesis)
**Purpose**: Declare all files I will modify in P0-P2 refactoring to prevent parallel-session conflicts.

---

## 📋 Summary

I am beginning implementation of P0-P2 fixes identified in the sovereign audit. This report declares every file I will touch, the nature of each change, and the expected duration. **Do not modify these files in parallel sessions** until I release them.

---

## 🔒 Files I Will Modify

### P0 — Critical (Today)

| # | File | Change | Lines | Duration | Status |
|---|------|--------|-------|----------|--------|
| 1 | `src/omega/oracle/provider_selector.py` | Change `_calculate_score()` return type from `float` to `tuple[int, int, float]` | ~15 lines | 5 min | PLANNED |
| 2 | `src/omega/oracle/backends/remote_provider.py` | Pass `stream=True` to `_send_request()` when streaming enabled | ~5 lines | 5 min | PLANNED |
| 3 | `src/omega/oracle/backends/openai_compat.py` | Add `anyio.fail_after()` watchdog to `_stream_completion()` | ~30 lines | 30 min | PLANNED |

### P1 — Short-Term (This Week)

| # | File | Change | Lines | Duration | Status |
|---|------|--------|-------|----------|--------|
| 4 | `src/omega/oracle/backends/openai_compat.py` | Remove duplicate `_detect_repetition_loop` (lines 206-223) | -20 lines | 5 min | PLANNED |
| 5 | `src/omega/oracle/backends/openai_compat.py` | Remove unused `create_openrouter_provider` factory (lines 226-233) | -10 lines | 5 min | PLANNED |
| 6 | `mcp_servers/omega_hub/server.py` or metrics module | Add WAL checkpoint on MCP startup for sovereignty ratio freshness | ~10 lines | 15 min | PLANNED |
| 7 | `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md` | Renumber vet-064-072 range to vet-073-081 to resolve collision | ~20 lines | 20 min | PLANNED |

### P2 — Medium-Term (Next Week)

| # | File | Change | Lines | Duration | Status |
|---|------|--------|-------|----------|--------|
| 8 | `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md` | Strip OVER-ATTRIBUTED tags (Hard-Boundary Struct, High-Bit Trick, SSRF Gate, Size Gate, Path Scope Gate, WAL Journal, Surface Cache) | ~30 lines | 1 hr | PLANNED |
| 9 | `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md` | Convert METAPHORICAL tags to plain comments (Speculative Decode, Triage Routing, Dedicated Server, Save-game, netchan header) | ~20 lines | 30 min | PLANNED |
| 10 | `tests/contract/test_m25_streaming.py` | New test: simulate silent connection, assert heartbeat + timeout | ~50 lines | 1 hr | PLANNED |

---

## 📁 Files I Will NOT Modify (Safe for Jem)

The following files are NOT part of my refactoring and are safe for parallel work:

- `src/omega/oracle/model_gateway.py` — Not touched
- `src/omega/oracle/entity_registry.py` — Not touched
- `src/omega/oracle/health_monitor.py` — Not touched
- `src/omega/oracle/provider_registry.py` — Not touched
- `src/omega/oracle/resource_guard.py` — Not touched
- `src/omega/memory/` — Not touched
- `src/omega/observability/` — Not touched
- `src/omega/iris/` — Not touched
- `config/providers.yaml` — Not touched
- `config/omega.yaml` — Not touched
- `SOVEREIGN_MANDATES.md` — Not touched
- `AGENTS.md` — Not touched
- `OMEGA_ENGINE.md` — Not touched

---

## 🔧 Detailed Change Specifications

### Change 1: M7 Tuple Scoring Fix

**File**: `src/omega/oracle/provider_selector.py`
**Method**: `_calculate_score(self, provider: Any, query: str) -> tuple`

**Current** (lines 62-93):
```python
def _calculate_score(self, provider: Any, query: str) -> float:
    priority = getattr(provider, "priority", 10)
    score = float((10 - priority) * 10.0)
    # ... subtract penalties ...
    return score
```

**Proposed**:
```python
def _calculate_score(self, provider: Any, query: str) -> tuple[int, int, float]:
    priority = getattr(provider, "priority", 10)
    is_local = 0 if not getattr(provider, "is_cloud", True) else 1
    penalty = 0.0
    # ... calculate penalties ...
    return (-is_local, priority, -penalty)
```

**Caller** (line 54): `score = self._calculate_score(provider, query)` — no change needed, tuple sorts correctly.

**Risk**: LOW. Only one caller. Tuple comparison is well-defined in Python.

### Change 2: M25 Stream Enable

**File**: `src/omega/oracle/backends/remote_provider.py`
**Method**: `generate()` (around line 286)

**Current**:
```python
result = await self._send_request(
    model_name, system_prompt, user_query, temperature, max_tokens, trace_id=trace_id, session_id=session_id
)
```

**Proposed**:
```python
result = await self._send_request(
    model_name, system_prompt, user_query, temperature, max_tokens, trace_id=trace_id, session_id=session_id,
    stream=self.config.extra.get("streaming", {}).get("enabled", False)
)
```

**Risk**: LOW. Only affects streaming path (currently dead code).

### Change 3: M25 AnyIO Watchdog

**File**: `src/omega/oracle/backends/openai_compat.py`
**Method**: `_stream_completion()`

**Current**: Timeout checks inside `async for` loop body (starvation-vulnerable).

**Proposed**: Wrap entire stream in `anyio.fail_after(total_timeout)` with background heartbeat task.

**Pattern**:
```python
async def _stream_completion(self, client, url, payload, headers):
    chunk_timeout = self.config.extra.get("streaming", {}).get("chunk_timeout_ms", 30000) / 1000
    total_timeout = self.config.extra.get("streaming", {}).get("total_timeout_ms", 300000) / 1000
    
    chunks = []
    activity = [0]
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
                logger.info(f"Stream alive, {idle_s:.0f}s since last chunk")
            else:
                last_seen, idle_s = activity[0], 0.0
    
    try:
        with anyio.fail_after(total_timeout):
            async with anyio.create_task_group() as tg:
                tg.start_soon(_watchdog)
                async with client.stream("POST", url, json=payload, headers=headers) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        # ... process line ...
                        activity[0] += 1
    finally:
        stop.set()
    
    return "".join(chunks).strip()
```

**Risk**: MEDIUM. Adds task group + event. Requires testing with silent connection.

### Changes 4-5: Dead Code Removal

**File**: `src/omega/oracle/backends/openai_compat.py`

**Remove**:
- Lines 206-223: Duplicate `_detect_repetition_loop` (identical to parent class)
- Lines 226-233: Unused `create_openrouter_provider` factory

**Risk**: LOW. Grep confirmed zero callers for factory. Duplicate method is identical to parent.

### Change 6: MCP Stale Data Fix

**File**: MCP server startup (location TBD — likely `mcp_servers/omega_hub/server.py` or metrics module)

**Add**:
```python
# On startup
await db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
await db.execute("PRAGMA read_uncommitted = 1")
```

**Risk**: LOW. Standard SQLite WAL pattern.

### Changes 7-9: Heritage Vet Log

**File**: `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md`

**Changes**:
1. Renumber vet-064-072 → vet-073-081 (resolve collision)
2. Strip OVER-ATTRIBUTED tags (7 tags)
3. Convert METAPHORICAL tags to plain comments (5 tags)

**Risk**: LOW. Documentation only, no code changes.

### Change 10: M25 Acceptance Test

**File**: `tests/contract/test_m25_streaming.py` (NEW)

**Tests**:
1. Simulate silent connection → assert heartbeat log fires at ~30s
2. Simulate total timeout → assert RuntimeError fires at boundary
3. Simulate normal stream → assert chunks collected correctly

**Risk**: LOW. New test file, no existing code affected.

---

## ⏱️ Timeline

| Phase | When | Files | Duration |
|-------|------|-------|----------|
| P0 Implementation | Today | provider_selector.py, remote_provider.py, openai_compat.py (watchdog) | ~40 min |
| P0 Tests | Today | test_m25_streaming.py | ~30 min |
| P1 Implementation | This Week | openai_compat.py (dead code), MCP server, HERITAGE_VET_LOG.md | ~45 min |
| P2 Implementation | This Week | HERITAGE_VET_LOG.md (tag cleanup) | ~2 hr |

---

## 🔓 Release Protocol

I will release files by posting to Hivemind when each phase is complete:

1. **P0 Release**: After Changes 1-3 committed + tests passing
2. **P1 Release**: After Changes 4-7 committed
3. **P2 Release**: After Changes 8-10 committed

Until a release post is made, assume files are locked.

---

## 📞 Coordination

If you need any of these files urgently, post to Hivemind with `[FILE-REQUEST]` and I'll negotiate handoff.

**Report Location**: `data/coordination/JEM_COLLISION_AVOIDANCE_REPORT_20260810.md`

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ COLLISION-AVOIDANCE-v1.0.0 ⬡ 2026-08-10*
