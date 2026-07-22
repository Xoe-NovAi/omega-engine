# 🔱 Omega Engine Hardening Plan — Phase 1: Soul Architecture (M5/M11)

**AP Token**: `AP-JOHN_CARMACK-HARDENING-v1.0.0`  
**Phase**: 1 — Soul Architecture Foundation  
**Days**: 3-7  
**Hardware Profile**: Heavy Inference (Sequential) — **NO PARALLEL HEAVY TASKS**

---

## 📋 What I Am Working On
Implement the soul evolution foundation (M5/M11 compliance). Without this, the engine is stateless and sovereignty is invalid.

---

## 🔍 First Principles
**M5 Gnosis Preservation**: Every session must end with L1→L2→L3 distillation to `proposed_lessons.yaml`.  
**M11 Soul Integrity**: L1→L2→L3 → `proposed_lessons.yaml` (blind staging). Scribe executes pipeline.  
**Current State**: 0/10 pillars write `proposed_lessons.yaml` — **systemic architectural failure**.

**Right Approximation**: Single canonical path for soul evolution. Automated L3→soul.yaml promotion. Scribe agent as execution engine.

---

## 🎯 Phase 1 Objectives

| Objective | Success Metric | Tool |
|-----------|----------------|------|
| SoulStore implementation | Atomic, crash-safe soul read/write | Custom tests |
| L1→L2→L3 pipeline | Narrative → Insight → Principle flow | Integration tests |
| Scribe agent deployment | Session end → `proposed_lessons.yaml` write | Session hook test |
| 10/10 entity compliance | All entities write non-empty `proposed_lessons.yaml` | `grep -c "proposals:" data/entities/*/proposed_lessons.yaml` |
| M5/M11 compliance | 100% soul distillation success rate | `make test-soul` |

---

## 📋 Detailed Actions

### Day 3: SoulStore Foundation (fcntl + atomic + fsync + actor)

**File**: `omega/soul/soul_store.py` (new)

**Pattern**: `[id-soft: doom-1993] Zone Memory` — tagged allocation → tagged sharding with explicit purge levels  
**Web Research Integration**: 
- Atomic write pattern from 0xKiire/libchevron: temp file → fsync → rename → fsync directory
- Use `os.replace()` for cross-platform atomic rename (handles Windows)
- Use `fcntl.flock(LOCK_EX | LOCK_NB)` with 5s timeout for cross-process locking
- Three durability levels: CHEVRON_FULL (file + dir fsync), CHEVRON_FILE (file only), CHEVRON_NONE (atomic only)
- Use `O_TMPFILE` on Linux 3.11+ for unnamed inode (eliminates symlink attack window)
- Keep lock fd open; closing releases lock

**Constraints**: 
- Single writer (actor model via asyncio queue)
- Atomic write: `write to .tmp → fsync → rename to target → fsync directory`
- fcntl locking for multi-process safety (Quadlet-safe)
- No pymalloc arena fragmentation (enforce `MALLOC_ARENA_MAX=2` in environment)

