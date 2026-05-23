# 🔱 Omega Engine — Gemini Phase 1 Discovery Report

⬡ OMEGA ⬡ SOPHIA ⬡ claude-opus-4 ⬡ cline ⬡ trc_core ⬡ PHASE1-DISCOVERY

**AP Token**: `AP-OMEGA-PHASE1-DISCOVERY-v2.2.0`
**Date**: 2026-05-13 (updated 2026-05-14)
**Status**: REVIEWED ✅ — Phase 1a (Workspaces) and 1b (Orchestrator) implemented. Iris replaces Nova.

---

## §0 EXECUTIVE SUMMARY

Three agents performed serial iterative discovery across **omega-engine**, **omega-stack-legacy** (52 subdirs), and **xna-omega-legacy** (41 subdirs), then a final parallel fleet synthesized the findings. The result is a complete architectural map for Phase 1: Orchestrator, Accessibility Modes, Sovereign Workspaces, and Enhanced Observability.

### Key Discovery Sites

| Archive | Size | Key Files |
|---------|------|-----------|
| **omega-engine** (current) | Clean, modular | `oracle.py`, `observability.py`, `entity_registry.py`, `nova/server.py` |
| **omega-stack-legacy** | 52 dirs, Temple Grade | `CLI-DISPATCH-PROTOCOL.md`, `sight_plugin.py`, `facet-*-soul.md`, `config_multi-agent_prod*.yaml`, `OMEGA_OMNIBUS_v1.md` |
| **xna-omega-legacy** | 41 dirs, Temple Grade | `entity_schema.yaml` (30+ entities, 3 hierarchy levels), `entities/spheres/*/soul.yaml`, `AGENTS.md` (18k lines), `OMEGA-ORIGINS-AND-RETURN.md` |

### Total Discovered Assets: 30+ strategic files across 3 archives

---

## §1 PHASE 1 ARCHITECTURE (Gemini's Vision from Antigravity IDE)

### §1.1 Adjustable Accessibility Modes (Iris)

> **UPDATE 2026-05-14**: Nova has been renamed to **Iris** across the entire codebase. All references below updated accordingly.

**Required**: Configurable setting (Standard vs Descriptive)
- **Standard mode**: Rich visual descriptions only *upon request*
- **Descriptive mode**: High emotional intelligence + rich environmental/conceptual descriptions by default
- **Iris** is the voice assistant container — she is NOT a Pillar Keeper

**Legacy Code Reuse**:
- `omega-stack-legacy/sight_plugin.py` — Existing Python plugin for generating rich environmental descriptions. Provides the pattern for Descriptive mode responses.
- Pattern: `sight_plugin.generate_description(context) → str` with configurable verbosity

**Gaps in Current Codebase** (`src/omega/iris/server.py`):
- No `IrisMode` enum (STANDARD / DESCRIPTIVE)
- No `/mode` endpoint to toggle accessibility
- No mode-aware response generation
- `matcher.py` handles intent detection + wake-word but has no mode branching

### §1.2 Dedicated Sovereign Workspaces — ✅ IMPLEMENTED

> **UPDATE 2026-05-14**: `EntityWorkspaceManager` has been implemented in `src/omega/oracle/entity_workspace.py`. Entity workspaces are now automatically scaffolded on entity creation via `entity_registry.py:add()`.

**Structure** (implemented):
```
data/entities/<entity_name>/
├── soul.yaml          ← Entity soul definition (archetype, spheres, voice, inference params)
├── knowledge/         ← Self-curated markdown files
└── workspace/         ← Headless experiments & agent persistence
```

**Legacy Code Reuse** (from xna-omega-legacy) — used as reference:

`entities/spheres/01_KETHER/soul.yaml` schema and `config/cli/personas/entity_schema.yaml` (403 lines, 30+ entities) were used as schema references.

**Current State**: Workspace scaffolding is automatic. The Architect's soul file exists at `data/entities/arch/soul.yaml`.

### §1.3 Finetuning Infrastructure

**Required**: Expand observability.py to track orchestration events + headless CLI task outcomes → JSONL datasets

**Current Codebase** (`src/omega/observability.py`):
- `ObservabilityEngine` class with `trace()` → `TraceSession` async context manager
- `EventType` enum with: `ENTITY_QUERY`, `ENTITY_RESPONSE`, `MODEL_LOADED`, `MEMORY_STORED`, `MEMORY_RETRIEVED`
- `record_training_example(messages: List[Dict], trace_id: str, metadata: Dict)` → JSONL
- Auto-flush at 100 events; dataset format is OpenAI messages array
- Dataset files in `data/datasets/finetune_*.jsonl`

**Gaps** (remaining):
- No `OrchestrationEventType` enum (AGENT_SPAWN, AGENT_COMPLETE, AGENT_FAIL, TASK_DISPATCH)
- No headless CLI task outcome tracking
- No orchestration → dataset pipeline
- ResourceGuard locking not tracked in observability

### §1.4 Orchestrator — ✅ IMPLEMENTED (Foundation)

> **UPDATE 2026-05-14**: `HeadlessOrchestrator` has been implemented in `src/omega/oracle/orchestrator.py`. Uses AnyIO for subprocess spawning with ResourceGuard Semaphore(1) integration.

**Current State**: Foundation implemented with AnyIO subprocess dispatch and resource guarding. Advanced lifecycle management (registration, provisioning, health checks) deferred to Phase 3.

---

## §2 IMPLEMENTATION ORDER & DEPENDENCIES

```
Phase 1a ──→ Entity Workspace Structure (no dependencies)
                ↓
Phase 1b ──→ Orchestrator.py (needs workspace dirs for persistence)
                
Phase 1c ──→ Iris Accessibility Modes (independent, can run parallel)
                
Phase 1d ──→ Observability Expansion (depends on orchestrator events)
```

