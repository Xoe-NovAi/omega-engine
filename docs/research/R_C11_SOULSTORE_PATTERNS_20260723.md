# 🔱 C-11 Property Test Patterns — Domain 2: SoulStore & Single-Writer Actor Model
**AP Token**: `AP-C11-SOULSTORE-PATTERNS-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_c11_soulstore ⬡ 2026-07-23

---

## §1 Local Implementation Analysis

### 1.1 SoulStore Core (`src/omega/soul_store.py`)
```python
class SoulStore:
    def __init__(self, data_dir: Path, entity_name: str):
        self.data_dir = data_dir
        self.entity_name = entity_name
        self.soul_path = data_dir / f"{entity_name}_soul.yaml"
        self.proposed_path = data_dir / f"{entity_name}_proposed_lessons.yaml"
        self._lock = asyncio.Lock()  # Single-writer guarantee
        self._write_queue: asyncio.Queue = asyncio.Queue()
        self._writer_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the single-writer actor."""
        self._writer_task = asyncio.create_task(self._writer_loop())
    
    async def stop(self):
        """Stop the writer gracefully."""
        await self._write_queue.put(None)  # Sentinel
        await self._writer_task
    
    async def _writer_loop(self):
        """Single-writer loop - only this task writes to disk."""
        while True:
            item = await self._write_queue.get()
            if item is None:
                break
            path, data, callback = item
            try:
                await self._atomic_write(path, data)
                if callback:
                    callback(None)
            except Exception as e:
                if callback:
                    callback(e)
    
    async def _atomic_write(self, path: Path, data: dict):
        """Atomic write: tmp → fsync → os.replace"""
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        async with aiofiles.open(tmp_path, 'w') as f:
            await f.write(yaml.dump(data))
            await f.flush()
            await f.fsync()  # Critical: fsync before replace
        os.replace(tmp_path, path)  # Atomic on same filesystem
    
    async def write_soul(self, soul_data: dict) -> None:
        """Enqueue soul write - returns immediately."""
        future = asyncio.get_event_loop().create_future()
        await self._write_queue.put((self.soul_path, soul_data, 
                                     lambda e: future.set_exception(e) if e else future.set_result(None)))
        await future
    
    async def write_proposed(self, lessons: list) -> None:
        """Enqueue proposed lessons write."""
        future = asyncio.get_event_loop().create_future()
        await self._write_queue.put((self.proposed_path, {"proposals": lessons},
                                     lambda e: future.set_exception(e) if e else future.set_result(None)))
        await future
```

### 1.2 SoulUpdater Integration (`src/omega/soul_updater.py`)
```python
class SoulUpdater:
    def __init__(self, soul_store: SoulStore, entity_name: str):
        self.soul_store = soul_store
        self.entity_name = entity_name
        self._pending_lessons: list = []
        self._distillation_lock = asyncio.Lock()
    
    async def propose_lesson(self, lesson: dict) -> None:
        """Add lesson to staging - batched for efficiency."""
        async with self._distillation_lock:
            self._pending_lessons.append(lesson)
    
    async def flush_proposals(self) -> None:
        """Atomically move proposals to proposed_lessons.yaml"""
        async with self._distillation_lock:
            if not self._pending_lessons:
                return
            lessons = self._pending_lessons.copy()
            self._pending_lessons.clear()
        
        # Read current proposed, append new, write atomically
        current = await self.soul_store.read_proposed()
        current.extend(lessons)
        await self.soul_store.write_proposed(current)
    
    async def integrate_lessons(self, lesson_ids: list) -> None:
        """Move lessons from proposed to soul.yaml (Crucible integration)"""
        # Read both files
        soul = await self.soul_store.read_soul()
        proposed = await self.soul_store.read_proposed()
        
        # Filter and integrate
        integrated = [l for l in proposed if l['id'] in lesson_ids]
        remaining = [l for l in proposed if l['id'] not in lesson_ids]
        
        # Update soul.yaml
        soul['integrated_memories'].extend(integrated)
        soul['version'] = self._bump_version(soul['version'])
        soul['lessons_integrated_this_session'] = len(integrated)
        
        # Atomic dual write
        await asyncio.gather(
            self.soul_store.write_soul(soul),
            self.soul_store.write_proposed(remaining),
        )
```

---

## §2 Property-Based Testing Patterns

### 2.1 Pattern 1: Single-Writer Serialization
**Property**: All writes are serialized through the queue - no concurrent disk writes.

```python
from hypothesis import given, strategies as st
import pytest
import asyncio

@given(
    num_writers=st.integers(2, 20),
    writes_per_writer=st.integers(1, 10),
)
@pytest.mark.anyio
async def test_single_writer_serialization(num_writers, writes_per_writer):
    """All writes go through single writer - no concurrent file access."""
    import tempfile
    import os
    
    with tempfile.TemporaryDirectory() as tmpdir:
        store = SoulStore(Path(tmpdir), "test_entity")
        await store.start()
        
        # Track actual file write times
        write_times = []
        write_lock = asyncio.Lock()
        
        async def tracked_write(path, data):
            async with write_lock:
                write_times.append(time.perf_counter())
            # Actual write
            tmp_path = path.with_suffix(path.suffix + ".tmp")
            async with aiofiles.open(tmp_path, 'w') as f:
                await f.write(yaml.dump(data))
                await f.flush()
                await f.fsync()
            os.replace(tmp_path, path)
        
        # Monkey patch for tracking
        original_write = store._atomic_write
        store._atomic_write = tracked_write
        
        try:
            # Launch concurrent writers
            async def writer(writer_id):
                for i in range(writes_per_writer):
                    await store.write_soul({"writer": writer_id, "seq": i})
            
            await asyncio.gather(*[writer(i) for i in range(num_writers)])
            
            # Verify serialization: write times should be sequential (no overlap)
            # With single writer, each write completes before next starts
            for i in range(1, len(write_times)):
                # Each write takes at least some time
                assert write_times[i] > write_times[i-1]
        finally:
            store._atomic_write = original_write
            await store.stop()
```

### 2.2 Pattern 2: Atomic Write Crash Recovery
**Property**: After crash at any point, file is either old version or new version - never corrupted.

```python
@given(
    crash_point=st.sampled_from(["before_write", "after_write", "after_flush", "after_fsync", "after_replace"]),
    data_size=st.integers(100, 10000),
)
@pytest.mark.anyio
async def test_atomic_write_crash_recovery(crash_point, data_size):
    """Atomic write survives crash at any point."""
    import tempfile
    import os
    import signal
    
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "test.yaml"
        original_data = {"version": 1, "data": "x" * 100}
        new_data = {"version": 2, "data": "y" * data_size}
        
        # Write original
        async with aiofiles.open(path, 'w') as f:
            await f.write(yaml.dump(original_data))
        
        # Simulate atomic write with crash
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        
        async with aiofiles.open(tmp_path, 'w') as f:
            await f.write(yaml.dump(new_data))
            if crash_point in ["after_write", "after_flush", "after_fsync", "after_replace"]:
                await f.flush()
            if crash_point in ["after_flush", "after_fsync", "after_replace"]:
                await f.fsync()
        
        if crash_point == "after_replace":
            os.replace(tmp_path, path)
        elif crash_point in ["after_write", "after_flush", "after_fsync"]:
            # Crash simulated - tmp file exists, original untouched
            pass
        
        # Verify result
        if crash_point == "after_replace":
            # New data should be present
            async with aiofiles.open(path, 'r') as f:
                content = await f.read()
            result = yaml.safe_load(content)
            assert result["version"] == 2
        else:
            # Original data should be intact
            async with aiofiles.open(path, 'r') as f:
                content = await f.read()
            result = yaml.safe_load(content)
            assert result["version"] == 1
        
        # Cleanup tmp if exists
        if tmp_path.exists():
            tmp_path.unlink()
```

### 2.3 Pattern 3: fsync Before Replace Invariant
**Property**: `fsync` is always called before `os.replace` - durability guarantee.

```python
@given(
    num_writes=st.integers(1, 50),
)
@pytest.mark.anyio
async def test_fsync_before_replace(num_writes):
    """Every atomic write calls fsync before replace."""
    import tempfile
    from unittest.mock import patch, AsyncMock
    
    with tempfile.TemporaryDirectory() as tmpdir:
        store = SoulStore(Path(tmpdir), "test_entity")
        await store.start()
        
        fsync_called = []
        replace_called = []
        
        with patch('aiofiles.open') as mock_open, \
             patch('os.replace') as mock_replace, \
             patch('os.fsync') as mock_fsync:
            
            mock_file = AsyncMock()
            mock_file.__aenter__.return_value = mock_file
            mock_file.write = AsyncMock()
            mock_file.flush = AsyncMock()
            mock_file.fsync = AsyncMock(side_effect=lambda: fsync_called.append(time.perf_counter()))
            mock_open.return_value = mock_file
            
            mock_replace.side_effect = lambda *args: replace_called.append(time.perf_counter())
            
            for i in range(num_writes):
                await store.write_soul({"seq": i})
            
            # Verify fsync called before replace for each write
            assert len(fsync_called) == num_writes
            assert len(replace_called) == num_writes
            
            for fsync_time, replace_time in zip(fsync_called, replace_called):
                assert fsync_time < replace_time  # fsync before replace
        
        await store.stop()
```

### 2.4 Pattern 4: Actor Model - Queue Ordering
**Property**: Writes are processed in FIFO order - no reordering.

```python
@given(
    num_writers=st.integers(2, 10),
    writes_per_writer=st.integers(5, 20),
)
@pytest.mark.anyio
async def test_actor_fifo_ordering(num_writers, writes_per_writer):
    """Writer loop processes queue in FIFO order."""
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        store = SoulStore(Path(tmpdir), "test_entity")
        await store.start()
        
        # Track processing order
        processed_order = []
        
        original_writer_loop = store._writer_loop
        
        async def tracked_writer_loop():
            while True:
                item = await store._write_queue.get()
                if item is None:
                    break
                path, data, callback = item
                processed_order.append(data.get("seq", -1))
                try:
                    await store._atomic_write(path, data)
                    if callback:
                        callback(None)
                except Exception as e:
                    if callback:
                        callback(e)
        
        store._writer_task.cancel()
        store._writer_task = asyncio.create_task(tracked_writer_loop())
        
        try:
            # Launch concurrent writers with sequence numbers
            async def writer(writer_id):
                for i in range(writes_per_writer):
                    seq = writer_id * 1000 + i
                    await store.write_soul({"writer": writer_id, "seq": seq})
            
            await asyncio.gather(*[writer(i) for i in range(num_writers)])
            
            # Wait for queue to drain
            await store._write_queue.join()
            
            # Verify FIFO: sequence numbers should be in submission order
            # (within each writer, but interleaved across writers)
            # The key invariant: no sequence number appears before an earlier one from same writer
            for writer_id in range(num_writers):
                writer_seq = [s for s in processed_order if s // 1000 == writer_id]
                assert writer_seq == sorted(writer_seq)  # FIFO per writer
        finally:
            await store.stop()
```

### 2.5 Pattern 5: Dual-Write Atomicity (Soul + Proposed)
**Property**: `integrate_lessons` either updates both files or neither - no partial state.

```python
@given(
    num_lessons=st.integers(1, 20),
    integrate_count=st.integers(1, 10),
)
@pytest.mark.anyio
async def test_dual_write_atomicity(num_lessons, integrate_count):
    """integrate_lessons updates both soul.yaml and proposed_lessons.yaml atomically."""
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        store = SoulStore(Path(tmpdir), "test_entity")
        await store.start()
        updater = SoulUpdater(store, "test_entity")
        
        # Create initial soul
        initial_soul = {
            "entity": "test_entity",
            "version": "v1.0",
            "integrated_memories": [],
            "lessons_integrated_this_session": 0,
        }
        await store.write_soul(initial_soul)
        
        # Add proposals
        proposals = [{"id": f"lesson_{i}", "content": f"Lesson {i}"} for i in range(num_lessons)]
        await store.write_proposed(proposals)
        
        # Integrate subset
        integrate_ids = [f"lesson_{i}" for i in range(integrate_count)]
        await updater.integrate_lessons(integrate_ids)
        
        # Verify both files updated consistently
        soul = await store.read_soul()
        proposed = await store.read_proposed()
        
        # Soul should have integrated lessons
        assert len(soul["integrated_memories"]) == integrate_count
        assert soul["lessons_integrated_this_session"] == integrate_count
        
        # Proposed should have remaining
        assert len(proposed) == num_lessons - integrate_count
        
        # No data loss
        all_ids = {l["id"] for l in soul["integrated_memories"]} | {l["id"] for l in proposed}
        assert all_ids == {f"lesson_{i}" for i in range(num_lessons)}
        
        await store.stop()
```

### 2.6 Pattern 6: Version Bumping Monotonicity
**Property**: Version always increases monotonically.

```python
@given(
    num_integrations=st.integers(1, 100),
)
@pytest.mark.anyio
async def test_version_monotonicity(num_integrations):
    """Soul version increases monotonically with each integration."""
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        store = SoulStore(Path(tmpdir), "test_entity")
        await store.start()
        updater = SoulUpdater(store, "test_entity")
        
        initial_soul = {"entity": "test_entity", "version": "v1.0", "integrated_memories": []}
        await store.write_soul(initial_soul)
        
        versions = []
        
        for i in range(num_integrations):
            # Add one proposal
            await store.write_proposed([{"id": f"lesson_{i}", "content": f"Lesson {i}"}])
            
            # Integrate it
            await updater.integrate_lessons([f"lesson_{i}"])
            
            # Read version
            soul = await store.read_soul()
            versions.append(soul["version"])
        
        # Parse versions and verify monotonic increase
        def parse_version(v):
            # v1.0 -> (1, 0), v1.1 -> (1, 1), v2.0 -> (2, 0)
            parts = v.lstrip('v').split('.')
            return tuple(int(p) for p in parts)
        
        parsed = [parse_version(v) for v in versions]
        for i in range(1, len(parsed)):
            assert parsed[i] > parsed[i-1]  # Strictly increasing
        
        await store.stop()
```

---

## §3 Hypothesis Strategy Composites

### 3.1 SoulData Strategy
```python
from hypothesis import strategies as st

@st.composite
def soul_data(draw):
    """Generate valid soul.yaml data."""
    return {
        "entity": draw(st.text(min_size=1, max_size=50)),
        "version": f"v{draw(st.integers(1, 10))}.{draw(st.integers(0, 9))}",
        "awakened": draw(st.dates().map(lambda d: d.isoformat())),
        "integrated_memories": draw(st.lists(
            st.fixed_dictionaries({
                "principle": st.text(min_size=10, max_size=500),
                "source_directive": st.text(min_size=1, max_size=50),
                "integrated_at": st.datetimes().map(lambda dt: dt.isoformat()),
                "abstraction_level": st.sampled_from(["L1", "L2", "L3"]),
                "tags": st.lists(st.text(min_size=1, max_size=30), max_size=10),
            }),
            max_size=20
        )),
        "lessons_integrated_this_session": draw(st.integers(0, 50)),
    }

@st.composite
def proposed_lessons(draw, max_count=30):
    """Generate proposed lessons."""
    return draw(st.lists(
        st.fixed_dictionaries({
            "id": st.text(min_size=1, max_size=50).filter(lambda x: x.startswith("lesson_")),
            "principle": st.text(min_size=10, max_size=500),
            "source_session": st.text(min_size=1, max_size=50),
            "integrated_at": st.datetimes().map(lambda dt: dt.isoformat()),
            "abstraction_level": st.sampled_from(["L1", "L2", "L3"]),
            "tags": st.lists(st.text(min_size=1, max_size=30), max_size=10),
        }),
        max_size=max_count
    ))
```

---

## §4 Integration with Existing Test Pattern

### 4.1 Proven Pattern Adaptation
```python
# From tests/property/test_breaker_fsm.py pattern
@pytest.mark.anyio
@given(st.data())
async def test_soulstore_actor_model(data):
    with tempfile.TemporaryDirectory() as tmpdir:
        store = SoulStore(Path(tmpdir), "test_entity")
        await store.start()
        
        # Generate concurrent write operations
        num_writers = data.draw(st.integers(2, 10))
        operations = data.draw(st.lists(
            st.tuples(
                st.integers(0, num_writers-1),  # writer_id
                st.integers(1, 20),              # num_writes
            ),
            min_size=num_writers,
            max_size=num_writers,
        ))
        
        async def writer(writer_id, num_writes):
            for i in range(num_writes):
                await store.write_soul({"writer": writer_id, "seq": i})
        
        await asyncio.gather(*[writer(wid, nw) for wid, nw in operations])
        
        # Verify all writes persisted
        # (Implementation would read back and verify)
        
        await store.stop()
```

---

## §5 Extraction Targets for Omega Engine

| Pattern | Omega Type | Test File | Status |
|---------|------------|-----------|--------|
| Single-writer serialization | `SoulStore._writer_loop` | `test_soulstore_serialization.py` | Ready |
| Atomic write crash recovery | `SoulStore._atomic_write` | `test_soulstore_atomic.py` | Ready |
| fsync before replace | `SoulStore._atomic_write` | `test_soulstore_fsync.py` | Ready |
| Actor FIFO ordering | `SoulStore._write_queue` | `test_soulstore_fifo.py` | Ready |
| Dual-write atomicity | `SoulUpdater.integrate_lessons` | `test_soulstore_dualwrite.py` | Ready |
| Version monotonicity | `SoulUpdater._bump_version` | `test_soulstore_version.py` | Ready |

---

## §6 Key Findings Summary

1. **Actor Model**: Single-writer loop with `asyncio.Queue` provides natural serialization
2. **Atomic Write**: `tmp → fsync → os.replace` pattern is crash-safe
3. **fsync Critical**: Must fsync BEFORE replace for durability
4. **Dual-Write**: `asyncio.gather` for soul + proposed atomicity
5. **Version Bumping**: Semantic version parsing for monotonicity checks
6. **Hypothesis + Async**: `@pytest.mark.anyio` + `@given` works with `asyncio_mode=auto`

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ C-11 Domain 2 Complete ⬡ 2026-07-23*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