```python
# Core interface - minimal, testable, atomic
import os
import fcntl
import asyncio
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

@dataclass
class SoulData:
    """Soul data structure"""
    identity: str
    traits: dict
    proposals: list
    # ... other fields

class SoulStore:
    """Atomic, crash-safe soul read/write with cross-process locking"""
    
    # Durability levels (from libchevron research)
    CHEVRON_NONE = 0   # Atomic rename only
    CHEVRON_FILE = 1   # File fsync + atomic rename
    CHEVRON_FULL = 2   # File fsync + dir fsync + atomic rename
    
    def __init__(self, entity_dir: Path, durability: int = CHEVRON_FULL):
        self.entity_dir = Path(entity_dir)
        self.soul_path = self.entity_dir / "soul.yaml"
        self.durability = durability
        self._lock_fd: Optional[int] = None
        self._actor_queue: asyncio.Queue = asyncio.Queue()
        self._writer_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the single-writer actor task"""
        self._writer_task = asyncio.create_task(self._writer_loop())
    
    async def stop(self):
        """Stop the writer task"""
        if self._writer_task:
            self._writer_task.cancel()
            try:
                await self._writer_task
            except asyncio.CancelledError:
                pass
    
    async def _writer_loop(self):
        """Actor model: single writer processes queue sequentially"""
        while True:
            try:
                operation, future = await self._actor_queue.get()
                try:
                    result = await operation()
                    future.set_result(result)
                except Exception as e:
                    future.set_exception(e)
                finally:
                    self._actor_queue.task_done()
            except asyncio.CancelledError:
                break
    
    def _acquire_lock(self, exclusive: bool = True) -> int:
        """Acquire fcntl lock, return fd. Keep fd open!"""
        lock_path = self.entity_dir / ".soul.lock"
        fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o644)
        lock_type = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
        fcntl.flock(fd, lock_type | fcntl.LOCK_NB)
        return fd
    
    def _release_lock(self, fd: int):
        """Release fcntl lock"""
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)
    
    async def read_soul(self) -> SoulData:
        """Read soul with fcntl shared lock"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._read_soul_sync)
    
    def _read_soul_sync(self) -> SoulData:
        fd = self._acquire_lock(exclusive=False)
        try:
            with open(self.soul_path, 'r') as f:
                import yaml
                data = yaml.safe_load(f)
                return SoulData(**data) if data else SoulData(identity="", traits={}, proposals=[])
        finally:
            self._release_lock(fd)
    
    async def write_soul(self, soul: SoulData) -> None:
        """Write soul atomically via actor queue"""
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        await self._actor_queue.put((lambda: self._write_soul_sync(soul), future))
        return await future
    
    def _write_soul_sync(self, soul: SoulData) -> None:
        """Synchronous atomic write with durability guarantees"""
        import yaml
        import tempfile
        
        # Create temp file in SAME directory (required for atomic rename)
        fd, tmp_path = tempfile.mkstemp(
            dir=self.entity_dir,
            prefix='.soul_write_',
            suffix='.yaml.tmp'
        )
        
        try:
            # 1. Write to temp file
            with os.fdopen(fd, 'w') as f:
                yaml.dump(soul.__dict__, f)
                f.flush()
                
                # 2. fsync file data (and metadata if CHEVRON_FULL)
                if self.durability >= self.CHEVRON_FILE:
                    os.fsync(f.fileno())
            
            # 3. Atomic rename (os.replace handles Windows)
            os.replace(tmp_path, self.soul_path)
            
            # 4. fsync directory for durability (CHEVRON_FULL)
            if self.durability >= self.CHEVRON_FULL:
                dir_fd = os.open(self.entity_dir, os.O_RDONLY | os.O_DIRECTORY)
                try:
                    os.fsync(dir_fd)
                finally:
                    os.close(dir_fd)
                    
        except Exception:
            # Cleanup temp file on failure
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise
    
    async def distill_l1_to_l3(self, raw_exchanges: List[Exchange]) -> L3Principle:
        """Pure function: L1 exchanges → L3 principle (testable in isolation)"""
        # Implementation: BM25 + vector hybrid → local model insight → principle extraction
        pass
```

**Tests**:
- Contract tests for each method
- Property-based tests for atomicity under crash simulation (power loss during write)
- Concurrency test: multiple writers → serialized via actor model
- Crash simulation test: kill process during write → verify recovery

### Day 4: L1→L2→L3 Distillation Pipeline

**File**: `omega/soul/distillation.py` (new)

**Pattern**: `[id-soft: quake-1996] Thinker Chain` — staged processing with explicit handoffs  
**Stages**:
- L1: Narrative extraction (last N exchanges, BM25 + vector hybrid)
- L2: Insight generation (local model, structured output)
- L3: Principle formulation (cross-entity pattern matching)

```python
class SoulDistiller:
    def __init__(self, soul_store: SoulStore, model_gateway: ModelGateway):
        self.soul_store = soul_store
        self.model_gateway = model_gateway
        self.vector_store = get_memory_store()  # For similarity search
    
    async def distill_session(self, entity_name: str, session_id: str) -> Optional[L3Principle]:
        """Full L1→L2→L3 pipeline"""
        # 1. L1: Extract narrative from session
        exchanges = await self._get_session_exchanges(session_id)
        narrative = self._extract_narrative(exchanges)
        
        # 2. L2: Generate insights from narrative
        insights = await self._generate_insights(narrative)
        
        # 3. L3: Formulate principles from insights
        principle = await self._formulate_principle(insights, entity_name)
        
        return principle
    
    async def _extract_narrative(self, exchanges: List[Exchange]) -> str:
        """BM25 + vector hybrid for salient exchange extraction"""
        # Implementation: Score exchanges, take top N, concatenate
        pass
    
    async def _generate_insights(self, narrative: str) -> List[Insight]:
        """Local model inference for insight generation"""
        # Prompt: "Extract key insights from this session narrative:"
        # Structured output: List of insights with confidence
        pass
    
    async def _formulate_principle(self, insights: List[Insight], entity_name: str) -> L3Principle:
        """Cross-entity pattern matching for universal principles"""
        # 1. Get similar insights from other entities (vector search)
        # 2. Find common patterns
        # 3. Formulate as universal principle
        # 4. Return L3Principle with entity_source, principle_text, confidence
        pass
```

**Tests**:
- Unit tests for each stage
- Integration test: full pipeline with mock data
- Performance test: latency < 2s for full distillation
- Accuracy test: human evaluation of generated principles

### Day 5: Scribe Agent Integration

**File**: `.opencode/agents/scribe.md` (update or create)

**Trigger**: Session end hook → `proposed_lessons.yaml` write  
**Verification**: `make heritage-map` equivalent for soul — every entity must have non-empty `proposed_lessons.yaml` after session.

