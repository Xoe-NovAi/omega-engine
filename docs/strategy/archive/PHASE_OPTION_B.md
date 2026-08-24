# 🔱 Option B — Mandate 9 Error Integrity Fixes
## ⬡ OMEGA ⬡ SOPHIA ⬡ trc_option_b ⬡ PHASE
**Target Model**: Gemma 4 31B (OpenCode default) — mechanical find-and-replace
**Est. Time**: 45 minutes
**Pre-flight**: ✅ 292/292 passing, clean working tree
**Rollback**: `git checkout HEAD -- <list of changed files>` per sub-step

---

## §0 Setup

```bash
source .venv/bin/activate
make test  # Confirm 292/292

# Verify file counts before starting:
echo "=== Bare excepts needing fix ==="
grep -rn "except Exception:" src/omega/ | grep -v "logger\.\|raise\|# health" | grep -v "\.pyc" | wc -l
# Should show: 27 (21 violations + 4 carve-outs + 1 logged + 1 structural)
```

## §1 Observability Structural Fix

### Model: DeepSeek V4 Flash or MiMo V2.5
This step requires structural reasoning. Do NOT use a basic model for this step.

### File: `src/omega/observability.py`
### Lines: 214-255 (entire method + dead code)

**Bug**: `_collect_system_info()` terminates at line 222 because `@staticmethod` at line 224 starts a new method. Lines 248-255 are unreachable dead code. The method returns `None` instead of system info, silently breaking crash dump forensics.

**Fix**: Rewrite the method to include the psutil block and return before defining the separate `_detect_anyio_backend()` method. Also replace `import asyncio` with sniffio-based detection.

**BEFORE (lines 214-255)**:
```python
    def _collect_system_info(self) -> Dict[str, Any]:
        info: Dict[str, Any] = {
            "anyio_backend": self._detect_anyio_backend(),
            "timestamp": time.time(),
        }

    @staticmethod
    def _detect_anyio_backend() -> str:
        try:
            from anyio._core._eventloop import get_async_backend
            return get_async_backend()
        except Exception:
            try:
                import asyncio
                asyncio.get_running_loop()
                return "asyncio"
            except RuntimeError:
                pass
            try:
                import trio
                trio.hazmat.current_call_from_trio()
                return "trio"
            except (ImportError, RuntimeError, AttributeError):
                pass
            return "unknown"

        try:
            import psutil
            info["rss_mb"] = psutil.Process().memory_info().rss / 1024 / 1024
            info["cpu_percent"] = psutil.cpu_percent(interval=0.1)
        except ImportError:
            pass

        return info
```

**AFTER (lines 214-246)**:
```python
    def _collect_system_info(self) -> Dict[str, Any]:
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

### Verification
```bash
make test  # Must show 292 passed
grep -rn "import asyncio" src/omega/
# Must return 0 matches
```

---

## §2 Add Logger to review_queue.py

### Model: Any model (Gemma 4 31B)
Simple additive change — add import and convert print() calls.

### File: `src/omega/workers/background_researcher/review_queue.py`
### Lines: Top + 104 + 121 + 137

**BEFORE (line 1-5 area):**
```python
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timezone
```

**AFTER:**
```python
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timezone

logger = logging.getLogger(__name__)
```

**Line 104**: `print(f"Error processing review item {file_path}: {e}")` → `logger.warning("Error processing review item %s: %s", file_path, e)`

**Line 121**: Currently bare `except Exception:` → add logging before `pass`:
```python
except Exception as e:
    logger.warning("TTL sweep unlink failed: %s", e)
```

**Line 137**: `print(f"Error pruning review queue: {e}")` → `logger.warning("Error pruning review queue: %s", e)`

### Verification
```bash
make test  # Must show 292 passed
grep -rn 'print(f"Error' src/omega/
# Must return 0 matches across entire src/omega/
```

---

## §3 Add Logger to scheduler.py

### Model: Any model (Gemma 4 31B)
Same pattern as review_queue.py.

### File: `src/omega/workers/background_researcher/scheduler.py`
### Lines: Top + 34 + 44 + 52

**BEFORE (top of file):**
```python
from pathlib import Path
from typing import Optional, List, Dict, Any
```

**AFTER:**
```python
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)
```

**Line 34**: `print(f"Error loading scheduler state: {e}")` → `logger.warning("Error loading scheduler state: %s", e)`

**Line 44**: `print(f"Error saving scheduler state: {e}")` → `logger.warning("Error saving scheduler state: %s", e)`

**Line 52**: `print(f"Error loading research topics config: {e}")` → `logger.warning("Error loading research topics config: %s", e)`

### Verification
```bash
make test
grep -rn 'print(f"Error' src/omega/
# Must still return 0
```

---

## §4 Fix 21 Bare excepts in 10 Files

### Model: Any model (Gemma 4 31B)
Mechanical find-and-replace. Run `make test` after each file.

### Fix Pattern (apply to ALL bare excepts)
**BEFORE**:
```python
except Exception:
    pass  # or return False, return {}, return None
