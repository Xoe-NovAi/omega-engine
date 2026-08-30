<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — Option B Execution (Gemma 4 31B)
# ⬡ OMEGA ⬡ GEMMA4 ⬡ trc_option_b_gem4 ⬡ 2026-06-01

**From**: SOPHIA (current session — verified all fixes against live code)
**To**: Gemma 4 31B via OpenCode
**Baseline**: ✅ 302/302 tests passing
**Estimated Time**: ~30–40 minutes

> [!IMPORTANT]
> This supersedes `HANDOFF_OPTION_B_OPENCODE.md`. Step 1 (observability.py) is already done.
> The test count is 302, not 292 (10 new Error Gauntlet tests were added).

---

## Pre-Flight

```bash
source .venv/bin/activate
make test  # Must show 302 passed, 0 failed
```

---

## Step 1: Fix 23 Bare `except Exception:` Without Logging

Work through each file in order. After fixing ALL exceptions in a single file, run `make test` before moving to the next.

**Fix pattern** (apply to every bare except listed):
```python
# BEFORE:
except Exception:
    pass  # or return False, return {}, return None

# AFTER:
except Exception as e:
    logger.warning("<describe what failed here>: %s", e)
    # keep the original fallback return value below
```

Each file must already have `import logging` and `logger = logging.getLogger(...)` at the top. Do NOT add a new logger — use the existing one.

### File 1: `src/omega/oracle/model_gateway.py`
- **Line 405**: `provider.is_available()` → `return False`. Add logging.
- **Line 422**: Observability log event → `pass`. Add logging.
- **Line 370**: Already has `logger.debug(..., exc_info=True)`. ✅ **LEAVE IT — not a violation.**

### File 2: `src/omega/observability.py`
- **Line 234** (`_detect_anyio_backend`): `except Exception: pass` → `logger.debug("anyio backend detection failed: %s", e)`
- **Line 250** (`_collect_engine_state`): `except Exception: pass` → `logger.warning("Failed to read /proc/self/status for RSS: %s", e)`
- **Line 282** (`snapshot`): `except Exception: continue` → `logger.warning("Failed to read event log for crash dump: %s", e)`
- **Line 359** (`learn`): `except Exception: continue` → `logger.warning("Failed to read crash dump file: %s", e)`

### File 3: `src/omega/oracle/providers.py`
- **Line 319**: Memory estimation → silent zeros. Add `logger.warning`.

### File 4: `src/omega/oracle/cpu_optimizer.py`
- **Line 385**: `awk` subprocess → wrong RAM estimate. Add `logger.warning`.

### File 5: `src/omega/memory/providers.py`
- **Line 135**: Redis `client.close()` → silent. Add `logger.warning`.
- **Line 256**: Lock file `unlink()` → silent. Add `logger.warning`.

### File 6: `src/omega/library/inbox.py`
- **Line 201**: JSON parse → silent default. Add `logger.warning`.
- **Line 221**: Item fetch → silent None. Add `logger.warning`.

### File 7: `src/omega/workers/background_researcher/loop.py`
- **Line 212** (`run_cycle` finally): `lock_path.rmdir()` → `logger.warning`.
- **Line 241** (`_local_discovery_scan`): file read error → `logger.warning`.
- **Line 301** (`_extract`): URL fetch → `logger.warning`.
- **Line 320** (`_fetch_content`): httpx GET fallback → `logger.warning`.
- **Line 440** (`_post_to_hivemind`): Cycle log append → `logger.warning`.
- **Line 448** (`_is_network_available`): First network check → `logger.debug`.
- **Line 454** (`_is_network_available`): Second network check → `logger.warning`.

### File 8: `src/omega/workers/background_researcher/review_queue.py`
> ⚠️ This file has **no logger defined**. Add at top of file (after imports):
> ```python
> import logging
> logger = logging.getLogger(__name__)
> ```

- **Line 104**: `print(f"Error processing review item...")` → `logger.warning("Error processing review item %s: %s", file_path, e)`
- **Line 121**: TTL sweep `unlink()` → `logger.warning`.
- **Line 137**: `print(f"Error pruning review queue: {e}")` → `logger.warning("Error pruning review queue: %s", e)`

### File 8b: `src/omega/workers/background_researcher/scheduler.py`
> ⚠️ This file has **no logger defined**. Add at top of file:
> ```python
> import logging
> logger = logging.getLogger(__name__)
> ```