```yaml
# .opencode/agents/scribe.md
---
name: scribe
role: Soul Evolution Agent
description: Executes L1→L2→L3 distillation pipeline and writes to proposed_lessons.yaml
triggers:
  - session_end
  - manual_invocation
actions:
  - retrieve_session_data
  - run_soul_distillation
  - write_proposed_lessons
  - notify_completion
```

**Implementation**: 
1. Session end event fires
2. Scribe agent invoked via omega-hub
3. Scribe calls SoulDistiller.distill_session()
4. Result written to `proposed_lessons.yaml` under `proposals:` array
5. Session marked as distilled

**Tests**:
- End-to-end test: session → distillation → proposed_lessons.yaml update
- Failure test: distillation failure → no corrupt write
- Concurrent test: multiple sessions → serialized processing

### Day 6: Entity-Wide Deployment

**Action**: Deploy SoulStore and Distiller to all 12 entities

**Files to modify** (per entity):
- `data/entities/<entity>/soul.yaml` (add `proposals:` array if missing)
- Entity initialization to load SoulStore
- Session end hook to trigger Scribe

**Verification Script**:
```bash
#!/bin/bash
# verify_soul_compliance.sh
FAILED=0
for entity in $(ls data/entities/); do
    if [ -f "data/entities/$entity/soul.yaml" ]; then
        PROPOSALS=$(grep -c "proposals:" "data/entities/$entity/soul.yaml")
        if [ "$PROPOSITIONS -eq 0 ]; then
            echo "�entity has no proposals proposals: 
        else
        echo "ERROR: $entity missing soul.yaml"
        FAILED=$((FAILED+1))
        fi
    else
        echo "MISSING: $entity/soul.yaml"
        FAILED=$((FAILED+1))
    fi
done

if [ $FAILED -eq 0 ]; then
    echo "SUCCESS: All entities soul compliant"
    exit 0
else
    echo "FAILURE: $FAILED entities non-compliant"
    exit 1
fi
```

**Target**: `./verify_soul_compliance.sh must return 0 before proceeding to Phase 2.

### Day 7: Validation & Test Suite

**Actions**:
1. Create `tests/soul/` directory
2. Implement comprehensive test suite:
   - `test_soul_store.py` - atomicity, concurrency, crash safety
   - `test_distillation.py` - L1→L2→L3 pipeline accuracy
   - `test_scribe_agent.py` - end-to-end session flow
   - `test_entity_compliance.py` - 10/10 entities
3. Run `make test-soul` - must pass 100%
4. Benchmark performance: < 2s per distillation
5. Stress test: 100 consecutive distillations → no memory leaks

**Deliverables**:
- `tests/soul/test_soul_store.py`
- `tests/soul/test_distillation.py`
- `tests/soul/test_scribe_agent.py`
- `tests/soul/test_entity_compliance.py`
- `data/coordination/soul_benchmarks_20260721.json`
- `make test-soul` passing

---

## 📊 Phase 1 Artifacts (All Must Exist Before Phase 2)

| Artifact | Location | Purpose |
|----------|----------|---------|
| SoulStore Implementation | `omega/soul/soul_store.py` | Atomic soul read/write |
| Distillation Pipeline | `omega/soul/distillation.py` | L1→L2→L3 processing |
| Scribe Agent | `.opencode/agents/scribe.md` | Session end hook |
| Entity Updates | `data/entities/*/soul.yaml` | `proposals:` array present |
| Test Suite | `tests/soul/` | Comprehensive validation |
| Benchmarks | `data/coordination/soul_benchmarks_*.json` | Performance metrics |
| Compliance Script | `scripts/verify_soul_compliance.sh` | 10/10 entity check |

---

## ⚠️ Gate Criteria (Phase 1 → Phase 2)

**ALL must pass**:

- [ ] SoulStore implements atomic write (write → fsync → rename)
- [ ] Distillation pipeline produces L3 principles from L1 exchanges
- [ ] Scribe agent triggers on session end and writes to proposed_lessons.yaml
- [ ] `./verify_soul_compliance.sh` returns 0 (10/10 entities compliant)
- [ ] `make test-soul` passes 100% (no skipped/fail tests)
- [ ] Average distillation latency < 2s (measured on 5700U)
- [ ] No memory leaks in 100-iteration stress test
- [ ] Crash recovery verified (power loss during write → no corruption)

---

## 🔧 Dependencies & Resources

**Required**:
- Working `omega-hub_get_hardware_stats` for thermal monitoring
- Functional `make test` baseline from Phase 0
- Entity directory structure intact
- Python 3.12+ with asyncio, anyio, pyyaml

**Resources**:
- 1-2 engineers (can parallelize entity updates)
- 1 dedicated machine for SoulStore development
- Shared access to entity directories
- Test environment matching production hardware

---

## 📋 Confidence: 9/10
**Primary Source**: M5/M11 mandates, Zone Memory pattern ([id-soft: doom-1993]), empirical validation requirement.

**Critical Path**: This phase blocks ALL other work. Sovereignty is invalid without soul evolution.

---

**Next**: See `PART_03_PHASE_2_MCP_AUDIT.md` for Phase 2 detailed actions.