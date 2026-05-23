# 🔱 Omega Engine — MCP Lifecycle & Connectivity Fix
# ⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b ⬡ opencode ⬡ trc_debug ⬡ R-MCP-FIX

**AP Token**: `AP-MCP-LIFECYCLE-v1.0.0`
**Status**: ✅ SPECIFIED
**Date**: 2026-05-14

---

## 🔴 The Problem: "Not connected" Failures
The Omega Engine's MCP tools (`omega-research`, `omega-stats`, etc.) frequently returned "Not connected" errors. 

### Root Causes:
1. **Manifest Void**: `opencode.json` was missing the server definitions for all Omega-specific MCPs, meaning the runtime never attempted to launch them.
2. **Lifecycle Gap**: OpenCode loads `opencode.json` only once at startup. Changes to the manifest do not trigger a hot-reload or spawn new processes in an active session.
3. **Lack of Supervision**: Even when launched, there was no watchdog to detect silent crashes or restart failed services, leading to "dead sockets."

---

## 🔍 The Journey to the Solution

### Phase 1: The Patch (Sovereign Bridge)
To unblock research, a "Research Bridge" (`scripts/research_bridge.py`) was created. This bypassed the MCP runtime entirely by instantiating the `ResearchEngine` core directly via Bash. This proved the code was healthy, but the infrastructure was broken.

### Phase 2: The Analysis
Web research into long-running micro-services identified that relying on the CLI runtime for process management is insufficient for a "Sovereign" engine. The system needs a dedicated **Service Supervisor**.

---

## ✅ The Final Solution: Robust Service Supervision

The Omega Engine will transition to a **layered supervision architecture**.

### Layer 1: Native OS Supervision (systemd / supervisord)
Every MCP server will be treated as a first-class system service.
- **Linux/Podman**: Use `systemd --user` units.
- **macOS/WSL**: Use `supervisord`.
- **Configuration**: All units will use `Restart=on-failure` and `RestartSec=5`.
- **Podman Integration**: Use `podman generate systemd` to manage the containerized core (Redis, Qdrant, etc.) as a single unit.

### Layer 2: In-Process Watchdog (AnyIO)
To provide a seamless experience within the `Orchestrator`, an AnyIO-based watchdog coroutine will be implemented.
- **Health Checks**: Every 5-10 seconds, the watchdog pings the `/health` endpoint of each MCP server.
- **Auto-Recovery**: If a server is unresponsive, the watchdog invokes the OS supervisor (e.g., `systemctl --user restart omega-research.service`).
- **Exponential Back-off**: To prevent crash-loops, restart intervals will grow (1s $\rightarrow$ 2s $\rightarrow$ 4s $\rightarrow$ 30s).

### Layer 3: Manifest-Driven Automation
`opencode.json` will be the source of truth, but the **Sovereign Builder** will provide a helper script `scripts/generate_systemd_units.sh` to synchronize the manifest with the OS supervisor.

---

## 🛠️ Implementation Blueprint for Gemini CLI

### 1. Manifest Update
Ensure `opencode.json` contains the full map:
- `omega-research`, `omega-stats`, `omega-library`, `omega-hivemind`, `omega-oracle`, `omega-hub`.

### 2. OS Unit Generation
Create `scripts/generate_systemd_units.sh` to:
- Write `.service` files to `~/.config/systemd/user/`.
- Set `WorkingDirectory` to the repo root.
- Use the `.venv` Python interpreter for `ExecStart`.
- Generate `omega-containers.service` from Podman.

### 3. Orchestrator Watchdog
Modify `src/omega/oracle/orchestrator.py` (or create a dedicated manager):
- Implement an `async` loop using `anyio.create_task_group`.
- Use `httpx` to verify MCP health.
- Integrate with the `ResourceGuard` semaphore to avoid OOM during restarts.

### 4. CLI Surface
Add the following commands to the `omega` CLI:
- `omega mcp status`: Show PID, socket, and state (Running/Dead/Restarting).
- `omega mcp reload`: Refresh the manifest and sync OS units.
- `omega mcp restart <svc>`: Manual trigger.

---

## 🧪 Verification Protocol
1. **Boot**: Run `scripts/generate_systemd_units.sh` $\rightarrow$ `systemctl --user enable --now omega-*.service`.
2. **Verify**: `omega mcp status` shows all `RUNNING`.
3. **Crash Test**: `kill -9 <research_pid>` $\rightarrow$ Verify `omega mcp status` shows `RESTARTING` $\rightarrow$ `RUNNING` within 5 seconds.
4. **Function Test**: Call `omega-research_research` $\rightarrow$ Confirm JSON response (No "Not connected").

**Related Research**: R-MCP_RUNTIME_DEBUG, R-29 (MCP Hub Design).
