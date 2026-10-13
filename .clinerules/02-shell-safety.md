# Shell Safety Patterns (Cline, 2026-10-13 — every rule here cost real debugging)

## 1. `$(fuser …)` under `set -euo pipefail` = SILENT DEATH

`fuser` exits **1 when nothing holds the file** — i.e. the *success* case for a lock check. Nonzero inside `$(…)` terminates the script with **no log line, no exit code** (root-caused twice in `scripts/opencode_db_reclaim.sh`).

```bash
HOLDERS=$(fuser "$FILE" 2>/dev/null | tr -s ' ' ' ' | sed 's/^ //' || true)   # || true is LOAD-BEARING
```
Same class: `grep -c` with zero matches, any command whose *clean* outcome is nonzero. Audit `$()` captures for these before shipping any `set -euo` script.

## 2. `timeout`-kill read as empty output = false-PASS gate

`RESULT=$(timeout N check | head -3)` — a kill (rc 124) yields EMPTY output, and `[ -n "$RESULT" ]` reads that as "clean". **The gate passes work that never ran.** On HDD this is not hypothetical: contention made a 300s budget unachievable while the check was still in `D` state.

```bash
set +e
OUT=$(timeout "$N" check 2>&1); RC=$?
set -e
[ "$RC" -eq 124 ] && die "TIMED OUT — unknown, not clean" 20
[ "$RC" -ne 0 ] && die "check errored (rc=$RC): $OUT" 20
```
Treat "unknown" as failure, never as pass. Kill budget must EXCEED worst observed runtime.

## 3. Validate shape before numeric comparison

Captured counts can be empty/error-text; `[ "$X" -lt 5 ]` on garbage silently misbehaves. Always:
```bash
case "$VAL" in ''|*[!0-9]*) die "not numeric: '$RAW'" 30;; esac
```

## 4. `pkill -f <pattern>` matches YOUR wrapper

`pkill -f 'install.sh'` kills the `bash -c` line containing the string — self-SIGTERM. **Kill by PID**, or use precise `pkill -x`/`pgrep` filtering.

## 5. Ordering traps

- Export env (e.g. `CMAKE_BUILD_PARALLEL_LEVEL`) **before** the first command that can consume it. A pre-fetch block placed above the export silently built at `-j16` and thrashed the box; default is **6**.
- `$(…)` captures in `$()` run when parsed in some contexts — assume ordering matters and verify with a log line.

## 6. Background + nohup discipline

- `nohup … &` inside a tool call: the launcher PID is NOT the job; don't `kill` the launcher and assume the job died.
- Poll with short sleeps (<30s tool budget); write logs to a file and `tail` them rather than blocking.
- Background giant-file work: `ionice -c 3` and never run two concurrently (see host rules).

## Canonical safe-gate skeleton (proven in opencode_db_reclaim.sh after fixes)

```bash
set +e
OUT=$(timeout "$N" cmd 2>&1); RC=$?
set -e
case 124 → die "timeout=unknown";  rc!=0 → die "error";  shape-check OUT;  then compare.
```
