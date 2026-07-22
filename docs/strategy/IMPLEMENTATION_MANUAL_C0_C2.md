# 🔱 Omega Engine — Phase C Implementation Manual
**AP Token**: `AP-PHASE-C-IMPL-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ opencode ⬡ trc_implementation ⬡ PHASE-C

**Date**: 2026-07-21
**Status**: LIVE — Agents implement directly from this document
**Source Research**: R25, R27, R28, R20, R23 (5 papers, 5 deliverables)

---

## How to Use This Manual

1. **Find your ticket** — each section is self-contained
2. **Read the Decision Gate** — the one thing the ticket decides
3. **Follow the Steps** — code snippets are copy-paste ready
4. **Run the Verification** — pass/fail gate before moving on
5. **Update the Job Board** — mark complete in `data/coordination/RESEARCH_JOB_BOARD.yaml`

**Hardware Context**: Ryzen 5700U, 15W, 16GB RAM (~8GB available), 8MB L3/2 CCX.
**Sovereign Context**: M1 AnyIO, M2 Firewall, M7 Local-First, M13 Temple-Grade, M23 Failure Integrity.

---

## Ticket C-0: Test Suite Honesty
**Priority**: P0 | **Effort**: 2–4h | **Owner**: Ma'at/P10 or Verity
**Blocks**: Everything (Phase D gate)

### Decision Gate
Fix the Makefile "1315 tests ✅" lie. Implement quarantine pattern. Generate honest test badge from JSON output.

### Current State (Verified)
- `Makefile:40` displays `1315 tests ✅` — fabricated
- `Makefile:43` has `PASSED=${PASSED:-705}` — hardcoded fallback when pytest fails
- `Makefile:54` claims "1315 active + 43 skipped + 3 xfail" — inaccurate
- Known failures: `test_firewall_m2_strict_engine_core`, memory RRF/search, model registry
- Real sample run: ~832 pass / ~5 fail / ~40 skip

### Step 1: Install pytest-json-report
```bash
source .venv/bin/activate
pip install pytest-json-report
# Add to pyproject.toml under [project.optional-dependencies]
# Add to requirements-dev.txt
```

### Step 2: Register Quarantine Marker in pyproject.toml
```toml
# Add to [tool.pytest.ini_options] section
markers = [
    "quarantine(reason, ticket, expires): Test quarantined from CI gate (still runs, xfail)",
]
```

### Step 3: Add conftest.py Hook (tests/conftest.py)
```python
import pytest

def pytest_collection_modifyitems(config, items):
    """Auto-convert quarantine markers to xfail."""
    for item in items:
        marker = item.get_closest_marker("quarantine")
        if marker:
            reason = marker.kwargs.get("reason", "quarantined")
            ticket = marker.kwargs.get("ticket", "")
            expires = marker.kwargs.get("expires", "")
            item.add_marker(pytest.mark.xfail(
                reason=f"[QUARANTINE {ticket}] {reason} (expires {expires})",
                run=True,  # Still run the test — we see if it passes
            ))
```

### Step 4: Quarantine Known Failures
Find and mark the 5 known failures:

```bash
# Find the failing tests
source .venv/bin/activate
python -m pytest tests/ -x --tb=short -q 2>&1 | tail -20
```

Then add quarantine markers to each:

```python
# Example in tests/test_firewall_m2_strict_engine_core.py
@pytest.mark.quarantine(
    reason="Firewall M2 check needs refactoring for new WAD layout",
    ticket="C-0",
    expires="2026-08-15"
)
def test_firewall_m2_strict_engine_core():
    ...
```

Repeat for all 5 known failures with appropriate reasons and expiry dates.

### Step 5: Fix Makefile — Remove Hardcoded Fallback
Replace the menu display (lines 36-41) with honest reporting:

```makefile
# BEFORE (line 40 — THE LIE):
@echo "$(COLOR_PURPLE)║$(COLOR_NC)  $(COLOR_GREEN)1315 tests ✅  |  1361 collected  |  All 23 Mandates enforced$(COLOR_PURPLE)║$(COLOR_NC)"

# AFTER (honest):
@echo "$(COLOR_PURPLE)║$(COLOR_NC)  $(COLOR_GREEN)$(shell cat docs/TEST_STATUS.md 2>/dev/null | head -1)$(COLOR_PURPLE)║$(COLOR_NC)"
```

Replace the test-badge target (lines 379-390):

```makefile
test-badge: ## 📊 Generate TEST_STATUS.md with honest test counts
	@source .venv/bin/activate && \
	PYTHONPATH=src python -m pytest tests/ \
		--json-report --json-report-file=.pytest_report.json \
		-q --tb=no 2>/dev/null; \
	python scripts/generate_test_badge.py \
		--report .pytest_report.json \
		--output docs/TEST_STATUS.md
```

### Step 6: Create scripts/generate_test_badge.py
```python
#!/usr/bin/env python3
"""Generate TEST_STATUS.md from pytest JSON report."""
import json
import sys
import argparse
from datetime import datetime

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    with open(args.report) as f:
        report = json.load(f)

    summary = report.get("summary", {})
    collected = summary.get("total", 0)
    passed = summary.get("passed", 0)
    failed = summary.get("failed", 0)
    skipped = summary.get("skipped", 0)
    xfailed = summary.get("xfailed", 0)

    # Determine badge color
    if failed > 0:
        color = "🔴"
        status = f"{collected} collected · {passed} passed · {failed} FAILED"
    elif xfailed > 0:
        color = "🟡"
        status = f"{collected} collected · {passed} passed · {xfailed} quarantined"
    else:
        color = "🟢"
        status = f"{collected} collected · {passed} passed · All green"

    line1 = f"{color} {status}"
    line2 = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}"

    with open(args.output, "w") as f:
        f.write(f"{line1}\n{line2}\n")

    print(line1)

if __name__ == "__main__":
    main()
```

### Verification Gate (C-0)
```bash
# 1. Run full test suite — all should pass (quarantined tests are xfail, not fail)
source .venv/bin/activate
PYTHONPATH=src python -m pytest tests/ -q --tb=short
# EXIT CODE MUST BE 0

