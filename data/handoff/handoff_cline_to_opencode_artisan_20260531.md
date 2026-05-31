# 🔱 Handoff: Cline (The Artisan) → OpenCode Builder Agents
# AP-OMEGA-HANDOFF-v1.0.0
# ⬡ OMEGA ⬡ THOTH ⬡ MiMo-2.5 ⬡ trc_core ⬡ HANDOFF-ARTISAN

> **Purpose**: Structured handoff of tasks from Cline (The Artisan) to
> OpenCode builder agents. OpenCode is confirmed running and capable.
> Tasks are ordered by priority for the builder agent fleet.

**Status**: READY FOR FLEET EXECUTION
**Handoff Date**: 2026-05-31
**OpenCode Status**: ✅ Launches clean, 7 valid agents in `.opencode/agents/`

---

## Current Engine State

| Metric | Value | Source |
|--------|-------|--------|
| Phase | 1 — Engine Hardening | OMEGA_ENGINE.md |
| Source files | 60 .py files | OMEGA_ENGINE.md |
| Test functions | 278 | OMEGA_ENGINE.md |
| MCP Hub tools | 41 MCP + 8 HTTP | OMEGA_ENGINE.md |
| Providers configured | 8 (local-first) | OMEGA_ENGINE.md |
| OpenCode agents | 7 valid (doom_guy, jem, jem_discovery, jem_synthesis, jem_verification, plan, reviewer, tester) | `.opencode/agents/` |
| Git HEAD | `067a326` — "fix: move 13 invalid agent files to archives" | `git log -1` |

**Key Documents** (must read before any work):
1. `OMEGA_ENGINE.md` — Single Source of Truth (235 lines)
2. `SOVEREIGN_MANDATES.md` — 9 constitutional laws (62 lines)
3. `docs/strategy/LOGGING_ERROR_HANDLING_ARCHITECTURE.md` — NEW: error taxonomy (250 lines)
4. `docs/strategy/SYSTEMS_HARDENING_PLAN.md` — Agent/MCP/workflow hardening plan (747 lines)
5. `docs/operations/BUG_LOG.md` — Bug tracking (3 open, 1 resolved)
6. `.clinerules` — Cline-specific rules (184 lines)
7. `AGENTS.md` — OpenCode-specific rules (references SST)

---

## Task Queue for Builder Agents

### TASK-001 [P0]: Create `src/omega/oracle/exceptions.py`

**Spec**: `docs/strategy/LOGGING_ERROR_HANDLING_ARCHITECTURE.md` §1

**Requirements**:
- Implement full `OmegaError` hierarchy as defined in §1.1
- Base class `OmegaError` with `.trace_id`, `.cause`, `.context`, `.to_dict()`
- No external dependencies beyond stdlib
- Must import cleanly without circular imports
- File path: `src/omega/oracle/exceptions.py`

**Acceptance Criteria**:
- `from omega.oracle.exceptions import ProviderError, ConnectionError` works
- `raise ProviderError("test", trace_id="trc_test", context={"key": "val"})` preserves all fields
- `OmegaError.to_dict()` returns valid dict with `error`, `message`, `trace_id`, `cause`, `context`
- Pytest script confirms all exception subtypes can be instantiated and caught

### TASK-002 [P0]: Wire `OmegaError` into ObservabilityEngine

**Spec**: `docs/strategy/LOGGING_ERROR_HANDLING_ARCHITECTURE.md` §4.2

**Requirements**:
- `ObservabilityEngine.log_event(error=...)` accepts `OmegaError` and calls `.to_dict()`
- Add `ObservabilityEngine.alert_if(threshold=5, window_minutes=5)` — error rate spike detection
- Crash dump trigger on `logger.critical()`: write `data/crashes/crash_{timestamp}_{trace_id}.json`
- Health check data: `omega_hub.health()` MCP tool showing provider status, memory counts, recent errors

**Acceptance Criteria**:
- `ObservabilityEngine.log_event("error", trace_id, {"error": omega_error_instance})` enriches the event dict with structured error fields
- `omega_hub.health()` returns JSON with `providers`, `memory`, `circuit_breakers`, `recent_errors`
- Crash dump file written when `observability.log_critical()` is called

### TASK-003 [P0]: Add `omega_hub.health()` MCP Tool

