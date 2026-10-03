<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Admission Control & L3 Cache — Deep Research
**AP Token**: `AP-ADMISSION-L3CACHE-20260726`
**Date**: 2026-07-26 | **Priority**: P0
**Researcher**: Sovereign Researcher

---

## Executive Summary

AdmissionController exists with OOMProtector integration, but RAM estimation is static. No software L3 cache layer exists — only hardware L3 (CPU) is tracked. The engine has no model weight caching/unloading mechanism.

## Current State

| Component | Status |
|-----------|--------|
| AdmissionController (Semaphore + OOM check) | ✅ Implemented |
| OOMProtector (PSI + MemAvailable + cgroup) | ✅ Implemented |
| ResourceGuard (RAM estimation + lock) | ✅ Implemented |
| RAM estimation | ⚠️ Static formula, not dynamic |
| L3 software cache | ❌ Does not exist |
| KV cache eviction | ❌ Does not exist |
| Model load/unload lifecycle | ⚠️ Implicit (process death) |

## RAM Budget (16GB System)

| Workload | RAM | Remaining |
|----------|-----|-----------|
| Fixed overhead | ~4.15 GB | 11.85 GB |
| Qwen3-1.7B (Q6_K) | ~3.9 GB | 7.95 GB ✅ |
| MiMo-7B Q4_K_M (32K ctx) | ~8.7 GB | 3.15 GB ❌ TIGHT |
| 8B + background researcher | ~11.4 GB | 0.45 GB ❌ OOM |

## Recommended Architecture: 3-Tier Local Inference Cache

```
L1: HOT MODEL CACHE — Currently-loaded model, active KV cache
L2: WARM WEIGHT CACHE — mmap'd weights in page cache, no KV
L3: COLD SWAP POOL — GGUF files on SSD, full load required
```

Key additions:
- **KV Cache Growth Predictor** — forward-looking memory estimation
- **ARC Eviction Policy** — dual-queue (recency + frequency) for L2
- **WAIT-style Admission** — flow-controlled admission to prevent eviction cascades

## Implementation Plan

| Phase | Task | Effort |
|-------|------|--------|
| 1 | KV Cache Growth Predictor | 8h |
| 2 | L2 Warm Weight Cache (mmap) | 12h |
| 3 | ARC Eviction Policy for L2 | 6h |
| 4 | WAIT-style Admission | 16h |
| 5 | Grafana Dashboard for Cache Tiers | 4h |
| **Total** | | **~46h** |