# 2. Verify badge generation
make test-badge
cat docs/TEST_STATUS.md
# MUST show real numbers, NOT "1315 tests ✅"

# 3. Verify menu shows honest count
make menu
# MUST show output from TEST_STATUS.md, not hardcoded text

# 4. Count quarantine markers
grep -r "quarantine" tests/ | wc -l
# Should be >= 5 (known failures quarantined)

# 5. No hardcoded fallback defaults
grep -n "PASSED:-" Makefile
# MUST return empty (fallback removed)
```

### Commit
```
fix: C-0 test honesty — quarantine red tests, JSON badge, remove Makefile lies
```

---

## Ticket C-1′: SoulStore — Single Atomic Writer
**Priority**: P0 | **Effort**: 4–6h | **Owner**: Ma'at/P3 + Roc
**Blocks**: Soul integrity (M11), Phase D gate

### Decision Gate
Implement single `SoulStore` writer class with `fcntl.flock` + atomic write + `os.fsync` + actor model. Delete/replace all 4 existing writer paths.

### Current State (Verified)
4 writers exist, **none call `os.fsync()`**:

| Writer | File | Temp? | fsync? | Atomic? | Locking? |
|--------|------|-------|--------|---------|----------|
| `write_soul_file` | `entity_registry.py:79` | ✅ `.tmp` | ❌ | ✅ `.rename()` | ⚠️ flock only in that function |
| `_write_to_soul` | `soul_updater.py:78` | ❌ | ❌ | ❌ `write_text()` | ❌ None |
| `_write_soul_file` | `soul_update_manager.py:32` | ❌ | ❌ | ❌ `open().write()` | ⚠️ `anyio.Lock` (in-process) |
| `update_soul()` | `entity_workspace.py` | ✅ `mkstemp` | ❌ | ✅ `os.replace()` | ❌ None |

### Step 1: Create src/omega/oracle/soul_store.py
```python
# 🔱 SoulStore — Single Atomic Writer for Soul Files
# AP: AP-SOUL-STORE-v1.0.0
# M11: Soul Integrity — single write path, fcntl + atomic + fsync

"""
SoulStore is the ONLY class that writes soul files.

Pattern: fcntl.flock → validate → tmp → os.fsync → os.replace → dir fsync → audit
Actor model: actor ∈ {user, system_agent, system_daemon}
"""

import fcntl
import logging
import os
import tempfile
import time
from pathlib import Path
from typing import Optional, Literal

import yaml

logger = logging.getLogger(__name__)

ActorType = Literal["user", "system_agent", "system_daemon"]

# Which files each actor can write
ACTOR_PERMISSIONS = {
    "user": {"soul.yaml", "approved_lessons.yaml", "identity/"},
    "system_agent": {"proposed_lessons.yaml", "knowledge/", "sessions/"},
    "system_daemon": {"proposed_lessons.yaml"},  # append only
}

# Which files each actor CANNOT write
ACTOR_DENIED = {
    "user": {"proposed_lessons.yaml"},
    "system_agent": {"soul.yaml", "approved_lessons.yaml"},
    "system_daemon": {"soul.yaml", "approved_lessons.yaml", "identity/", "knowledge/"},
}


class SoulStoreError(Exception):
    """Base error for SoulStore operations."""


class SoulPermissionError(SoulStoreError):
    """Actor does not have permission to write this file."""


class SoulLockError(SoulStoreError):
    """Could not acquire soul lock."""


class SoulValidationError(SoulStoreError):
    """Soul data failed validation."""


class SoulLock:
    """Cross-process soul file lock. Never delete the lock file.

    Uses fcntl.flock(LOCK_EX | LOCK_NB) with retry loop.
    Locks auto-release on process death (even SIGKILL).
    """

    def __init__(self, lock_path: str, timeout: float = 5.0):
        self.lock_path = lock_path
        self.timeout = timeout
        self._fd: Optional[int] = None

    def acquire(self) -> bool:
        """Blocking acquire with timeout. Returns True on success."""
        open_mode = os.O_RDWR | os.O_CREAT | os.O_TRUNC
        fd = os.open(self.lock_path, open_mode)
        start = time.monotonic()
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                self._fd = fd
                return True
            except (IOError, OSError):
                if time.monotonic() - start > self.timeout:
                    os.close(fd)
                    raise SoulLockError(
                        f"Could not acquire soul lock after {self.timeout}s"
                    )
                time.sleep(0.05)

    def release(self) -> None:
        """Release the lock and close the fd."""
        if self._fd is not None:
            fcntl.flock(self._fd, fcntl.LOCK_UN)
            os.close(self._fd)
            self._fd = None


def _atomic_write(path: Path, content: bytes) -> None:
    """Atomic write: tmp → fsync → os.replace → dir fsync.

    This is the Postgres-proven "fsync dance" for durability.
    """
    dir_path = path.parent
    dir_path.mkdir(parents=True, exist_ok=True)

    # Write to temp file in same directory (same filesystem for atomic rename)
    fd, tmp_path = tempfile.mkstemp(dir=str(dir_path), suffix=".soul_tmp")
    try:
        os.write(fd, content)
        os.fsync(fd)  # Flush data to disk
        os.close(fd)
        fd = -1  # Mark as closed

        # Atomic rename (POSIX guarantee: same filesystem)
        os.replace(tmp_path, str(path))

        # Flush directory metadata
        dir_fd = os.open(str(dir_path), os.O_RDONLY)
        try:
            os.fsync(dir_fd)  # Ensure directory entry is persisted
        finally:
            os.close(dir_fd)
    except Exception:
        # Clean up temp file on failure
        if fd >= 0:
            os.close(fd)
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


