# 🔱 The Sovereign Guardrails (The Steel Script v3)
**AP Token**: `AP-GUARDRAILS-v3.0.0`
⬡ OMEGA ⬡ OVERSEER ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_overseer ⬡ GUARDRAILS

These rules are absolute. Any implementation that violates these guardrails is to be vetoed and refactored immediately.

## 🛡️ Rule 1: The AnyIO Absolute
**"If it touches the disk or the network, it must be Awaited."**
- No `pathlib` synchronous methods (`exists`, `read_text`, `write_text`, `mkdir`) in the runtime path.
- No `open()`, `os.mkdir()`, `os.replace()`, `os.remove()`.
- No `subprocess.run()` or `subprocess.Popen()` unless wrapped in `anyio.to_thread.run_sync`.
- No `time.sleep()`.

## 🛡️ Rule 2: The Engine-Stack Firewall
**"The Engine is the Fire; the WAD is the Tool."**
- The Engine core (`src/omega/`) must remain **Mythology-Agnostic**.
- No hardcoded entity names (except `Iris` as the default messenger).
- All domain-specific logic must be loaded dynamically from a WAD manifest.
- If a feature only serves a specific stack (e.g., Arcana-NovAi), it does not belong in the Engine.

## 🛡️ Rule 3: The zRAM Buffer Rule
**"Use the reserve for spikes, not for residency."**
- The 14GB-18GB "Yellow Zone" is for graceful degradation and temporary spikes.
- Permanent model residency must stay within the 14GB physical limit to avoid CPU thrashing during zRAM compression.

## 🛡️ Rule 4: The Sequentiality Mandate
**"One weight-set at a time."**
- All multi-model reasoning (Lattice/Council) must be implemented as a sequential pipeline.
- Parallel local inference is prohibited to prevent OOM and CPU starvation.

## 🛡️ Rule 5: The Iris Constant
**"Iris is the Anchor."**
- The always-on assistant is **Iris**.
- No changes may be proposed that require shutting down the Iris container.

## 🛡️ Rule 6: The AnyIO Lock Absolute (MCP Middleware)
**"If it locks, it must be `anyio.Lock`."**
- No `threading.Lock()` or `threading.RLock()` in any async code path.
- All synchronization in MCP servers, middleware, and hub modules MUST use `anyio.Lock()`.
- Violation pattern: `mcp_servers/omega_hub/middleware.py:108` used `threading.Lock()` causing race conditions and deadlocks in the MCP server event loop. This is the canonical failure mode to avoid.
- **Remediation**: `grep -rn "threading\.Lock\|threading\.RLock" mcp_servers/ src/omega/` — zero tolerance.

## 🛡️ Rule 7: The Atomic File Lock (State Integrity)
**"If two processes touch the same file, one must see a consistent state."**
- All MCP server file I/O must use atomic file locking (e.g., `portalocker` or `fcntl.flock`) or atomic rename patterns (`.tmp` → `.json`).
- No concurrent reads without a lock guard when a write may be in progress.
- Violation pattern: `mcp_servers/omega_hub/state.py:82-90` had no atomic file locking, causing race conditions during init when multiple clients connected simultaneously.
- **Remediation**: All state files in `data/coordination/` must use atomic write patterns. If a file is shared across processes, it must have a lock.

## 🛡️ Rule 8: The Defined Import Gate (MCP Server Integrity)
**"Every name used in the module must be resolvable at import time."**
- No `NameError`-causing undefined references in MCP server modules.
- Every function called in a handler must be imported or defined in the same file.
- Violation pattern: `mcp_servers/omega_hub/server.py:98` called `get_engine()` which was never defined or imported — caused complete observability failure on SSE initialization.
- **Remediation**: Before any MCP server deployment, run `python3 -c "from mcp_servers.omega_hub.server import *"` to verify all names resolve.

## 🛡️ Rule 9: The Pre-Flight Gate (MCP Deployment)
**"Test the server before starting the timer."**
- Before deploying any MCP server or systemd timer, run:
  1. `python3 -m py_compile <server.py>` — syntax check.
  2. `python3 -c "from <module> import <entrypoint>"` — import check.
  3. `omega talk "hello"` — end-to-end smoke test.
- No MCP server may be merged without passing all three pre-flight checks.
- The 3 critical MCP bugs (undefined `get_engine()`, `threading.Lock()` race, missing atomic file locking) would all have been caught by this gate.

## 🛡️ Rule 10: The Middleware Atomicity Principle
**"A middleware chain is only as strong as its weakest link."**
- Every middleware function must be independently testable — no shared mutable state between middleware layers.
- If a middleware function acquires a resource, it must release it in a `finally` block.
- No middleware function may assume another middleware ran before it (no ordering dependencies).
- **Remediation**: Each middleware should pass a contract test that verifies it can run in isolation.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: gemma-4-31b-it | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
