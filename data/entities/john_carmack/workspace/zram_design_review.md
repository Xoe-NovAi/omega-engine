<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# zRAM Design Review — @john_carmack
## Review of Jem + Researcher + roc_racoon synthesis

**AP Token**: `AP-JOHN_CARMACK-v1.0.0`
**Date**: 2026-08-10
**Documents reviewed**:
- `data/entities/jem/workspace/zram_excavation_report.md`
- `data/entities/researcher/workspace/zram_tuning_guide.md`
- `data/entities/roc_racoon/workspace/zram_integrated_plan.md`

---

## 1. Executive Verdict

**REQUEST CHANGES** — The plan correctly identifies the root cause (swappiness=180 causing 6.4 GiB of unnecessary swap at zero PSI pressure) and the critical sudoers vulnerability, but the proposed solution is over-engineered by a factor of 3x. The 8-step implementation plan bundles three independent concerns (security fix, kernel tuning, code refactoring) that should be separated. The cgroup v2 memory limits (MemoryMax=12G) are unreachable on this hardware — the 8GB UMA carveout leaves only ~6.5GB for processes, making a 12GB cgroup ceiling physically impossible to hit. The 16GB zRAM expansion wastes ~2.6GB of physical RAM on compression buffers that provide no marginal benefit over 8GB. The zRAM writeback cron + 32GB NVMe swap file is solution theater for a 14.5GB system.

**Confidence**: 9/10 — primary source code (`oom_protector.py`, `resource_guard.py`) and live system state verified.

## 2. Architectural Assessment

### 2.1 The 3-Signal → 2-Signal Simplification (G-8)

**Finding**: The plan proposes adding `use_cgroup: bool = False` to `OOMProtectorConfig` to make cgroup monitoring optional. This is **redundant** — the code already conditionally skips cgroup reads via `self._cgroup_available = cgroup_pressure_available(cgroup_path)` at line 99 of `oom_protector.py`. The `_take_snapshot()` method already guards cgroup reads with `if not self._cgroup_available: results["cgroup"] = None; return` (lines 138-145).

**The real issue**: The plan adds a *config flag* to control behavior that is already *runtime-detected*. This is the wrong abstraction. The cgroup pressure monitor should be instantiated lazily — only when the cgroup path is actually a cgroup v2 mount with pressure files. The current code already does this correctly via `cgroup_pressure_available()`.

**Carmack verdict alignment**: The verdict was "3-signal fusion is server-grade theater for single-user desktop." The plan's approach of keeping all three signals but making cgroup optional via a config flag is a half-measure. The correct approach is to **remove the cgroup signal entirely from the desktop path** and only instantiate `CgroupPressureMonitor` when running inside a container (detected at runtime, not via config).

**Code evidence**: `oom_protector.py:98-99` — `self.cgroup = CgroupPressureMonitor(cgroup_path)` is always instantiated, even on bare metal where it's redundant. The `_fuse_signals()` method (lines 197-211) still carries 4 lines of cgroup-specific logic that will never fire on a desktop.

### 2.2 cgroup v2 Memory Protection — Unreachable Limits

**Finding**: The proposed `MemoryMax=12G` on a 14.5GB system with 8GB UMA carveout is **physically impossible to reach**. Here's the math:

- Total RAM: 14,793 MB (14.5 GB)
- UMA carveout: 8,192 MB (8 GB) — reserved for Vega 8 iGPU
- Available for OS + processes: ~6,601 MB (6.5 GB)
- Proposed MemoryMax: 12,288 MB (12 GB)

The cgroup limit of 12GB exceeds the total available process memory (6.5GB). The kernel will OOM-kill the process at ~6.5GB before the cgroup limit is ever hit. The cgroup protection is **dead code** on this hardware.

**The correct values** for a 14.5GB system with 8GB UMA carveout:
- `MemoryMin=2G` — guarantee 2GB for inference (never reclaimed)
- `MemoryHigh=5G` — throttle at 5GB (soft ceiling, ~77% of available)
- `MemoryMax=6G` — hard limit at 6GB (leaves 0.5GB for OS overhead)

**Confidence**: 10/10 — hardware profile (`config/hardware_profile.yaml`) confirms `total_mb: 14793`, `uma_carveout_mb: 8192`.

### 2.3 zRAM Writeback to NVMe Swap — Over-Engineering