```

**AFTER**:
```python
except Exception as e:
    logger.warning("description of what failed here: %s", e)
    # keep the original return/fallback below
```

### File-by-File Fixes

#### 4.1 `src/omega/observability.py` — 2 fixes
**Line 193**: Provider counter collection
```python
except Exception as e:
    logger.warning("Failed to collect provider state for crash dump: %s", e)
```

**Line 209**: `/proc/self/status` fallback
```python
except Exception as e:
    logger.warning("Failed to read /proc/self/status for RSS: %s", e)
```

#### 4.2 `src/omega/oracle/model_gateway.py` — 2 fixes
**Line 405**: Provider availability check fails
```python
except Exception as e:
    logger.warning("Provider %s availability check failed: %s",
                   getattr(provider, 'name', '?'), e)
return False
```

**Line 422**: Observability event logging fails
```python
except Exception as e:
    logger.warning("Failed to log BACKEND_FALLBACK event for provider %s: %s",
                   getattr(provider, 'name', '?'), e)
```

**LEAVE LINE 370 ALONE** — it already has `logger.debug(..., exc_info=True)`. Not a violation.

#### 4.3 `src/omega/oracle/providers.py` — 1 fix
**Line 319**: Memory estimation
```python
except Exception as e:
    logger.warning("Failed to estimate memory for provider config: %s", e)
```

#### 4.4 `src/omega/oracle/cpu_optimizer.py` — 1 fix
**Line 385**: `awk` subprocess for RAM estimate
```python
except Exception as e:
    logger.warning("Failed to run awk for RAM detection: %s", e)
```

#### 4.5 `src/omega/memory/providers.py` — 2 fixes
**Line 135**: Redis `client.close()` fails
```python
except Exception as e:
    logger.warning("Failed to close Redis connection: %s", e)
```

**Line 256**: Lock file `unlink()` fails
```python
except Exception as e:
    logger.warning("Failed to unlink lock file: %s", e)
```

#### 4.6 `src/omega/library/inbox.py` — 2 fixes
**Line 201**: JSON parse fails
```python
except Exception as e:
    logger.warning("Failed to parse inbox JSON: %s", e)
```

**Line 221**: Item fetch fails
```python
except Exception as e:
    logger.warning("Failed to fetch inbox item: %s", e)
```

#### 4.7 `src/omega/workers/background_researcher/loop.py` — 7 fixes
Each bare except at lines 212, 241, 301, 320, 440, 448, 454:

**Line 212** (lock cleanup):
```python
except Exception as e:
    logger.warning("Failed to rmdir lock path: %s", e)
```

**Line 241** (file read error):
```python
except Exception as e:
    logger.warning("Failed to read file in local discovery: %s", e)
    continue
```

**Line 301** (URL fetch):
```python
except Exception as e:
    logger.warning("Failed to fetch URL for extraction: %s", e)
    continue
```

**Line 320** (raw httpx GET):
```python
except Exception as e:
    logger.warning("Failed to fetch content via httpx: %s", e)
    return None
```

**Line 440** (hivemind post):
```python
except Exception as e:
    logger.warning("Failed to post to hivemind: %s", e)
```

**Line 448** (network check 1 — use logger.debug, network probes are noisy):
```python
except Exception as e:
    logger.debug("Network check 1 failed (expected if offline): %s", e)
```

**Line 454** (network check 2):
```python
except Exception as e:
    logger.warning("Network check 2 failed: %s", e)
    return False
```

#### 4.8 `src/omega/workers/background_researcher/soul_updater.py` — 1 fix
**Line 86**: Soul YAML load
```python
except Exception as e:
    logger.warning("Failed to load soul YAML: %s", e)
```

#### 4.9 `src/omega/cli/repl.py` — 2 fixes
**Line 100**: State load
```python
except Exception as e:
    logger.warning("Failed to load REPL state: %s", e)
```

**Line 286**: WAD load
```python
except Exception as e:
    logger.warning("Failed to load WAD in REPL: %s", e)
