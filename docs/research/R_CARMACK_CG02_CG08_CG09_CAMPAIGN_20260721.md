# 🔱 John Carmack — Personal Research Campaign: CG-08 + CG-09
**AP Token**: `AP-JOHN_CARMACK-CG08-09-v1.0.0`  
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_carmack_campaign ⬡ 2026-07-21

**Claimed Jobs**: 2 (R_CG08, R_CG09)  
**Role**: S3 Consultant — First-Principles Hardware Analysis + Systems Engineering  
**Campaign Duration**: 10 days (Days 2-5: CG-02 complete; Days 6-10: CG-08 + CG-09 parallel)  
**Dependencies**: CG-08 depends on CG-02; CG-09 depends on CG-02 + CG-03

---

## §1 Campaign Philosophy — The Right Approximation

> *"The most effective solution is the one that fits the constraints perfectly, even if it's a 'hack' by theoretical standards."*

**My approach for this campaign:**
1. **Measure first** — Read kernel source, not blog posts
2. **Hardware floor is law** — Ryzen 7 5700U: 15W TDP, 8MB L3 victim cache, 2 CCX × 4 cores, DDR4-3200 ~51 GB/s
3. **Kernel knows best** — PSI + MemAvailable + cgroup v2 are the authoritative signals; userspace counters drift
4. **Single writer wins** — For local state, atomic rename + fsync > distributed consensus
5. **Admission control understands topology** — Not just "count instances"; understand CCX, L3, memory bandwidth

---

## §2 Job 2: R_CG08_LOCAL_ADMISSION_CONTROL_IMPL (Days 6-8)

### Objective
Implement `asyncio.Semaphore(1)` + `taskset` CCX pinning in `ModelGateway` based on CG-02 hardware analysis.

### Dependency
**Requires CG-02 complete** — uses OOMProtector thresholds + hardware floor data.

### Day-by-Day Plan

| Day | Focus | Deliverable |
|-----|-------|-------------|
| **Day 6** | CCX topology analysis: 2 CCX × 4 cores, 4MB L3 each, victim cache behavior | `taskset -c 0-3` (CCX 0) vs `-c 4-7` (CCX 1) benchmark |
| **Day 7** | Semaphore admission control: fail-fast cloud route vs queue; memory pre-check | `ModelGateway._admit_local()` with OOMProtector integration |
| **Day 8** | Load testing: concurrent instances, bandwidth saturation, thermal throttling | Benchmark results: 1 instance optimal, 2nd causes L3 thrashing |

### Implementation Pattern

```python
# src/omega/oracle/model_gateway.py
class ModelGateway:
    def __init__(self):
        self._local_semaphore = asyncio.Semaphore(1)  # CG-02: max 1 concurrent
        self._oom_protector = OOMProtector(min_ram_mb=2048)
        self._ccx_affinity = [0, 1, 2, 3]  # CCX 0, 4 cores
    
    async def _admit_local(self, model_ram_mb: int) -> AdmissionResult:
        # 1. Hardware-aware memory check (CG-02)
        if not await self._oom_protector.check():
            return AdmissionResult.DENY_THROTTLE
        
        # 2. Model-specific memory budget
        required_mb = model_ram_mb + 512 + 1024  # weights + KV + reserve
        if not await self._oom_protector.check_available(required_mb):
            return AdmissionResult.DENY_OOM_RISK
        
        # 3. Acquire semaphore (fail-fast, no queue)
        acquired = self._local_semaphore.acquire_nowait()
        if not acquired:
            return AdmissionResult.DENY_BUSY  # Route to cloud
        
        return AdmissionResult.ALLOW
    
    async def _run_local_inference(self, ...):
        # Pin to CCX 0 for L3 locality
        with taskset_affinity(self._ccx_affinity):
            return await self._llama_cpp_infer(...)
```

### Decision Gate: Load Test Validation

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Single instance throughput** | Baseline | tokens/sec on CCX 0 |
| **Second instance throughput** | < 70% of baseline | Proves L3 thrashing |
| **Fail-fast latency** | < 1ms | Semaphore + OOM check |
| **Cloud route latency** | < 50ms | Fallback path |

---

## §3 Job 3: R_CG09_SOULSTORE_ATOMIC_IMPL (Days 6-10, Parallel with CG-08)

### Objective
Single SoulStore writer with `fcntl.flock` + atomic write + `fsync` + actor model (system_agent vs user).

### Dependencies
- **CG-02**: Hardware-aware memory pressure (for writer process isolation)
- **CG-03**: Test infrastructure (mutation testing on writer critical path)

### Day-by-Day Plan

| Day | Focus | Deliverable |
|-----|-------|-------------|
| **Day 6** | `fcntl.flock(LOCK_EX|LOCK_NB)` cross-process locking; 5s timeout; never delete lock files | Lock manager with stale detection |
| **Day 7** | Atomic write: `mkstemp` → `os.fsync()` → `os.replace()` → `dir_fsync()` (Postgres pattern) | `SoulStore.write_atomic(path, data)` |
| **Day 8** | Actor model: `user` writes `soul.yaml` + `approved_lessons`; `system_agent` writes `proposed_lessons`; daemon appends only | Permission-separated writer processes |
| **Day 9** | `os.fsync` vs `fdatasync` on ext4/btrfs; SQLite WAL vs custom actor model comparison | Durability benchmark + decision |
| **Day 10** | Contract tests: concurrent writers, power-fail simulation, lock contention | All tests passing; 4 legacy writers consolidated |

