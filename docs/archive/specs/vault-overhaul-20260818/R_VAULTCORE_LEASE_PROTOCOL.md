<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 VaultCore Lease Protocol — Pattern Extract from AGY OAuth Fix
**AP Token**: `AP-VAULTCORE-LEASE-v1.0.0`
⬡ OMEGA ⬡ MAAT ⬡ TRACK-C ⬡ 2026-07-25

## Overview

The AGY OAuth atomic write-back fix (P0-1) established a proven pattern for file-based lease management with cross-platform locking and crash-safe atomic writes. This document extracts that pattern as the **VaultCore Lease Protocol** — the foundation for VaultCore's credential management, session caching, and lease revocation subsystems.

---

## §1 The Pattern

### Core Components

| Component | AGY Implementation | VaultCore Abstraction |
|-----------|-------------------|----------------------|
| **Lease Store** | `antigravity-accounts.json` | Configurable JSON/YAML file path |
| **Lease Lock** | `FileLock(.json.lock, timeout=10)` | `FileLock(path.lock, timeout=configurable)` |
| **Lease Acquisition** | `lock.__enter__()` | Lock context manager |
| **Lease Publication** | `atomic_write_sync()` — temp + fsync + replace | Atomic write helper |
| **Lease Eviction** | `del accounts[account_id]` | Delete key + atomic write |
| **Lease Enumeration** | `load_all_accounts()` | Full lease inventory scan |
| **Concurrency Model** | `anyio.to_thread.run_sync(_write)` | AnyIO thread-pool bridge |

### Locking Protocol

```python
# ACQUIRE → READ → MODIFY → WRITE → RELEASE
with self.lock:                              # ACQUIRE (blocking, timeout=10s)
    accounts = self._read_accounts()         # READ    (in-memory snapshot)
    accounts[key] = updated_value            # MODIFY  (in-place)
    atomic_write_sync(path, json.dumps(...))  # WRITE   (crash-safe)
# RELEASE (implicit on __exit__)
```

### Atomic Write (Crash-Safe)

```python
def atomic_write_sync(path: str, content: str):
    """Write with temp file + fsync + atomic replace."""
    parent = Path(path).parent
    tmp_path = parent / f".{Path(path).name}-{os.getpid()}.tmp"
    with open(tmp_path, 'w') as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())     # Force to disk
    os.replace(tmp_path, path)    # Atomic rename (POSIX)
```

---

## §2 Lease Types

### Short-Lived Lease (Session / OAuth Token)

| Property | Value |
|----------|-------|
| TTL | 3600s (1 hour) |
| Renewal | On each successful refresh |
| Lock timeout | 10s |
| Concurrency risk | High (multiple accounts refreshing) |
| Recovery | On restart: scan, validate expiry, batch refresh |

### Medium-Lived Lease (API Key / Service Credential)

| Property | Value |
|----------|-------|
| TTL | 86400s (24 hours) |
| Renewal | Periodic refresh before expiry |
| Lock timeout | 30s |
| Concurrency risk | Medium |
| Recovery | On restart: scan, validate expiry, single refresh |

### Long-Lived Lease (Master Key / Identity)

| Property | Value |
|----------|-------|
| TTL | 30 days (configurable) |
| Renewal | Manual rotation |
| Lock timeout | 60s |
| Concurrency risk | Low |
| Recovery | On restart: validate signature, fall back to re-auth |

---

## §3 VaultCore Lease API Design

