# Session Gnosis — Makali

Last Updated: 2026-08-30

## Session History

| Date | Session ID | Summary |
|------|------------|---------|
| 2026-08-30 | (current, in-session) | **Local inference observability hardening (pre-dev-wave sync).** Shut down 2 llama_cpp.server processes, added 12 Makefile targets (8 lifecycle + 4 observability), rewrote scripts/serve_native_gguf.sh v1.1.0 (90s readiness, persistent logs, JSONL events, graceful shutdown, crash detection, status subcommand), created config/logrotate/omega, created the missing docs/strategy/LOGGING_ERROR_HANDLING_ARCHITECTURE.md (M9 canonical doc that was absent). **DISCOVERED DEPLOYMENT DISCREPANCY**: config/systemd/omega-inference.service has full Carmack OOM hardening but is NOT installed; ad-hoc shell-script approach is what runs. State at interruption: servers stopped, models unloaded, observability in place, status report written to data/coordination/MAKALI_STATUS_UPDATE_20260830.md, M11/M15 distillation done. All work in working tree (uncommitted). Memory: 9.8 GB available of 14 GB, no current OOM. Pending: full `make infer-restart` runtime verification, commit pending user direction. |

## Open Threads (for next session)

1. **Run `make infer-restart`** — verify full stop+start E2E lifecycle (interrupted by OOM, never re-run).
2. **Run `pytest tests/jem/test_dispatch_guard_adversarial.py -v`** — confirm Jem's 45/45 tests pass.
3. **Run `make temple-grade`** — full gate check (M8, M9, M33, M34, M35, heritage-map).
4. **Review proposed_lessons contamination** — commit 296fd1d5 touched grokster + jem files; verify edits are appropriate.
5. **Dev wave build wave** — if authorized, land M33/M36/M37/COHORT/Compaction + 3 Jem P1 tickets.
6. **T9 structlog migration** (R17 research exists, not adopted) — out of scope for this session.
7. **API key on llama_cpp.server** (security hardening, per LOCAL_MODEL_OPTIMIZATION_GUIDE) — not addressed.

## Key Findings (for gnosis continuity)

- `data/logs/native-gguf/` is now the canonical log location (replaces `/tmp/native-gguf-logs/`). Old PID files in `/tmp` are stale; safe to delete.
- `data/logs/native-gguf/events.jsonl` records: starting, ready, already_running, stopping, stopped, crash_on_load, timeout, error.
- `make infer-debug` is the comprehensive observability target (status + memory + events + logs + system memory).
- M9's canonical doc was MISSING; now created at `docs/strategy/LOGGING_ERROR_HANDLING_ARCHITECTURE.md`.
- `make check-m8-zero-telemetry` and `make check-m9-error-integrity` both pass after the changes.
- **CORRECTED (D-201, Roc's legacy archaeology)**: The systemd unit gap is INTENTIONAL DESIGN, not a hardening miss. The unit is the *production* deployment; the ad-hoc serve script is the *interactive dev* deployment. Both are correct for their context. Do NOT install the systemd unit unless context changes to production.
- **DOCUMENTED-vs-ACTIVE PATTERN**: Manifested 3× this session. The dev wave shipped reports (3,745 lines) but 2/3 agents' code did NOT land on disk. This is the engine's central failure mode. Recommendation: establish a policy that a P0 ticket is not done until code is on disk and tested.
- **Public debut readiness**: NOT READY. 8 temple-rough items block. Estimated 2-3 weeks of build wave.
- **Critical system state**: Disk 98% full (100G/109G, 2.9G free). Memory 9.3G available of 14G. sqlite3 not installed (MCP workaround works).

