<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Phase 3 — Code Structure, Data Architecture, Sync I/O Audit

**Timestamp**: 2026-07-30T06:30Z

## 1. SQLite database footprint
Current `data/*.db` files:
- `omega_memory.db` 118M primary
- `metrics.db` 504K + `latency_metrics.db` 408K observability
- `workbench.db` 236K
- `search_history.db` 76K
- `model_study.db` 44K
- `state/index.db` 24K
- `youtube_research/provenance.db` 40K
- `archive/.crush/crush.db` 404K

There is also a secondary memory copy path under `data/memory/omega_memory.db` referenced in older docs; present size unclear from this scan because I did not descend into every subdir.

**Gap status**: PROCESS_IMPROVEMENT_PLAN’s consolidation plan remains valid. No regression evidence, but also no consolidation executed.

## 2. Breaker count update
- `rg class.*Breaker/breaker` in `src/omega` + `mcp_servers`: **18** hits.
- Earlier docs cite 17.
- Delta from new matches in `workers/background_researcher/search_fleet.py`, `distiller.py`, `ingestion/pipeline.py`, `oracle/health_monitor.py`, `oracle/search_circuit_breaker.py`, `council/failure_layer.py`, `research/sandbox.py`.
- **Action**: update plan number to 18; still pybreaker candidate.

## 3. YAML / sync I/O audit
- Broader scan found 60 `yaml.safe_load` references across `src/omega`.
- Hot-path review shows:
  - `entity_workspace.py` uses `anyio.to_thread.run_sync` for several YAML/read paths — good.
  - `soul_updater.py` uses `await anyio.Path.read_text` plus inline `yaml.safe_load`, then `await anyio.Path.write_text`. This is still effectively **single-writer async, but no cross-process lock**.
  - `entity_registry.py` uses `fcntl.flock` for cross-process locking, confirming the cross-process mechanism exists elsewhere.
  - `config/loader.py`, `cli/bundle.py`, `oracle/hierarchy.py`, `model_registry/registry.py`, and `meditate/lens_registry.py` are mostly sync; some bundle paths delegate to `anyio.to_thread`.

**Gap status**: GAP-01 race condition is still **execution-open** because `soul_updater.py` does not call the existing `with_soul_lock()` path. Fix is straightforward and should remain P0.

## 4. Council / concurrency / god modules
- `council/failure_layer.py` has `CircuitBreaker`/`CircuitBreakerState`.
- Prior notes cite WAL TODO in `council/coordator.py` at line ~194; still likely open from earlier reports.
- God-module gap unresolved: `memory_store.py` 1114+ lines, `library/` multi-file CMS creep.

---
*⬡ OMEGA ⬡ CLINE ⬡ KNOWLEDGE-GAP RESEARCH ⬡ PHASE 3 ⬡ 2026-07-30*