```python
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from filelock import FileLock
import anyio

@dataclass
class LeaseProtocol:
    """Core lease protocol for VaultCore."""
    
    store_path: Path
    lock_timeout: int = 10
    ttl_seconds: int = 3600
    on_expired: Optional[Callable] = None  # Callback on lease expiry
    
    def __post_init__(self):
        self.lock = FileLock(
            str(self.store_path.with_suffix(".lock")),
            timeout=self.lock_timeout
        )
    
    async def acquire(self, lease_id: str, payload: Dict[str, Any]) -> bool:
        """Acquire a lease with lock."""
        def _write():
            with self.lock:
                leases = self._read_store()
                leases[lease_id] = {
                    **payload,
                    "acquired_at": datetime.utcnow().isoformat(),
                    "expires_at": (datetime.utcnow() + 
                                  timedelta(seconds=self.ttl_seconds)).isoformat()
                }
                self._atomic_write(leases)
        await anyio.to_thread.run_sync(_write)
        return True
    
    async def renew(self, lease_id: str) -> bool:
        """Extend lease TTL."""
        def _renew():
            with self.lock:
                leases = self._read_store()
                if lease_id not in leases:
                    return False
                leases[lease_id]["expires_at"] = (
                    datetime.utcnow() + timedelta(seconds=self.ttl_seconds)
                ).isoformat()
                self._atomic_write(leases)
                return True
        return await anyio.to_thread.run_sync(_renew)
    
    async def release(self, lease_id: str) -> bool:
        """Release/evict a lease."""
        def _release():
            with self.lock:
                leases = self._read_store()
                if lease_id not in leases:
                    return False
                del leases[lease_id]
                self._atomic_write(leases)
                return True
        return await anyio.to_thread.run_sync(_release)
    
    def _read_store(self) -> Dict[str, Any]:
        """Read current lease store (must hold lock)."""
        if self.store_path.exists():
            import json
            return json.loads(self.store_path.read_text())
        return {}
    
    def _atomic_write(self, data: Dict[str, Any]):
        """Crash-safe atomic write."""
        import json, os, tempfile
        fd, tmp = tempfile.mkstemp(
            dir=self.store_path.parent,
            prefix=f".{self.store_path.name}-",
            suffix=".tmp"
        )
        try:
            with os.fdopen(fd, 'w') as f:
                json.dump(data, f, indent=2)
                f.flush()
                os.fsync(fd)
            os.replace(tmp, self.store_path)
        except Exception:
            try:
                os.remove(tmp)
            except OSError:
                pass
            raise
```

---

## §4 Provenance: AGY OAuth Persistence Fix

The pattern was proven in `src/omega/agents/scribe/agy_oauth_persistence.py`:

| Aspect | Implementation |
|--------|---------------|
| **File** | `src/omega/agents/scribe/agy_oauth_persistence.py` |
| **Class** | `AGYAuthPersistence` |
| **Atomic write** | `atomic_write_sync()` — uses `tempfile.mkstemp()` + `os.fsync()` + `os.replace()` |
| **Locking** | `filelock.FileLock` — fcntl on POSIX, msvcrt on Windows |
| **AnyIO bridge** | `try: anyio.from_thread.run_sync() except NoEventLoopError: _write()` |
| **Concurrency test** | 5 threads × 10 writes each = 50 concurrent operations without data loss |
| **Status** | ✅ Tested and verified in PR #2 to `0xYiliu/opencode-antigravity-auth` |

### Verification Results

```
✅ AGY OAuth persistence verification passed (including concurrent writes)
   - Single-threaded write: PASS
   - Atomic update overwrite: PASS
   - 5-thread × 10-write concurrent: PASS (0 errors, 5 accounts persisted)
```

---

## §5 VaultCore Integration Points

| Week | Integration | Lease Protocol Component |
|------|-------------|--------------------------|
| Week 1 (Credential Mgmt) | Encrypted credential store | `acquire()`, `release()`, TTL enforcement |
| Week 2 (Session Cache) | Multi-account session persistence | `renew()`, bulk `load_all()`, expiry sweeper |
| Week 3 (Lease Revocation) | Kill switch for compromised credentials | `release()`, audit log, emergency purge |

---

## §6 Sources

1. `src/omega/agents/scribe/agy_oauth_persistence.py` — AGY OAuth persistence fix (proven implementation)
2. `src/omega/agents/scribe/lock.py` — `atomic_write`, `atomic_write_sync` primitives
3. `filelock` 3.x — Cross-platform file locking (fcntl/msvcrt)
4. POSIX `os.replace()` — Atomic file rename semantics
5. `anyio` — AnyIO thread pool bridging (`anyio.to_thread.run_sync`)

---

## Decision Gate

✅ **Lease protocol pattern extracted from AGY fix** — Acquire → Read → Modify → Write → Release
✅ **Atomic write pattern** — Temp file + fsync + atomic replace (crash-safe)
✅ **AnyIO concurrency bridge** — Thread-pool with fallback to sync
✅ **3 lease types defined** — Short (1h), Medium (24h), Long (30d)
✅ **VaultCore Lease API designed** — `acquire()`, `renew()`, `release()` with lock-safe semantics

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: TRACK-C | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
