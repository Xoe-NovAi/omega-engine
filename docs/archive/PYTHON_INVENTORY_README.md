<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Python Inventory Documentation

This directory contains comprehensive documentation of the Omega Engine's Python codebase.

## Documents

### 1. **PYTHON_INVENTORY.md** (27 KB)
The complete, exhaustive inventory of all 69 Python files in src/omega/

**Contains:**
- Executive summary with status and work package breakdown
- Detailed descriptions of all 13 CORE files
- Complete CP-1 through CP-8 subsystem documentation
- PP-1 background researcher worker documentation
- Dependency chains and critical import relationships
- Test coverage analysis
- Mandate compliance checklist
- High-priority recommendations

**Use this when:**
- You need to understand a specific file's purpose
- You're looking for dependencies and imports
- You want to see which files have test coverage
- You need detailed mandate compliance information
- Planning refactoring or optimization work

### 2. **PYTHON_QUICK_REFERENCE.md** (9.1 KB)
A condensed quick-lookup guide for rapid navigation

**Contains:**
- File quick access tables (organized by priority)
- Status summary (65% production, 26% beta, 9% stub)
- Work package distribution
- Key dependencies (simplified)
- Test coverage statistics
- Mandate compliance at a glance
- Common task routing ("If I need to modify X...")
- Top 10 largest files
- Import examples

**Use this when:**
- You need to quickly find a file
- You're deciding where to make a change
- You want a one-page overview
- You need to check mandate compliance status

---

## File Statistics

| Metric | Value |
|--------|-------|
| Total Python Files | 69 |
| Total Lines of Code | 20,759 |
| Average File Size | 301 LOC |
| Production Files | 45 (65%) |
| Beta Files | 18 (26%) |
| Stub Files | 6 (9%) |
| Files with Tests | 42 (61%) |
| Files without Tests | 27 (39%) |

---

## Quick Navigation

### By Priority

**Start here if you're new:**
1. `oracle/oracle.py` (1100 LOC) — Entry point
2. `oracle/model_gateway.py` (944 LOC) — Inference pipeline
3. `oracle/entity_registry.py` (746 LOC) — Entity management
4. `cli/oracle_cli.py` (672 LOC) — User commands

### By Size (Top 10)

1. `workers/background_researcher/distiller.py` (1159 LOC)
2. `oracle/oracle.py` (1100 LOC)
3. `oracle/model_gateway.py` (944 LOC)
4. `observability.py` (870 LOC)
5. `oracle/cpu_optimizer.py` (808 LOC)
6. `oracle/entity_registry.py` (746 LOC)
7. `oracle/providers.py` (621 LOC)
8. `cli/oracle_cli.py` (672 LOC)
9. `cli/link_p9_cli.py` (538 LOC)
10. `memory_store.py` (507 LOC)

### By Work Package

- **CORE** (13 files) — Universal engine runtime
- **CP-1** (16 files) — Oracle subsystem
- **CP-2** (5 files) — Agent orchestration (BETA)
- **CP-3** (10 files) — Library & knowledge (mixed)
- **CP-4** (1 file) — Interactive CLI
- **CP-5** (4 files) — Voice & gateway
- **CP-6** (1 file) — Memory persistence
- **CP-7** (2 files) — Routing (BETA)
- **CP-8** (1 file) — Benchmarking
- **PP-1** (16 files) — Background researcher

---

## Common Questions

**Q: Where is the entry point?**
A: `src/omega/oracle/oracle.py` — the `Oracle` class with `talk()` and `summon()` methods

**Q: How does inference work?**
A: Flow is: `oracle.py` → `model_gateway.py` → providers (google, lmster, ollama, etc.)

**Q: Where are entities stored?**
A: YAML-only in `config/wads/{stack_name}/entities.yaml`, managed by `oracle/entity_registry.py`

**Q: How is memory handled?**
A: 4-tier architecture in `memory_store.py`: Hot (dict) → Warm (SQLite) → Cold (YAML/Qdrant)

**Q: What about background research?**
A: `workers/background_researcher/loop.py` orchestrates the full pipeline

**Q: Is there error handling?**
A: Yes, structured hierarchy in `errors.py` with 40+ typed error classes

**Q: How many tests are there?**
A: 42/69 files have tests (61% coverage). See PYTHON_INVENTORY.md for gaps.

**Q: Which mandates are critical?**
A: M1 (AnyIO), M2 (firewall), M7 (local-first), M9 (errors) — all compliant

---

## Mandate Coverage

✅ **Fully Compliant** (12/14):
- M1 — AnyIO Absolute
- M2 — Engine-Stack Firewall
- M3 — Iris Constant
- M4 — Sequentiality
- M6 — Podman Sovereignty
- M7 — Local-First
- M8 — Zero Telemetry
- M9 — Error Integrity
- M10 — Fleet Integrity
- M12 — Queue Integrity
- M13 — Temple-Grade
- M14 — Heritage Vetting

⚠️ **Partially Compliant** (2/14):
- M5 — Gnosis Preservation (BETA distiller needs completion)
- M11 — Soul Integrity (BETA distiller needs completion)

---

## High-Priority Actions

### Sprint 1 (This Week)

1. **Add tests to CP-2 agent orchestration**
   - `subagent_dispatcher.py` (350 LOC)
   - `link_p9_runtime.py` (398 LOC)
   - `orchestration/triage_router.py` (335 LOC)

2. **Complete soul distillation (M5, M11)**
   - `soul_distiller.py` (384 LOC) — add tests
   - `workers/background_researcher/distiller.py` (1159 LOC) — add tests

3. **Stabilize CLI commands**
   - `oracle_cli.py` (672 LOC) — add unit tests
   - `link_p9_cli.py` (538 LOC) — stabilize interface

### Sprint 2

4. **Library subsystem hardening**
   - `extractor.py` (310 LOC) — complete file format support
   - `discovery.py` (403 LOC) — improve classification

5. **Background researcher completion**
   - `credit_budget.py` (191 LOC) — STUB → PRODUCTION
   - `convergence.py` (85 LOC) — STUB → PRODUCTION

---

## Key Insights

1. **Core is solid** — 65% production, all critical files at ✅ status
2. **Agent system is in progress** — CP-2 mostly BETA, needs tests & completion
3. **Library is mixed** — Core aggregator working, extractors need completion
4. **Background researcher is active** — Main loop solid, distillation needs work
5. **Test coverage is good** — 61% overall, 78% for production files
6. **Mandates enforced** — 12/14 fully compliant, 2/14 partially (both BETA)
7. **Heritage documented** — All id-software patterns tagged with [id-soft: doom-1993]

---

## Integration Points

**Key Entry Points:**
- `Oracle.talk()` — User conversation
- `Oracle.summon()` — Direct entity invocation
- `ModelGateway.generate()` — Inference pipeline
- `EntityRegistry.create()` — New entity creation
- `BackgroundResearcherLoop.run()` — Background research

**Key Interfaces:**
- `OmegaError` — All errors inherit from this
- `TraceSession` — Call tracking & observability
- `Entity` — Entity data model
- `ResearchTask` — Research pipeline task
- `MemoryStore` — Memory persistence

---

## Further Reading

- Read **PYTHON_INVENTORY.md** for comprehensive details
- Read **PYTHON_QUICK_REFERENCE.md** for quick lookups
- Read **OMEGA_ENGINE.md** for overall engine architecture
- Read **SOVEREIGN_MANDATES.md** for compliance requirements

---

**Generated**: 2026-06-06
**For questions**: See PYTHON_INVENTORY.md or PYTHON_QUICK_REFERENCE.md
