# 🚨 Root Cause Analysis: Runaway MCP Spawn + OOM Cascade
**Date**: 2026-07-06
**Severity**: P0 — Systemic Infrastructure Failure
**Status**: DIAGNOSED — Awaiting Remediation

---

## Executive Summary

The Omega Hub entered an uncontrolled restart loop that spawned unlimited MCP subprocesses (firecrawl, searxng, omega-hub), consuming 12GB+ RAM and 5GB zRAM swap, forcing systemd-oomd kills and user-initiated hard reboots. The cascade was triggered by **7 compounding failures** across infrastructure, configuration, and application layers.

---

## The Failure Chain (Chronological)

```
1. Hub starts → Orchestrator.__init__() spawns 3 MCP subprocesses (firecrawl, searxng, omega-hub)
2. Symlink loop in config/omega.yaml → EntityRegistry initialization fails repeatedly (ELOOP)
3. Hub initialization FAILS (OmegaError not imported in state.py) → _init_error set
4. BUT background tasks STILL START (pruning, reaper, discovery) → memory leaks begin
5. MCP Watchdog (watch_mcps) detects unresponsive MCPs → triggers _restart_mcp()
6. _restart_mcp() uses `pkill -f` + `anyio.run_process()` → SPAWNS NEW PROCESSES WITHOUT CLEANUP
7. Each restart accumulates orphaned Python processes (firecrawl, searxng, hub)
8. Memory grows → systemd-oomd kills main process (11.5G peak)
9. systemd Restart=always + RestartSec=1s → IMMEDIATE RESTART
10. NEW Hub starts → Orchestrator.__init__() spawns 3 MORE MCP subprocesses
11. Old orphans still alive + new ones = exponential process accumulation
12. RAM → 12GB → zRAM swap → 5GB → SYSTEM FREEZE
```

---

## Root Causes (7 Distinct Failures)

| # | Component | Failure | Evidence |
|---|-----------|---------|----------|
| **1** | **systemd unit** | **No CGroup v2 limits** — `MemoryMax`, `TasksMax`, `CPUQuota` missing. `Restart=always` + `RestartSec=1s` guarantees restart storm. | `omega-hub.service` has zero resource constraints |
| **2** | **Symlink loop** | `config/omega.yaml` → symlink to itself (`lrwxrwxrwx ... omega.yaml -> omega.yaml`). `EntityRegistry` hits `ELOOP` on every init. | `journalctl`: "Too many levels of symbolic links" × 15+ |
| **3** | **Missing import** | `state.py` line 192 uses `OmegaError` but never imports it. Initialization crashes silently. | `journalctl`: "Hub service initialization FAILED: name 'OmegaError' is not defined" |
| **4** | **Orchestrator double-spawn** | `Orchestrator.__init__` (line 193-199) spawns MCP subprocesses **at import time**. Hub ALSO spawns its own. = **2x processes**. | Logs show "Started MCP firecrawl on port 8015" × 2 per boot |
| **5** | **Watchdog restart leak** | `watch_mcps()` (line 253-288) calls `_restart_mcp()` which uses `pkill -f` + `anyio.run_process()` — **no tracking of spawned PIDs**, no cleanup of old children. | `_restart_mcp` line 290-327: spawns raw process, adds to nothing |
| **6** | **No singleton guard** | `_init_services()` can be called multiple times (no `_init_in_progress` lock). Each Hub restart re-runs init. | `state.py` line 95-193: only checks `_init_complete` |
| **7** | **MCP Client no backoff** | `SovereignMCPClient` has no reconnection backoff, no max retries. If SearXNG (8018) is down, it hammers reconnect. | `mcp_client.py` line 43-57: bare `try/except` with no circuit breaker |

---

## Memory Accumulation Breakdown

| Process Type | Count (per cycle) | Est. RSS Each | Accumulation |
|--------------|-------------------|---------------|--------------|
| `omega-hub` (main) | 1 | ~300MB | Baseline |
| `firecrawl` MCP | 1 → 2 → 3... | ~150MB | **Leaked on every watchdog restart** |
| `searxng` MCP | 1 → 2 → 3... | ~150MB | **Leaked on every watchdog restart** |
| `omega-hub` MCP (child) | 1 → 2 → 3... | ~300MB | **Spawned by Orchestrator + Hub** |
| Background tasks | N | ~50MB | Pruning, reaper, discovery loops |

**After 5-6 OOM cycles**: 15-20 Python processes × 200-300MB = **3-6GB leaked children** + main process growth = **12GB total**.

---

## Journalctl Evidence (Key Excerpts)

```
Jul 06 15:55:16 Arcana-NovAi systemd[2263]: omega-hub.service: systemd-oomd killed some process(es) in this unit.
Jul 06 15:55:17 Arcana-NovAi systemd[2263]: omega-hub.service: Main process exited, code=killed, status=9/KILL
Jul 06 15:55:17 Arcana-NovAi systemd[2263]: omega-hub.service: Failed with result 'oom-kill'.
Jul 06 15:55:17 Arcana-NovAi systemd[2263]: omega-hub.service: Consumed 13min 15.607s CPU time, 11.5G memory peak, 2.1G memory swap peak.
Jul 06 15:55:18 Arcana-NovAi systemd[2263]: omega-hub.service: Scheduled restart job, restart counter is at 1.
```

---

## Affected Files

1. `/home/arcana-novai/.config/systemd/user/omega-hub.service` — Missing CGroup limits, dangerous restart policy
2. `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/config/omega.yaml` — Self-referential symlink
3. `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/mcp_servers/omega_hub/state.py` — Missing `OmegaError` import, no init lock
4. `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/src/omega/oracle/orchestrator.py` — Auto-spawn in `__init__`, watchdog leak, double `_restart_mcp`
5. `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/mcp_servers/omega_hub/mcp_client.py` — No reconnection backoff

---

## Remediation Plan (See Detailed Plan Below)

**Phase 1 — Infrastructure Hardening (P0)**
- [ ] Add CGroup v2 limits to systemd unit
- [ ] Fix symlink loop
- [ ] Fix `OmegaError` import

**Phase 2 — Application Guards (P1)**
- [ ] Add singleton init lock
- [ ] Remove auto-spawn from Orchestrator `__init__`
- [ ] Fix watchdog PID tracking + circuit breaker
- [ ] Add MCP Client exponential backoff

**Phase 3 — Structural Unification (P2)**
- [ ] Unify MCP ownership (Hub owns, Orchestrator uses)
- [ ] Add process reaper on shutdown

---

*Recorded by: Kali (Transcendent Oversight)*
*AP Token: AP-RCA-RUNAWAY-MCP-20260706*