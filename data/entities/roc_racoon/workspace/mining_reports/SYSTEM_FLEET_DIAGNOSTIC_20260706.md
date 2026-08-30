# 🔱 SYSTEM FLEET DIAGNOSTIC — Full Machine Audit
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ big-pickle ⬡ opencode ⬡ TRC_DIAGNOSTIC ⬡ FLEET-STATUS

**Date**: 2026-07-06 22:30 ADT
**Requested by**: User (direct)
**Scope**: Background workers, service health, observability gaps, systemd state
**Model**: MiMo V2.5 Free (big-pickle)

---

## §1 EXECUTIVE SUMMARY

The Omega Engine infrastructure is **healthy at the container level** but **crippled at the coordination layer**. The central Hub MCP server is dead (OOM-killed), the only watchdog that restarted it is also dead, and there is zero visual dashboard for humans or agents to understand system state at a glance. Six observability data collectors write to disk but nobody reads the data.

**Critical numbers**:
- 5/5 Podman containers running (1 unhealthy healthcheck)
- 0/1 Omega Hub processes alive (OOM timeout, 1.6GB peak vs 2GB limit)
- 74 MCP tools registered but unreachable (port 8016 dead)
- 6 observability modules writing data, 0 dashboards reading it
- 13 failed systemd units (1 actual failure, 3 false failures, 6 ghosts, 3 healthcheck probes)
- 3 OpenCode sessions running concurrently (this is normal)
- 82% root disk usage (84G/109G) — trending up

---

## §2 CONTAINER STATUS (Podman — pod_infra)

| Container | Image | Status | Port | Health | Notes |
|-----------|-------|--------|------|--------|-------|
| omega-postgres | postgres:16-alpine | ✅ Up 50m | 5432/tcp | **healthy** | Clean |
| omega-qdrant | qdrant/qdrant:v1.18.0 | ✅ Up 48m | :6333 | **healthy** | Clean |
| omega-caddy | caddy:2.8-alpine | ✅ Up 48m | :8088→80 | **healthy** | Serves static "Reclaimed Vision" page |
| omega-redis | redis:7.4-alpine | ✅ Up 43m | :6379 | **healthy** | Clean |
| omega-iris | infra_iris:latest | ⚠️ Up 43m | :8080 | **unhealthy** | Health endpoint responds 200 OK but podman reports unhealthy — PATH issue in container healthcheck command |

**Iris healthcheck root cause**: Container runs `python -c 'import urllib.request; urllib.request.urlopen("http://localhost:8080/health")'` but the container's PATH may not include `/usr/local/bin/python3.13`. The health endpoint itself works: `curl :8080/health` returns `{"status":"ok","version":"1.0.0"}`.

---

## §3 MCP SERVICES (Python processes — NOT systemd-managed)

| Service | Port | Process | Status | Notes |
|---------|------|---------|--------|-------|
| **Firecrawl MCP** | :8015 | `.venv/bin/python mcp_servers/firecrawl/server.py` | ✅ RUNNING | Manual start, not systemd |
| **SearXNG MCP** | :8018 | `.venv/bin/python mcp_servers/searxng/server.py` | ✅ RUNNING | Manual start, not systemd |
| **Omega Hub MCP** | :8016 | Multiple python processes, port NOT responding | ❌ **DEAD** | OOM-killed at 1.6GB (2GB limit). systemd restart loop exhausted retries. |

**Omega Hub OOM root cause**: The Hub initializes **12 service singletons** at startup:
```
EntityRegistry + ModelGateway + Oracle + SovereignHierarchy
+ InboxManager + CurationPipeline + Library + Indexer
+ DiscoveryOrchestrator + ResearchEngine + SovereignSearchService
+ SovereignGateway + SovereignMCPClient
```
Plus **74 MCP tools** registered on FastMCP.
Plus **3 background loops** (pruning @ 60s, reaper @ 300s, batch writer).
Plus **SSE connection handling** for every connected client.

All in a single Python process with `MemoryMax=2G`. Peak usage 1.6GB + 512MB swap = no headroom for Python GC pauses or import spikes.

