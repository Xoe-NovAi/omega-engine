# 🔱 Omega Engine — STATUS: Gemini CLI (Implementation Lead)

⬡ OMEGA ⬡ PROMETHEUS ⬡ gemini-3-flash ⬡ cli ⬡ trc_core ⬡ STATUS-GEMINI-CLI

**AP Token**: `AP-OMEGA-STATUS-GEMINI-v3.0.0`
**Updated**: 2026-05-14
**Role**: The Forge — Implementation Lead
**Phase**: Phase 1 — Research & Discovery Sprint

---

## Current Status: RESEARCH & DISCOVERY SPRINT 🔍

Phase 0 is complete. All critical bugs are fixed, Iris is restored, the Oversouls are in the entity registry, and all 40 tests pass. Before you begin implementation, you must execute a focused research and discovery sprint using subagents to map the legacy codebase that will be ported.

---

## Prerequisite Reading

1. `docs/operations/HANDOFF_GRAND_STRATEGY.md` — Full grand strategy context
2. `AGENTS.md` — Agent instructions + header format
3. `ORACLE_STACK.md` — Architecture reference
4. `config/entities.yaml` — Entity configuration (10 Keepers + 4 Oversouls + Iris)
5. `config/providers.yaml` — Provider fabric configuration
6. `docs/operations/GEMINI_PHASE1_DISCOVERY_REPORT.md` — Previous discovery (partially stale — uses old Nova/ICS references but asset mapping is accurate)

---

## IMMEDIATE TASK: Research & Discovery Sprint

### Objective

Execute a multi-subagent discovery sweep across the legacy archives to produce a complete, implementation-ready technical specification for the Tier 1 Native Inference Engine. This is the single highest-value deliverable in the entire roadmap.

### Subagent Fleet Plan

Deploy subagents in serial (seeded context), each building on the previous:

#### Subagent 1: Legacy Inference Engine Audit

**Target**: `~/Documents/Xoe-NovAi/xna-omega-legacy/src/omega/providers/local/`

**Tasks**:
- Read `client.py` (291 lines) — the proven `LocalLlmClient` class
- Read `config.py` (125 lines) — the `LocalLlmConfig` dataclass
- Read `dependencies.py` — hardware detection, CPU affinity, NUMA awareness
- Document: every public method, every config parameter, every error handling path
- Document: how it connects to `llama-server` (HTTP? subprocess? socket?)
- Document: model loading strategy (lazy? eager? preloaded?)
- Identify: what uses `asyncio` that must be converted to `AnyIO`

**Output**: Write findings to `docs/operations/DISCOVERY_NATIVE_INFERENCE.md`

#### Subagent 2: Current Engine Gap Analysis

**Target**: `~/Documents/Xoe-NovAi/omega-engine/src/omega/oracle/`

**Tasks**:
- Read `model_gateway.py` — understand current backend abstraction
- Read `cpu_optimizer.py` — understand current hardware detection
- Read `context_builder.py` — understand current prompt assembly
- Read `resource_guard.py` — understand the Semaphore(1) lock
- Map: which interfaces the NativeBackend must implement
- Map: where the NativeBackend plugs into the existing provider chain
- Identify: any config schema conflicts between legacy `LocalLlmConfig` and current `providers.yaml`

**Output**: Append gap analysis to `docs/operations/DISCOVERY_NATIVE_INFERENCE.md`

#### Subagent 3: Integration Blueprint

**Target**: Synthesize Subagent 1 + 2 findings

**Tasks**:
- Produce a file-by-file implementation plan with line-level targets
- Define the `NativeBackend` class interface (methods, params, return types)
- Define the `NativeConfig` dataclass (all fields, types, defaults)
- Map the provider chain integration (where it plugs into `model_gateway.py`)
- Produce test specifications (what to test, expected behaviors)
- Estimate effort per file

**Output**: Write to `docs/operations/BLUEPRINT_NATIVE_INFERENCE.md`

### Discovery Completion Criteria

