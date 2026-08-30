<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — Quick Reference Guide

**Date**: 2026-06-06 | **Total**: 69 files, 20,759 LOC

---

## File Quick Access

### 🔴 CRITICAL (Start here)

| File | LOC | Status | Purpose |
|------|-----|--------|---------|
| `oracle/oracle.py` | 1100 | ✅ | Entry point, user queries |
| `oracle/model_gateway.py` | 944 | ✅ | Local-first inference (7 providers) |
| `oracle/entity_registry.py` | 746 | ✅ | Entity CRUD (YAML-backed) |
| `cli/oracle_cli.py` | 672 | ✅ | User CLI commands |

### 🟡 SUPPORTING CORE

| File | LOC | Status | Purpose |
|------|-----|--------|---------|
| `observability.py` | 870 | ✅ | Tracing & events |
| `memory_store.py` | 507 | ✅ | 4-tier memory (Hot/Warm/Cold) |
| `cvar_table.py` | 490 | ✅ | Named constants |
| `request_queue.py` | 300 | ✅ | Atomic work queue |
| `constants.py` | 75 | ✅ | ZONEID patterns |
| `errors.py` | 151 | ✅ | Error hierarchy |
| `ics.py` | 276 | ✅ | Session headers |
| `hardware.py` | 43 | ✅ | CPU/RAM detection |

### 🟢 ORACLE SUBSYSTEM (CP-1)

**Entity Management:**
- `entity_workspace.py` (356 LOC) — Scaffold `soul.yaml`, `knowledge/`, `workspace/`
- `session_manager.py` (150 LOC) — Rolling sessions per entity
- `wad_loader.py` (269 LOC) — IWAD/PWAD override system

**Context & Memory:**
- `context_builder.py` (190 LOC) — Inject memory into prompts
- `feed_utils.py` (245 LOC) — Demand signal processing

**Health & Performance:**
- `health_monitor.py` (450 LOC) — Circuit breaker state machine
- `cpu_optimizer.py` (808 LOC) — Zen 2 tuning
- `resource_guard.py` (165 LOC) — Semaphore(1) for OOM protection

**Infrastructure:**
- `capability_registry.py` (123 LOC) — Agent capabilities
- `hierarchy.py` (150 LOC) — 10 Pillar governance
- `gnosis_proxy.py` (112 LOC) — Soul access guard
- `orchestrator.py` (413 LOC) — Cline/OpenCode agent launcher

**Providers:**
- `providers.py` (621 LOC) — Google, LMStudio, Ollama, etc.
- `backends/mock.py` (19 LOC) — Deterministic testing
- `backends/openai_compat.py` (122 LOC) — OpenAI wrapper
- `backends/remote_provider.py` (254 LOC) — Base class + retry

### 🔵 AGENT SYSTEM (CP-2, mostly BETA)

- `subagent_dispatcher.py` (350 LOC) — Handoff protocol
- `link_p9_runtime.py` (398 LOC) — Agent presence tracking
- `soul_distiller.py` (384 LOC) — L1→L2→L3 distillation
- `cli/link_p9_cli.py` (538 LOC) — Agent CLI
- `oracle/handoff.py` (63 LOC) — Protocol structs

### 📚 LIBRARY (CP-3, mixed status)

**PRODUCTION:**
- `library.py` (209 LOC) — Aggregator
- `catalog.py` (221 LOC) — Metadata
- `curator.py` (187 LOC) — Curation pipeline
- `indexer.py` (395 LOC) — Qdrant indexing

**BETA/STUB:**
- `extractor.py` (310 LOC) — Content extraction
- `discovery.py` (403 LOC) — Classification
- `inbox.py` (265 LOC) — Document ingestion
- `greek.py` (245 LOC) — Indexing scheme
- `research.py` (222 LOC) — Stub

### 🎤 VOICE & GATEWAY (CP-5)

- `gateway/server.py` (149 LOC) — FastAPI endpoint
- `iris/server.py` (145 LOC) — Voice assistant
- `iris/matcher.py` (86 LOC) — Intent routing
- `bridge/elevenlabs.py` (67 LOC) — TTS (BETA)

### 🔀 ROUTING (CP-7, BETA)

- `orchestration/triage_router.py` (335 LOC) — Request routing
- `mcp_runtime.py` (97 LOC) — MCP config

### 💾 PERSISTENCE (CP-6)

- `memory/providers.py` (317 LOC) — Redis/Qdrant backends

### 🧪 BENCHMARKING (CP-8)

- `benchmarks/runner.py` (177 LOC) — Performance tests

### 🔬 BACKGROUND RESEARCHER (PP-1)

**PRODUCTION:**
- `background_researcher/loop.py` (497 LOC) — Main loop
- `background_researcher/models.py` (221 LOC) — Data models
- `background_researcher/scheduler.py` (137 LOC) — Topic scheduler
- `background_researcher/review_queue.py` (159 LOC) — Result ranking
- `background_researcher/metrics.py` (61 LOC) — Metrics
- `background_researcher/checkpoint.py` (97 LOC) — State recovery
- `background_researcher/run.py` (104 LOC) — Entrypoint
- `workers/model_updater.py` (480 LOC) — Model downloader

**BETA/STUB:**
- `background_researcher/distiller.py` (1159 LOC) — Largest file, processes results
- `background_researcher/search_fleet.py` (265 LOC) — Multi-engine search
- `background_researcher/searxng_client.py` (107 LOC) — Local search
- `background_researcher/soul_updater.py` (215 LOC) — Write to soul
- `background_researcher/cli.py` (120 LOC) — Researcher CLI
- `background_researcher/convergence.py` (85 LOC) — Convergence detection
- `background_researcher/credit_budget.py` (191 LOC) — API budgeting
- `background_researcher/soul_update_manager.py` (78 LOC) — Coordinator

