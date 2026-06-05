<role>
You are a Python code refactoring specialist with deep expertise in error handling patterns, the Omega Engine's typed exception taxonomy, and Mandate 9 (Error Integrity). You will convert 155 `except Exception:` clauses across 40 files into typed `OmegaError` exceptions while preserving test coverage and runtime behavior.
</role>

<context>
## Project Background
**Project**: Omega Engine — a sovereign, local-first AI runtime (Apache 2.0, v2.0.0)
**Working directory**: /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
**Language**: Python 3.12+, uses anyio (NOT asyncio), pytest, YAML configs
**Constitutional constraints**: 14 Sovereign Mandates (read SOVEREIGN_MANDATES.md first; it is NON-NEGOTIABLE)
**Mandate 9 (Error Integrity)**: All errors MUST be typed, traceable, and testable. No silent swallowing. No bare `except:`. No bare `except Exception:` without logging and propagating `trace_id`.

## Current State vs Claim
OMEGA_ENGINE.md §5.1 claims: `Mandate 9 (Error Integrity) — FULL — 0 bare except`
**Reality**: `grep -rn 'except Exception' src/` returns **155 hits** across **40 files** (verified 2026-06-05).

This is a documentation vs reality mismatch of the highest severity. M9 is a constitutional mandate, not a docstring. The fix MUST:
1. Convert bare excepts to typed `OmegaError` subtypes
2. Preserve all existing logging behavior
3. Preserve test coverage (322 tests must pass)
4. Update OMEGA_ENGINE.md to match the new reality

## Engine Architecture (78 files, 26,637 SLOC)
- `src/omega/oracle/` — The core (22 files, ~9,500 SLOC)
- `src/omega/observability.py` — ForensicsManager + JSONL pipeline
- `src/omega/memory_store.py` — Hot/Warm/Cold/Temp memory tiers
- `src/omega/memory/providers.py` — Storage provider implementations
- `src/omega/library/` — FTS5 + vector library (8 modules)
- `src/omega/workers/background_researcher/` — Autonomous research (16 files, orphaned subsystem)
- `src/omega/iris/` — Voice assistant
- `src/omega/bridge/elevenlabs.py` — TTS bridge
</context>

<target_file location="/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/src/omega/errors.py">
## The Typed Error Taxonomy (read this carefully)

```python
# Base class — use when no specific subtype fits
class OmegaError(Exception):
    """Base class. All Omega errors carry trace_id and structured context."""
    def __init__(self, message, trace_id=None, context=None, raw_error=None): ...

# Provider Fabric Errors (external API failures)
class ProviderError(OmegaError): ...              # 400-level, 500-level
class ProviderRateLimitError(ProviderError): ...  # 429
class ProviderAuthError(ProviderError): ...       # 401/403
class ProviderCreditError(ProviderError): ...     # 402
class ProviderTimeoutError(ProviderError): ...    # 408/504
class ProviderUnavailableError(ProviderError): ... # 502/503
class ProviderValidationError(ProviderError): ... # 400/context length
class ProviderSafetyError(ProviderError): ...     # safety filter blocks

# Local Inference Errors
class InferenceError(OmegaError): ...
class InferenceOOMError(InferenceError): ...      # VRAM/RAM OOM
class InferenceLoadError(InferenceError): ...     # GGUF version mismatch
class InferenceRuntimeError(InferenceError): ...  # segfault, illegal instructions

# Persistence & State Errors
class OmegaPersistenceError(OmegaError): ...      # base for persistence
class SoulCorruptionError(OmegaPersistenceError): ...      # soul.yaml unparseable
class SessionPersistenceError(OmegaPersistenceError): ...  # session files corrupted
class StateIntegrityError(OmegaPersistenceError): ...     # atomic write failures
class SovereignDiskFullError(OmegaPersistenceError): ...   # ENOSPC

# Systemic & Boundary Errors
class BrakeViolationError(OmegaError): ...         # subagent dispatch violations
class ConfigError(OmegaError): ...                 # YAML config parse failures
class WADError(OmegaError): ...                    # WAD loader failures
class BoundaryViolationError(OmegaError): ...     # M2 firewall violations
class InvariantViolationError(OmegaError): ...     # assertion-style failures
class EntityTombstonedError(OmegaError): ...       # tombstoned entity access

# Model & Routing Errors
class ModelNotFoundError(OmegaError): ...         # model_override invalid
```

