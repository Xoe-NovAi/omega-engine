<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# SoulStore Race Condition & Multi-Path Write Architecture — Deep Research
**AP Token**: `AP-SOULSTORE-RACE-20260726`
**Date**: 2026-07-26 | **Priority**: P0 — BLOCKER
**Researcher**: Sovereign Researcher (Council of Four)

---

## Executive Summary

The Omega Engine has **8 distinct write paths** to soul-related files, using **4 incompatible locking mechanisms**, with **3 of them completely bypassing the canonical SoulStore**. The result: lost-update race conditions, zero-fsync durability gaps on ext4, and silent data-corruption surface area.

## Current State — Every Writer Audited

| Writer | File | Lock | fsync | Race Risk |
|--------|------|------|-------|-----------|
| **SoulStore.write_atomic()** | soul_store.py | fcntl.flock ✅ | ✅ fsync data+dir | ✅ Safe |
| **SoulUpdater._write_to_soul()** | soul_updater.py | Inherits SoulStore flock | ✅ Inherits | 🔴 Read-modify-write without read lock |
| **SoulUpdateManager._write_soul_file()** | soul_update_manager.py | anyio.Lock + SoulStore flock | ✅ Inherits | 🔴 Event-loop blocking (fcntl in async) |
| **EntityWorkspace._atomic_write_yaml()** | entity_workspace.py | threading.Lock | ❌ ZERO | 🔴 Cross-process unprotected |
| **EntityWorkspace.update_soul()** | entity_workspace.py | threading.Lock | ❌ ZERO | 🔴 Zero durability on ext4 |
| **EntityWorkspace.append_session_anchor()** | entity_workspace.py | ❌ NONE | ❌ ZERO | 🔴 CRITICAL — no locking at all |
| **write_soul_file()** | entity_registry.py | ❌ NONE | ❌ ZERO | 🔴 CRITICAL — no locking, no durability |
| **Scribe Distiller._write_proposed_lessons()** | scribe/distiller.py | ❌ NONE | ✅ fsync | 🔴 Unlocked read-modify-write |

## 5 Race Conditions Found

### RC-1: Read-Modify-Write Without Read Lock (CRITICAL)
All writers except SoulStore read soul.yaml, modify in memory, then write — but the read is unprotected. Two concurrent readers both see old state, both append different lessons, last writer wins → data loss.

### RC-2: fcntl.flock Blocking Inside Async Context (HIGH)
SoulStore's flock is blocking. When called directly (not via `anyio.to_thread.run_sync`), it blocks the event loop.

### RC-3: Zero fsync on ext4 (CRITICAL)
Writers 4-7 have no fsync. On power loss: zero-length file, partial content, or corrupted YAML. The 2026 FITO paper confirms this is not theoretical.

### RC-4: Cross-Process Lock Incompatibility (HIGH)
`threading.Lock` is process-local. If OpenCode + MCP Hub write simultaneously, only SoulStore's flock provides protection.

### RC-5: SoulDistiller Poison Loop (PARTIALLY FIXED)
Two concurrent distillations can overwrite each other's entries in proposed_lessons.yaml.

## Recommended Architecture: SoulStore.mutate()

```python
async def mutate_soul(entity_name: str, mutator: Callable[[dict], dict]):
    """Read soul, apply mutation, write atomically — all under one flock."""
    soul_path = get_soul_path(entity_name)
    lock_path = soul_path.with_suffix(".lock")
    
    lock_fd = os.open(str(lock_path), os.O_CREAT | os.O_RDWR)
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        content = await anyio.to_thread.run_sync(soul_path.read_text)
        data = yaml.safe_load(content) or {}
        data = mutator(data)
        await soul_store.write_atomic(soul_path, yaml.dump(data))
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        os.close(lock_fd)
```

## Migration Plan

| Phase | Task | Files | Effort |
|-------|------|-------|--------|
| 1 | Add `mutate_soul()` + `mutate_file()` to SoulStore | soul_store.py | 2h |
| 2 | Replace EntityWorkspace writers (4-7) with SoulStore | entity_workspace.py, entity_registry.py | 3h |
| 3 | Fix SoulUpdater + SoulUpdateManager read-modify-write | soul_updater.py, soul_update_manager.py | 2h |
| 4 | Audit USM write path | state_manager.py | 1h |
| 5 | Chaos tests (100 concurrent writers, power loss) | tests/chaos/ | 3h |
| **Total** | | | **~11h** |

## Key Sources
- Postgres fsyncgate pattern (SoulStore docstring)
- Git lock file pattern (O_CREAT|O_EXCL → write → fsync → rename)
- FITO paper 2026 (arXiv:2603.01384) — durable replacement requires dir fsync
- LWN ext4 data loss article (2009) — confirmed by FITO 2026