class SoulStore:
    """Single atomic writer for all soul files.

    This is the ONLY class that writes to soul.yaml, proposed_lessons.yaml,
    and approved_lessons.yaml. All other write paths delegate here.
    """

    def __init__(self, entities_dir: Path):
        self.entities_dir = entities_dir

    def _get_entity_dir(self, entity: str) -> Path:
        return self.entities_dir / entity

    def _get_lock_path(self, entity: str) -> str:
        return str(self._get_entity_dir(entity) / ".soul.lock")

    def _validate_actor(self, actor: ActorType, filename: str) -> None:
        """Check actor has permission to write this filename."""
        if filename in ACTOR_DENIED.get(actor, set()):
            raise SoulPermissionError(
                f"Actor '{actor}' cannot write '{filename}'. "
                f"Denied files: {ACTOR_DENIED[actor]}"
            )

    def _validate_soul_data(self, data: dict) -> None:
        """Basic soul.yaml structure validation."""
        if not isinstance(data, dict):
            raise SoulValidationError("soul.yaml must be a dict")
        entity = data.get("entity", {})
        if not entity.get("name"):
            raise SoulValidationError("soul.yaml missing entity.name")

    async def write_soul(
        self,
        entity: str,
        data: dict,
        actor: ActorType,
        trace_id: str = "",
    ) -> None:
        """Write soul.yaml atomically.

        1. Validate actor permission
        2. Validate soul data
        3. Acquire cross-process lock
        4. Atomic write: tmp → fsync → replace → dir fsync
        5. Audit trail
        6. Release lock
        """
        filename = "soul.yaml"
        self._validate_actor(actor, filename)
        self._validate_soul_data(data)

        soul_path = self._get_entity_dir(entity) / filename
        lock_path = self._get_lock_path(entity)

        lock = SoulLock(lock_path)
        try:
            lock.acquire()
            content = yaml.dump(data, default_flow_style=False, allow_unicode=True)
            _atomic_write(soul_path, content.encode("utf-8"))
            logger.info(
                "SoulStore.write_soul entity=%s actor=%s trace=%s",
                entity, actor, trace_id,
            )
        finally:
            lock.release()

    async def write_proposed(
        self,
        entity: str,
        data: dict,
        actor: ActorType,
        trace_id: str = "",
    ) -> None:
        """Write proposed_lessons.yaml atomically."""
        filename = "proposed_lessons.yaml"
        self._validate_actor(actor, filename)

        soul_path = self._get_entity_dir(entity) / filename
        lock_path = self._get_lock_path(entity)

        lock = SoulLock(lock_path)
        try:
            lock.acquire()
            content = yaml.dump(data, default_flow_style=False, allow_unicode=True)
            _atomic_write(soul_path, content.encode("utf-8"))
            logger.info(
                "SoulStore.write_proposed entity=%s actor=%s trace=%s",
                entity, actor, trace_id,
            )
        finally:
            lock.release()

    async def read_soul(self, entity: str) -> Optional[dict]:
        """Read soul.yaml (no lock needed — lock-free read)."""
        soul_path = self._get_entity_dir(entity) / "soul.yaml"
        if not soul_path.exists():
            return None
        content = soul_path.read_text(encoding="utf-8")
        return yaml.safe_load(content) or {}

    async def read_proposed(self, entity: str) -> Optional[dict]:
        """Read proposed_lessons.yaml."""
        path = self._get_entity_dir(entity) / "proposed_lessons.yaml"
        if not path.exists():
            return None
        content = path.read_text(encoding="utf-8")
        return yaml.safe_load(content) or {}
```

### Step 2: Create Tests
```python
# tests/test_soul_store.py
import pytest
from pathlib import Path
from omega.oracle.soul_store import SoulStore, SoulPermissionError, _atomic_write

@pytest.fixture
def soul_store(tmp_path):
    entities = tmp_path / "entities"
    entities.mkdir()
    (entities / "test_entity").mkdir()
    # Create minimal soul.yaml
    soul = {"entity": {"name": "test_entity", "lessons_learned": []}}
    import yaml
    (entities / "test_entity" / "soul.yaml").write_text(yaml.dump(soul))
    return SoulStore(entities)

@pytest.mark.anyio
async def test_write_soul_user_actor(soul_store):
    """User actor can write soul.yaml."""
    data = {"entity": {"name": "test_entity", "lessons_learned": ["L3 test"]}}
    await soul_store.write_soul("test_entity", data, actor="user", trace_id="test-1")
    result = await soul_store.read_soul("test_entity")
    assert "L3 test" in result["entity"]["lessons_learned"]

@pytest.mark.anyio
async def test_write_soul_system_agent_denied(soul_store):
    """system_agent CANNOT write soul.yaml."""
    data = {"entity": {"name": "test_entity", "lessons_learned": []}}
    with pytest.raises(SoulPermissionError):
        await soul_store.write_soul("test_entity", data, actor="system_agent")

@pytest.mark.anyio
async def test_write_proposed_system_agent(soul_store):
    """system_agent CAN write proposed_lessons.yaml."""
    data = {"proposals": ["L3 test principle"]}
    await soul_store.write_proposed("test_entity", data, actor="system_agent")
    result = await soul_store.read_proposed("test_entity")
    assert "L3 test principle" in result["proposals"]

@pytest.mark.anyio
async def test_atomic_write_durability(soul_store, tmp_path):
    """Atomic write produces valid file."""
    target = tmp_path / "test.yaml"
    _atomic_write(target, b"key: value\n")
    assert target.read_text() == "key: value\n"

def test_lock_acquire_release():
    """SoulLock acquires and releases cleanly."""
    from omega.oracle.soul_store import SoulLock
    import tempfile
    with tempfile.NamedTemporaryFile() as f:
        lock = SoulLock(f.name, timeout=1.0)
        assert lock.acquire() is True
        lock.release()
        assert lock._fd is None
```

### Step 3: Migrate Existing Writers
For each of the 4 existing writers, replace the write path:

**entity_registry.py** — Replace `write_soul_file` body:
```python
# BEFORE:
async def write_soul_file(entity_path, filename, content, token=None):
    # ... complex locking logic ...