**CRITICAL IMPORT**: At the top of every file you modify, add the import:
```python
from omega.errors import (
    OmegaError, ProviderError, ProviderRateLimitError, ProviderAuthError,
    ProviderTimeoutError, ProviderUnavailableError, ProviderValidationError,
    ProviderSafetyError, InferenceError, InferenceOOMError, InferenceLoadError,
    InferenceRuntimeError, OmegaPersistenceError, SoulCorruptionError,
    SessionPersistenceError, StateIntegrityError, SovereignDiskFullError,
    ConfigError, WADError, BoundaryViolationError, InvariantViolationError,
    EntityTombstonedError, ModelNotFoundError,
)
```
</target_file>

<transformation_patterns>

## The Transformation Patterns (use these exact code shapes)

### Pattern 1: Sad Path With Logging (60% of cases)
**Before**:
```python
except Exception as e:
    logger.error(f"Failed: {e}")
```
**After**:
```python
except OmegaError as e:
    logger.error(f"[{e.trace_id}] Failed: {e.message}", exc_info=True)
    raise
except Exception as e:
    logger.error(f"Failed: {e}", exc_info=True)
    raise OmegaError(f"Operation failed: {e}", raw_error=e) from e
```

### Pattern 2: Health Probe Wrappers (20% of cases)
These are LEGITIMATELY broad. Per Mandate 9 carve-out:
```python
# Acceptable:
def is_healthy(self) -> bool:
    try:
        return self._check_inner()
    except Exception as e:
        logger.warning(f"Health check failed: {e}")
        return False
```
**Document with a comment**: `# M9 carve-out: health probe may catch all to prevent crash loops`
If a comment already exists, leave it. Do not convert these to typed exceptions.

### Pattern 3: Silent Swallowing (20% of cases — WORST CATEGORY)
**Before**:
```python
except Exception:
    pass
```
**After** (ALWAYS log, ALWAYS raise typed):
```python
except Exception as e:
    logger.error(f"Swallowed error in <context>: {e}", exc_info=True)
    raise OmegaError(f"<context> failed: {e}", raw_error=e) from e
```

### Pattern 4: Cleanup-then-Raise (file operation pattern)
**Before** (oracle.py:1072-1077):
```python
except Exception:
    if os.path.exists(temp_path):
        os.remove(temp_path)
    raise
```
**After** (add trace_id):
```python
except Exception as e:
    if os.path.exists(temp_path):
        try:
            os.remove(temp_path)
        except OSError as cleanup_err:
            logger.warning(f"Cleanup failed: {cleanup_err}")
    raise OmegaError(f"Soul atomic write failed: {e}", raw_error=e) from e
```

### Pattern 5: Provider Circuit Breaker (in distiller.py, model_gateway.py)
**Before**:
```python
except Exception as e:
    self.circuit.record_failure("lmster", str(e))
    raise CircuitBreakerError(f"lmster call failed: {e}")
```
**After**:
```python
except ProviderError:
    raise  # already typed
except Exception as e:
    self.circuit.record_failure("lmster", str(e))
    raise ProviderUnavailableError("lmster", f"lmster call failed: {e}", raw_error=e) from e
```