---

## §4 OTHER BACKGROUND PROCESSES

| Process | PID | Status | Notes |
|---------|-----|--------|-------|
| **Ollama** | 3733 | ✅ Serving | `nomic-embed-text:v1.5` (137M) + `qwen2.5:0.5b` (494M) |
| **Deluge daemon** | 444194 | ✅ Running | BT client, ~34MB RSS |
| **Unattended upgrades** | 2223 | 🔄 System | Shutdown guard |
| **WSDD** | 114573 | ✅ Running | LAN network discovery |
| **3x OpenCode** | 763273, 641812, 1015285 | ✅ Running | User sessions (you!) |
| **Pytest** | 1021842 | ✅ Running | Test suite in progress |
| **Playwright** | 1022725 | ✅ Running | Browser driver for tests |

---

## §5 SYSTEMD STATE (13 failed units)

| Category | Units | Root Cause |
|----------|-------|------------|
| **Actually broken** | `omega-hub.service` | OOM timeout. `MemoryMax=2G` too tight for 12 singletons + 74 tools + 3 background loops. |
| **False failures** | `omega-infra-pod.service`, `omega-qdrant.service`, 3x container healthcheck | Containers are RUNNING HEALTHY. systemd recorded shutdown as `exit-code=1`. Lifecycle mismatch. |
| **Ghost units** | `omega-belial.service`, `warp-ns-prep@1-3`, `warp-reg@1-3` | Unit files deleted but systemd still tracks. Need `reset-failed`. |
| **Healthcheck failures** | 3x container healthcheck probes | Iris healthcheck fails in podman despite endpoint working. |

**Warning in logs**: `omega-hub.service:23: Unknown key 'StartLimitIntervalSec'` — this key belongs in `[Unit]`, not `[Service]` for systemd user mode.

---

## §6 LISTENING PORTS MAP

| Port | Service | Status |
|------|---------|--------|
| :11434 | Ollama | ✅ Serving models |
| :6333 | Qdrant (container) | ✅ Healthy |
| :6379 | Redis (container) | ✅ Healthy |
| :8015 | Firecrawl MCP | ✅ Responding |
| :8016 | **Omega Hub MCP** | ❌ **NOT RESPONDING** |
| :8018 | SearXNG MCP | ✅ Responding |
| :8080 | Iris (container) | ✅ Health OK |
| :8081 | Unknown | 🟡 Empty response |
| :8082 | Unknown | 🟡 Empty response |
| :8083 | Unknown | 🟡 Empty response |
| :8088 | Caddy (container) | ✅ Serving static page |
| :38221 | Unknown (Python?) | 🟡 404 Page Not Found |

---

## §7 EXISTING OBSERVABILITY — INVENTORY

### Data Collectors (all writing, nobody reading)

| Module | Data Written | Format | Destination | Dashboard? |
|--------|-------------|--------|-------------|------------|
| `metrics_db.py` | Events, errors, breaker transitions, performance, baselines | SQLite WAL | `data/observability/metrics.db` | ❌ NO |
| `token_ledger.py` | Token usage per provider | SQLite | Same DB | ❌ NO |
| `bleg.py` | Body-level error guards | JSONL | `data/crashes/` | ❌ NO |
| `ufl.py` | Unified forensic ledger | JSONL | `data/traces/` | ❌ NO |
| `health_monitor.py` | Circuit breaker states, latency percentiles | In-memory | CLI only | ⚠️ CLI only |
| `latency_tracker.py` | Per-provider latency | In-memory | Nowhere persistent | ❌ NO |
| `observability/__init__.py` | Trace JSONL + fine-tuning datasets | JSONL | `data/logs/`, `data/datasets/` | ❌ NO |

### CLI Status Tools (what you can run today)