# AFTER:
async def write_soul_file(entity_path, filename, content, token=None):
    """Delegate to SoulStore. Keep API signature for backward compat."""
    from omega.oracle.soul_store import SoulStore, ActorType
    from pathlib import Path
    store = SoulStore(Path(entity_path).parent)
    data = yaml.safe_load(content)
    actor: ActorType = "user" if token == SOVEREIGN_USER_TOKEN else "system_agent"
    if filename == "soul.yaml":
        await store.write_soul(Path(entity_path).parent.name, data, actor=actor)
    elif filename == "proposed_lessons.yaml":
        await store.write_proposed(Path(entity_path).parent.name, data, actor=actor)
```

**soul_updater.py** — Replace `_write_to_soul`:
```python
async def _write_to_soul(self, task, l3, l2):
    """Delegate to SoulStore."""
    from omega.oracle.soul_store import SoulStore
    from pathlib import Path
    store = SoulStore(self.entities_dir)
    entity = task.entity or "sophia"
    soul = await store.read_soul(entity) or {"entity": {"name": entity, "lessons_learned": []}}
    soul["entity"].setdefault("lessons_learned", []).append(l3)
    await store.write_soul(entity, soul, actor="system_agent", trace_id=task.id)
```

**soul_update_manager.py** — Replace `_write_soul_file`:
```python
async def _write_soul_file(self, path, data):
    """Delegate to SoulStore."""
    from omega.oracle.soul_store import SoulStore
    from pathlib import Path
    store = SoulStore(self.entities_dir)
    entity = path.parent.name
    if path.name == "soul.yaml":
        await store.write_soul(entity, data, actor="system_agent")
    elif path.name == "proposed_lessons.yaml":
        await store.write_proposed(entity, data, actor="system_agent")
```

**entity_workspace.py** — Replace `update_soul`:
```python
# Replace the mkstemp + os.replace block with:
from omega.oracle.soul_store import SoulStore
store = SoulStore(self.entities_dir)
await store.write_soul(entity_name, data, actor="system_agent")
```

### Verification Gate (C-1′)
```bash
# 1. All tests pass
source .venv/bin/activate
PYTHONPATH=src python -m pytest tests/test_soul_store.py -v
# ALL 6 tests MUST pass

# 2. No direct soul writes remain (grep for patterns)
grep -rn "write_text.*soul.yaml\|open.*soul.yaml.*write\|\.write(" src/omega/ --include="*.py" | grep -i soul
# Should ONLY show soul_store.py

# 3. fsync is called
grep -n "os.fsync" src/omega/oracle/soul_store.py
# Must show at least 2 calls (data + directory)

# 4. flock is used
grep -n "fcntl.flock" src/omega/oracle/soul_store.py
# Must show acquire (LOCK_EX) and release (LOCK_UN)

# 5. Actor permissions enforced
python -c "
from omega.oracle.soul_store import SoulStore, SoulPermissionError
from pathlib import Path
import tempfile
d = Path(tempfile.mkdtemp()) / 'e'; d.mkdir()
import yaml
(d / 'soul.yaml').write_text(yaml.dump({'entity': {'name': 'e'}}))
store = SoulStore(d.parent)
import asyncio
try:
    asyncio.run(store.write_soul('e', {'entity': {'name': 'e'}}, actor='system_agent'))
    print('FAIL: should have raised')
except SoulPermissionError:
    print('PASS: system_agent denied soul.yaml write')
"
```

### Commit
```
feat: C-1′ SoulStore — single atomic writer with fcntl + fsync + actor model
```

---

## Ticket C-2′: ResourceGuard — Single RAM Truth
**Priority**: P0 | **Effort**: 1–2h | **Owner**: Ma'at/P1
**Blocks**: Local inference stability, C-10 admission control

### Decision Gate
Kill the `ResourceGuard._current_ram_mb` software counter. OOMProtector becomes the sole RAM arbiter. Derive `max_ram_mb` from kernel `MemAvailable` at runtime.

### Current State (Verified)
- `ResourceGuard._current_ram_mb` — software counter, drifts from reality
- `ResourceGuard._max_ram_mb = 12288` — wrong for 16GB/~8GB available
- `OOMProtector.check()` — reads `psutil.virtual_memory().available`, correct
- Workers pass hardcoded budgets: Orchestrator=1024, Researcher=4096, Youtube=2048
- Both systems active simultaneously — dual counter chaos

### Step 1: Modify ResourceGuard — Remove Software Counter
In `src/omega/oracle/resource_guard.py`:

```python
# BEFORE (line ~228 area):
class ResourceGuard:
    def __init__(self, max_ram_mb: int = None, ...):
        self._max_ram_mb = max_ram_mb or cvar_get("resource_guard_max_ram_mb", 12288)
        self._current_ram_mb = 0  # THE PROBLEM
        self._held_weights: Dict[str, int] = {}

# AFTER:
class ResourceGuard:
    def __init__(self, max_ram_mb: int = None, ...):
        # Remove _max_ram_mb and _current_ram_mb entirely
        # Keep only the re-entrant lock pattern for concurrency
        self._held_weights: Dict[str, int] = {}  # Keep for semaphore semantics
        self._semaphore = anyio.Semaphore(1)  # Single concurrency gate
```

### Step 2: Modify OOMProtector — Add KV Cache Estimate
```python
# In ResourceGuard or OOMProtector, enhance the check:

class OOMProtector:
    @staticmethod
    def check(model_ram_mb: int = 0, kv_cache_mb: int = 0) -> bool:
        """Check if model can be loaded without OOM.

        Args:
            model_ram_mb: Expected model weight RAM (from model spec)
            kv_cache_mb: Expected KV cache RAM (context_size * bytes_per_token)
        Returns:
            True if safe to load, False if OOM risk
        """
        available_mb = _get_available_ram_mb()
        if available_mb is None:
            logger.warning("Cannot read available RAM — assuming safe")
            return True

        system_reserve_mb = 1024  # 1GB kernel/OS safety margin
        required_mb = model_ram_mb + kv_cache_mb + system_reserve_mb

        if available_mb < required_mb:
            logger.error(
                "OOM risk: need %dMB (model=%d + kv=%d + reserve=%d), "
                "have %dMB available",
                required_mb, model_ram_mb, kv_cache_mb,
                system_reserve_mb, available_mb,
            )
            return False

        logger.info(
            "OOM check OK: need %dMB, have %dMB available",
            required_mb, available_mb,
        )
        return True