**Finding**: The 32GB NVMe swap file + writeback cron (Step 5) is **solution theater** for a 14.5GB system. Here's why:

1. **zRAM is already RAM-backed** — writeback moves idle pages from compressed RAM to disk. But if you have enough zRAM, pages rarely go idle. The 6.4GB swap usage at swappiness=180 was caused by *aggressive proactive swapping*, not by zRAM being too small.

2. **The writeback cron adds failure modes**: A cron job writing to `/sys/block/zram0/idle` and `/sys/block/zram0/writeback` can fail silently, corrupt state, or race with the kernel's own reclaim. The `2>/dev/null || true` pattern masks these failures.

3. **32GB swap file is wasteful**: On a system with 14.5GB RAM, a 32GB swap file is 2.2x the physical RAM. Even if you never use it, it consumes disk space and increases backup/restore time.

**The right approach**: Skip writeback entirely. If you need more swap, increase zRAM size or fix swappiness. Writeback is a server-scale optimization for systems with 64GB+ RAM where you need to evict cold pages from compressed memory to make room for hot pages.

### 2.4 The 8-Step Plan — Wrong Granularity

**Finding**: The 8-step plan conflates three independent concerns:

1. **Security fix** (Step 1: sudoers) — should be a standalone emergency patch
2. **Kernel tuning** (Steps 2-4, 6-8: sysctl, zram-generator, systemd unit, tune_ryzen.sh) — should be a single deployment script
3. **Code refactoring** (Step 7: OOMProtector) — should be a separate engineering ticket

Bundling these into one plan means you can't ship the security fix without also shipping the zRAM expansion, which may not be ready. The sudoers vulnerability is a **P0 emergency** — it should be fixed immediately, independently of any zRAM tuning.

### 2.5 zRAM Signal in OOMProtector (G-15) — Contradicts Carmack Verdict

**Finding**: Adding zRAM fill ratio as a 4th signal to OOMProtector **directly contradicts** the Carmack verdict of simplifying to 2 signals. The plan adds complexity (4th signal, new PressureSnapshot field, new threshold) when the verdict was to *remove* complexity.

**The right approach**: If zRAM is >90% full, that's a kernel-level problem — the kernel will start OOM-killing processes. The OOMProtector doesn't need to know about zRAM fill ratio. MemAvailable already accounts for zRAM usage (it's part of the kernel's reclaimable memory calculation). Adding a zRAM signal is redundant with MemAvailable.

**Confidence**: 9/10 — `memavailable.py` confirms MemAvailableReader reads `/proc/meminfo` MemAvailable, which is `si_mem_available()` in the kernel. This function accounts for zRAM usage.

## 3. Modularity & Portability

### 3.1 Hardcoded Values — Not Portable

**Finding**: The plan is hardcoded to a single machine. Every config file contains machine-specific values:

| Artifact | Hardcoded Value | Portability Impact |
|----------|----------------|-------------------|
| `zram-generator.conf` | `zram-size = 16384` | Assumes 14.5GB+ RAM |
| `99-omega-memory.conf` | `vm.swappiness = 100` | Assumes zRAM present |
| `omega.service` | `User=arcana-novai` | Assumes specific user |
| `omega.service` | `WorkingDirectory=/home/arcana-novai/...` | Assumes specific path |
| `omega.service` | `ExecStart=.../.venv/bin/omega-hub` | Assumes venv layout |
| `omega.service` | `LLAMA_CPP_N_THREADS=7` | Assumes 8-core CPU |
| `omega-zram-tune.sh` | `/usr/sbin/zramctl` | Assumes systemd-zram-setup |

**The right approach**: These configs should be **templated** with variables that are resolved at install time. The systemd unit should use `%h` (home directory) and `%u` (user) specifiers. The zRAM size should be computed as `min(ram_total / 2, 8192)` — not hardcoded to 16GB.

**Sovereign Mandate M16 (Modularization & Portability) violation**: The plan does not address portability. A portable design would:
1. Detect RAM at install time and compute zRAM size dynamically
2. Use systemd specifiers (`%h`, `%u`) instead of hardcoded paths
3. Template the user/group names
4. Make swappiness conditional on zRAM presence

### 3.2 Engine-Stack Firewall (M2) Violation