| Command | What It Shows | Works? |
|---------|--------------|--------|
| `omega backends` | Provider fabric status table | ✅ Yes |
| `omega model-status` | Model config table | ✅ Yes |
| `omega queue-status` | Pending queue items | ✅ Yes |
| `omega entity-info <name>` | Entity details | ✅ Yes |
| `omega list-entities` | Entity list | ✅ Yes |
| `omega library-status` | Library stats | ✅ Yes |
| `make infra-status` | Container status | ✅ Yes |
| `make mcp-check` | MCP port health | ⚠️ Hub down |
| `make health` | Alias for backends | ✅ Yes |
| `make wad-status` | IWAD/PWAD listing | ✅ Yes |

### What's MISSING

1. **No aggregate status command** — Must run 6+ commands to understand system state
2. **No web dashboard** — Caddy serves static "Reclaimed Vision" page, no /status endpoint
3. **No real-time monitoring** — No watch mode, no auto-refresh, no live feed
4. **No alerting** — When Hub dies, only the (dead) watchdog knew about it

---

## §8 DISK & MEMORY

| Resource | Value | Status |
|----------|-------|--------|
| Root (/) | 109G total, 84G used (82%) | 🟡 Trending up |
| omega_library | 110G total, 71G used (68%) | ✅ 34G free |
| RAM | 14G total, 8.4G used, 6.1G available | ✅ OK |
| Swap | 8G total, 679M used | ✅ OK |
| System load | 4.26 / 4.81 / 3.68 | 🟡 Elevated (3 OpenCode sessions + pytest) |

---

## §9 RECOMMENDATIONS — PRIORITIZED

### 🔴 P0 — Immediate (Tonight)

| # | Action | Effort | Impact |
|---|--------|--------|--------|
| 1 | **Increase Hub MemoryMax to 4G** — Edit `~/.config/systemd/user/omega-hub.service` line 27, then `systemctl --user daemon-reload && systemctl --user start omega-hub.service` | 2 min | Hub comes back online. 74 MCP tools reachable. |
| 2 | **Clean systemd ghosts** — `systemctl --user reset-failed omega-belial.service warp-ns-prep@{1,2,3}.service warp-reg@{1,2,3}.service` | 1 min | Cleans `--failed` output, reduces confusion. |
| 3 | **Restart MCP watchdog** — `systemctl --user start omega-mcp-watchdog.service` | 1 min | Watchdog restarts Hub automatically if it dies again. |
| 4 | **Fix Iris healthcheck** — Either fix container PATH or change healthcheck to use full path `/usr/local/bin/python3.13` | 5 min | Container reports healthy instead of unhealthy. |

### 🟡 P1 — This Week

| # | Action | Effort | Impact |
|---|--------|--------|--------|
| 5 | **Build `make fleet-status`** — Aggregate command: containers + services + ports + disk + memory + circuit breakers + last 5 traces | 30 min | Single command to understand entire system state. |
| 6 | **Add `/status` to Caddy** — HTML page at `http://localhost:8088/status` with auto-refresh showing fleet status | 2 hours | Visual dashboard for agents and humans. |
| 7 | **Fix systemd lifecycle** — Add `ExecStopPost=` and `Type=notify` to infra-pod and qdrant services so shutdowns don't register as failures | 1 hour | Eliminates false failures from `--failed` output. |

### 🟢 P2 — Next Sprint

| # | Action | Effort | Impact |
|---|--------|--------|--------|
| 8 | **Lazy-load Hub services** — Don't init ResearchEngine until someone calls research tools | 2 hours | Cuts Hub startup memory 30-40%. |
| 9 | **Metrics dashboard** — Read from metrics.db, show inference traces, error rates, latency percentiles | 4 hours | Historical visibility into system performance. |
| 10 | **Disk cleanup** — 82% root partition, identify large files, archive old data | 1 hour | Prevents disk-full emergencies. |

---

## §10 META-INSIGHT

> Every layer of the system was built correctly in isolation. The gaps are **between** the layers.

- 6 observability data sources → 0 dashboards
- 12 Hub services → 1 process → OOM at 2GB
- 1 watchdog → it died → nothing else watches
- 13 systemd units → 6 ghosts, 3 false failures, 1 actual failure

**The fix isn't more code. It's wiring what exists.**

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ big-pickle ⬡ opencode ⬡ TRC_DIAGNOSTIC ⬡ FLEET-STATUS*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: big-pickle | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