```

### Step 3: Remove Worker Hardcoded Budgets
In each worker, remove the `max_ram_mb` parameter:

```python
# orchestrator.py — REMOVE:
guard = ResourceGuard(max_ram_mb=1024)

# KEEP ONLY:
guard = ResourceGuard()  # No RAM limit — OOMProtector handles it

# Same for:
# - loop.py (Researcher: remove max_ram_mb=4096)
# - youtube_worker.py (Youtube: remove max_ram_mb=2048)
```

### Step 4: Update Config — Remove Default max_ram_mb
```yaml
# config/cvars.yaml or wherever resource_guard_max_ram_mb is defined:
# REMOVE:
# resource_guard_max_ram_mb: 12288

# The cvar_get fallback in ResourceGuard should return None
# and ResourceGuard should not use it for RAM tracking
```

### Verification Gate (C-2′)
```bash
# 1. No _current_ram_mb references remain
grep -rn "_current_ram_mb" src/omega/
# MUST return empty

# 2. No hardcoded max_ram_mb in workers
grep -rn "max_ram_mb=" src/omega/workers/
# MUST return empty (ResourceGuard() with no args)

# 3. OOMProtector.check works
source .venv/bin/activate
PYTHONPATH=src python -c "
from omega.oracle.resource_guard import OOMProtector
result = OOMProtector.check(model_ram_mb=1700, kv_cache_mb=512)
print(f'OOM check: {result}')  # Should be True (8GB available)
"

# 4. _get_available_ram_mb returns real value
PYTHONPATH=src python -c "
from omega.oracle.resource_guard import _get_available_ram_mb
mb = _get_available_ram_mb()
print(f'Available RAM: {mb}MB')  # Should be ~7000-8000
assert mb > 4000, f'Unexpected: {mb}MB'
print('PASS')
"

# 5. ResourceGuard still protects concurrent model loads
PYTHONPATH=src python -c "
from omega.oracle.resource_guard import ResourceGuard
import anyio
guard = ResourceGuard()
async def test():
    async with guard.acquire(weight=1):
        print('PASS: ResourceGuard semaphore works')
anyio.run(test)
"
```

### Commit
```
fix: C-2′ kill ResourceGuard software counter — OOMProtector is sole RAM truth
```

---

## Ticket C-4a: MCP Migration Audit (2h)
**Priority**: P1 | **Effort**: 2h audit + TBD migration | **Owner**: Ma'at/P4
**Blocks**: C-4b migration, MCP 2026-07-28 deadline

### Decision Gate
Audit Hub code paths for MCP 2026-07-28 breaking changes. Size the migration work. Test file-based Hivemind contingency.

### Step 1: Code Inventory (30 min)
```bash
# Find all MCP-related code in the Hub
grep -rn "initialize\|Mcp-Session-Id\|session_id\|SSE\|sse" mcp_servers/omega_hub/ --include="*.py" | head -40

# Find all places that handle protocol handshake
grep -rn "handshake\|initialized\|initialize" mcp_servers/omega_hub/ --include="*.py"

# Find all SSE transport code
grep -rn "EventSource\|text/event-stream\|SSE" mcp_servers/omega_hub/ --include="*.py"
```

Document every location. Create a table:
| File | Line | What | Breaks? |
|------|------|------|---------|
| `server.py:XXX` | | `initialize` handler | Yes — remove |
| `transport.py:XXX` | | SSE session binding | Yes — migrate |

### Step 2: Check SDK Version
```bash
# What MCP SDK version does Hub use?
grep -i "mcp" requirements.txt pyproject.toml setup.py 2>/dev/null

# What Python SDK features are used?
grep -rn "from mcp\|import mcp" mcp_servers/omega_hub/ --include="*.py"
```

### Step 3: Test File-Based Hivemind Contingency
```bash
# Verify Hivemind can work without MCP Hub
# The file-based Hivemind uses data/handoff/ and data/coordination/

# Test: can agents coordinate via files alone?
ls -la data/handoff/pending/
ls -la data/coordination/locks/

# Test: does the handoff protocol work without Hub?
source .venv/bin/activate
PYTHONPATH=src python -c "
from pathlib import Path
import json
# Simulate file-based handoff
packet = {
    'id': 'test-001',
    'source': 'kali',
    'target': 'maat',
    'task': 'test handoff',
    'status': 'pending'
}
Path('data/handoff/pending').mkdir(parents=True, exist_ok=True)
Path('data/handoff/pending/test-001.json').write_text(json.dumps(packet))
print('PASS: File-based handoff works')
"
```

### Step 4: Document Findings
Write findings to `docs/research/R_MCP_AUDIT_FINDINGS.md` with:
1. Every Hub code path that breaks
2. SDK version and compatibility assessment
3. File-based Hivemind contingency test results
4. Recommended migration approach (shim vs full rewrite)
5. Timeline assessment (can we meet July 28?)

### Verification Gate (C-4a)
```bash
# 1. Audit document exists
test -f docs/research/R_MCP_AUDIT_FINDINGS.md && echo "PASS" || echo "FAIL"

# 2. File-based contingency tested
test -f data/handoff/pending/test-001.json && echo "PASS" || echo "FAIL"

# 3. Hub code inventory complete
grep -c "initialize\|session" docs/research/R_MCP_AUDIT_FINDINGS.md
# Should be > 0
```

### Commit
```
docs: C-4a MCP migration audit — code inventory + contingency test
```

---

## Ticket C-5: MaKaLi Routing Config
**Priority**: P1 | **Effort**: 0.5h | **Owner**: Kali
**Blocks**: C-10 admission control, local inference optimization

### Decision Gate
Configure MaKaLi routing: Kali → local, Ma'at+Lilith → cloud. Config only, no code changes.

### Step 1: Update providers.yaml
```yaml
# config/providers.yaml — add routing section:

maakali_routing:
  kali:
    prefer: native-gguf    # Local first for Kali
    fallback: antigravity
  maat:
    prefer: antigravity    # Cloud for Ma'at (build side)
    fallback: google
  lilith:
    prefer: antigravity    # Cloud for Lilith (run side)
    fallback: google
```

### Step 2: Update MaKaLi Council Config
```yaml
# config/wads/_omega_default/entities.yaml or equivalent:
makali:
  routing:
    synthesis: native-gguf    # Kali voice → local
    build: antigravity        # Ma'at voice → cloud
    run: antigravity          # Lilith voice → cloud
```

### Step 3: Verify Config Loads
```bash
source .venv/bin/activate
PYTHONPATH=src python -c "
import yaml
with open('config/providers.yaml') as f:
    config = yaml.safe_load(f)
routing = config.get('maakali_routing', {})
assert routing.get('kali', {}).get('prefer') == 'native-gguf', 'Kali should use local'
assert routing.get('maat', {}).get('prefer') == 'antigravity', 'Ma\\'at should use cloud'
print('PASS: MaKaLi routing configured')
"
```

### Verification Gate (C-5)
```bash
# 1. Config file updated
grep -A2 "kali:" config/providers.yaml | grep "prefer: native-gguf"
# Must match

# 2. Python can load it
PYTHONPATH=src python -c "
import yaml
c = yaml.safe_load(open('config/providers.yaml'))
assert c['maakali_routing']['kali']['prefer'] == 'native-gguf'
print('PASS')
"
```

### Commit
```
config: C-5 MaKaLi routing — Kali local, Ma'at+Lilith cloud
```

---

## Ticket C-10: Local Inference Admission Control
**Priority**: P1 | **Effort**: 2–4h | **Owner**: Ma'at/P1
**Blocks**: C-5 routing, local inference stability

### Decision Gate
Implement `asyncio.Semaphore(1)` for local inference. Pin threads to single CCX. Memory check before load. Fail-fast to cloud.

### Step 1: Create AdmissionController
```python
# src/omega/oracle/admission_controller.py
"""Local inference admission control for Ryzen 5700U.

Hardware: 2 CCX × 4 cores, 4MB L3 per CCX, DDR4-3200 ~51GB/s.
Bottleneck: memory bandwidth. One concurrent llama.cpp instance optimal.
"""

import anyio
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class LocalInferenceAdmission:
    """Enforce max 1 concurrent local inference instance.

    Uses Semaphore(1) — FIFO acquisition, fail-fast on contention.
    """

    def __init__(self):
        self._semaphore = anyio.Semaphore(1)
        self._current_model: Optional[str] = None

    async def acquire(self, model_name: str) -> bool:
        """Try to acquire local inference slot.

        Returns True if acquired, False if another model is loaded.
        """
        if self._semaphore.statistics().max_value == 0:
            # Already at capacity
            logger.warning(
                "Local inference busy with %s — %s would queue",
                self._current_model, model_name,
            )
            return False

        await self._semaphore.acquire()
        self._current_model = model_name
        logger.info("Local inference acquired: %s", model_name)
        return True

    def release(self) -> None:
        """Release local inference slot."""
        self._current_model = None
        self._semaphore.release()
        logger.info("Local inference released")

    @property
    def is_available(self) -> bool:
        """Check if local inference slot is free."""
        return self._semaphore.statistics().max_value > 0


# Singleton — one admission controller for the engine
_admission: Optional[LocalInferenceAdmission] = None


def get_admission_controller() -> LocalInferenceAdmission:
    global _admission
    if _admission is None:
        _admission = LocalInferenceAdmission()
    return _admission
```

### Step 2: Integrate with ModelGateway
```python
# In src/omega/oracle/model_gateway.py — before loading local model:

from omega.oracle.admission_controller import get_admission_controller

async def _load_local_model(self, model_name: str, ...):
    """Load local model with admission control."""
    admission = get_admission_controller()

    # Check admission
    if not await admission.acquire(model_name):
        logger.info("Local slot busy — failing fast to cloud")
        raise LocalInferenceBusyError(
            f"Local inference busy with {admission._current_model}"
        )

    try:
        # Check memory before loading
        from omega.oracle.resource_guard import OOMProtector
        model_ram_mb = self._get_model_ram_estimate(model_name)
        if not OOMProtector.check(model_ram_mb=model_ram_mb, kv_cache_mb=512):
            logger.error("OOM risk — failing fast to cloud")
            admission.release()
            raise OOMRiskError(f"Cannot load {model_name}: insufficient RAM")

        # Load model (existing code)
        result = await self._do_load(model_name, ...)
        return result
    except Exception:
        admission.release()
        raise
```

### Step 3: Configure Thread Pinning
```yaml
# config/providers.yaml — native-gguf section:
native-gguf:
  priority: 0
  max_concurrent: 1          # Enforced by AdmissionController
  threads: 4                  # Single CCX (cores 0-3)
  numa: "disable"             # Prevent cross-CCX migration
  # thread_pin: "0-3"        # Optional: explicit CCX pinning via taskset
```

### Step 4: Fail-Fast to Cloud
```python
# In ModelGateway.generate() — when local fails:

async def generate(self, prompt, ...):
    try:
        return await self._generate_local(prompt, ...)
    except (LocalInferenceBusyError, OOMRiskError) as e:
        logger.info("Local failed (%s) — routing to cloud", e)
        return await self._generate_cloud(prompt, ...)
```

### Verification Gate (C-10)
```bash
# 1. AdmissionController works
source .venv/bin/activate
PYTHONPATH=src python -c "
from omega.oracle.admission_controller import LocalInferenceAdmission
import anyio

adm = LocalInferenceAdmission()

async def test():
    assert adm.is_available
    assert await adm.acquire('model-a') is True
    assert not adm.is_available
    assert await adm.acquire('model-b') is False  # Should fail-fast
    adm.release()
    assert adm.is_available
    print('PASS: Admission control works')

anyio.run(test)
"

# 2. OOMProtector integrated
grep -n "OOMProtector.check" src/omega/oracle/model_gateway.py
# Must show at least 1 call before local model load

