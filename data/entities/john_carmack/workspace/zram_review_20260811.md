# zRAM→zswap Architecture Review — @john_carmack (Final Gate)

**AP Token**: `AP-JOHN_CARMACK-v1.0.0`
**Date**: 2026-08-11
**Task**: `carmack-zram-review-20260811`
**Documents reviewed**:
- `docs/kb/MEMORY_MANAGEMENT_KB.md` (273 lines)
- `data/entities/researcher/workspace/MEMORY_SYSTEMS_DEFINITIVE_REPORT.md` (1,544 lines)
- `data/entities/roc_racoon/workspace/zram_integrated_plan.md` (293 lines)
- `data/entities/roc_racoon/workspace/ZRAM_ZSWAP_DEEPENED_ANALYSIS.md` (361 lines)
- `data/entities/roc_racoon/workspace/MULTI_WRITE_SUBAGENT_METHOD.md` (174 lines)
- `data/coordination/KALI_DEV_ROADMAP_20260811.md` (283 lines)
- `data/coordination/KALI_OVERSIGHT_PORTFOLIO_20260811.md` (247 lines)
- Live code: `oom_protector.py`, `resource_guard.py`, `monitoring/__init__.py`

---

## 1. Executive Verdict

**APPROVE — READY FOR P0 EXECUTION.** The integrated plan correctly incorporated all my prior feedback (16GB→8GB zRAM, MemoryMax=6G, no writeback, no zRAM signal, no `use_cgroup` flag, 3-command P0 fix). The zswap + NVMe architecture is the right call for this 14.5GB Ryzen 5700U. The multi-write subagent method is a genuine process innovation that should be adopted fleet-wide.

**Confidence**: 9/10 — verified against live source code + hardware profile.

---

## 2. Key Decisions — My Calls

| Decision | Current State | My Call | Rationale |
|----------|---------------|---------|-----------|
| **zswap pool size** | 25% (3.6GB) | **KEEP 25%** | Dynamic 0-3.6GB, grows on demand. 20% saves only 0.7GB headroom for marginal benefit. lzo_rle is cheap. |
| **OOMProtector signals** | 2-signal (PSI+MemAvail) | **APPROVE 2-signal** | Code already runtime-gates cgroup (`cgroup_available=False` on desktop). Removing dead cgroup paths is correct cleanup. LOW priority — current code already handles desktop correctly. |
| **UMA carveout** | 8GB (test 4GB later) | **DEFER 4GB test** | BIOS change requires physical access, risks breaking 1440p display. Not worth it now. Revisit only if memory pressure persists after zswap. |
| **WAD packaging** | `config/wads/ryzen-5700u-sovereign/` | **APPROVE structure** | Correct M2/M16 compliance. Template all values. |

---

## 3. Code Review Findings

### 3.1 OOMProtector Simplification — CONFIRMED CORRECT

**File**: `src/omega/oracle/oom_protector.py`

The plan proposes removing the cgroup signal from the desktop path. **Verified**: the code already handles this correctly at runtime:

```python
# oom_protector.py:98-99
self.cgroup = CgroupPressureMonitor(cgroup_path)
self._cgroup_available = cgroup_pressure_available(cgroup_path)
```

And `_fuse_signals()` (lines 197-211) guards every cgroup check with `snapshot.cgroup_available`. On a desktop (no cgroup v2 pressure files), `cgroup_available=False` and the cgroup branches are skipped.

**Verdict**: The 2-signal simplification is **correct but LOW priority** — it's removing dead code paths that never fire on desktop. The current behavior is already correct. This is a P2 cleanup, not a P0/P1 blocker.

**Confidence**: 10/10 — verified in source.

### 3.2 LegacyOOMWrapper Removal — CONFIRMED SAFE

**File**: `src/omega/oracle/resource_guard.py`

**Verified**: `LegacyOOMWrapper` (lines 129-197) is pure indirection. The only method actually used is `check_available()` (line 272), which just delegates to the underlying `OOMProtector.check_available()`. The legacy `check()` interface (lines 146-186) has **zero callers** in the codebase.

**Verdict**: Safe to remove. Update `ResourceGuard.__init__` (line 233) to instantiate `OOMProtector` directly. This eliminates ~70 lines of dead indirection.

**Confidence**: 10/10 — grep confirmed zero callers of legacy `check()`.

