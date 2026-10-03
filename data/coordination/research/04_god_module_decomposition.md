<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# God-Module Decomposition — Deep Research
**AP Token**: `AP-GODMODULE-DECOMP-20260726`
**Date**: 2026-07-26 | **Priority**: P0 — Structural Debt Gate
**Researcher**: Sovereign Researcher

---

## Executive Summary

6 files exceed 1000 lines, violating single responsibility. Phase D features will grow them further. Adding features to 1K+ files is structural regression.

## Files Audited

| File | Lines | Responsibilities | Extractable Modules |
|------|-------|-----------------|---------------------|
| **model_gateway.py** | 1432 | Routing, providers, generation, health, config, OOM | 6 modules |
| **observability/__init__.py** | 1380 | Traces, events, metrics, logs, dashboard | 5 modules |
| **oracle.py** | 1348 | talk(), summon(), close_session(), config, memory, soul | 5 modules |
| **distiller.py** | 1186 | L1→L2→L3 pipeline, T1/T2/T3 backends, convergence, circuit breaker | 5 modules |
| **memory_store.py** | 1110 | FTS5, vec0, hybrid search, TTL, decay, promotion | 4 modules |
| **oracle_cli.py** | 1036 | REPL, commands, entity discovery, system info, help | 4 modules |

## model_gateway.py Decomposition (1432 → ~350 lines)

| Extract To | What | Lines |
|------------|------|-------|
| `providers/registry.py` | Provider registration, health tracking, fallback chain | ~250 |
| `providers/factory.py` | Provider creation, model resolution | ~200 |
| `generation/streaming.py` | Chunk timeout, heartbeat, streaming pipeline | ~200 |
| `generation/policy.py` | GenerationPolicy, temperature, logit_bias (Gemma fix) | ~150 |
| `admission/memory_budget.py` | OOMProtector integration, RAM estimation | ~150 |
| `model_gateway.py` (remaining) | Facade: talk(), route(), status() | ~350 |

## observability/__init__.py Decomposition (1380 → ~200 lines)

| Extract To | What | Lines |
|------------|------|-------|
| `observability/traces.py` | Trace creation, span management, context propagation | ~300 |
| `observability/events.py` | Event recording, structured logging | ~250 |
| `observability/metrics.py` | Metrics collection, aggregation, export | ~250 |
| `observability/dashboard.py` | Dashboard rendering, SSE streaming | ~200 |
| `observability/__init__.py` (remaining) | Facade + public API | ~200 |

## Decomposition Strategy

1. **Extract facade pattern**: Each god module becomes a thin facade that imports from sub-modules
2. **No behavior changes**: Pure structural refactoring, no logic changes
3. **Test after each extraction**: Run full test suite after each module extraction
4. **Parallel extraction possible**: Different files can be decomposed independently

## Migration Strategy

| Phase | Files | Effort |
|-------|-------|--------|
| 1 | Dead code cleanup (140 lines from model_gateway) | 30min |
| 2 | Remove deprecated circuit breaker classes (170 lines from distiller) | 30min |
| 3 | Extract observability sub-modules | 4h |
| 4 | Extract model_gateway sub-modules | 4h |
| 5 | Extract oracle.py sub-modules | 4h |
| 6 | Extract memory_store sub-modules | 3h |
| 7 | Extract distiller sub-modules | 3h |
| 8 | Extract oracle_cli sub-modules | 2h |
| **Total** | | **~21h** |