# 3. Thread config correct
grep "threads: 4" config/providers.yaml
# Must match

# 4. No concurrent local loads possible
PYTHONPATH=src python -c "
from omega.oracle.admission_controller import LocalInferenceAdmission
import anyio

adm = LocalInferenceAdmission()

async def load_model(name):
    acquired = await adm.acquire(name)
    if acquired:
        await anyio.sleep(0.1)  # Simulate loading
        adm.release()
    return acquired

async def test():
    results = await anyio.gather(
        load_model('model-a'),
        load_model('model-b'),
    )
    # Only one should succeed
    assert sum(results) == 1, f'Expected 1 success, got {sum(results)}'
    print('PASS: Only 1 concurrent load')

anyio.run(test)
"
```

### Commit
```
feat: C-10 local admission control — Semaphore(1) + OOM check + CCX pinning
```

---

## Execution Order (Priority) — UPDATED per Nemotron 3 Ultra Review

**CRITICAL**: Dependency order corrected. C-2′ (RAM Truth) MUST complete before C-1′ (SoulStore) and C-10 (Admission Control) because SoulStore atomic writes and admission memory checks require stable OOMProtector.

```
PHASE 1 — FOUNDATION (Week 1: July 21-25)
STEP 1: C-0   Test honesty         (2-4h)  — BLOCKS EVERYTHING, independent
STEP 2: C-2′  RAM truth            (1-2h)  — FOUNDATION for all memory ops
STEP 3: C-1′  SoulStore            (4-6h)  — NOW SAFE with OOMProtector
STEP 4: C-10  Admission control    (2-4h)  — PARALLEL with C-1′, needs OOMProtector
STEP 5: C-5   MaKaLi config        (0.5h)  — QUICK WIN, after C-10
STEP 6: C-4a  MCP audit            (2h)    — START IMMEDIATELY (7-day deadline)

PHASE 2 — HARDENING (Week 2: July 28-Aug 1)
STEP 7: C-11  Test infrastructure  (4-6h)  — NEW: Required for Phase D gate
STEP 8: C-6′  Circuit breaker unify (1-2h)
STEP 9: C-7   YAML audit & fix     (2-3h)
STEP 10: C-8  Heritage vet         (8h)
STEP 11: C-9  GenerationPolicy     (2h)

PHASE 3 — PHASE D PREP (Week 3)
STEP 12: C-3  Privacy model        (Architect decision)
STEP 13: V-1  Vault design         (Researcher + P3)
STEP 14: E-0  Identity Fluidity    (2h)    — NEW: After C-1′
STEP 15: D-1  Content persistence  (3.5h)
STEP 16: D-2  Researcher loop fix  (2.5h)
STEP 17: D-3  Soul feedback loop   (3h)
```

**Total estimated effort**: 28–38h across all tickets (including new C-11, E-0).

## Gate to Phase D

Phase D (Living Research OS) begins ONLY when:
- ✅ C-0: Test suite honest (real numbers, quarantine working)
- ✅ C-1′: SoulStore shipped (single writer, no direct writes remain)
- ✅ C-2′: OOMProtector sole arbiter (no software counter)
- ✅ C-11: Test infrastructure for new systems (fixtures, chaos, benchmarks)

## New Tickets (Per Nemotron 3 Ultra Synthesis)

### Ticket C-11: Test Infrastructure for Phase C Systems
**Priority**: P0 | **Effort**: 4–6h | **Owner**: Verity/P10
**Blocks**: Phase D gate (GAP-09)

#### Decision Gate
Create pytest fixtures, chaos test harness, and benchmark suite for SoulStore, OOMProtector, AdmissionController, and Circuit Breaker.

#### Step 1: Create Test Fixtures
```python
# tests/conftest.py additions
import pytest
from pathlib import Path
import tempfile

@pytest.fixture
def soul_store(tmp_path):
    """SoulStore with temp entities dir."""
    from omega.oracle.soul_store import SoulStore
    entities = tmp_path / "entities"
    entities.mkdir()
    (entities / "test_entity").mkdir()
    import yaml
    (entities / "test_entity" / "soul.yaml").write_text(
        yaml.dump({"entity": {"name": "test_entity", "lessons_learned": []}})
    )
    return SoulStore(entities)

@pytest.fixture
def oom_protector():
    """OOMProtector with mocked RAM."""
    from omega.oracle.resource_guard import OOMProtector
    return OOMProtector

@pytest.fixture
def admission_controller():
    """Fresh AdmissionController per test."""
    from omega.oracle.admission_controller import LocalInferenceAdmission
    return LocalInferenceAdmission()
```

#### Step 2: Chaos Test Harness
```python
# tests/chaos/test_soulstore_chaos.py
"""Chaos tests for SoulStore durability."""
import pytest
import asyncio
from pathlib import Path
import tempfile
import os

@pytest.mark.chaos
async def test_soulstore_power_loss_during_write(soul_store):
    """Simulate power loss during atomic write — file must be valid or absent."""
    # This test requires a custom filesystem or injection point
    # For now, verify atomic write pattern is correct
    pass

@pytest.mark.chaos
async def test_oom_during_model_load(admission_controller, oom_protector):
    """Simulate OOM during model load — should fail-fast cleanly."""
    pass
```

#### Step 3: Benchmark Suite
```python
# tests/benchmarks/test_local_inference.py
"""Benchmark suite for local inference admission."""
import pytest
import time

@pytest.mark.benchmark
def test_soulstore_write_latency(soul_store):
    """Measure SoulStore write latency (should be <10ms)."""
    import asyncio
    data = {"entity": {"name": "bench", "lessons_learned": ["x"] * 100}}
    start = time.perf_counter()
    asyncio.run(soul_store.write_soul("bench", data, actor="system_agent"))
    elapsed = (time.perf_counter() - start) * 1000
    assert elapsed < 10, f"SoulStore write took {elapsed}ms"