```

---

## §5 Fix Hardcoded Paths

### Model: Any model (Gemma 4 31B)

### 5.1 `src/omega/oracle/backends/openai_compat.py` — Line 102
**Bug**: `config.timeout_seconds or 15.0` — if timeout_seconds is `0`, it becomes 15.0.
**Fix**:
```python
# BEFORE:
config.timeout_seconds = config.timeout_seconds or 15.0  # Groq is fast
# AFTER:
if config.timeout_seconds is None:
    config.timeout_seconds = 15.0  # Groq is fast
```
**LEAVE LINE 91 ALONE** — `config.base_url or "..."` is correct (empty string is never a valid URL).

### 5.2 `src/omega/library/greek.py` — Line 200
**Bug**: Hardcoded `/media/arcana-novai/omega_library/models/gguf/Krikri-8b-Instruct-Q5_K_M.gguf`
**Fix**: Use `OMEGA_MODELS_DIR` env var with fallback:
```python
# BEFORE:
"path": "/media/arcana-novai/omega_library/models/gguf/Krikri-8b-Instruct-Q5_K_M.gguf",
# AFTER:
"path": str(Path(os.environ.get(
    "OMEGA_MODELS_DIR",
    str(Path.home() / "omega" / "models" / "gguf")
)) / "Krikri-8b-Instruct-Q5_K_M.gguf"),
```

### 5.3 `src/omega/oracle/cpu_optimizer.py` — Lines 185-186
**Bug**: Hardcoded `/home/arcana-novai/.local/bin/`
**Fix**: Use `Path.home()`:
```python
# BEFORE:
"cp build/bin/llama-server /home/arcana-novai/.local/bin/\n"
"cp build/bin/llama-cli /home/arcana-novai/.local/bin/\n\n"
# AFTER:
f"cp build/bin/llama-server {Path.home()}/.local/bin/\n"
f"cp build/bin/llama-cli {Path.home()}/.local/bin/\n\n"
```

### Verification
```bash
grep -rn "/home/arcana-novai" src/omega/  # Must return 0
grep -rn "/media/arcana-novai" src/omega/  # Must return 0
make test  # 292 must pass
```

---

## §6 Do NOT Touch (Carve-Outs)

These bare excepts are intentional and correct:
- `src/omega/oracle/health_monitor.py:140` — health probe exception (Mandate 9 carve-out)
- `src/omega/oracle/health_monitor.py:165` — health probe exception (Mandate 9 carve-out)
- `src/omega/oracle/oracle.py:873` — `except Exception: raise` — correctly re-raises
- `src/omega/library/searxng_client.py:92` — health check returning False (carve-out)
- `src/omega/oracle/model_gateway.py:370` — already has `logger.debug(..., exc_info=True)`
- `src/omega/observability.py:233` — handled by structural fix in §1

---

## §7 Final Quality Gates

Run these in order:
```bash
# Gate 1: Full test suite
make test
# Must show: 292 passed, 0 failed

# Gate 2: Zero harmful bare excepts remain
grep -rn "except Exception:" src/omega/ | grep -v "logger\.\|raise\|# health"
# Must return ONLY the 4 carve-outs:
# health_monitor.py:140, health_monitor.py:165, oracle.py:873, searxng_client.py:92

# Gate 3: Zero hardcoded user paths
grep -rn "/home/arcana-novai" src/omega/  # Must return 0
grep -rn "/media/arcana-novai" src/omega/  # Must return 0

# Gate 4: Zero asyncio imports (including indented)
grep -rn "import asyncio" src/omega/  # Must return 0

# Gate 5: Zero print() used for error logging
grep -rn 'print(f"Error' src/omega/  # Must return 0
```

## §8 Commit

```bash
git add -A
git commit -m "fix: Option B — Mandate 9 violations, falsy-trap, hardcoded paths"
git push origin main
```

Then update `OMEGA_ENGINE.md`:
1. In **Current State** table: remove "Mandate 9" pending items
2. In **Phase Priority Queue**: mark Option B block as `✅ DONE`
3. Update `Last Updated` line

---

## §9 Report Back

Post to the session:
1. Which files were changed
2. Final `make test` result
3. Any deviations from this plan (and why)
4. Gates 2-5 output (paste the grep results)

---

*⬡ OMEGA ⬡ SOPHIA ⬡ trc_option_b ⬡ PHASE*
*Target model: Gemma 4 31B (mechanical work). Deep reasoning model required for §1.*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: trc_option_b | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