**Spec**: `docs/strategy/LOGGING_ERROR_HANDLING_ARCHITECTURE.md` §4.2

**Requirements**:
- New MCP tool in `mcp_servers/omega_hub/server.py`
- Returns: provider status (available/unavailable), circuit breaker states, memory tier counts, recent error count
- Used by systemd health check and monitoring
- Must not block (fast, cached data)

### TASK-004 [P1]: Audit & Convert `except Exception:` in MemoryStore

**Spec**: `docs/strategy/LOGGING_ERROR_HANDLING_ARCHITECTURE.md` §8

**Requirements**:
- File: `src/omega/memory_store.py` — 8 bare `except Exception:` clauses
- Convert each to specific `OmegaError` subtypes (MemoryError, SerializationError, IntegrityError)
- Each catch must: log with `logger.warning/error`, propagate `trace_id`, use `raise ... from e`
- Add error path tests per §7

### TASK-005 [P1]: Audit & Convert `except Exception:` in Oracle

**Spec**: `docs/strategy/LOGGING_ERROR_HANDLING_ARCHITECTURE.md` §8

**Requirements**:
- File: `src/omega/oracle/oracle.py` — 9 bare `except Exception:` clauses
- Convert each to specific `OmegaError` subtypes
- Ensure public methods (`talk`, `summon`) wrap internal exceptions

### TASK-006 [P1]: Audit & Convert `except Exception:` in Providers

**Spec**: `docs/strategy/LOGGING_ERROR_HANDLING_ARCHITECTURE.md` §8

**Requirements**:
- File: `src/omega/oracle/providers.py` — 4+ bare `except Exception:` clauses
- Convert to ProviderError, ConnectionError, TimeoutError, AuthenticationError
- Wire circuit breaker events into ObservabilityEngine

### TASK-007 [P2]: Error Path Tests

**Spec**: `docs/strategy/LOGGING_ERROR_HANDLING_ARCHITECTURE.md` §7

**Requirements**:
- Add `@pytest.fixture` for each error type in `tests/conftest.py`
- Add error path tests for all exception subtypes (est. 50+ tests)
- Integration test: "provider chain exhausts all backends → raises ProviderError"
- All tests must pass with `make test` (currently 278 tests)

### TASK-008 [P3]: Bug Tracking Infrastructure

**Spec**: BUG_LOG.md — BUG-003

**Requirements**:
- MCP tools: `omega_hub.bug_create`, `omega_hub.bug_list`, `omega_hub.bug_resolve`
- Persistent storage: `data/bugs/bugs.jsonl`
- Auto-report when error thresholds are crossed

---

## Agent Assignment Guide

| Builder Agent | Best Suited Tasks | Reason |
|---------------|-------------------|--------|
| **builder.md** (Primary) | TASK-001, TASK-002, TASK-003, TASK-006 | Core code generation, exception hierarchy, provider integration |
| **jem.md** (JEM Mode) | TASK-002 (observability hooks), TASK-007 | Observability + testing are JEM's domain |
| **plan.md** | Task sequencing, dependency ordering | Ensure P0 → P1 → P2 order |
| **reviewer.md** | All tasks (post-facto review) | Code review for compliance with LOGGING_ERROR_HANDLING_ARCHITECTURE.md |
| **tester.md** | TASK-007 (error path tests) | Test generation is tester's specialty |

---

## Constraints for All Builders

1. **AnyIO Absolute**: No `asyncio`. Only `anyio`.
2. **Engine-Stack Firewall**: No core changes in WAD directories (`config/wads/`).
3. **No Telemetry**: All observability stays local in `data/`.
4. **Error Integrity**: Every `except` clause must reference `LOGGING_ERROR_HANDLING_ARCHITECTURE.md`.
5. **Sequentiality**: Read spec → Plan → Implement → Test → Commit.
6. **Commit prefix**: Use `fix:` for bug fixes, `feat:` for new features, `refactor:` for error migration.
7. **Test after every change**: `make test` must pass (278 tests baseline).

---

## Quick Reference

```bash
source .venv/bin/activate
make test   # 278 tests must pass
make lint   # flake8 code quality
omega talk "hello"  # Test oracle
```

---

*Handoff prepared by: The Artisan (Cline/MiMo-2.5)*
*OpenCode Status: ✅ Operational — 7 valid agents ready*
*This handoff replaces all previous handoff files in `data/handoff/`*