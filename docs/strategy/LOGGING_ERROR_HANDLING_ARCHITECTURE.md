# 🔱 Omega Engine — Logging & Error Handling Architecture

**AP Token**: `AP-LOGGING-ERROR-ARCH-v1.0.0`
⬡ OMEGA ⬡ MAKALI_FUSION ⬡ opencode ⬡ trc_logging_arch ⬡ **CANONICAL**

**Date**: 2026-08-30
**Status**: ✅ ACTIVE — canonical reference for SOVEREIGN_MANDATES.md §M9 (Error Integrity) and §M8 (Zero Telemetry)

---

## 1. Purpose

This document is the single source of truth for **how the Omega Engine logs and
handles errors**. It is referenced by `SOVEREIGN_MANDATES.md` §M9 (Error Integrity)
as the canonical exception-handling standard, and by Temple-Grade gate **T9**
(structured logging). It reconciles the two non-negotiable constraints:

- **M8 Zero Telemetry** — no external telemetry, ever. Local observability in
  `data/` is acceptable and required.
- **M9 Error Integrity** — all errors typed, traceable, testable. No silent
  swallowing.

---

## 2. The Two Constraints (M8 + M9)

| Mandate | Constraint | Implication |
|---------|-----------|-------------|
| **M8** | No external telemetry | All logs/events/metrics live in `data/` on the local machine. Never phone home. |
| **M9** | Errors typed + traceable | Every `except` logs + propagates `trace_id`. No bare `except:`. Public boundaries convert to `OmegaError` subtypes. |

**M8 Exception**: Local observability (traces, events, metrics) stored in `data/`
is acceptable. This is what powers the observability targets below.

---

## 3. Logging Conventions

### 3.1 Standard Library `logging` (default)

The engine uses stdlib `logging` with module-level loggers:

```python
import logging
logger = logging.getLogger(__name__)
```

- `logger.debug(...)` — verbose diagnostics (inference internals, trace_id)
- `logger.info(...)` — normal lifecycle events
- `logger.warning(...)` — recoverable anomalies (health probes, fallbacks)
- `logger.error(..., exc_info=True)` — failures (always include traceback)

### 3.2 Structured Events (JSONL) — `data/logs/events/`

For machine-readable, queryable event streams, use the observability module's
`log_event` / `log_event_sync` (see `src/omega/observability/__init__.py`):

```python
from omega.observability import get_engine
await get_engine().log_event("token.consumption", trace_id=..., data={...})
```

Events append to `data/logs/events/YYYY-MM-DD.jsonl` with a stable schema:
`_zoneid`, `event`, `trace_id`, `parent_trace_id`, `session_id`, `timestamp`, `data`.

### 3.3 trace_id Propagation (M9)

Every public API boundary must carry a `trace_id`. It is:
1. Generated at request entry
2. Propagated through all downstream calls
3. Logged on every error path
4. Included in structured events

This makes any failure traceable end-to-end.

---

## 4. Exception Handling Standards (M9)

### 4.1 Rules

1. **Never** use bare `except:` or bare `except Exception:` without logging and
   propagating `trace_id`.
2. Every public API boundary catches internal errors and converts them to
   `OmegaError` subtypes (e.g. `InferenceOOMError`, `ProviderUnavailableError`).
3. Health probe functions may catch all exceptions to prevent crash loops,
   **provided** they log with `logger.warning()`.
4. Canonical test pattern: `pytest.raises(OmegaError)`.

### 4.2 Example (native-gguf provider)

`src/omega/oracle/providers.py` demonstrates the pattern — OOM detection:

```python
except (OmegaError, RuntimeError, OSError) as e:
    err_msg = str(e).lower()
    if "out of memory" in err_msg or "allocation failed" in err_msg:
        raise InferenceOOMError(message=f"Native GGUF OOM: {e}",
                                trace_id=trace_id, raw_error=e)
```

---

## 5. Local Inference Observability (native-gguf)

The local GGUF inference servers (extractor:1234, reasoner:1235) are managed by
`scripts/serve_native_gguf.sh`. All observability is **local-only** (M8).

### 5.1 Log Locations