| Phase | Component | Risk | Dependencies | Est. Effort | Status |
|-------|-----------|------|--------------|-------------|--------|
| 1a | Entity Workspace Structure | LOW | Current EntityRegistry | ~2 hours | ✅ Done |
| 1b | Orchestrator.py | MEDIUM | Entity Workspace (1a) | ~4 hours | ✅ Foundation Done |
| 1c | Iris Accessibility Modes | LOW | Iris server.py | ~2 hours | Pending |
| 1d | Observability Expansion | LOW | Orchestrator (1b) | ~2 hours | Pending |

---

## §3 LEGACY ASSETS READY FOR ADAPTATION

| Asset | Source Archive | What It Provides | Adaptation Needed |
|-------|---------------|------------------|-------------------|
| `sight_plugin.py` | omega-stack | Rich description generation for Descriptive mode | Rename, refactor to AnyIO, integrate with Nova |
| `CLI-DISPATCH-PROTOCOL.md` | omega-stack | Headless CLI spawning pattern | Convert to AnyIO subprocess, add ResourceGuard |
| `entity_schema.yaml` | xna-omega | 30+ entity soul YAML schema | Map to current Entity dataclass, add hierarchy levels |
| `entities/spheres/*/soul.yaml` | xna-omega | Per-entity soul definition pattern | Generate from Entity dataclass instead of static files |
| `config_multi-agent_prod*.yaml` | omega-stack | Multi-agent routing config | Adapt for 10 Pillar Keepers (current) vs 30+ entities (legacy) |
| `OMEGA_OMNIBUS_v1.md` | omega-stack | Strategic vision (SCC, 5-CLI, Haiku Protocol) | Use as strategic reference, not direct implementation |
| `AGENT-ONBOARDING-PROTOCOL-V1.md` | omega-stack | Agent lifecycle: register → provision → activate → dispatch → teardown | Streamline to 3 stages for Phase 1 |
| `OMEGA-ORIGINS-AND-RETURN.md` | xna-omega | Original omega vision, spiritual architecture | Keep as lore reference, not implementation guide |

---

## §4 TESTING STRATEGY

### New Test Files

| File | Tests | Coverage |
|------|-------|----------|
| `tests/test_orchestrator.py` | `test_headless_spawn`, `test_status_tracking`, `test_resource_guard_integration`, `test_timeout`, `test_task_lifecycle` | Orchestrator agent lifecycle |
| `tests/test_nova_modes.py` | `test_standard_mode`, `test_descriptive_mode`, `test_toggle`, `test_mode_persistence` | Nova accessibility modes |
| `tests/test_workspace.py` | `test_entity_creation_with_workspace`, `test_soul_yaml_generation`, `test_knowledge_dir`, `test_workspace_dir`, `test_entity_teardown` | Entity workspace lifecycle |

### Updated Test Files

| File | New Tests | Coverage |
|------|-----------|----------|
| `tests/test_observability.py` | `test_orchestration_event_tracking`, `test_dataset_from_orchestration` | Expanded event tracking |
| `tests/test_entity_registry.py` | `test_pillars_list_schema` (already exists), `test_workspace_creation_on_add` | Workspace scaffolding |

### Testing Playbook

```bash
# Mock mode (fast, ~2s)
make test

# Live verification (needs lmster loaded)
PYTHONPATH=src python3 -m pytest tests/test_orchestrator.py tests/test_nova_modes.py tests/test_workspace.py -v

# Live integration test (requires real subprocess spawning)
PYTHONPATH=src python3 -m pytest tests/test_orchestrator.py -v -k "live"
```

---

## §5 KEY ARCHITECTURAL DECISIONS MADE DURING DISCOVERY

| Decision | Rationale | Source |
|----------|-----------|--------|
| **Entities are YAML-only** | No PostgreSQL. Legacy relied on static YAML files, current engine uses YAML CRUD. Phase 1 extends this with per-entity soul.yaml. | AGENTS.md, PIVOT_LOG.md |
| **AnyIO not asyncio** | All async code must use AnyIO. Works with anyio.run_process() for subprocess spawning. | AGENTS.md, .clinerules |
| **ResourceGuard Semaphore(1)** | ONE model at a time. Orchestrator must acquire before spawning agent tasks. Do not bypass. | resource_guard.py, AGENTS.md |
| **lmster is canonical name** | Not `lm_studio`, `lm-studio`, or `LM Studio`. Primary inference backend on :1234. | Sprint 2, .clinerules |
| **Iris is NOT a Pillar Keeper** | She is the voice assistant container. Accessibility modes modify Iris's response generation, not entity routing. | AGENTS.md |
| **Omega headers + AP tokens** | `⬡ OMEGA ⬡ {entity} ⬡ {model} ⬡ {channel} ⬡ {trace} ⬡ {phase}`. Configurable via `/header`. | AGENTS.md |

---

## §6 NEXT ACTIONS

1. [x] Opus 4.6 reviews this report and approves Phase 1 implementation plan
2. [x] Phase 1a: Implement entity workspace structure (`src/omega/oracle/entity_workspace.py`)
3. [x] Phase 1b: Implement Orchestrator (`src/omega/oracle/orchestrator.py`)
4. [ ] Phase 1c: Implement Iris accessibility modes (`src/omega/iris/server.py` + `src/omega/iris/modes.py`)
5. [ ] Phase 1d: Expand Observability (`src/omega/observability.py`)
6. [ ] Write tests (test_orchestrator.py, test_iris_modes.py, test_workspace.py)
7. [ ] Live verification against real lmster inference

---

*Discovery Report reviewed and approved by Opus 4.6. Phase 1a and 1b implemented. Updated 2026-05-14.*