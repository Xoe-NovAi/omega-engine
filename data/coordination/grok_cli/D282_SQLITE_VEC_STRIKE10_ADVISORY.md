# D-282 sqlite-vec Strike 10 — Concurrency Hardening (Advisory Spec)
**Packet**: `ho_28064f96a360`  
**Author**: `grok-cli/grok` · 2026-07-17  
**Role**: Advisory only — **do not** write tests under this packet (M16)

---

## Live code vs handoff PRAGMA table

**File**: `src/omega/memory/sqlite_vec_adapter.py` (`_get_conn` ~L73–106)

| Knob | Kali handoff target | **Shipped code** | Advisory |
|------|---------------------|------------------|----------|
| journal_mode | WAL | WAL ✅ | Keep |
| busy_timeout | 30000 | 30000 ✅ | Keep |
| synchronous | NORMAL | NORMAL ✅ | Keep |
| wal_autocheckpoint | **500** | **1000** | Align decision needed |
| mmap_size | **512MB** | **256MB** (268435456) | Align decision needed |
| cache_size | **32MB** (-32768) | **512MB** (-524288) | **Conflict** — code is more aggressive |

### 5700U / zRAM judgment (Grok)

- **cache_size=-524288 (512MB)** on a 14Gi box with concurrent inference + zRAM is **risky** under memory pressure. Handoff’s **32MB** is safer for multi-process contention.  
- **mmap 256MB** is a reasonable middle; 512MB mmap + 512MB cache can double-count pressure.  
- Recommend **document one stack as SSOT** (Forge Gap 2 vs adapter comments diverge). Prefer:

```
journal_mode=WAL
busy_timeout=30000
synchronous=NORMAL
cache_size=-32768        # 32MB — 5700U-safe
mmap_size=268435456      # 256MB — keep unless measured need
wal_autocheckpoint=500   # more frequent than 1000 under writer load
journal_size_limit=67108864  # keep (already present)
```

Do **not** change values in advisory pass — Triad/Roc measures + commits.

---

## BEGIN IMMEDIATE coverage

Rough scan of write-ish methods: **upsert / delete / delete_session** (and sync helpers) already use `BEGIN IMMEDIATE` with comments citing SQLITE_BUSY_SNAPSHOT.

**Residual risks to verify in implementation review** (not claiming bugs without line audit of every branch):

1. Schema init paths (`_ensure_vec_table`, `_sync_create_vec`) — ensure IMMEDIATE or single-writer at startup.  
2. `query` path marked writes in crude scan — confirm read path does not hold unnecessary write locks.  
3. **ArchivalMemory** (`archival.py`) opens its **own** SQLite connection with similar PRAGMA but need to verify IMMEDIATE on archival write APIs (separate DB fabric risk).

---

## Four concurrency tests (spec for `tests/test_sqlite_vec_concurrency.py`)

| # | Test | Assert |
|---|------|--------|
| 1 | **Writer starvation** | N readers + 1 writer; writer completes within busy_timeout; no permanent hang |
| 2 | **Checkpoint contention** | Concurrent upsert + `wal_checkpoint(PASSIVE|TRUNCATE)` does not corrupt; error is busy-retry not crash |
| 3 | **Multi-process** | Two processes upsert disjoint keys; both commit; count matches |
| 4 | **IMMEDIATE vs DEFERRED** | Forced DEFERRED-like race (if harness can inject) loses; IMMEDIATE path passes under same race |

**Constraints**: AnyIO in tests; no asyncio; use tmp_path; skip if sqlite-vec extension missing.

**Do not invent pass criteria numbers** without measurement — use “completes < 30s” aligned to busy_timeout.

---

## Cross-ref

- Adapter already has checkpoint helpers (~L666+) and health PRAGMA reads.  
- Existing `tests/test_sqlite_vec_adapter.py` — extend rather than duplicate unit coverage.

---

## Verdict

| Item | Answer |
|------|--------|
| Is BEGIN IMMEDIATE present on primary writes? | **Yes (upsert/delete family)** |
| Is PRAGMA stack = handoff table? | **No — document and converge** |
| Ship tests now (Grok)? | **No (M16 advisory)** |
| Highest risk | cache_size 512MB on 5700U under load |

*Deliverable for `ho_28064f96a360`.*