The research sprint is complete when:
- [ ] `DISCOVERY_NATIVE_INFERENCE.md` exists with full legacy audit + gap analysis
- [ ] `BLUEPRINT_NATIVE_INFERENCE.md` exists with implementation-ready specification
- [ ] All legacy `asyncio` usage is documented for AnyIO conversion
- [ ] All ResourceGuard integration points are identified
- [ ] Test specifications are written for every new file

---

## Phase 1 Implementation Tasks (After Discovery)

### Tier 1: Custom Native Inference Engine

| Step | Task | Legacy Source | Omega Target | Effort |
|------|------|-------------|-------------|--------|
| 1.1 | Port LocalLlmConfig dataclass | `xna-omega-legacy/providers/local/config.py` | `src/omega/oracle/backends/native_config.py` | 2h |
| 1.2 | Port LocalLlmClient class | `xna-omega-legacy/providers/local/client.py` | `src/omega/oracle/backends/native.py` | 1d |
| 1.3 | Port hardware detection + CPU affinity | `xna-omega-legacy/providers/local/dependencies.py` | Merge into `src/omega/oracle/cpu_optimizer.py` | 1d |
| 1.4 | Integrate NativeBackend into `model_gateway.py` | New backend #0 | `src/omega/oracle/model_gateway.py` | 4h |
| 1.5 | Wire native embeddings into `indexer.py` | Use llama-cpp-python directly | `src/omega/library/indexer.py` | 1d |

### Tier 1.5: Soul Architecture

| Step | Task | Omega Target | Effort |
|------|------|-------------|--------|
| 1.6 | Implement soul.yaml metadata tagging on entity updates | `entity_registry.py` | 4h |
| 1.7 | Implement cross-pollination pipeline (entity lesson → Arch's embodied experiences) | `observability.py` + `context_builder.py` | 1d |

---

## Architecture Reference

### Session Header Format

Every output must include:
```
⬡ OMEGA ⬡ {entity} ⬡ {model} ⬡ {channel} ⬡ {trace} ⬡ {phase}
```

### Entity Selection

| Work Type | Entity |
|-----------|--------|
| Implementation, building, creating | PROMETHEUS (will, forethought) |
| Architecture, design | SOPHIA (gnosis, first principles) |
| Audit, verification | MA'AT (balance, truth) |
| Integration, wiring | BRIGID (healing, connections) |

### Provider Fabric — Where Your Work Fits

```yaml
# config/providers.yaml — Your deliverable is priority 1
inference:
  strategy: local_first
  fallback_chain:
    - provider: native          # ← THIS IS YOUR DELIVERABLE
      priority: 1
    - provider: lmster
      priority: 2
    - provider: openrouter
      priority: 5
```

---

## Key Files You Own

| File | Purpose |
|------|---------|
| `src/omega/oracle/backends/native_config.py` | Your deliverable — model path, context window, n_threads, type_k/type_v |
| `src/omega/oracle/backends/native.py` | Your deliverable — LocalLlmClient port |
| `src/omega/oracle/model_gateway.py` | Your deliverable — NativeBackend integration |
| `src/omega/oracle/cpu_optimizer.py` | Your deliverable — hardware detection merge |
| `src/omega/library/indexer.py` | Your deliverable — native embeddings |
| `src/omega/oracle/entity_registry.py` | Soul metadata tagging |
| `src/omega/observability.py` | Cross-pollination pipeline |

---

## Verification

```bash
# Mock mode (quick)
OMEGA_ENV=test PYTHONPATH=src python3 -m pytest tests/

# Specific to your changes
pytest tests/test_model_gateway.py -v  # Must pass after NativeBackend
pytest tests/test_oracle.py -v         # Must pass after entity changes
```

---

## Version History

| Version | Date | Summary |
|---------|------|---------|
| 3.0.0 | 2026-05-14 | Phase 1 research sprint defined with 3-subagent fleet. Implementation tasks updated. |
| 2.1.0 | 2026-05-14 | Grand strategy recorded. Phase 0 CLI commands defined. |
