<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# John Carmack Session Gnosis — 2026-07-21 (Day 1-2 Campaign)

## 🔬 Campaign Overview

```
R_CG02 OOMProtector  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  100%  DONE
R_CG08 Admission     ▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   10%  BLOCKED
R_CG09 SoulStore     ▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   10%  BLOCKED
                     0%        25%        50%        75%   100%
```

## ✅ Day 1 — Research Complete

| Research Doc | Lines | Depth | Status |
|:-------------|:------|:------|:-------|
| `R_CG02_OOMPROTECTOR_HARDWARE_AWARE.md` | 430 | Kernel sources (PSI, MemAvailable, OOM, cgroup) | ✅ |
| `R_CG03_TEST_INFRASTRUCTURE_STACK.md` | 631 | 4-gate CI (pytest-benchmark, ordeal, mutmut, pact) | ✅ |
| `R_CARMACK_CG02_CG08_CG09_CAMPAIGN_20260721.md` | 15KB | 10-day plan, decision gates, L3 targets | ✅ |

**Knowledge gaps closed**: 15 across both research docs (10/10 confidence on all kernel sources)

## ✅ Day 2 — Implementation Complete

### Module Health  13/13  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  PASS

| Module | File | Lines | Tests | Status |
|:-------|:-----|:-----:|:-----:|:------|
| PSI Monitor | `psi_monitor.py` | 230 | ─ | 🟢 compiles |
| MemAvailable | `memavailable.py` | 210 | ─ | 🟢 compiles |
| cgroup Pressure | `cgroup_pressure.py` | 280 | ─ | 🟢 compiles |
| OOMProtector | `oom_protector.py` | 368 | ─ | 🟢 compiles |
| ResourceGuard | `resource_guard.py` | 318 | ─ | 🟢 updated |
| Contract Tests | `test_resource_guard_oom.py` | 520 | **13/13** | 🟢 ALL PASS |

### Three-Signal Fusion Priority Chain

```
INPUT ──┬── PSI (/proc/pressure/memory) ─────► some.avg60, full.avg10
         ├── MemAvailable (/proc/meminfo) ────► si_mem_available() in GB
         └── cgroup v2 (/sys/fs/cgroup) ─────► memory.pressure, pressure_level

FUSION:
  MemAvailable < 2GB  ──────────► DENY_OOM_RISK     (hard floor)
  PSI full.avg10 > 5% ──────────► DENY_THRASHING    (system frozen)
  cgroup full.avg10 > 5% ───────► DENY_THRASHING    (container frozen)
  PSI some.avg60 > 10% ─────────► THROTTLE          (sustained pressure)
  cgroup some.avg60 > 15% ──────► THROTTLE          (container pressure)
  MemAvailable 2-4GB ───────────► THROTTLE          (low headroom)
  All healthy ──────────────────► ALLOW

OUTPUT: AdmissionResult.ALLOW | THROTTLE | DENY_OOM_RISK | DENY_THRASHING
```

### Hardware Floor (Ryzen 7 5700U)

```
         ┌──────────────────────────────────┐
    TDP  │ 15W ■■■■■■■■■■■■■■■■■■■■■■■□□□□ │  thermal ceiling
         ├──────────────────────────────────┤
    RAM  │ 16GB total / 8GB idle available  │
         ├──────────────────────────────────┤
    L3   │  8MB victim cache (NOT inclusive)│
         ├──────────────────────────────────┤
    CCX  │  2 CCX × 4 cores = 8 total      │
         ├──────────────────────────────────┤
    BW   │ DDR4-3200 dual channel ~51 GB/s  │
         └──────────────────────────────────┘
```

### Threshold Calibration

| Signal | Healthy ▓▓▓ | Warning ▓▓░ | Critical ░░░ |
|:-------|:------------|:------------|:-------------|
| PSI some.avg60 | < 5% | 5-10% | > 10% |
| PSI full.avg10 | < 1% | 1-5% | > 5% |
| MemAvailable | > 4 GB | 2-4 GB | < 2 GB |
| cgroup some.avg60 | < 5% | 5-15% | > 15% |
| cgroup full.avg10 | < 1% | 1-5% | > 5% |

## 🧠 L3 Principles Distilled (for proposed_lessons.yaml)

### CG-02: Kernel-Authoritative Memory Signals

> **Kernel knows memory pressure better than userspace counters.** Always prefer `/proc/pressure/memory` (PSI) + `MemAvailable` (`si_mem_available()`) + `cgroup memory.pressure` over software accounting. The kernel computes stall time and reclaimable memory from page allocator internals — userspace counters drift by definition.

**Evidence**: `kernel/sched/psi.c` tracks 10 distinct memstall types via `psi_memstall_enter/leave`. `mm/page_alloc.c` `si_mem_available()` accounts free pages + page cache + reclaimable slab minus watermark reserves. The OOM killer (`mm/oom_kill.c`) uses the same MemAvailable logic.

**L3 Rating**: Universal principle — applies to any Linux-native OOM prevention system.

### CG-08: Topology-Aware Admission Control (future)

> **Admission control must understand hardware topology (CCX, L3, memory bandwidth), not just instance counts.** On a 2-CCX Ryzen with 8MB victim L3, pinning inference to one CCX halves L3 thrash. The right approximation is topology-aware semaphores, not flat counting.

### CG-09: Atomic File Semantics > Consensus (future)

> **Single writer + atomic rename + fsync > distributed consensus for local state.** The Postgres fsync dance (`write → fsync → rename → fsync(dir)`) is the right approximation for crash-safe local persistence. NO distributed consensus protocols for single-machine state.

## 📝 Engineering Observations

1. **Python em-dashes break imports**: Using `—` (U+2014) in module-level comments outside strings causes `SyntaxError: invalid character`. Python 3.13 is stricter about non-ASCII outside string literals. Lesson: keep `#` comments ASCII-only.

2. **anyio.create_task_group() returns None**: Unlike `asyncio.gather()`, `tg.start_soon()` doesn't return futures. Use a mutable container (dict/list) to collect return values from concurrent coroutines.

3. **Legacy wrapper pattern works**: `LegacyOOMWrapper` lets us replace internals (single-signal → three-signal fusion) without breaking `ResourceGuard.lock()` which expects `check() -> bool`. No call sites changed.

4. **Visual aids reduce cognitive load**: Progress bars (`▓▓▓▓░░░░`), matrix tables, ASCII flow charts, and color-coded status columns make state instantly scannable. Use them in all status reports going forward.

## 🔜 Next Session

```
What to resume:   Day 3 — CG-08 Admission Control (CCX Topology)
First file:       src/omega/oracle/admission_controller.py
Depends on:       CG-02 thresholds (DONE ✅)
Key reference:    docs/research/R_CG02_OOMPROTECTOR_HARDWARE_AWARE.md §6-7
```

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ session_gnosis ⬡ 2026-07-21*
