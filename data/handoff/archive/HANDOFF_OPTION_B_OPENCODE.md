<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — Option B Execution Handoff (Kali Strategic Review — Corrected)
# ⬡ OMEGA ⬡ KALI → OPENCODE ⬡ trc_option_b_exec ⬡ 2026-06-01

**From**: Kali (Antigravity Strategic Layer — post full codebase audit)
**To**: OpenCode Executor (doom_guy / quality / pillar agents)
**Pre-flight snapshot**: `git reset --hard HEAD` to roll back if needed
**Baseline**: ✅ 292/292 tests passing
**Estimated Time**: ~40–50 minutes
**Reference**: `data/handoff/HANDOFF_BIG_PICKLE_OPTION_A.md` (§2 and §5)

> [!IMPORTANT]
> This handoff supersedes the original Option B scope with **3 corrections** from a live codebase audit:
> 1. `loop.py` has **7** bare excepts, not 4. Lines 320, 448, 454 were missed.
> 2. `model_gateway.py` line 370 already has `logger.debug(..., exc_info=True)` — it is **NOT** a Mandate 9 violation. Leave it.
> 3. The `asyncio` fix in `observability.py` is a **2-line removal** inside `_detect_anyio_backend()` (lines 235-236), NOT a module-level import. `import asyncio` appears nowhere else.

> [!WARNING]
> **Opus 4.6 Deep Audit — 5 Additional Findings** (2026-06-01T22:17 UTC)
>
> 1. **STRUCTURAL BUG in `observability.py`**: `_collect_system_info()` (line 214) is **broken**. The `@staticmethod` decorator at line 224 *terminates the method body* — the psutil block at lines 248-255 and `return info` at line 255 are **unreachable dead code**. The method builds an `info` dict at line 219 but **never returns it**. This must be fixed alongside the asyncio cleanup (see Step 1 addendum below).
> 2. **Falsy-trap location corrected**: The trap is in `create_groq_provider()` (a **factory function**, not a method on the class), at line 102 of `openai_compat.py`. The `ProviderConfig` dataclass already defaults `timeout_seconds=30.0` in `remote_provider.py:72`, so the `or` is only dangerous if someone explicitly passes `timeout_seconds=0`. Low risk but still a correctness issue.
> 3. **`review_queue.py` and `scheduler.py` use `print()` instead of `logger`**: Both files use `print(f"Error...")` for error reporting and have **no logger defined at all** — they need `import logging` + `logger = logging.getLogger(__name__)` added, and all `print()` calls converted to `logger.warning()`.
> 4. **`searxng_client.py:92`** is listed as a carve-out, but verify it actually has `logger` imported — if not, the carve-out reasoning ("health probe returning False") needs to remain but should still get `as e` + a `logger.debug` to satisfy Mandate 9's "provided they log the error" clause.
> 5. **Gate 4 grep pattern is incomplete**: `grep -rn "^import asyncio"` only matches module-level imports. The actual violation is an *indented* `import asyncio` at line 235. Use `grep -rn "import asyncio" src/omega/` instead (no `^` anchor).

---

## Mission

Fix all remaining Mandate 9 violations and hardened issues identified in the Big Pickle Review.
This is the final gate for Horizon 1. Do not open Horizon 2 tasks in this session.

**Always**: `source .venv/bin/activate && <command>`
**After every file change**: `make test` (292 must pass)

---

## Execution Order (STRICT — do not reorder)

### Step 0: Verify Baseline & Confirm Live Counts
```bash
source .venv/bin/activate && make test
# Must show: 292 passed, 0 failed

# Also confirm the bare except count before you start:
grep -rn "except Exception:" src/omega/ | grep -v "# health probe"
# Should show 27 matches. If different, count before vs after your changes.

# Confirm asyncio import location:
grep -rn "import asyncio" src/omega/
# Should show ONLY: observability.py:235 (inside _detect_anyio_backend method)
```

### Step 1: Fix `observability.py` — asyncio import AND structural bug (FIRST — most dangerous)

**File**: `src/omega/observability.py`
**Two bugs in one area** (lines 214-255) that must be fixed together:

#### Bug 1A: `_collect_system_info()` is structurally broken (lines 214-255)