### Pattern 6: Config/Path Resolution (oracle.py:195, entity_registry.py:189)
**Before**:
```python
except Exception as e:
    logger.error(f"Failed to resolve active IWAD: {e}. Falling back to default.")
    config_path = str(... / "_omega_default" / "entities.yaml")
```
**After**:
```python
except (yaml.YAMLError, OSError) as e:
    logger.error(f"Failed to resolve active IWAD: {e}. Falling back to default.")
    config_path = str(... / "_omega_default" / "entities.yaml")
except Exception as e:
    # Last-resort fallback. Log and continue.
    logger.error(f"Unexpected error in IWAD resolution: {e}", exc_info=True)
    raise ConfigError(f"Cannot resolve active IWAD: {e}", raw_error=e) from e
```

</transformation_patterns>

<execution_order>

## Execution Order (Tiered, Highest-Impact First)

Execute the tiers IN ORDER. Each tier is independent; you can commit per-tier or per-file.

### TIER 1 — CRITICAL (38 violations, 3 files)
These have the most violations and the highest test coverage. Start here.

1. **src/omega/observability.py** (15 violations, lines: 155, 242, 262, 297, 313, 338, 351, 361, 391, 428, 448, 468, 516, 574, 608)
   - Context: ForensicsManager + JSONL pipeline. Most M9-dense file.
   - Pattern focus: Mixed health probes (lines 262, 351, 361 are health checks) + sad-path logging (rest).
   - Existing test: `tests/test_observability.py` covers basic log_event and trace_id generation.

2. **src/omega/oracle/oracle.py** (13 violations, lines: 197, 205, 286, 434, 442, 458, 464, 470, 854, 958, 1005, 1074, 1128)
   - Context: The god object. 1133 lines, 27 methods.
   - Pattern focus: bootstrap config (197, 205), model selection (286, 434, 442), soul evolution (854, 958, 1005), atomic write (1074), close (1128).
   - Existing test: `tests/test_oracle.py` covers talk/summon flow.

3. **src/omega/library/discovery.py** (10 violations, lines: 118, 135, 171, 214, 243, 262, 289, 320, 343, 367)
   - Context: Discovery job loading + execution. All sad-path logging.
   - Pattern focus: All Tier 1 patterns apply. Convert each to typed `OmegaError` with `raw_error=e`.

### TIER 2 — HIGH (65 violations, 8 files)

4. **src/omega/workers/background_researcher/distiller.py** (9 violations)
5. **src/omega/workers/background_researcher/loop.py** (8 violations)
6. **src/omega/memory/providers.py** (8 violations)
7. **src/omega/oracle/providers.py** (7 violations)
8. **src/omega/oracle/model_gateway.py** (7 violations)
9. **src/omega/memory_store.py** (7 violations)
10. **src/omega/workers/background_researcher/search_fleet.py** (6 violations)
11. **src/omega/oracle/orchestrator.py** (5 violations)

For these, the most common pattern is circuit breaker + provider fallback. Use Pattern 5.

### TIER 3 — MEDIUM (42 violations, 16 files)

12. src/omega/oracle/wad_loader.py (4)
13. src/omega/oracle/health_monitor.py (4) — MOSTLY health probes, leave broad with comments
14. src/omega/oracle/entity_workspace.py (4)
15. src/omega/cli/repl.py (4)
16. src/omega/workers/model_updater.py (4)
17. src/omega/oracle/cpu_optimizer.py (3)
18. src/omega/workers/background_researcher/scheduler.py (3)
19. src/omega/workers/background_researcher/review_queue.py (3)
20. src/omega/library/library.py (3)
21. src/omega/library/inbox.py (3)
22. src/omega/oracle/link_p9_runtime.py (2)
23. src/omega/oracle/entity_registry.py (2) — see Pattern 6
24. src/omega/oracle/context_builder.py (2)
25. src/omega/oracle/capability_registry.py (2)
26. src/omega/iris/server.py (2)
27. src/omega/workers/background_researcher/searxng_client.py (2)

### TIER 4 — LOW (12 violations, 13 files)