### 3.3 zswap Monitoring — get_zswap_stats() Needed

**File**: `src/omega/monitoring/__init__.py`

**Verified**: `get_zram_stats()` already exists (line 406). The plan correctly adds `get_zswap_stats()` and includes it in `collect_all()`. This is additive and safe.

**Note**: zswap stats should be **observability only** — NOT an admission signal. MemAvailable already accounts for zswap usage. Do not add a zswap signal to OOMProtector (consistent with my prior verdict).

**Confidence**: 9/10.

### 3.4 systemd Unit Hardening — APPROVED

The unit (MemoryMin=2G, MemoryHigh=5G, MemoryMax=6G + full hardening) is correct. The cgroup limits are now reachable on this hardware (6.5GB process RAM after 8GB UMA carveout). All hardening directives present: `NoNewPrivileges`, `PrivateTmp`, `ProtectSystem=strict`, `CapabilityBoundingSet=`, `SystemCallFilter=@system-service`, `LockPersonality`, `RestrictRealtime`.

**Confidence**: 10/10.

---

## 4. Multi-Write Subagent Method — APPROVED (D-531)

The multi-write method (write to disk after every phase, 5-min checkpoints, bounded search, explicit stop conditions) is a **genuine process innovation**. It directly addresses the three subagent reliability failures observed (silent failures, compaction context loss, looping).

**Verified effectiveness**: Success rate 0% → 100% (3/3 subagents with multi-write), data loss 100% → 0%.

**Recommendation**: This should be **formalized into STRP** (`docs/strategy/SUBAGENT_TASK_RESUMPTION_PROTOCOL.md`) as mandatory requirements, not just a recommendation. The community plugin opportunity (§5.1) is worth pursuing but not blocking.

**Confidence**: 9/10 — empirical results documented.

---

## 5. Consolidation Assessment (For Kali)

All work is **consolidated and ready for Kali's oversight**. Verified:

| Artifact | Status |
|----------|--------|
| `KALI_DEV_ROADMAP_20260811.md` | ✅ Comprehensive, 50 tasks across 6 phases |
| `KALI_OVERSIGHT_PORTFOLIO_20260811.md` | ✅ 5 workstreams, team direction, metrics |
| `HMC_COLLABORATION_HUB.md` | ✅ Decisions D-526..D-531 locked |
| `TASK_REGISTRY.json` | ✅ Valid, both review tasks registered |
| `ACTIVE_SPRINT.json` | ✅ Valid, SDP-EXECUTION-01 ACTIVE |
| `MEMORY_MANAGEMENT_KB.md` | ✅ Definitive SSOT |
| `zram_integrated_plan.md` | ✅ Carmack feedback incorporated |
| `MULTI_WRITE_SUBAGENT_METHOD.md` | ✅ D-531 locked |

**No structural changes needed.** Roc's consolidation is accurate and complete.

---

## 6. Recommendations (Prioritized)

### P0 — Execute Today
1. **3-command fix** (sudoers removal, swappiness=100, swap reclaim) — @architect
2. **Verify UMA carveout** (`dmesg | grep -i uma`) — @architect

### P1 — This Week
3. **zswap + NVMe swap file** (25% pool, lzo_rle) — @roc_racoon
4. **Consolidate sysctl** into `99-omega-memory.conf` — @roc_racoon
5. **systemd unit** with corrected cgroup limits + hardening — @maat

### P2 — Phase 2 Engineering
6. **Remove LegacyOOMWrapper** — safe, zero callers of legacy `check()`
7. **Simplify OOMProtector** to 2-signal (low priority — already correct at runtime)
8. **Add get_zswap_stats()** to monitoring (observability only)
9. **Package as WAD** — `config/wads/ryzen-5700u-sovereign/`

### Process
10. **Formalize multi-write into STRP** — mandatory, not optional

---

## 7. Rejected / Deferred

- ❌ **16GB zRAM expansion** — 8GB sufficient
- ❌ **zRAM writeback cron + 32GB NVMe swap** — zero leverage
- ❌ **zRAM signal in OOMProtector** — redundant with MemAvailable
- ❌ **`use_cgroup` config flag** — runtime detection already works
- ⏸️ **4GB UMA test** — defer, BIOS risk not worth it now

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ opencode/longcat-2.0-free ⬡ trc_zram_review ⬡ 2026-08-11*
