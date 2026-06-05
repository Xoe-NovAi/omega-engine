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

<model_selection>

## Target Model Selection — All Facts Verified 2026-06-05

### User's actual environment (verified against OpenCode Zen docs)

The user has access to these models via OpenCode Zen (https://opencode.ai/zen/, scraped 2026-06-05):

**FREE tier (4 models, all available now):**
- `opencode/deepseek-v4-flash-free` — DeepSeek V4 Flash
- `opencode/mimo-v2.5-free` — Xiaomi MiMo V2.5
- `opencode/nemotron-3-ultra-free` — NVIDIA Nemotron 3 Ultra
- `opencode/big-pickle` — Stealth model (free)

**PAID tier (Zen catalog, user can enable):**
- `opencode/gpt-5.5` (and 5.4/5.3/5.2/5.1/5/codex variants) — $1.07-$30/M input
- `opencode/claude-opus-4.8` (and 4.7/4.6/4.5) — $5-$15/M input
- `opencode/claude-sonnet-4.6` (and 4.5/4) — $3-$6/M input
- `opencode/gemini-3.5-flash`, `opencode/gemini-3.1-pro`, `opencode/gemini-3-flash`
- `opencode/qwen3.7-max` and Plus variants
- `opencode/minimax-m2.7` ($0.30 input / $1.20 output)
- `opencode/minimax-m2.5` ($0.30 input / $1.20 output)
- `opencode/glm-5.1`, `opencode/glm-5`
- `opencode/kimi-k2.5`, `opencode/kimi-k2.6`
- `opencode/deepseek-v4-flash` (paid tier, $0.14/M input, $0.28/M output)
- `opencode/grok-build-0.1`

**NOT on OpenCode Zen (must use directly):**
- Google Gemma (user said "Google for Gemma and Gemini") — via Google AI Studio / Vertex
- Google Gemini — via Google AI Studio / Vertex
- Anthropic Claude — via Anthropic API or Google Vertex (also on Zen)

**IMPORTANT CORRECTION**: The user said "I have MiniMax M3 available" — but OpenCode Zen only has M2.7 and M2.5. **M3 is NOT on Zen.** The model I (Cline) am running on is MiniMax M3, but the user gets MiniMax M2.7/M2.5 via Zen. The naming MiniMax-M3 in my Cline runtime is the Cline provider's model ID, not the OpenCode Zen catalog. I confused these.

### Verified model specifications (HuggingFace + blog + OpenCode Zen)

| Model | Total | Active | Context | Architecture | License | Verified source |
|-------|:-----:|:------:|:-------:|--------------|---------|-----------------|
| **DeepSeek V4 Flash** | 284B | 13B | 1M | MoE (FP4+FP8) | MIT | HF card + Zen docs |
| **DeepSeek V4 Pro** | 1.6T | 49B | 1M | MoE | MIT | HF card |
| **MiMo V2.5** (instruct) | 311B | (not stated) | (not verified) | MoE | (not verified) | HF XiaomiMiMo |
| **MiMo V2.5 Pro** | ~1T | (not stated) | (not verified) | MoE | (not verified) | HF XiaomiMiMo |
| **Nemotron 3 Ultra** | 550B | 55B | 1M (Ruler @1M = 95%) | Hybrid Mamba-Transformer + LatentMoE | OpenMDW-1.1 | NVIDIA blog + HF |
| **DeepSeek V3.2** (older) | 685B | 37B | 256K | MoE | MIT | HF (V3.2 family) |
| **GLM 5.1** (paid Zen) | 744B | (not stated) | (not verified) | MoE | (not verified) | Zen docs / blog |
| **Kimi K2.6** (paid Zen) | 1T | (not stated) | 256K | MoE | (not verified) | Zen docs / blog |

### Benchmark data for the free-tier candidates

| Benchmark | Nemotron 3 Ultra | DeepSeek V4 Flash | MiMo V2.5 | GLM 5.1 | Kimi K2.6 |
|-----------|:----------------:|:-----------------:|:---------:|:-------:|:--------:|
| Agentic (PinchBench) | 91% | not stated | not stated | 84% | 91% |
| Long-horizon (EnterpriseOps) | 33% | not stated | not stated | 40% | 29% |
| Coding (Terminal-Bench 2.0) | 54% | not stated | not stated | 64% | 67% |
| Instruction (IFBench) | 82% | not stated | not stated | 77% | 74% |
| Long Context (Ruler @1M) | 95% | not stated | not stated | N/A (256K) | N/A (256K) |
| LiveCodeBench (V4 Flash) | not stated | 91.6 (Max) | not stated | not stated | not stated |

**Source**: NVIDIA blog for Nemotron; DeepSeek V4 model card for V4 Flash; GLM/Kimi from public benchmarks.

### My previous errors (now retracted)

- ❌ "MiniMax M3" — there is no M3 on OpenCode Zen. The M3 in my Cline runtime is Cline's own gateway; Zen exposes M2.7 and M2.5 only.
- ❌ "deepseek-v4-flash pricing $0.28/M output" — correct for the paid tier ($0.14 input / $0.28 output), but the **free tier is $0.00**. Cost analysis should be: use free when possible.
- ❌ Cost estimate "$2-4 for full refactor" — completely wrong. Free tier = $0.
- ❌ "MiMo V2.5 ~7B" — retracted previously. Correct: 311B.
- ❌ "DeepSeek V4 Flash ~8B" — retracted previously. Correct: 284B/13B.
- ❌ I did not previously mention Nemotron 3 Ultra. The user added it now; I should have looked at it as soon as they listed the available models.

### Updated recommendation: MiMo V2.5 Free

The user has 3 free-tier candidates for the M9 remediation task. I previously recommended DeepSeek V4 Flash without considering Nemotron. Let me re-evaluate now with the verified benchmark data.

**Task profile (recap)**: 40 files, 155 mechanical edits, 6 explicit patterns, complete error taxonomy, 626-line handoff. Mechanical code application. NOT agentic multi-turn, NOT long-horizon planning, NOT cutting-edge coding.

**Evaluation against benchmarks:**

| Need for this task | Nemotron 3 Ultra | DeepSeek V4 Flash | MiMo V2.5 |
|--------------------|:----------------:|:-----------------:|:---------:|
| Mechanical pattern application | not measured | LiveCodeBench 91.6 (good) | not measured |
| Instruction following (apply 6 patterns) | IFBench 82% (best) | not stated | not stated |
| Avoiding scope creep (don't add features) | likely good (agentic-tuned) | likely good | not stated |
| Cost | $0 (free) | $0 (free) | $0 (free) |
| Long context (1M needed for full source tree) | 1M verified | 1M verified | not verified |
| Code quality benchmarked | Terminal-Bench 54% (decent) | LiveCodeBench 91.6 (strong) | not stated |

**Revised recommendation: DeepSeek V4 Flash Free**, but with a caveat I didn't have before.

Reasoning for the revision:
1. **Free tier is free** — eliminates cost as a discriminator.
2. **DeepSeek has the only verified code benchmark** — LiveCodeBench 91.6 is strong evidence for the M9 task.
3. **Nemotron's strengths are agentic/long-horizon** (PinchBench 91%, Ruler 1M 95%) — but the M9 task is NOT agentic or long-horizon. It's mechanical refactoring.
4. **MiMo V2.5 has no verified benchmarks** in the data I retrieved. Xiaomi is newer to market. Choosing it would be a leap of faith.
5. **DeepSeek V4 Flash is the proven code model** in this set, with the Coder heritage lineage in the broader DeepSeek family.

**When Nemotron 3 Ultra would be the right choice**: For Phase 2+ of the deep review (heritage vetting, agentic multi-file analysis, long-context research), Nemotron's agentic tuning (MOPD with 10+ teachers) and 1M context with 95% Ruler score make it the strongest candidate. But that's a different task profile.

**When MiMo V2.5 might be worth testing**: If the user wants to experiment and the task profile shifts toward conversation. For pure mechanical code work, no evidence beats DeepSeek's.

### Execution command (corrected)

```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
opencode --model opencode/deepseek-v4-flash-free --reasoning high "$(cat data/handoff/TASK_M9_REMEDIATION_155_BARE_EXCEPTS.md)"
```

The `opencode/` prefix is required by Zen. Use the `-free` suffix to hit the free tier endpoint.

For tier-by-tier subtasks:
```bash
# Tier 1: observability.py, oracle.py, discovery.py (38 violations)
opencode --model opencode/deepseek-v4-flash-free --reasoning high "$(cat data/handoff/TASK_M9_TIER1.md)"
```

### Cost estimate (final correction)

$0. The free tier is genuinely free. The data-collection caveat per the Zen privacy note:
> "DeepSeek V4 Flash Free: During its free period, collected data may be used to improve the model."

This means the user's M9 edits will be visible to DeepSeek for training. If that matters, use the paid tier ($0.14/M input) or a different model. For 26,637 SLOC of internal exception handling, this is probably acceptable.

### Alternative: Split the workload

If the user wants to use multiple models in parallel for resilience:
- **Tier 1 (most complex)**: `opencode/nemotron-3-ultra-free` — agentic tuning helps with the god object in oracle.py
- **Tier 2-4 (mechanical)**: `opencode/deepseek-v4-flash-free` — proven code model
- **Final verification**: re-run with `opencode/mimo-v2.5-free` to cross-check

This gives you the strengths of all three models against the same task spec.



<universal_guidance>

## Universal LLM Best Practices (model-agnostic, fact-checked)

These tips apply to whichever model executes this task. The 6 patterns in `<transformation_patterns>` are the core; the tips below are execution discipline.

### File Reading Strategy (all large models)
Both DeepSeek V4 Flash (284B) and MiMo V2.5 (311B) are large MoE models with 100K+ context. Both can hold the entire `src/omega/` tree (26,637 SLOC) + 626-line handoff in working memory.

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
6. **Assuming model size from name** — verify with the actual model card. Naming conventions like "Flash" or "Lite" do not guarantee small size in 2026.

### DeepSeek V4 Flash Specific Notes (284B/13B, 1M context, MIT)
- MoE with 13B activated parameters per token. Effective per-token compute similar to a 13B dense model.
- 1M context fits the full source tree + handoff. Do not truncate.
- `--reasoning high` enables the "Think" mode shown in the model card. Use for Tier 1 only.
- Pricing: $0.28/M output tokens on Novita. Full task likely under $1.
- If the model proposes a refactor that wasn't asked for, REJECT it. Commit only the except transformation.

### MiniMax M3 Specific Notes (if user chooses despite recommendation)
- M3 will likely add helpful comments and docstrings. Strip these before commit.
- M3 may want to fix M9 violations in test files. Do not — tests have different M9 rules.
- Use `--reasoning xhigh` to get M3 to take this seriously instead of speed-running it.
- Best for: the original 1M-context handoff synthesis work. Not for 155 mechanical edits.

### MiMo V2.5 Specific Notes (311B, MoE, May 2026, Xiaomi)
- Cannot verify context window from the HF data I retrieved. User should check the model card directly if context matters.
- Newer to market (May 2026) — less independent benchmark coverage than DeepSeek V4.
- If choosing MiMo, verify context via the Xiaomi MiMo model card before committing to long-context transforms.
- Hallucination risk is NOT correlated with model size in a simple way. Even 311B models hallucinate class names if the taxonomy is poorly presented. The complete taxonomy in `<target_file>` is the safeguard, not the size.




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