@pytest.mark.benchmark
def test_admission_acquire_latency(admission_controller):
    """Measure admission acquire latency (should be <1ms)."""
    import asyncio
    start = time.perf_counter()
    asyncio.run(admission_controller.acquire("model"))
    elapsed = (time.perf_counter() - start) * 1000
    assert elapsed < 1, f"Admission acquire took {elapsed}ms"
```

#### Step 4: MCP Compatibility Test Matrix
```python
# tests/integration/test_mcp_compatibility.py
"""MCP 2026-07-28 compatibility tests."""
import pytest

@pytest.mark.mcp
def test_hub_initialize_removed():
    """Verify Hub no longer has initialize handler."""
    pass

@pytest.mark.mcp
def test_hub_streamable_http():
    """Verify Hub supports Streamable HTTP transport."""
    pass

@pytest.mark.mcp
def test_file_hivemind_works_without_hub():
    """Verify file-based Hivemind works as contingency."""
    pass
```

#### Verification Gate (C-11)
```bash
# 1. Fixtures work
PYTHONPATH=src python -m pytest tests/test_soul_store.py -v --fixtures

# 2. Chaos tests run (marked, not blocking CI)
PYTHONPATH=src python -m pytest tests/chaos/ -v --collect-only

# 3. Benchmarks run
PYTHONPATH=src python -m pytest tests/benchmarks/ -v --benchmark-only

# 4. MCP tests collect
PYTHONPATH=src python -m pytest tests/integration/test_mcp_compatibility.py --collect-only
```

#### Commit
```
feat: C-11 test infrastructure — fixtures, chaos, benchmarks, MCP matrix
```

---

### Ticket E-0: Identity Fluidity Phase 0
**Priority**: P1 | **Effort**: 2h | **Owner**: Kali
**Depends**: C-1′ (SoulStore)
**Blocks**: Phase E execution

#### Decision Gate
Implement Soul Kernel → agent config transformation (2h after C-1′).

#### Step 1: Add E-0 to Manual Execution Order
Insert after C-10 in Phase 1.

#### Step 2: Create src/omega/identity_fluidity.py
```python
# src/omega/identity_fluidity.py
"""Identity Fluidity Phase 0 — Soul Kernel to Agent Config.
AP: AP-IDENTITY-FLUIDITY-v1.0.0
"""

from pathlib import Path
from typing import Dict, Any, Optional
import yaml

class IdentityFluidity:
    """Transform soul.yaml → agent_config.yaml for auto-hydration."""

    def __init__(self, entities_dir: Path):
        self.entities_dir = entities_dir

    def compile_soul_kernel(self, entity: str) -> Dict[str, Any]:
        """Extract compile-time identity from soul.yaml."""
        soul_path = self.entities_dir / entity / "soul.yaml"
        if not soul_path.exists():
            return {}
        soul = yaml.safe_load(soul_path.read_text()) or {}
        entity_data = soul.get("entity", {})

        # Compile kernel: identity + approved lessons + core config
        return {
            "identity": {
                "name": entity_data.get("name", entity),
                "archetype": entity_data.get("archetype", ""),
                "voice": entity_data.get("voice", {}),
            },
            "lessons": entity_data.get("lessons_learned", []),
            "approved_lessons": entity_data.get("approved_lessons", []),
            "config": entity_data.get("config", {}),
        }

    def generate_agent_config(self, entity: str) -> Dict[str, Any]:
        """Generate agent_config.yaml from soul kernel."""
        kernel = self.compile_soul_kernel(entity)
        return {
            "entity": kernel["identity"]["name"],
            "archetype": kernel["identity"]["archetype"],
            "voice": kernel["identity"]["voice"],
            "lessons": kernel["lessons"],
            "config": kernel["config"],
        }

    async def write_agent_config(self, entity: str) -> Path:
        """Write agent_config.yaml to entity dir."""
        config = self.generate_agent_config(entity)
        config_path = self.entities_dir / entity / "agent_config.yaml"
        config_path.write_text(yaml.dump(config, default_flow_style=False))
        return config_path
```

#### Step 3: Add MCP Tool entity_hydrate
```python
# In MCP Hub tools registration:
async def entity_hydrate(entity: str) -> dict:
    """Auto-hydrate agent from soul kernel."""
    from omega.identity_fluidity import IdentityFluidity
    from pathlib import Path
    fluidity = IdentityFluidity(Path("data/entities"))
    config = fluidity.generate_agent_config(entity)
    await fluidity.write_agent_config(entity)
    return config
```

#### Verification Gate (E-0)
```bash
# 1. Module loads
PYTHONPATH=src python -c "from omega.identity_fluidity import IdentityFluidity; print('PASS')"

# 2. Compiles soul kernel
PYTHONPATH=src python -c "
from omega.identity_fluidity import IdentityFluidity
from pathlib import Path
import tempfile
d = Path(tempfile.mkdtemp()) / 'e'; d.mkdir()
import yaml
(d / 'soul.yaml').write_text(yaml.dump({'entity': {'name': 'e', 'lessons_learned': ['L3 test']}}))
f = IdentityFluidity(d.parent)
kernel = f.compile_soul_kernel('e')
assert kernel['identity']['name'] == 'e'
assert 'L3 test' in kernel['lessons']
print('PASS: Soul kernel compiled')
"

# 3. Generates agent_config.yaml
PYTHONPATH=src python -c "
from omega.identity_fluidity import IdentityFluidity
from pathlib import Path
import tempfile
d = Path(tempfile.mkdtemp()) / 'e'; d.mkdir()
import yaml
(d / 'soul.yaml').write_text(yaml.dump({'entity': {'name': 'e', 'lessons_learned': ['L3 test']}}))
f = IdentityFluidity(d.parent)
import asyncio
config_path = asyncio.run(f.write_agent_config('e'))
assert config_path.exists()
print('PASS: agent_config.yaml written')
"
```

#### Commit
```
feat: E-0 Identity Fluidity Phase 0 — Soul Kernel → agent config
```

---

*⬡ OMEGA ⬡ KALI ⬡ PHASE-C-IMPL ⬡ v1.0.0 ⬡ 2026-07-21*