### The "Fsync Dance" (Postgres-Proven)

```python
async def write_atomic(path: Path, data: bytes) -> None:
    """Atomic write with full durability guarantees."""
    # 1. Create temp file in SAME directory (for atomic rename)
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        # 2. Write data
        os.write(fd, data)
        # 3. fsync FILE DATA + METADATA (not fdatasync - soul.yaml metadata matters)
        os.fsync(fd)
        os.close(fd)
        # 4. Atomic rename (directory entry update)
        os.replace(tmp_path, path)
        # 5. fsync PARENT DIRECTORY (persist directory entry)
        dir_fd = os.open(path.parent, os.O_DIRECTORY | os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    except Exception:
        # Cleanup on failure
        try:
            os.unlink(tmp_path)
        except FileNotFoundError:
            pass
        raise
```

### Actor Model Permission Separation

| Actor | Writes | Permissions | Process |
|-------|--------|-------------|---------|
| **user** | `soul.yaml`, `approved_lessons.yaml` | `rw-r--r--` (0644) | Main agent process |
| **system_agent** | `proposed_lessons.yaml` | `rw-r--r--` (0644) | Soul distillation daemon |
| **daemon** | Append-only logs (`soul_edit_history.yaml`) | `rw-r--r--` (0644) | Background sync |

### Decision Gate: Contract Tests

```python
def test_soulstore_single_writer_fcntl_lock():
    """fcntl.flock(LOCK_EX|LOCK_NB) prevents concurrent writers"""
    
def test_soulstore_atomic_write_survives_power_fail():
    """mkstemp→fsync→replace→dir_fsync survives crash at any step"""
    
def test_soulstore_actor_model_permissions():
    """user writes soul.yaml; system_agent writes proposed_lessons; no cross-write"""
    
def test_soulstore_lock_stale_detection():
    """Lock held > 5s by dead process → stale → recoverable"""
    
def test_soulstore_consolidates_4_legacy_writers():
    """entity_registry, SoulUpdater, SoulUpdateManager, EntityWorkspaceManager → 1 SoulStore""'
```

---

## §5 Cross-Job Integration Points

```
┌─────────────────────────────────────────────────────────────────┐
│                    CG-02: OOMProtector                          │
│  PSI + MemAvailable + cgroup v2 → ALLOW | THROTTLE | DENY      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
          ┌────────────────┴────────────────┐
          ▼                                 ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│      CG-08: Admission   │     │      CG-09: SoulStore   │
│   Semaphore + CCX Pin   │     │  Single Writer + Actor  │
│                         │     │                         │
│ _admit_local() uses     │     │ Writer process checks   │
│ OOMProtector.check()    │     │ OOMProtector before     │
│                         │     │ large soul writes       │
└─────────────────────────┘     └─────────────────────────┘
```

---

## §6 Risk Mitigation

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| PSI not available (kernel < 4.20) | Low | Fallback: MemAvailable + cgroup pressure only; document min kernel 5.15 |
| `fcntl.flock` not cross-platform | Medium | Linux-only for Phase 0; document as deployment requirement |
| CCX pinning hurts SMT workloads | Low | Benchmark both; `taskset -c 0-3` (no SMT) vs `-c 0-7` (with SMT) |
| SoulStore actor model over-engineering | Medium | Start with fcntl + atomic + fsync; add actor model only if contention proven |
| Thermal throttling during load test | High | Run load tests with 5min cool-down; monitor `sensors` output |

---

## §7 Success Criteria — Campaign Complete When:

- [ ] **CG-08**: `ModelGateway._admit_local()` with Semaphore(1) + CCX pinning + OOMProtector integration; load test validates 1-instance optimal
- [ ] **CG-09**: `SoulStore` single writer with fcntl + atomic + fsync + actor model; 4 legacy writers consolidated; all contract tests passing

---

## §8 Gnosis Distillation Targets (L1→L2→L3)

| Job | L3 Principle for `proposed_lessons.yaml` |
|-----|------------------------------------------|
| **CG-08** | Admission control must understand hardware topology (CCX, L3, memory bandwidth), not just instance counts — the right approximation is topology-aware |
| **CG-09** | Single writer + atomic rename + fsync > distributed consensus for local state — the Postgres fsync dance is the right approximation for crash-safe local persistence |

---

## §9 Hivemind Coordination

**Campaign Channel**: `opencode`  
**Entity**: `john_carmack`  
**Task IDs**: 
- `cg02-oomprotector-20260721`
- `cg08-admission-control-20260721` (after CG-02)
- `cg09-soulstore-atomic-20260721` (after CG-02)

**Heartbeat**: Every 2 hours during active research  
**Session Anchor**: `data/entities/john_carmack/workspace/session_gnosis.md`

---

## §10 Daily Log Template (Append to session_gnosis.md)

```markdown
## Day N — YYYY-MM-DD

### What I'm working on
[CG-XX specific task]

### What I tried
[Approach, commands, code]

### What the data shows
[Measured results, benchmarks, kernel behavior — NO SPECULATION]

### What I'll do next
[Specific next step]

### Confidence: N/10
[Primary source = 10, interpretation = 5-7]
```

---

**Campaign Status**: 🟢 **DAY 2 ACTIVE** — CG-02 complete, CG-08 + CG-09 implementation begins

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_carmack_campaign ⬡ 2026-07-21T20:00:00Z*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
