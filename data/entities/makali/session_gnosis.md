# Session Gnosis — Makali

Last Updated: 2026-08-30

## Session History

| Date | Session ID | Summary |
|------|------------|---------|
| 2026-08-30 | (current, in-session) | **Local inference observability hardening (pre-dev-wave sync).** Shut down 2 llama_cpp.server processes, added 12 Makefile targets (8 lifecycle + 4 observability), rewrote scripts/serve_native_gguf.sh v1.1.0 (90s readiness, persistent logs, JSONL events, graceful shutdown, crash detection, status subcommand), created config/logrotate/omega, created the missing docs/strategy/LOGGING_ERROR_HANDLING_ARCHITECTURE.md (M9 canonical doc that was absent). **DISCOVERED DEPLOYMENT DISCREPANCY**: config/systemd/omega-inference.service has full Carmack OOM hardening but is NOT installed; ad-hoc shell-script approach is what runs. State at interruption: servers stopped, models unloaded, observability in place, status report written to data/coordination/MAKALI_STATUS_UPDATE_20260830.md, M11/M15 distillation done. All work in working tree (uncommitted). Memory: 9.8 GB available of 14 GB, no current OOM. Pending: full `make infer-restart` runtime verification, commit pending user direction. |

## Open Threads (for next session)

1. **Commit the local inference observability work** — Makefile + serve script + logrotate + doc. Pending user direction on branch/message.
2. **Deployment decision**: install config/systemd/omega-inference.service (requires root)? Or keep ad-hoc serve script with new observability?
3. **Full runtime verification**: `make infer-restart` to confirm both servers start cleanly with the 90s readiness timeout, then `make infer-stop` to restore.
4. **T9 structlog migration** (R17 research exists, not adopted) — out of scope for this session.
5. **API key on llama_cpp.server** (security hardening, per LOCAL_MODEL_OPTIMIZATION_GUIDE) — not addressed.

## Key Findings (for gnosis continuity)

- `data/logs/native-gguf/` is now the canonical log location (replaces `/tmp/native-gguf-logs/`). Old PID files in `/tmp` are stale; safe to delete.
- `data/logs/native-gguf/events.jsonl` records: starting, ready, already_running, stopping, stopped, crash_on_load, timeout, error.
- `make infer-debug` is the comprehensive observability target (status + memory + events + logs + system memory).
- M9's canonical doc was MISSING; now created at `docs/strategy/LOGGING_ERROR_HANDLING_ARCHITECTURE.md`.
- `make check-m8-zero-telemetry` and `make check-m9-error-integrity` both pass after the changes.