- **Line 34**: `print(f"Error loading scheduler state: {e}")` → `logger.warning("Error loading scheduler state: %s", e)`
- **Line 44**: `print(f"Error saving scheduler state: {e}")` → `logger.warning("Error saving scheduler state: %s", e)`
- **Line 52**: `print(f"Error loading research topics config: {e}")` → `logger.warning("Error loading research topics config: %s", e)`

### File 9: `src/omega/workers/background_researcher/soul_updater.py`
- **Line 86**: Soul YAML load → blank default. Add `logger.warning`.

### File 10: `src/omega/cli/repl.py`
- **Line 100**: State load → silent default. Add `logger.warning`.
- **Line 286**: WAD load → silent default. Add `logger.warning`.

---

## Step 2: Fix Falsy-Trap in `openai_compat.py` (B2)

**File**: `src/omega/oracle/backends/openai_compat.py` line 102

```python
# BEFORE:
config.timeout_seconds = config.timeout_seconds or 15.0  # Groq is fast

# AFTER:
if config.timeout_seconds is None:
    config.timeout_seconds = 15.0  # Groq is fast
```

Leave line 91 (`config.base_url or "https://openrouter.ai/api"`) alone — `""` is not a valid base_url so `or` is correct there.

---

## Step 3: Fix Hardcoded Paths (B3/B4)

### File 1: `src/omega/library/greek.py` line 200

```python
# BEFORE:
"path": "/media/arcana-novai/omega_library/models/gguf/Krikri-8b-Instruct-Q5_K_M.gguf",

# AFTER:
"path": str(Path(os.environ.get(
    "OMEGA_MODELS_DIR",
    str(Path.home() / "omega" / "models" / "gguf")
)) / "Krikri-8b-Instruct-Q5_K_M.gguf"),
```

### File 2: `src/omega/oracle/cpu_optimizer.py` lines 185-186

```python
# BEFORE:
"cp build/bin/llama-server /home/arcana-novai/.local/bin/\n"
"cp build/bin/llama-cli /home/arcana-novai/.local/bin/\n\n"

# AFTER:
f"cp build/bin/llama-server {Path.home()}/.local/bin/\n"
f"cp build/bin/llama-cli {Path.home()}/.local/bin/\n\n"
```

---

## Do NOT Touch (Legitimate Carve-Outs)

These bare excepts are intentional and correct:
- `src/omega/oracle/health_monitor.py` lines 140 and 165 — health probe exceptions
- `src/omega/oracle/oracle.py:873` — `except Exception: raise` — correctly re-raises
- `src/omega/workers/background_researcher/searxng_client.py:92` — health check returning False
- `src/omega/oracle/model_gateway.py:370` — already has `logger.debug(..., exc_info=True)`

---

## Quality Gates (Run After ALL Fixes)

```bash
# Gate 1: Full test suite
make test
# MUST show: 302 passed, 0 failed

# Gate 2: Zero harmful bare excepts remain
grep -rn "except Exception:" src/omega/ | grep -v "logger\.\|raise\|# health probe"
# MUST return ONLY the 4 carve-outs listed above

# Gate 3: Zero hardcoded user paths (GitHub org URL is OK)
grep -rn "/home/arcana-novai" src/omega/ --include="*.py" | grep -v "__pycache__"
grep -rn "/media/arcana-novai" src/omega/ --include="*.py" | grep -v "__pycache__"
# Both MUST return 0

# Gate 4: Zero asyncio imports (including indented)
grep -rn "import asyncio" src/omega/ --include="*.py" | grep -v "__pycache__"
# MUST return 0

# Gate 5: No print() used for error logging
grep -rn 'print(f"Error' src/omega/ --include="*.py" | grep -v "__pycache__"
# MUST return 0
```

---

## Commit & Documentation Update

When all 5 gates pass:

```bash
git add -A
git commit -m "fix: Option B — Mandate 9 violations, falsy-trap, hardcoded paths"
git push origin main
```

Then update `OMEGA_ENGINE.md`:
1. In **Phase Priority Queue**: mark `⏳ REMAINING — Option B` block as `✅ DONE`
2. Update `Last Updated` line

```bash
git add OMEGA_ENGINE.md
git commit -m "docs: mark Option B complete in OMEGA_ENGINE.md"
git push origin main
```

---

## On Completion

When complete, post a brief summary covering:
1. Which files were changed
2. Final `make test` result
3. Gate 2-5 output (paste the grep results)

---

*⬡ OMEGA ⬡ GEMMA4 ⬡ Option B — Horizon 1 Final Gate*
*"Code that looks right but has the wrong constants is invisible. Code that fails silently is worse."*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: trc_option_b_gem4 | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
