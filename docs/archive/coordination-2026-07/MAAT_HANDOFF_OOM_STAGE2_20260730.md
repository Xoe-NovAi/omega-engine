# 🔱 MA'AT: PHASE 1 STAGE 2 — OOM Refactoring Handoff

**Date**: 2026-07-30  
**For**: Ma'at (P1: Infrastructure)  
**Task**: Resolve Blocker #1 — OOM/PSI/Cgroup refactoring  
**Status**: ⏳ Awaiting Kali decision on refactoring strategy  

---

## Your Mission

The plan to delete `psi_monitor.py`, `memavailable.py`, and `cgroup_pressure.py` will cause system failure because `oom_protector.py` hard-imports them.

**You decide:** Which refactoring option works best for the architecture?

---

## Option A: psutil-Only Approach [RECOMMENDED]

**What:**
- Refactor `oom_protector.py` to use ONLY `psutil.virtual_memory().available`
- Remove PSI/Cgroup signal reading entirely
- Simplifies from kernel-level signals to process-level checks
- Aligns with Mandate 7 (Local-First) — no kernel APIs needed

**Work:**
1. Replace oom_protector.py lines 19-21 imports with: `import psutil`
2. Replace OOMProtector._check_signals() with: `psutil.virtual_memory().available`
3. Remove PSIMonitor, MemAvailableReader, CgroupPressureMonitor instantiation
4. Reduce oom_protector.py from ~350 lines to ~100 lines
5. Rewrite OOM tests in tests/test_resource_guard_oom.py to use psutil assertions
6. Archive old tests for kernel monitors to tests/archive/
7. Delete psi_monitor.py, memavailable.py, cgroup_pressure.py

**Timeline:** 2-3 hours

**Risk:** LOW
- psutil is already a dependency
- psutil.virtual_memory() is stable, well-documented
- OOM logic becomes simpler (less room for bugs)

**Upside:** 
- Removes ~840 lines of kernel-level complexity
- Easier to understand (process-level not kernel-level)
- Reduces test count (old kernel tests archived)

**Downside:**
- Loses fine-grained PSI/Cgroup signals (less precise)
- May miss some edge cases (but psutil is sufficient for single-user desktop app)

**Decision:** ✅ RECOMMENDED — Go with this unless architecture has strong reason for kernel signals

---

## Option B: Consolidate Into oom_protector.py

**What:**
- Move PSI/Cgroup reading logic INTO oom_protector.py itself
- Delete psi_monitor.py, memavailable.py, cgroup_pressure.py but move their code inline
- oom_protector.py becomes self-contained (~500 lines)
- No external imports for OOM monitoring

**Work:**
1. Copy PSI/Cgroup reading functions into oom_protector.py
2. Remove imports of psi_monitor, memavailable, cgroup_pressure
3. Keep all OOM logic in one file
4. Delete three modules (move code, not delete)
5. Tests remain largely unchanged (reading logic is identical)

**Timeline:** 1-2 hours

**Risk:** MEDIUM
- Consolidation is straightforward but adds ~300 lines to oom_protector
- Less modular (everything in one file)

**Upside:**
- Self-contained OOM monitoring
- No external module dependencies
- Tests don't need major rewrite

**Downside:**
- Larger single file (harder to maintain)
- Duplicates code if anyone else needs PSI/Cgroup reading

**Decision:** ⚠️ FALLBACK — Use only if Option A is rejected for architectural reasons

---

## Option C: Delete oom_protector.py Entirely [NOT RECOMMENDED]

**What:**
- Remove oom_protector.py, psi_monitor.py, memavailable.py, cgroup_pressure.py
- resource_guard.py and admission_controller.py call psutil directly
- No abstraction layer

**Work:**
1. Replace oom_protector.py usage in resource_guard.py with direct psutil calls
2. Replace oom_protector.py usage in admission_controller.py with direct psutil calls
3. Delete oom_protector.py and three monitor modules
4. Increase coupling in critical path

**Timeline:** 4-5 hours

**Risk:** HIGH
- Increases coupling in critical admission control path
- Harder to test (no abstraction boundary)
- More code duplication

**Upside:**
- Maximum simplification (delete 4 modules)

**Downside:**
- Fragile critical path
- Makes testing harder
- Harder to evolve OOM strategy later

**Decision:** 🚫 NOT RECOMMENDED — Only if Kali explicitly requires maximum simplification

---

## Decision Gate for Kali

**Ma'at recommendation: OPTION A (psutil-only)**

**Request:** By EOD 2026-07-30, Kali please confirm:
- [ ] Option A (psutil-only) — APPROVED
- [ ] Option B (consolidate) — APPROVED if A rejected
- [ ] Option C (delete abstraction) — Only if explicitly required

Once approved, Ma'at will execute the refactoring and commit by end of day.

---

## Files You'll Touch

```
src/omega/oracle/oom_protector.py (refactor)
src/omega/oracle/psi_monitor.py (delete)
src/omega/oracle/memavailable.py (delete)
src/omega/oracle/cgroup_pressure.py (delete)
src/omega/oracle/resource_guard.py (if needed)
src/omega/oracle/admission_controller.py (if needed)
tests/test_resource_guard_oom.py (rewrite)
tests/property/test_oom_protector_fuse.py (archive or rewrite)
tests/contract/test_oom_protector.py (rewrite)
tests/chaos/test_oom_kill.py (archive or rewrite)
```

---

## Verification Checklist (Before Commit)

- [ ] oom_protector.py imports only psutil (or has consolidated code)
- [ ] All three monitor modules deleted (or consolidated)
- [ ] OOM tests rewritten and passing
- [ ] No ImportError in resource_guard.py or admission_controller.py
- [ ] `make test` runs to completion and passes
- [ ] `make temple-grade` passes
- [ ] Commit message: `refactor(oom): Replace kernel-level monitoring with psutil`

---

⬡ **OMEGA** ⬡ **MA'AT** ⬡ **PHASE_1_STAGE_2** ⬡ **2026-07-30**