The `@staticmethod` decorator at line 224 **terminates** `_collect_system_info()` — it never reaches the psutil block or `return info`. The current code:

```python
    def _collect_system_info(self) -> Dict[str, Any]:     # line 214
        info: Dict[str, Any] = {                           # line 219
            "anyio_backend": self._detect_anyio_backend(),
            "timestamp": time.time(),
        }                                                  # line 222
                                                           # ← BODY ENDS HERE!
    @staticmethod                                          # line 224 — starts NEW method
    def _detect_anyio_backend() -> str:
        ...                                                # lines 225-246

        try:                                               # line 248 — DEAD CODE!
            import psutil
            info["rss_mb"] = ...                           # NameError: 'info' not defined
        except ImportError:
            pass
        return info                                        # line 255 — UNREACHABLE
```

**Fix**: Close `_collect_system_info` properly with the psutil block and return, THEN define `_detect_anyio_backend` as a separate static method:

```python
    def _collect_system_info(self) -> Dict[str, Any]:
        """Collect system-level info for crash dump.

        Lightweight, synchronous — safe to call from signal handlers.
        """
        info: Dict[str, Any] = {
            "anyio_backend": self._detect_anyio_backend(),
            "timestamp": time.time(),
        }

        try:
            import psutil
            info["rss_mb"] = psutil.Process().memory_info().rss / 1024 / 1024
            info["cpu_percent"] = psutil.cpu_percent(interval=0.1)
        except ImportError:
            pass

        return info

    @staticmethod
    def _detect_anyio_backend() -> str:
        # ... (see Bug 1B fix below)
```

#### Bug 1B: `_detect_anyio_backend()` imports asyncio (lines 235-236)

Replace the entire method body with sniffio-based detection:

```python
    @staticmethod
    def _detect_anyio_backend() -> str:
        """Detect the running anyio backend in a portable way."""
        try:
            from anyio._core._eventloop import get_async_backend
            return get_async_backend()
        except Exception:
            try:
                import sniffio
                return sniffio.current_async_library()
            except Exception:
                pass
            return "unknown"
```