**Finding**: The plan places system-level configuration (systemd unit, sysctl, sudoers, zram-generator) in the **engine core** rather than in a **WAD**. Per Sovereign Mandate M2, the Engine-Stack Firewall requires absolute separation:

- **Core** (`src/omega/`): Universal runtime — no machine-specific config
- **Stacks** (`config/wads/`): Machine-specific implementation

The systemd unit, sysctl configs, and sudoers entries are **machine-specific deployment artifacts**. They belong in a WAD like `config/wads/ryzen-5700u-sovereign/`, not in the engine core or in entity workspaces.

**The right approach**: Create a `config/wads/ryzen-5700u-sovereign/` WAD containing:
- `zram-generator.conf` (templated)
- `99-omega-memory.conf` (templated)
- `omega.service` (templated with systemd specifiers)
- `omega-engine.sudoers` (surgical whitelist)
- `omega-zram-tune.sh` (root-owned, input-validated)
- `install.sh` (applies all configs atomically)

### 3.3 WAD-ability Assessment

**Finding**: The plan is **not WAD-able** in its current form. The configs are scattered across shell commands in a markdown document, not structured as a deployable package. To make this WAD-able:

1. **Separate concerns**: Security fix (sudoers) should be a standalone WAD patch
2. **Template all values**: Use Jinja2 or envsubst for user paths, RAM sizes, CPU counts
3. **Add install/uninstall scripts**: Atomic apply/revert
4. **Add validation**: `visudo -c`, `systemd-analyze verify`, `sysctl --system`

**Confidence**: 8/10 — the configs themselves are correct, but the packaging is not portable.

## 4. Efficiency & Leverage

### 4.1 16GB zRAM — Wrong Size

**Finding**: 16GB zRAM is **over-provisioned** for a 14.5GB system. Here's the math:

- zRAM virtual size: 16GB
- Expected compression ratio (zstd level=3): ~2.5:1 to 3:1
- Physical RAM consumed by zRAM buffers: ~5.3GB to ~6.4GB
- Available process RAM (after 8GB UMA carveout): ~6.5GB
- zRAM consumes **81-98%** of available process RAM

This is wasteful. The current 8GB zRAM with 3:1 compression uses ~2.7GB — 41% of available RAM. That's already sufficient for the workload.

**The right approach**: Keep 8GB zRAM. If you need more, increase to 10GB (not 16GB). The marginal benefit of 16GB over 8GB is negligible because:
1. The system only has 6.5GB of process RAM — you can't actually use 16GB of zRAM
2. zstd level=3 already provides good compression
3. The kernel's swapout logic will naturally prefer zRAM over NVMe swap

**Confidence**: 9/10 — compression ratio math is straightforward. zram-advisor (2026) confirms effective memory = compressed data + metadata.

### 4.2 swappiness=100 — Correct but Conservative

**Finding**: swappiness=100 is the kernel-documented sweet spot for in-memory swap, but it's **conservative** for a desktop workload. The kernel docs say "values beyond 100 can be considered" for zRAM. The current problem is swappiness=180 causing excessive proactive swapping.

**The right approach**: Start at swappiness=100, but **measure** the actual swap usage after 24 hours of normal operation. If swap usage is still high (>2GB), reduce to 80. If swap usage is near zero, you can even increase to 120. The key insight is that swappiness should be **workload-driven**, not folklore-driven.

**Carmack note**: The kernel docs are authoritative here. 100 is correct. Don't overthink it.

### 4.3 8-Step Plan — Over-Engineered

**Finding**: The 8-step plan is 3x longer than necessary. The **minimum viable path** is 3 steps:

1. **Fix swappiness** (1 command): `sudo sysctl vm.swappiness=100`
2. **Fix sudoers** (1 command): `sudo rm /etc/sudoers.d/zram`
3. **Flush swap** (1 command): `sudo swapoff -a && sudo swapon -a`

This immediately solves the root cause (excessive proactive swapping) and the security vulnerability. The remaining 5 steps (zRAM expansion, systemd unit, cgroup protection, writeback, tune_ryzen.sh update) are **optimizations** that can be deferred.

**The right approach**: Ship the 3-step fix first. Measure the results. Then decide if the additional 5 steps are worth the complexity.

### 4.4 tune_ryzen.sh Inconsistency — Minor

**Finding**: The plan correctly identifies the swappiness inconsistency (60 vs 80 vs 180). But the fix is trivial — just update the script to match the sysctl.d value. This is a 1-line change, not a separate step in an 8-step plan.