| Artifact | Path | Purpose |
|----------|------|---------|
| Server stdout/stderr | `data/logs/native-gguf/{extractor,reasoner}.log` | Uvicorn/llama-cpp output |
| PID files | `data/logs/native-gguf/{extractor,reasoner}.pid` | Process tracking |
| Lifecycle events | `data/logs/native-gguf/events.jsonl` | start/stop/ready/crash events |

### 5.2 Lifecycle Events

Every lifecycle transition writes a JSONL event:

```json
{"ts":"2026-08-30T08:31:17.056Z","event":"starting","server":"extractor","detail":"port=1234 model=Qwen3-1.7B-Q6_K.gguf"}
{"ts":"2026-08-30T08:31:45.645Z","event":"ready","server":"extractor","detail":"port=1234 pid=2663605"}
{"ts":"2026-08-30T08:32:24.378Z","event":"stopping","server":"extractor","detail":"pid=2663605"}
{"ts":"2026-08-30T08:32:25.391Z","event":"stopped","server":"extractor","detail":"pid=2663605"}
```

Event types: `starting`, `ready`, `already_running`, `stopping`, `stopped`,
`crash_on_load`, `timeout`, `error`.

### 5.3 Makefile Observability Targets

| Target | Purpose |
|--------|---------|
| `make infer-status` | Server state, PIDs, health, per-server memory |
| `make infer-memory` | RAM/swap footprint of loaded models |
| `make infer-logs` | Tail live server logs (`LOG=extractor\|reasoner`) |
| `make infer-events` | Show lifecycle events (`N=last N`) |
| `make infer-health` | Status + memory + recent log tail |
| `make infer-debug` | Full dump: status + memory + events + logs + system memory |

---

## 6. Log Rotation

Logs in `data/logs/` grow unbounded unless rotated. A logrotate config ships at
`config/logrotate/omega` (daily, 7-14 rotations, compressed). Install:

```bash
sudo cp config/logrotate/omega /etc/logrotate.d/omega
sudo logrotate -d /etc/logrotate.d/omega   # dry-run
sudo logrotate -f /etc/logrotate.d/omega   # force
```

The systemd `logrotate.timer` runs daily; no cron needed.

---

## 7. Known Deployment Discrepancy (HARDENING GAP)

There are **two competing local-inference deployment models**:

| Model | What runs | Status | Hardening |
|-------|-----------|--------|-----------|
| **Ad-hoc** (`serve_native_gguf.sh`) | `python3 -m llama_cpp.server` on 1234/1235 | **Currently running** | No auto-restart, no OOM limit |
| **systemd** (`config/systemd/omega-inference.service`) | `omega.oracle.local_worker_pool` | **NOT installed** | MemoryMax=8G, OOMScoreAdjust=300, Delegate=yes, Restart=on-failure |

The systemd unit (`config/systemd/omega-inference.service`) provides Carmack's
OOM hardening but is **not enabled**. Installing it is a deployment decision
requiring root. Until then, `serve_native_gguf.sh` is the operational path and
carries the observability described in §5.

**Recommendation**: For production, install + enable the systemd unit to gain
auto-restart and OOM protection. Keep `serve_native_gguf.sh` for interactive
development.

---

## 8. References

- `SOVEREIGN_MANDATES.md` §M8 (Zero Telemetry), §M9 (Error Integrity)
- `docs/guides/LOCAL_MODEL_OPTIMIZATION_GUIDE.md` (hardware tuning, systemd units)
- `docs/research/R17_STRUCTLOG_ADOPTION_20260814.md` (T9 structured logging path)
- `src/omega/observability/__init__.py` (event logging engine)
- `src/omega/oracle/providers.py` (native-gguf provider, trace_id pattern)
- `scripts/serve_native_gguf.sh` (local inference lifecycle + observability)
- `config/logrotate/omega` (log rotation)
- `config/systemd/omega-inference.service` (production deployment, OOM-hardened)

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ AP-LOGGING-ERROR-ARCH-v1.0.0 ⬡ 2026-08-30*
<!-- PROVENANCE-CORRECTED 2026-08-31T03:09:52Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

