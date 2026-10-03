<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Vector Collections, Background Researcher, Oracle CLI, Model Gateway — Deep Research
**AP Token**: `AP-P1-BATCH1-20260726`
**Date**: 2026-07-26 | **Priority**: P1
**Researcher**: Sovereign Researcher

---

## Gap 1: Vector Collections (R5)

### Executive Summary

7 named collections in SQLite-vec adapter, but only `omega_vec_gemma_768` is actively used. Qdrant adapter is deprecated but not removed. No collection usage telemetry.

### Collections

| Collection | Dimension | Used? |
|------------|-----------|-------|
| omega_vec_gemma_768 | 768 | ✅ Active (library indexer) |
| omega_vec_nomic_768 | 768 | ⚠️ Fallback |
| omega_vec_nomic_512 | 512 | ❌ Unused |
| omega_vec_nomic_256 | 256 | ❌ Unused |
| omega_vec_minilm_384 | 384 | ❌ Unused |
| omega_vec_static_64 | 64 | ❌ Unused |
| omega_vec_library_256 | 256 | ❌ Unused |

### Effort: ~10h

---

## Gap 2: Background Researcher (R18)

### Executive Summary

Fully-featured autonomous research state machine (17 modules, ~3000 lines). Runs via systemd timer every 20 minutes. Two deprecated circuit breakers. RotationState is ephemeral (resets on restart). No web search result persistence for interactive sessions.

### State Machine

```
IDLE → TRIAGE → SEARCH → EXTRACT → DISTILL → CONVERGE → UPDATE → IDLE
```

### Issues

1. Two deprecated circuit breakers (search_fleet.py, distiller.py)
2. RotationState resets to index 0 on every systemd invocation
3. Sovereign Ingestion Pipeline dependency hardcoded
4. No web search result persistence for interactive sessions

### Effort: ~21h

---

## Gap 3: Oracle CLI (R21)

### Executive Summary

1043-line god-file with 25+ commands in one file. YouTube, Bundle, Vault already extracted to sub-CLIs — pattern works. 10 sub-CLIs proposed.

### Decomposition

| Sub-CLI | Commands | Lines |
|---------|----------|-------|
| omega oracle | talk, summon, default-entity, entity, list-entities, add-entity | ~250 |
| omega provider | backends, model-status | ~40 |
| omega queue | queue-status, process-queue, review-pending, queue-prune | ~70 |
| omega library | library-curate, library-status, library-search | ~55 |
| omega bench | bench-run, bench-compare, bench-rank, bench-list | ~85 |
| omega feed | check-feed, demand-status, demand-claim, demand-fulfill | ~100 |
| omega worker | worker-spawn | ~25 |
| omega governance | vet, soul-stage | ~45 |
| omega obs | hardware-stats | ~100 |

### Effort: ~16.5h

---

## Gap 4: Model Gateway (R30)

### Executive Summary

1529-line god-module. `generate()` method is 295 lines. Legacy `_try_*` methods are dead code. Sovereign sampling (Gemma 4 logit bias) is hardcoded.

### Sub-modules to Extract

| Module | Responsibility | Lines |
|--------|---------------|-------|
| generate_pipeline.py | Decompose generate() into stages | ~150 |
| config_merger.py | Config parsing + provider instantiation | ~100 |
| legacy_backends.py | Dead _try_* methods (or delete) | ~100 |
| health_check.py | Consolidate health check methods | ~50 |

### Effort: ~15h

---

## Summary

| Gap | Effort | Priority |
|-----|--------|----------|
| Vector Collections | 10h | Medium |
| Background Researcher | 21h | High |
| Oracle CLI | 16.5h | Medium |
| Model Gateway | 15h | High |