### 4.5 zRAM Writeback — Zero Leverage

**Finding**: The zRAM writeback cron (Step 5) has **zero leverage** on a 14.5GB system. It adds:
- 1 cron job (failure mode)
- 1 swap file management (32GB disk space)
- 1 backing device configuration (complexity)
- 1 idle page detection loop (CPU overhead)

For what benefit? On a system with 6.5GB of process RAM, zRAM writeback moves cold pages from compressed RAM to disk. But if you have 8GB zRAM with 3:1 compression, you already have ~24GB of effective swap space. Writeback is for systems where zRAM is full and you need to evict cold pages to make room for hot pages. That's not this system.

**The right approach**: Delete Step 5 entirely. If you need more swap, increase zRAM size or add a smaller (8GB) NVMe swap file without writeback.

## 5. Security Review

### 5.1 Sudoers Vulnerability — Correctly Identified, Correctly Fixed

**Finding**: The plan correctly identifies the critical sudoers vulnerability: `/tmp/reset_zram.sh` and `/tmp/activate_zram.sh` in NOPASSWD entries. This is a **critical privilege escalation** — any user who can write to `/tmp/` can create these scripts and execute arbitrary code as root.

**The fix is correct**: Remove the `/tmp/` entries and replace with root-owned scripts in `/usr/local/bin/`. The heritage lessons H-SUDO-001 and H-SUDO-002 are properly applied:
- H-SUDO-001: Scripts MUST reside in root-owned, immutable directory (not `/tmp/`)
- H-SUDO-002: Scripts expose ONLY required sub-commands

**However**: The proposed `omega-zram-tune.sh` only exposes a `status` subcommand. This is overly restrictive — it doesn't actually allow any tuning. If the intent is to allow runtime zRAM management, the script needs to expose specific, validated subcommands (e.g., `reset`, `reconfigure`). If the intent is read-only monitoring, then the sudoers entry is unnecessary — `zramctl` can be read without sudo.

**The right approach**: Either:
1. **Read-only**: Remove the sudoers entry entirely. `zramctl` and `swapon --show` can be read by any user.
2. **Write access**: Create a script that exposes specific, validated subcommands with input validation (e.g., `omega-zram-tune.sh reset` only resets zram, nothing else).

### 5.2 systemd Unit Security Hardening — Good but Incomplete

**Finding**: The proposed systemd unit includes good security hardening directives:
- `NoNewPrivileges=true`
- `PrivateTmp=true`
- `ProtectSystem=strict`
- `ProtectHome=read-only`
- `ProtectKernelTunables=true`
- `ProtectKernelModules=true`
- `ProtectControlGroups=true`
- `RestrictSUIDSGID=true`

**Missing**:
- `CapabilityBoundingSet=` — should restrict to empty (no capabilities needed)
- `AmbientCapabilities=` — should be empty
- `SystemCallFilter=` — should restrict to a minimal syscall set
- `LockPersonality=true`
- `RestrictRealtime=true`
- `RestrictSUIDSGID=true` (already present)

**The right approach**: Add the missing hardening directives. The systemd unit should be as locked down as possible.

### 5.3 Privilege Escalation Risk — None Beyond Sudoers

**Finding**: Beyond the sudoers vulnerability (which is correctly fixed), there are no privilege escalation risks in the plan. The systemd unit runs as `User=arcana-novai` (non-root), and the cgroup limits are set by systemd (not by the process itself).

**Confidence**: 9/10 — the sudoers fix is correct, the systemd hardening is good but could be more complete.

## 6. Code Quality

### 6.1 OOMProtector zRAM Signal Integration (G-15) — Wrong Direction

**Finding**: The plan proposes adding zRAM fill ratio as a 4th signal to OOMProtector. This is **wrong** for two reasons:

1. **Contradicts Carmack verdict**: The verdict was to *simplify* to 2 signals (PSI + MemAvailable). Adding a 4th signal is the opposite of simplification.

2. **Redundant with MemAvailable**: `MemAvailable` from `/proc/meminfo` is `si_mem_available()` in the kernel, which already accounts for zRAM usage. When zRAM is full, MemAvailable decreases. Adding a separate zRAM signal is double-counting.

