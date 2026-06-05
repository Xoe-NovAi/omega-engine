# 🔱 TASK: M9 Error Integrity — Remediate 155 Bare `except Exception:` Violations
**Target**: Gemma 4 31B (via OpenCode CLI)
**Priority**: P0 🔴 (Constitutional Mandate violation)
**Source**: DEEP_REVIEW_PHASE1_CODE_ARCHITECTURE.md

---

## The Problem

OMEGA_ENGINE.md §5.1 claims: `Mandate 9 (Error Integrity) — FULL — 0 bare except`

**Reality: 155 `except Exception:` across 31 source files.**

The documentation claim is false at the constitutional level. M9 requires typed, traceable exceptions. Every bare `except Exception:` undermines debuggability and sovereignty.

---

## The Pattern to Apply

Convert each `except Exception:` to:

```python
# BAD (current):
except Exception as e:
    logger.error(f"Failed: {e}")

# GOOD (target):
except OmegaErrorCategory as e:
    logger.error(f"[{e.trace_id}] Failed: {e.message}", exc_info=True)
    raise
```

### Canonical Error Subtypes Available (from src/omega/errors.py)
- `OmegaError` — base class, use when no specific subtype fits
- `ProviderError` — external API failures
- `ProviderRateLimitError` — 429
- `ProviderAuthError` — 401/403
- `ProviderTimeoutError` — 408/504
- `ProviderUnavailableError` — 502/503
- `ProviderValidationError` — 400/context length
- `ProviderSafetyError` — safety filter blocks
- `InferenceError` — local runtime failures
- `InferenceOOMError` — VRAM/RAM OOM
- `InferenceLoadError` — GGUF version mismatch
- `InferenceRuntimeError` — illegal instructions
- `OmegaPersistenceError` — file/YAML failures
- `SoulCorruptionError` — soul.yaml parse failures
- `StateIntegrityError` — state machine violations
- `ConfigError` — YAML config parse failures
- `WADError` — WAD loader failures
- `BoundaryViolationError` — M2 firewall violations
- `InvariantViolationError` — assertion-style failures
- `EntityTombstonedError` — tombstoned entity access

---

## Violations by File (ordered by severity, highest first)

### TIER 1 — CRITICAL (10+ violations, highest impact)

1. **`src/omega/observability.py`** — 15 violations
   - Lines: grep for exact locations
   - Category: Mixed (some health probes, most sad-path logging)
   - Fix: Convert to typed `OmegaError` variants. Health probes may keep broad catch with explicit log

2. **`src/omega/oracle/oracle.py`** — 13 violations
   - Lines: grep for exact locations
   - Category: Serves as facade. 13 excepts in query routing + soul evolution
   - Fix: Route through typed exceptions. Soul evolution excepts should be `SoulCorruptionError`

3. **`src/omega/library/discovery.py`** — 10 violations
   - Lines: grep for exact locations
   - Category: External search calls
   - Fix: Wrap in `ProviderError` subtypes for each search backend

### TIER 2 — HIGH (5-9 violations)

4. `src/omega/workers/background_researcher/distiller.py` — 9 violations
5. `src/omega/workers/background_researcher/loop.py` — 8 violations
6. `src/omega/memory/providers.py` — 8 violations
7. `src/omega/oracle/providers.py` — 7 violations
8. `src/omega/oracle/model_gateway.py` — 7 violations
9. `src/omega/memory_store.py` — 7 violations
10. `src/omega/workers/background_researcher/search_fleet.py` — 6 violations
11. `src/omega/oracle/orchestrator.py` — 5 violations

### TIER 3 — MEDIUM (2-4 violations)

12. `src/omega/oracle/wad_loader.py` — 4 violations
13. `src/omega/oracle/health_monitor.py` — 4 violations
14. `src/omega/oracle/entity_workspace.py` — 4 violations
15. `src/omega/cli/repl.py` — 4 violations
16. `src/omega/workers/model_updater.py` — 4 violations
17. `src/omega/oracle/cpu_optimizer.py` — 3 violations
18. `src/omega/workers/background_researcher/scheduler.py` — 3 violations
19. `src/omega/workers/background_researcher/review_queue.py` — 3 violations
20. `src/omega/library/library.py` — 3 violations
21. `src/omega/library/inbox.py` — 3 violations
22. `src/omega/oracle/link_p9_runtime.py` — 2 violations
23. `src/omega/oracle/entity_registry.py` — 2 violations
24. `src/omega/oracle/context_builder.py` — 2 violations
25. `src/omega/oracle/capability_registry.py` — 2 violations
26. `src/omega/iris/server.py` — 2 violations
27. `src/omega/workers/background_researcher/searxng_client.py` — 2 violations

### TIER 4 — LOW (1 violation each)

28. `src/omega/request_queue.py` — 1 violation
29. `src/omega/oracle/session_manager.py` — 1 violation
30. `src/omega/oracle/hierarchy.py` — 1 violation
31. `src/omega/oracle/backends/remote_provider.py` — 1 violation
32. `src/omega/library/indexer.py` — 1 violation
33. `src/omega/library/extractor.py` — 1 violation
34. `src/omega/gateway/server.py` — 1 violation
35. `src/omega/cli/oracle_cli.py` — 1 violation
36. `src/omega/cli/link_p9_cli.py` — 1 violation
37. `src/omega/bridge/elevenlabs.py` — 1 violation
38. `src/omega/services/intake_digestor.py` — 1 violation
39. `src/omega/workers/background_researcher/soul_updater.py` — 1 violation
40. `src/scripts/soul_inscriber.py` — 1 violation

---

## Execution Strategy

### Phase A: Audit & Classify (estimated 30 min)
For each file, classify every `except Exception:` into:
- **TYPED**: Convert to appropriate OmegaError subtype (60% of cases)
- **HEALTH**: Keep broad catch IF it's a health probe AND it logs (20%)
- **SILENT**: Add logging AND typed exception (20% — worst category)

### Phase B: Fix by Tier (estimated 4 hours)
1. Tier 1 (files 1-3, 38 violations) — oracle.py, observability.py, discovery.py
2. Tier 2 (files 4-11, 65 violations) — memory, providers, gateway, workers
3. Tier 3 (files 12-27, 42 violations) — remaining oracle + library + workers
4. Tier 4 (files 28-40, 12 violations) — one-offs

### Phase C: Verify (estimated 30 min)
```bash
make test                    # 322 tests must pass
grep -rn 'except Exception' src/ | wc -l  # should approach 0
grep -rn 'except:' src/ | wc -l  # bare except should be 0
```

### Phase D: Update Documentation
- OMEGA_ENGINE.md §5.1: `Mandate 9 (Error Integrity) — FULL — 0 bare except`

---

## Acceptance Criteria
- [ ] `grep -rn 'except Exception' src/ | wc -l` returns 0 (or explicit health-probe exceptions documented)
- [ ] `grep -rn 'except:' src/ | wc -l` returns 0 (no bare excepts)
- [ ] All 322 tests pass
- [ ] OMEGA_ENGINE.md M9 claim updated to match reality

---

## For Gemma 4 31B

Execute one file at a time. For each file:
1. Read the full file
2. Find every `except Exception:`
3. Classify it (TYPED/HEALTH/SILENT)
4. Apply the fix using `editor`
5. Run tests for that file's domain

Start with Tier 1: `src/omega/observability.py` (15 violations, highest count).