Note: `sniffio` is already in the venv (it's an AnyIO dependency).

**Both fixes must be applied atomically** — they occupy the same line range (214-255).

```bash
make test  # 292 must pass
```

### Step 2: Fix 17 Bare `except Exception:` Without Logging (B1)

Work through each file below in order. After fixing ALL exceptions in a single file, run `make test` before moving to the next.

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

#### File 1: `src/omega/oracle/model_gateway.py`

Grep finds 3 bare excepts: lines 370, 405, 422.

- **Line 370** (`_resolve_ollama_model`): Already has `logger.debug(..., exc_info=True)`. ✅ **LEAVE IT — not a violation.**
- **Line 405** (`_precheck_provider`): `provider.is_available()` raises silently → returns False. Add logging.
- **Line 422** (`_record_provider_failure`): Observability log event raises silently → `pass`. Add logging.

```python
# Line 405 fix:
except Exception as e:
    logger.warning("Provider %s availability check failed: %s", getattr(provider, 'name', '?'), e)
    return False

# Line 422 fix:
except Exception as e:
    logger.warning("Failed to log BACKEND_FALLBACK event for provider %s: %s",
                   getattr(provider, 'name', '?'), e)
```

```bash
make test
```

#### File 2: `src/omega/observability.py` (bare excepts — separate from asyncio fix)

- **Line 193**: Provider counter collection inside `_collect_engine_state()` → `pass`. Add `logger.warning`.
- **Line 209**: `/proc/self/status` fallback → `pass`. Add `logger.warning`.

```python
# Line 193 fix:
except Exception as e:
    logger.warning("Failed to collect provider state for crash dump: %s", e)

# Line 209 fix:
except Exception as e:
    logger.warning("Failed to read /proc/self/status for RSS: %s", e)
```

```bash
make test
```

#### File 3: `src/omega/oracle/providers.py`
- **Line 319**: Memory estimation → silent zeros. Add `logger.warning`.

```bash
make test
```

#### File 4: `src/omega/oracle/cpu_optimizer.py`
- **Line 385**: `awk` subprocess → wrong RAM estimate. Add `logger.warning`.

```bash
make test
```

#### File 5: `src/omega/memory/providers.py`
- **Line 135**: Redis `client.close()` → silent. Add `logger.warning`.
- **Line 256**: Lock file `unlink()` → silent. Add `logger.warning`.

```bash
make test
```

#### File 6: `src/omega/library/inbox.py`
- **Line 201**: JSON parse → silent default. Add `logger.warning`.
- **Line 221**: Item fetch → silent None. Add `logger.warning`.

```bash
make test
```

#### File 7: `src/omega/workers/background_researcher/loop.py`

Actual grep count: **7 bare excepts** at lines 212, 241, 301, 320, 440, 448, 454.

The original handoff missed lines 320, 448, and 454. Here's what each one is:

- **Line 212** (`run_cycle` finally): `lock_path.rmdir()` — lock cleanup. Add `logger.warning`.
- **Line 241** (`_local_discovery_scan`): file read error → `continue`. Already in a loop over files. Add `logger.warning` before `continue`.
- **Line 301** (`_extract`): URL fetch → `continue`. Add `logger.warning`.
- **Line 320** (`_fetch_content`): Raw httpx GET fallback → `return None`. Add `logger.warning`.
- **Line 440** (`_post_to_hivemind`): Cycle log append → `pass`. Add `logger.warning`.
- **Line 448** (`_is_network_available`): First network check → `pass`. Add `logger.warning` (with level `debug` acceptable here — network probes are noisy).
- **Line 454** (`_is_network_available`): Second network check → `return False`. Add `logger.warning`.

```bash
make test
```

#### File 8: `src/omega/workers/background_researcher/review_queue.py`

> [!WARNING]
> This file has **no logger defined**. You must add these lines at the top of the file (after `from pathlib import Path`):
> ```python
> import logging
> logger = logging.getLogger(__name__)
> ```

- **Line 104**: `print(f"Error processing review item...")` → convert to `logger.warning("Error processing review item %s: %s", file_path, e)`.
- **Line 121**: TTL sweep `unlink()` → silent. Add `logger.warning`.
- **Line 137**: `print(f"Error pruning review queue: {e}")` → convert to `logger.warning("Error pruning review queue: %s", e)`.

```bash
make test
```

#### File 8b: `src/omega/workers/background_researcher/scheduler.py`

> [!WARNING]
> This file also has **no logger defined**. You must add these lines at the top of the file:
> ```python
> import logging
> logger = logging.getLogger(__name__)
> ```

- **Line 34**: `print(f"Error loading scheduler state: {e}")` → convert to `logger.warning("Error loading scheduler state: %s", e)`.
- **Line 44**: `print(f"Error saving scheduler state: {e}")` → convert to `logger.warning("Error saving scheduler state: %s", e)`.
- **Line 52**: `print(f"Error loading research topics config: {e}")` → convert to `logger.warning("Error loading research topics config: %s", e)`.

```bash
make test
```

#### File 9: `src/omega/workers/background_researcher/soul_updater.py`
- **Line 86**: Soul YAML load → blank default. Add `logger.warning`.

```bash
make test
```

#### File 10: `src/omega/cli/repl.py`
- **Line 100**: State load → silent default. Add `logger.warning`.
- **Line 286**: WAD load → silent default. Add `logger.warning`.

```bash
make test
```

### Step 3: Fix Falsy-Trap in `openai_compat.py` (B2)

**File**: `src/omega/oracle/backends/openai_compat.py` line 102

This is inside `create_groq_provider()` (a **factory function**, not a class method). The `ProviderConfig` dataclass already defaults `timeout_seconds=30.0` in `remote_provider.py:72`, so the `or` only triggers if someone explicitly passes `0` — but correctness matters:

```python
# BEFORE (line 102):
config.timeout_seconds = config.timeout_seconds or 15.0  # Groq is fast

# AFTER:
if config.timeout_seconds is None:
    config.timeout_seconds = 15.0  # Groq is fast
```

Also check line 91 in the same file — `config.base_url = config.base_url or "https://openrouter.ai/api"` has the same pattern, but `""` is not a valid base_url so `or` is correct here. Leave line 91 alone.

```bash
make test
```

### Step 4: Fix Hardcoded Paths (B3/B4)

**File**: `src/omega/library/greek.py` line 200

The hardcoded path is inside `get_krikri_model_spec()` — a function that returns a static dict. The fix is to use an environment variable or a relative path from config:

```python
# BEFORE (line 200):
"path": "/media/arcana-novai/omega_library/models/gguf/Krikri-8b-Instruct-Q5_K_M.gguf",

# AFTER:
"path": str(Path(os.environ.get(
    "OMEGA_MODELS_DIR",
    str(Path.home() / "omega" / "models" / "gguf")
)) / "Krikri-8b-Instruct-Q5_K_M.gguf"),
```

Note: `os` and `Path` are already imported in this file.

**File**: `src/omega/oracle/cpu_optimizer.py` lines 185-186

These are inside a string template returned by `get_build_instructions()`. The fix:

```python
# BEFORE (lines 185-186):
"cp build/bin/llama-server /home/arcana-novai/.local/bin/\n"
"cp build/bin/llama-cli /home/arcana-novai/.local/bin/\n\n"

# AFTER:
f"cp build/bin/llama-server {Path.home()}/.local/bin/\n"
f"cp build/bin/llama-cli {Path.home()}/.local/bin/\n\n"
```

Note: `Path` is already imported. The `get_build_instructions()` method at line 176 already returns a string, but the current implementation uses regular string concatenation — change lines 185-186 to f-strings. Since the surrounding lines already use f-strings (line 182), this is consistent.

> [!NOTE]
> `openai_compat.py:93` also references `arcana-novai` but in a GitHub URL (`https://github.com/arcana-novai/omega-engine`). This is the project's actual GitHub org name, NOT a hardcoded user path. **Leave it.**

```bash
make test
```

---

## Do NOT Touch (Legitimate Carve-Outs)

These bare excepts are intentional and correct. Leave them alone:
- `src/omega/oracle/health_monitor.py` lines 140 and 165 — health probe exceptions, explicit Mandate 9 carve-out
- `src/omega/oracle/oracle.py:873` — `except Exception: raise` — correctly re-raises
- `src/omega/library/searxng_client.py:92` — health check returning False, covered by health probe exception

---

## Quality Gates (Run After ALL Fixes)

```bash
# Gate 1: Full test suite
make test
# MUST show: 292 passed, 0 failed

# Gate 2: Zero harmful bare excepts remain
grep -rn "except Exception:" src/omega/ | grep -v "logger\.\|raise\|# health probe"
# MUST return ONLY the carve-outs (health_monitor.py:140, health_monitor.py:165, oracle.py:873, searxng_client.py:92)
# If searxng_client.py was updated with logger.debug, it will disappear from this list — that's fine.

# Gate 3: Zero hardcoded user paths (GitHub org URL is OK)
grep -rn "/home/arcana-novai" src/omega/
grep -rn "/media/arcana-novai" src/omega/
# Both MUST return 0

# Gate 4: Zero asyncio imports (including indented)
grep -rn "import asyncio" src/omega/
# MUST return 0 — note: no ^ anchor, catches indented imports too

# Gate 5 (NEW): No print() used for error logging
grep -rn 'print(f"Error' src/omega/
# MUST return 0
```

---

## Commit & Documentation Update

When all 4 gates pass:

```bash
git add -A
git commit -m "fix: Option B — Mandate 9 violations, falsy-trap, hardcoded paths, asyncio import"
git push origin main
```

Then update `OMEGA_ENGINE.md`:
1. In **Current State** table: remove "17 bare except + 4 others (Option B)" row
2. In **Phase Priority Queue**: mark the entire `⏳ REMAINING — Option B` block as `✅ DONE`
3. Update `Last Updated` line at bottom

```bash
git add OMEGA_ENGINE.md
git commit -m "docs: mark Option B complete in OMEGA_ENGINE.md"
git push origin main
```

---

## On Completion: Report Back

When complete, post a brief summary covering:
1. Which files were changed
2. Final `make test` result
3. Any deviations from this plan (and why)
4. Gate 2-4 output (paste the grep results)

**Horizon 2 does not open until this report is received by Kali.**

---

*⬡ OMEGA ⬡ KALI → OPENCODE ⬡ Option B — Horizon 1 Final Gate*
*"Code that looks right but has the wrong constants is invisible. Code that fails silently is worse."*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: trc_option_b_exec | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