---

## Status Summary

```
✅ PRODUCTION   = 45 files (65%) — Ready to use
⚠️  BETA        = 18 files (26%) — Feature-complete, active dev
🚧 STUB        = 6 files  (9%)  — Scaffolding only
```

---

## Work Package Summary

```
CORE            13 files    Universal engine runtime
├── CP-1        16 files    Oracle subsystem
├── CP-2         5 files    Agent orchestration (BETA)
├── CP-3        10 files    Library & knowledge (mixed)
├── CP-4         1 file     Interactive CLI
├── CP-5         4 files    Voice & gateway
├── CP-6         1 file     Memory persistence
├── CP-7         2 files    Routing (BETA)
├── CP-8         1 file     Benchmarking
└── PP-1        16 files    Background researcher
```

---

## Key Dependencies

### What imports what?

```
oracle.py (1100 LOC)
  ├── entity_registry (746 LOC)
  ├── model_gateway (944 LOC)
  ├── session_manager (150 LOC)
  ├── context_builder (190 LOC)
  ├── wad_loader (269 LOC)
  ├── entity_workspace (356 LOC)
  ├── hierarchy (150 LOC)
  ├── memory_store (507 LOC)
  ├── triage_router (335 LOC)
  ├── health_monitor (450 LOC)
  └── soul_distiller (384 LOC)

model_gateway (944 LOC)
  ├── backends/* (395 LOC total)
  ├── providers (621 LOC)
  ├── resource_guard (165 LOC)
  ├── health_monitor (450 LOC)
  ├── entity_registry (746 LOC)
  └── gnosis_proxy (112 LOC)

entity_registry (746 LOC)
  ├── entity_workspace (356 LOC)
  ├── constants (75 LOC)
  └── errors (151 LOC)
```

---

## Test Coverage

```
PRODUCTION files with tests:    35/45 (78%)
BETA files with tests:           6/18 (33%)
STUB files with tests:           1/6  (17%)
─────────────────────────────────────────
TOTAL with tests:               42/69 (61%)
```

**Gap areas:**
- `oracle/cpu_optimizer.py` (808 LOC) — Compiled flags, hard to test
- `workers/background_researcher/distiller.py` (1159 LOC) — CRITICAL gap
- `orchestration/triage_router.py` (335 LOC) — Needs tests
- `oracle/subagent_dispatcher.py` (350 LOC) — Needs tests

---

## Mandate Compliance

| Mandate | Status |
|---------|--------|
| M1 — AnyIO Absolute | ✅ |
| M2 — Engine-Stack Firewall | ✅ |
| M3 — Iris Constant | ✅ |
| M4 — Sequentiality | ✅ |
| M5 — Gnosis Preservation | ⚠️ (BETA distiller) |
| M6 — Podman Sovereignty | ✅ |
| M7 — Local-First | ✅ |
| M8 — Zero Telemetry | ✅ |
| M9 — Error Integrity | ✅ |
| M10 — Fleet Integrity | ✅ |
| M11 — Soul Integrity | ⚠️ (BETA distiller) |
| M12 — Queue Integrity | ✅ |
| M13 — Temple-Grade | ✅ |
| M14 — Heritage Vetting | ✅ |

---

## Common Tasks

### "I need to modify X"

**User queries?** → Edit `oracle/oracle.py` (1100 LOC)

**Inference pipeline?** → Edit `oracle/model_gateway.py` (944 LOC)

**Entity creation?** → Edit `oracle/entity_registry.py` (746 LOC)

**Add new provider?** → Edit `oracle/providers.py` (621 LOC)

**CLI commands?** → Edit `cli/oracle_cli.py` (672 LOC)

**Circuit breaker logic?** → Edit `oracle/health_monitor.py` (450 LOC)

**Memory management?** → Edit `memory_store.py` (507 LOC)

**Background research?** → Edit `workers/background_researcher/loop.py` (497 LOC)

---

## File Sizes (Top 10)

```
1. workers/background_researcher/distiller.py — 1159 LOC
2. oracle/oracle.py — 1100 LOC
3. oracle/model_gateway.py — 944 LOC
4. observability.py — 870 LOC
5. oracle/cpu_optimizer.py — 808 LOC
6. oracle/entity_registry.py — 746 LOC
7. oracle/providers.py — 621 LOC
8. cli/oracle_cli.py — 672 LOC
9. cli/link_p9_cli.py — 538 LOC
10. memory_store.py — 507 LOC
```

---

## Import It

```python
# Main entry point
from omega.oracle import Oracle, OracleResponse

# Entities
from omega.oracle import EntityRegistry, Entity

# Providers
from omega.oracle import ModelGateway

# CLI
from omega.cli.oracle_cli import app  # Typer CLI

# Workers
from omega.workers import ModelUpdaterWorker, BackgroundResearcherLoop

# Errors
from omega.errors import OmegaError, ProviderError, InferenceError

# Observability
from omega.observability import TraceSession, EventType

# Constants
from omega.constants import ZONEID_ENTITY, validate_zoneid

# Memory
from omega.memory_store import get_memory_store

# Library
from omega.library import Library

# Iris
from omega.iris import matcher, server
```

---

**Generated**: 2026-06-06 | **Next Update**: Post-Sprint-1