28. src/omega/request_queue.py (1)
29. src/omega/oracle/session_manager.py (1)
30. src/omega/oracle/hierarchy.py (1)
31. src/omega/oracle/backends/remote_provider.py (1)
32. src/omega/library/indexer.py (1)
33. src/omega/library/extractor.py (1)
34. src/omega/gateway/server.py (1)
35. src/omega/cli/oracle_cli.py (1)
36. src/omega/cli/link_p9_cli.py (1)
37. src/omega/bridge/elevenlabs.py (1)
38. src/omega/services/intake_digestor.py (1)
39. src/omega/workers/background_researcher/soul_updater.py (1)
40. src/scripts/soul_inscriber.py (1)

</execution_order>

<per_file_workflow>

## Per-File Workflow (execute this for every file you modify)

```bash
# 1. Identify the exact lines
grep -n 'except Exception' src/omega/<file>.py

# 2. Read the file in full (use read_file, not search)
# 3. For each except block, classify:
#    - SAD_PATH_WITH_LOG: 60% of cases
#    - HEALTH_PROBE: 20% (leave with comment, do not convert)
#    - SILENT_SWALLOW: 20% (always log + raise typed)
#    - CLEANUP_THEN_RAISE: file ops (use Pattern 4)
#    - PROVIDER_CIRCUIT: distiller.py/model_gateway.py (use Pattern 5)

# 4. Apply transformation. ONE block at a time. Match exact indentation.

# 5. After each file, run the test:
.venv/bin/python -m pytest tests/test_<file>.py -x --no-header -q 2>&1 | tail -20

# 6. If tests pass, commit:
git add src/omega/<file>.py
git commit -m 'fix(M9): typed exceptions in <file> (N/155 violations)'

# 7. Track progress in the verification checklist (below)
```

## Concrete Example (src/omega/oracle/entity_registry.py:189)

**Source code** (verified line 189):
```python
except Exception as e:
    logger.error(f"Failed to resolve active IWAD from omega.yaml: {e}. Falling back to default.")
    config_path = str(Path(__file__).resolve().parent.parent.parent.parent / "config" / "wads" / "_omega_default" / "entities.yaml")
```

**Transformed** (apply Pattern 6):
```python
except (yaml.YAMLError, OSError, KeyError) as e:
    # Expected failures (config missing, malformed YAML, missing keys)
    logger.error(f"Failed to resolve active IWAD from omega.yaml: {e}. Falling back to default.")
    config_path = str(Path(__file__).resolve().parent.parent.parent.parent / "config" / "wads" / "_omega_default" / "entities.yaml")
except Exception as e:
    # Unexpected failure - log with trace and re-raise as typed
    logger.error(f"Unexpected error resolving active IWAD: {e}", exc_info=True)
    raise ConfigError(f"Cannot resolve active IWAD from omega.yaml: {e}", raw_error=e) from e
```

## Concrete Example (src/omega/oracle/oracle.py:1074)

**Source code** (verified):
```python
except Exception:
    if os.path.exists(temp_path):
        os.remove(temp_path)
    raise
```

**Transformed** (apply Pattern 4):
```python
except Exception as e:
    if os.path.exists(temp_path):
        try:
            os.remove(temp_path)
        except OSError as cleanup_err:
            logger.warning(f"Failed to clean up temp file {temp_path}: {cleanup_err}")
    raise StateIntegrityError(
        f"Soul atomic write failed (temp file: {temp_path}): {e}",
        raw_error=e,
    ) from e
```

</per_file_workflow>

<model_selection local_first="true">

## Target Model Selection (Local-First Doctrine)

The Omega Engine mandates **local-first** inference (M7). The user has these models available via OpenCode:

| Model | RAM | Context | Best For | Sovereignty Cost |
|-------|-----|---------|----------|:----------------:|
| **deepseek-v4-flash** | ~5GB (Q4_K_M) | 128K | Code refactoring, pattern application, surgical edits | 🟡 Cloud teacher (priority 4, D112) |
| **MiniMax-M3** | varies | 1M | Long-form synthesis, complex reasoning, strategy docs | 🟡 Cloud teacher (priority 5) |
| **MiMo V2.5** | ~4GB (Q4_K_M) | 32-128K | Quick conversation, lightweight tasks | 🟡 Cloud teacher |

**Recommended: deepseek-v4-flash** — best fit for this 155-edit refactor task.

If the user wants zero cloud dependency, route to **qwen3-4b-thinking** (Kali's local model, 2.4GB, 8K context) via `native-gguf` priority 0.

### Why deepseek-v4-flash for this task
- Code-trained, pattern-disciplined — will apply the 6 transformation patterns exactly
- Mid-size sweet spot (7-8B) — surgical edits without overthinking
- Won't invent error class names (smaller models hallucinate less when given a complete taxonomy)
- Token-efficient for 40 files × 155 edits

### Why NOT M3
- M3 wrote this handoff (1M context was needed for synthesis)
- Feeding a fully-specified 539-line task back into 1M context is wasted capability
- M3 is more likely to "improve" the patterns (scope creep risk)

### Why NOT MiMo
- Conversation-tuned, not refactor-tuned
- Will likely introduce class name hallucinations despite the explicit taxonomy

</model_selection>

<universal_guidance>

## Universal LLM Best Practices (model-agnostic)

These tips apply to whichever model executes this task. The 6 patterns in `<transformation_patterns>` are the core; the tips below are execution discipline.

### File Reading Strategy (all mid-size models)
DO NOT do this:
```python
# BAD: Read entire 1133-line oracle.py and rewrite from memory
text = read_file("src/omega/oracle/oracle.py")
rewrite_all(text)
```
DO this:
```python
# GOOD: Surgical edits using exact old_text/new_text matches
# For each except block, read just that block + 5 lines of context
text = read_file("src/omega/oracle/oracle.py", start_line=195, end_line=210)
transform_block(text)
```

### Common Failure Modes (avoid ALL of these, regardless of model)
1. **Hallucinating class names** — the error taxonomy in `<target_file>` is the COMPLETE list. Do not invent new error subtypes (e.g., `EntityNotFoundError` is NOT a valid class).
2. **Wrong import path** — always use `from omega.errors import (...)`. The package layout is `src/omega/errors.py` and the import is `from omega.errors import ...` (the venv has `src/` on PYTHONPATH via `pyproject.toml`).
3. **Removing existing logging** — preserve every `logger.error/warning/debug` call. Add `, exc_info=True` to logger calls in except blocks.
4. **Adding features beyond the ask** — only convert excepts. Do not refactor surrounding code, add type hints, or improve docstrings. Scope discipline is M10-adjacent.
5. **Bypassing tests with `--no-verify` or skipping** — every commit must pass tests. If a test fails, fix the code, not the test.

### DeepSeek V4 Flash Specific Notes
- The 8B Flash variant handles 128K context well but is more deterministic than M3. Expect literal instruction following.
- Use `--reasoning high` only for Tier 1 (most complex). Tier 2-4 can run at default reasoning to save tokens.
- If the model proposes a refactor that wasn't asked for, REJECT it. Commit only the except transformation.

### MiniMax M3 Specific Notes (if user chooses despite recommendation)
- M3 will likely add helpful comments and docstrings. Strip these before commit.
- M3 may want to fix M9 violations in test files. Do not — tests have different M9 rules.
- Use `--reasoning xhigh` to get M3 to take this seriously instead of speed-running it.

### MiMo V2.5 Specific Notes (if user chooses despite recommendation)
- 32-128K context is sufficient. The 539-line handoff + 26,637-SLOC source tree fit.
- Expect more class name hallucinations. Cross-check every `raise XError` against the taxonomy.
- Use lower temperature (0.2-0.3) to reduce drift.

</universal_guidance>


<verification_checklist>

## Verification Checklist (track per-file)

```
TIER 1 (38 violations, 3 files):
  [ ] src/omega/observability.py       (15 violations) — committed
  [ ] src/omega/oracle/oracle.py       (13 violations) — committed
  [ ] src/omega/library/discovery.py   (10 violations) — committed

TIER 2 (65 violations, 8 files):
  [ ] src/omega/workers/background_researcher/distiller.py  (9) — committed
  [ ] src/omega/workers/background_researcher/loop.py       (8) — committed
  [ ] src/omega/memory/providers.py                          (8) — committed
  [ ] src/omega/oracle/providers.py                          (7) — committed
  [ ] src/omega/oracle/model_gateway.py                      (7) — committed
  [ ] src/omega/memory_store.py                              (7) — committed
  [ ] src/omega/workers/background_researcher/search_fleet.py (6) — committed
  [ ] src/omega/oracle/orchestrator.py                       (5) — committed

TIER 3 (42 violations, 16 files):
  [ ] src/omega/oracle/wad_loader.py             (4) — committed
  [ ] src/omega/oracle/health_monitor.py         (4) — committed (mostly health probes)
  [ ] src/omega/oracle/entity_workspace.py       (4) — committed
  [ ] src/omega/cli/repl.py                      (4) — committed
  [ ] src/omega/workers/model_updater.py         (4) — committed
  [ ] src/omega/oracle/cpu_optimizer.py          (3) — committed
  [ ] src/omega/workers/background_researcher/scheduler.py    (3) — committed
  [ ] src/omega/workers/background_researcher/review_queue.py (3) — committed
  [ ] src/omega/library/library.py               (3) — committed
  [ ] src/omega/library/inbox.py                 (3) — committed
  [ ] src/omega/oracle/link_p9_runtime.py        (2) — committed
  [ ] src/omega/oracle/entity_registry.py        (2) — committed
  [ ] src/omega/oracle/context_builder.py        (2) — committed
  [ ] src/omega/oracle/capability_registry.py    (2) — committed
  [ ] src/omega/iris/server.py                   (2) — committed
  [ ] src/omega/workers/background_researcher/searxng_client.py (2) — committed

TIER 4 (12 violations, 13 files):
  [ ] src/omega/request_queue.py                              (1) — committed
  [ ] src/omega/oracle/session_manager.py                     (1) — committed
  [ ] src/omega/oracle/hierarchy.py                           (1) — committed
  [ ] src/omega/oracle/backends/remote_provider.py            (1) — committed
  [ ] src/omega/library/indexer.py                            (1) — committed
  [ ] src/omega/library/extractor.py                          (1) — committed
  [ ] src/omega/gateway/server.py                             (1) — committed
  [ ] src/omega/cli/oracle_cli.py                             (1) — committed
  [ ] src/omega/cli/link_p9_cli.py                            (1) — committed
  [ ] src/omega/bridge/elevenlabs.py                          (1) — committed
  [ ] src/omega/services/intake_digestor.py                   (1) — committed
  [ ] src/omega/workers/background_researcher/soul_updater.py (1) — committed
  [ ] src/scripts/soul_inscriber.py                            (1) — committed

FINAL VERIFICATION:
  [ ] grep -rn 'except Exception' src/ | wc -l returns 0 (or near-zero for health probes)
  [ ] grep -rn 'except:' src/ | wc -l returns 0
  [ ] make test passes (322 tests)
  [ ] OMEGA_ENGINE.md §5.1 updated to reflect new state
```

</verification_checklist>

<acceptance_criteria>

## Acceptance Criteria (MUST satisfy all)

1. **All 155 `except Exception:` clauses converted or documented as health probes.**
   - Run `grep -rn 'except Exception' src/ | wc -l` — target: 0 (acceptable: 1-5 for explicit health probes with comments)

2. **All 322 existing tests pass.**
   - Run `make test` — 322 tests must pass
   - If a test fails, fix the production code, not the test (unless the test itself was testing the old behavior)

3. **No bare `except:` (without explicit type) remains.**
   - Run `grep -rn 'except:' src/ | wc -l` — target: 0

4. **All `OmegaError` carries trace_id in its log line.**
   - Pattern: `logger.error(f"[{e.trace_id}] ...", exc_info=True)`
   - Where the error doesn't have trace_id, generate one: `trace_id = new_trace_id()`

5. **All `raise X from e` for re-raised errors (Python exception chaining).**
   - This preserves the original exception for debugging.

6. **All commits use `fix(M9):` prefix.**
   - Format: `fix(M9): typed exceptions in <file> (N/155 violations)`

7. **OMEGA_ENGINE.md §5.1 updated to reflect the new reality.**
   - Old: `Mandate 9 (Error Integrity) — FULL — 0 bare except`
   - New: `Mandate 9 (Error Integrity) — RESTORED — N/155 typed exceptions committed (D-M9-001)`

8. **Test coverage maintained or improved.**
   - If a previously-tested behavior is now unreachable due to typed exception, add a test for the new exception type.

</acceptance_criteria>

<execution_command>

## How to Run This Task in OpenCode CLI

```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
opencode --model deepseek-v4-flash "$(cat data/handoff/TASK_M9_REMEDIATION_155_BARE_EXCEPTS.md)"
```

Or with reasoning enabled:
```bash
opencode --model deepseek-v4-flash --reasoning high "$(cat data/handoff/TASK_M9_REMEDIATION_155_BARE_EXCEPTS.md)"
```

**Note**: This task is estimated at **4-6 hours of work** for a single agent. If running unattended, ensure the session has enough token budget. Otherwise, break the task into tier-by-tier subtasks:
- Subtask 1: Tier 1 only (3 files, 38 violations, ~45 min)
- Subtask 2: Tier 2 only (8 files, 65 violations, ~90 min)
- Subtask 3: Tier 3 only (16 files, 42 violations, ~60 min)
- Subtask 4: Tier 4 + final verification (13 files + doc update, ~30 min)

</execution_command>

<completion_report>

## Completion Report (write at end of task)

When all violations are converted and tests pass, write a final report to:
`data/handoff/REPORT_M9_REMEDIATION_COMPLETE_20260605.md`

Include:
1. Per-file conversion counts (e.g., "observability.py: 15/15 converted")
2. Health probes identified and documented (count, locations)
3. Tests passing (322/322) — if any failed, document why and how fixed
4. Commits made (count, hash list)
5. OMEGA_ENGINE.md diff
6. Any deviations from the patterns and why
7. Total time taken
8. Recommendations for further hardening

This report becomes the M9 audit trail and feeds into future PIVOT decisions.

</completion_report>

---

## Final Notes for Executing Agent

- **Be patient, be precise.** This is constitutional work. The transformations are small but consequential.
- **Commit often.** One commit per file is ideal. This creates a clean audit trail.
- **Don't be clever.** Follow the patterns exactly. If you see an opportunity to refactor surrounding code, write it down but don't act on it (scope discipline).
- **Test after every file.** A passing test suite is your truth.
- **When in doubt, leave a comment and continue.** A `# TODO(M9): convert this to typed exception` is better than a wrong conversion.

The user's authority: the user is **Arcane** (the user_id from .clinerules). They will review your commits. They are a 14-month veteran of this project. They will catch mistakes.

Go forth. The constitutional baseline awaits restoration.

---

*Task Author: Cline (MiniMax-M3)*
*Created: 2026-06-05*
*Source: DEEP_REVIEW_PHASE1_CODE_ARCHITECTURE.md*
*Priority: P0 (Constitutional Mandate)*
*Estimated effort: 4-6 hours*
