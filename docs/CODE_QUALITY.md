# CODE QUALITY — Omega Engine Alpha + WanderGround

Living standard for every Python/JS/TS project under the Omega Engine umbrella
(`omega-engine-alpha`, `~/WanderGround`, federation tooling, knative-harness bits).

---

## 1. Async wiring: absolute anyio (HIGHEST PRIORITY — user directive)

> "We observe **absolute anyio full async wiring**."

Any async Python code in this ecosystem MUST be written exclusively against
[anyio](https://anyio.readthedocs.io/) primitives. No bare `asyncio`, no bare
`trio`, no `uvloop`-specific calls in application code.

### Allowed imports (app/scripts/plugins)
- `import anyio` — THE namespace.
- `anyio.run`, `anyio.to_thread.run_sync`, `anyio.to_process.run_sync`
- `anyio.create_task_group`, `anyio.CancelScope`, `anyio.move_on_after`, `anyio.fail_after`
- `anyio.Stream`, `anyio.AsyncFile`, `anyio.open_process`, `anyio.connect_tcp`
- `anyio.Event`, `anyio.Semaphore`, `anyio.Lock`, `anyio.CapacityLimiter`
- `anyio.lowlevel` only when explicitly documented (rare)

### Forbidden in application code
- `import asyncio` (bare event-loop calls)
- `import trio` (application code)
- `uvloop.install()`
- `asyncio.run(...)` in anything not a one-shot script entrypoint — use `anyio.run`

### Why
- Backend-agnostic (asyncio OR trio) — the engine can adopt Trio for structured
  concurrency without a rewrite.
- Cancellation, timeouts, and task groups behave identically across backends.
- Matches the modern stack: httpx, starlette/fastapi, and opencode SDK internals
  are anyio-native.

### Enforcement
- `make lint-async` / grep gate: reject `^\s*(import|from) (asyncio|trio)\b` in
  `scripts/`, `spatial/scripts/`, `*.py` at repo root (allow `trio`/`asyncio`
  ONLY inside a clearly-named stdlib-vs-anyio adapter module with a comment).
- Exceptions: MemPalace/ChromaDB internals (vendored, third-party) are NOT our code.

---

## 2. General Python standards
- **Type hints** on all public functions; `from __future__ import annotations`.
- **No torch. Ever.** CPU-only, memory-bounded. (See HARDWARE.md memory discipline.)
- Prefer stdlib + small deps; heavy ML stacks live behind optional extras.
- CLI entrypoints: `if __name__ == "__main__": main()`, `parse_args` explicit, exit codes.
- Never block on network inside a hot path; use `timeout`/`fail_after` everywhere.
- Secrets stay in `{env:...}` placeholders — never literals.
- Subprocess safety: non-interactive runs pipe `</dev/null` and carry a hard `timeout`.

## 3. Bash
- `set -euo pipefail`; every helper under `~/.local/bin/` idempotent.
- Never `pkill -f "<self-matching-string>"` — use explicit PIDs or bracket patterns
  (`mem[p]alace`) to avoid killing the invoking shell.
- Dangerous/unknown commands run through `withey` (pre/post snapshot).

## 4. Docs & ground truth
- Every research claim that changes behavior must be dated + cited in the
  relevant spec’s “Research Findings” section.
- SSOT: `docs/HARDWARE.md`, `docs/SYSTEM_GUIDE.md`, `docs/WANDERGROUND_SPEC.md`.