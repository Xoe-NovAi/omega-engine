<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# ResourceGuard & OOMProtector — Deep Research
**AP Token**: `AP-RESEARCHER-RG-OOM-v1.0.0`
**Date**: 2026-07-26 | **Priority**: P0 — CRITICAL OOM risk
**Researcher**: Sovereign Researcher (Council of Four)

---

## Executive Summary

The Omega Engine has a **mature three-signal fusion OOMProtector** (PSI + MemAvailable + cgroup v2) that is architecturally sound but has **three calibration drifts** and **one critical integration gap**: the background researcher creates its own ResourceGuard bypassing OOMProtector entirely.

## Current State

| Component | Status | Issue |
|-----------|--------|-------|
| OOMProtector | ✅ 3-signal fusion | Correct architecture, thresholds need zRAM calibration |
| ResourceGuard cvar (12288 MB) | ❌ Dead code | Software counter removed in v1.2.0 but cvar remains |
| Background Researcher | 🔴 BROKEN | Hardcodes `max_ram_mb=4096`, bypasses OOMProtector |
| PSI Monitor | 🔴 M1 VIOLATION | Uses `asyncio` instead of AnyIO |
| zRAM monitoring | ❌ MISSING | MemAvailable may be inflated by zRAM |

## Memory Budget: 16GB Allocation

| Workload | RAM | Remaining | Status |
|----------|-----|-----------|--------|
| Fixed overhead (OS+zRAM+engine) | ~4.15 GB | 11.85 GB | — |
| Qwen3-1.7B (Q6_K) | ~3.9 GB | 7.95 GB | ✅ SAFE |
| Qwen3-1.7B × 2 instances | ~7.8 GB | 4.05 GB | ⚠️ MARGINAL |
| MiMo-7B Q4_K_M (32K ctx) | ~8.7 GB | 3.15 GB | ❌ TIGHT |
| Krikri-8B Q4_K_M (8K ctx) | ~7.5 GB | 4.35 GB | ⚠️ MARGINAL |
| 8B + background researcher | ~11.4 GB | 0.45 GB | ❌ OOM IMMINENT |

## Key Finding: zRAM Trap

zRAM is thin-provisioned. `MemAvailable` from `/proc/meminfo` may report ~6 GB when actual usable RAM is ~3-4 GB. PSI `some.avg10` spikes before MemAvailable drops — it's the leading indicator.

## 5 Fixes Required

| Fix | File | Effort |
|-----|------|--------|
| Route background researcher through OOMProtector | loop.py:121 | 1h |
| Remove M1 violation in PSI monitor (asyncio→AnyIO) | psi_monitor.py | 2h |
| Add zRAM physical cost signal (4th signal) | oom_protector.py | 2h |
| Add PSI trigger for proactive eviction (epoll) | psi_monitor.py | 3h |
| Calibrate thresholds for zRAM | oom_protector.py | 1h |
| **Total** | | **~9h** |

## Recommended Architecture: Unified Memory Truth

```
Tier 1: Kernel-Primary (PSI + MemAvailable + cgroup)
Tier 2: Derived (zRAM cost + process RSS + effective available)
Tier 3: Predictive (model weight + KV cache estimate + compute buffer)
Tier 4: Governance (Budget Guard tiers + Admission Controller)
```

The background researcher must acquire a "memory budget token" — check out RAM like a library book, return when done.