**Code evidence**: `oom_protector.py:190` — `if snapshot.memavailable_gb < cfg.min_reserve_gb: return AdmissionResult.DENY_OOM_RISK`. This already catches the case where zRAM is consuming too much memory.

**The right approach**: Do NOT add a zRAM signal. If zRAM is >90% full, MemAvailable will be low, and the existing MemAvailable check will catch it. Trust the kernel's memory accounting.

### 6.2 `use_cgroup: bool = False` Config Flag — Redundant

**Finding**: The plan proposes adding `use_cgroup: bool = False` to `OOMProtectorConfig`. This is **redundant** because the code already detects cgroup availability at runtime:

```python
# oom_protector.py:99
self._cgroup_available = cgroup_pressure_available(cgroup_path)
```

And in `_take_snapshot()`:
```python
# oom_protector.py:138-145
async def read_cgroup():
    if not self._cgroup_available:
        results["cgroup"] = None
        return
```

**The right approach**: Remove the config flag. The runtime detection is correct. If you want to force-disable cgroup monitoring, use the existing `cgroup_path` parameter — pass a path that doesn't exist.

### 6.3 LegacyOOMWrapper — Unnecessary Indirection

**Finding**: `resource_guard.py` contains a `LegacyOOMWrapper` class that wraps `OOMProtector` with a legacy `check(model_name, model_spec) -> bool` interface. This is **unnecessary indirection** — the wrapper converts `AdmissionResult` back to a boolean, losing the rich decision information.

**Code evidence**: `resource_guard.py:129-186` — `LegacyOOMWrapper.check()` calls `self._protector.check()` and converts the result to `True`/`False`. The `AdmissionResult` enum (ALLOW/THROTTLE/DENY_OOM_RISK/DENY_THRASHING) is lost.

**The right approach**: Remove `LegacyOOMWrapper`. Update callers to use `OOMProtector` directly. The `ResourceGuard.lock()` method already calls `self._oom_protector.check_available(required_gb)` (line 272), which is the correct interface.

### 6.4 M1 Compliance — Already Correct

**Finding**: The plan correctly identifies that the M1 asyncio violations claimed in the excavation report are **resolved**. The live code audit confirms:
- `psi_monitor.py`: Uses `anyio.create_task_group()`, `anyio.sleep()`, `aiofiles.open()` — M1 compliant
- `cgroup_pressure.py`: Uses `anyio.create_task_group()`, `anyio.sleep()`, `aiofiles.open()` — M1 compliant
- `oom_protector.py`: Uses `anyio.create_task_group()` — M1 compliant

**Confidence**: 10/10 — verified by reading the actual source files.

### 6.5 ZONEID Pattern — Properly Applied

**Finding**: The `[id-soft: vet-015] ZONEID Pattern` heritage tag in `resource_guard.py` is **legitimate**. The `ZONEID_PROBE` and `ZONEID_ATOMIC` constants are used to guard critical sections against use-after-free and double-release bugs. This is a direct port of the id Software zone memory management pattern, adapted for async lock integrity.

**Confidence**: 9/10 — the pattern is correctly applied and the heritage tag is justified.

## 7. Recommendations

### 7.1 Immediate (P0 — Do Today)

1. **Remove sudoers vulnerability** — `sudo rm /etc/sudoers.d/zram`
2. **Fix swappiness** — `sudo sysctl vm.swappiness=100` (consolidate sysctl.d files)
3. **Flush swap** — `sudo swapoff -a && sudo swapon -a` (reclaim 4.1GB RAM)

These three commands solve the root cause and the security vulnerability. **Ship this first.**

### 7.2 Short-Term (P1 — This Week)

4. **Fix cgroup limits** — Change `MemoryMax=12G` to `MemoryMax=6G` (reachable on 14.5GB system with 8GB UMA carveout). Change `MemoryHigh=10G` to `MemoryHigh=5G`. Change `MemoryMin=4G` to `MemoryMin=2G`.
5. **Keep 8GB zRAM** — Do NOT expand to 16GB. 8GB with 3:1 compression is sufficient.
6. **Remove zRAM writeback** — Delete Step 5 entirely. No cron job, no 32GB swap file.
7. **Add systemd hardening** — Add `CapabilityBoundingSet=`, `SystemCallFilter=`, `LockPersonality=true`, `RestrictRealtime=true`.

### 7.3 Medium-Term (P2 — Phase 2 Engineering)

