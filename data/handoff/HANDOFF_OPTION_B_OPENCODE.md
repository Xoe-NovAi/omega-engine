# 🔱 Omega Engine — Option B Execution Handoff
# ⬡ OMEGA ⬡ KALI → OPENCODE ⬡ trc_option_b_exec ⬡ 2026-06-01

**From**: Kali (Antigravity Strategic Layer)
**To**: OpenCode Executor (doom_guy / quality / pillar agents)
**Pre-flight**: `git reset --hard HEAD` to roll back if needed
**Baseline**: ✅ 292/292 tests passing
**Estimated Time**: ~35–45 minutes
**Reference**: `data/handoff/HANDOFF_BIG_PICKLE_OPTION_A.md` (§2 and §5)

---

## Mission

Fix all remaining Mandate 9 violations and hardened issues identified in the Big Pickle Review.
This is the final gate for Horizon 1. Do not open Horizon 2 tasks in this session.

**Always**: `source .venv/bin/activate && <command>`
**After every file change**: `make test` (292 must pass)

---

## Execution Order (STRICT — do not reorder)

### Step 0: Verify Baseline
```bash
source .venv/bin/activate
make test
# Must show: 292 passed, 0 failed
```

### Step 1: Fix `asyncio` import in `observability.py` (MOST DANGEROUS)

**File**: `src/omega/observability.py` around line 235
**Bug**: `import asyncio; asyncio.get_running_loop()` — creates second event loop reference under AnyIO/Python 3.13

**Action**: Find the `import asyncio` line and the code block using it. Replace the asyncio event loop detection with AnyIO-native detection or remove if it's a dead-code fallback. If it's detecting "are we in an async context", use:
```python
import sniffio
try:
    sniffio.current_async_library()
    _in_async = True
except sniffio.AsyncLibraryNotFoundError:
    _in_async = False
```
If the entire block is a fallback that can be cleanly removed without breaking logic, remove it.

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
- Line ~405: Provider pre-check returns False silently
- Line ~422: Observability event passes silently

```bash
make test  # after this file
```

#### File 2: `src/omega/observability.py`
- Line ~193: Provider counter collection
- Line ~209: `/proc/self/status` fallback

```bash
make test
```

#### File 3: `src/omega/oracle/providers.py`
- Line ~319: Memory estimation → silent zeros

```bash
make test
```

#### File 4: `src/omega/oracle/cpu_optimizer.py`
- Line ~385: `awk` subprocess → wrong RAM estimate

```bash
make test
```

#### File 5: `src/omega/memory/providers.py`
- Line ~135: Redis `client.close()`
- Line ~256: Lock file `unlink()`

```bash
make test
```

#### File 6: `src/omega/library/inbox.py`
- Line ~201: JSON parse → silent default
- Line ~221: Item fetch → silent None

```bash
make test
```

#### File 7: `src/omega/workers/.../loop.py` (background researcher worker loop)
- Line ~212: Lock dir rmdir
- Line ~241: File read failure
- Line ~301: URL fetch failure
- Line ~440: Cycle log append

```bash
make test
```

#### File 8: `src/omega/workers/.../review_queue.py`
- Line ~121: TTL sweep unlink

```bash
make test
```

#### File 9: `src/omega/workers/.../soul_updater.py`
- Line ~86: Soul YAML load → blank default

```bash
make test
```

#### File 10: `src/omega/cli/repl.py`
- Line ~100: State load → silent default
- Line ~286: WAD load → silent default

```bash
make test
```

### Step 3: Fix Falsy-Trap in `openai_compat.py` (B2)

**File**: `src/omega/oracle/backends/openai_compat.py` line ~102

```python
# BEFORE:
config.timeout_seconds = config.timeout_seconds or 15.0

# AFTER:
if config.timeout_seconds is None:
    config.timeout_seconds = 15.0
```

```bash
make test
```

### Step 4: Fix Hardcoded Paths (B3/B4)

**File**: `src/omega/library/greek.py` line ~200
- Replace hardcoded GGUF path with a reference to the model path from `config/models.yaml`
- If dynamic lookup is complex, at minimum use `Path.home() / ".lmstudio" / ...` instead of `/media/arcana-novai/...`

**File**: `src/omega/oracle/cpu_optimizer.py` lines ~185-186
- Replace `/home/arcana-novai/` with `str(Path.home())` or `$HOME` in string template

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
# MUST return only the 3 carve-outs above

# Gate 3: Zero hardcoded absolute paths
grep -rn "/home/arcana-novai" src/omega/
# MUST return 0

# Gate 4: Zero direct asyncio imports
grep -rn "^import asyncio" src/omega/
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