8. **Simplify OOMProtector** — Remove cgroup signal from desktop path. Use runtime detection (already implemented) instead of config flag. Remove `LegacyOOMWrapper` indirection.
9. **Do NOT add zRAM signal** — MemAvailable already accounts for zRAM usage.
10. **Package as WAD** — Move all system configs to `config/wads/ryzen-5700u-sovereign/` with templated values.
11. **Update tune_ryzen.sh** — Change swappiness from 60 to 100, add rationale comment.

### 7.4 Rejected

- **16GB zRAM expansion** — Wastes 2.6GB of physical RAM on compression buffers
- **zRAM writeback cron** — Zero leverage on 14.5GB system
- **32GB NVMe swap file** — 2.2x physical RAM, unnecessary
- **`use_cgroup: bool = False` config flag** — Redundant with runtime detection
- **zRAM fill ratio signal in OOMProtector** — Redundant with MemAvailable, contradicts simplification verdict
- **8-step plan granularity** — Should be 3 steps (security) + 4 steps (tuning) + 1 step (code) = 3 separate deliverables

## 8. Carmack Alternative

**The highest-leverage, lowest-effort path — what I would build first:**

### The 3-Command Fix

```bash
# 1. Security: Remove the sudoers backdoor (P0 emergency)
sudo rm /etc/sudoers.d/zram

# 2. Root cause: Fix swappiness from 180 to 100
sudo sysctl vm.swappiness=100

# 3. Reclaim memory: Flush the 4.1GB of unnecessary swap
sudo swapoff -a && sudo swapon -a
```

**Why this works**:
- **swappiness=180** was the root cause. It told the kernel to treat zRAM swap as *cheaper* than filesystem paging. The kernel aggressively swapped idle anonymous pages into zRAM, consuming 4.1GB of real RAM for compression buffers at zero PSI pressure.
- **swappiness=100** tells the kernel that zRAM swap and filesystem paging are *equal cost*. This is the kernel-documented sweet spot for in-memory compressed swap. The kernel will still use zRAM when beneficial, but won't aggressively swap idle pages.
- **swapoff -a && swapon -a** immediately reclaims the 4.1GB of compression buffers. The pages are already in RAM (they were just swapped to zRAM unnecessarily).

**What this does NOT do**:
- Does NOT expand zRAM to 16GB (8GB is sufficient)
- Does NOT add cgroup protection (unreachable limits on this hardware)
- Does NOT add zRAM writeback (zero leverage)
- Does NOT add a 4th signal to OOMProtector (redundant with MemAvailable)
- Does NOT create a systemd unit (not needed for the fix)

**The leverage ratio**: 3 commands, 10 seconds of execution time, solves the root cause + security vulnerability. The remaining 5 steps in the 8-step plan are optimizations that can be deferred until the 3-command fix is measured and validated.

**If I had to pick ONE more thing to do after the 3-command fix**:
- Package the configs as a WAD with templated values (portability)
- Fix the cgroup limits to be reachable (MemoryMax=6G, not 12G)

Everything else is solution theater.

### The Right Abstraction for OOMProtector

Instead of adding `use_cgroup: bool = False` to the config, the correct approach is:

```python
# oom_protector.py — simplified
class OOMProtector:
    def __init__(self, config=None):
        self.config = config or OOMProtectorConfig()
        self.psi = PSIMonitor()
        self.memavailable = MemAvailableReader()
        # cgroup is optional — only instantiate if available
        self.cgroup = CgroupPressureMonitor() if self._cgroup_available() else None
    
    def _fuse_signals(self, snapshot):
        # 1. MemAvailable < reserve → DENY_OOM_RISK
        # 2. PSI full.avg10 > 5% → DENY_THRASHING
        # 3. PSI some.avg60 > 10% → THROTTLE
        # 4. MemAvailable < 4GB → THROTTLE
        # 5. ALL CLEAR
        # NO cgroup signal on desktop — it's redundant with PSI
```

This is 2-signal fusion (PSI + MemAvailable) for desktop, with cgroup as an optional add-on for containers. No config flag needed — runtime detection handles it.

**Confidence**: 10/10 — this is the right abstraction. The kernel knows best; userspace should not second-guess it.

---
*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ opencode/laguna-s-2.1-free ⬡ trc_audit ⬡ 2026-08-10*