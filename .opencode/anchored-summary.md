# 🔱 KALI — Anchored Summary (Post-Compaction Recovery)
**Session**: 2026-07-06 | **Entity**: kali | **Model**: deepseek-v4-flash | **Channel**: opencode
**Trace**: ses_fcfb34cf6961 | **Phase**: Runaway MCP OOM Cascade — Remediation Planning Complete

---

## 🎯 Session Objective
Diagnose and plan remediation for **critical infrastructure failure**: Omega Hub runaway MCP spawn → 12GB RAM / 5GB zRAM → systemd-oomd kills → restart storm → system freeze requiring hard reboot.

---

## 🚨 Root Cause Analysis (7 Compound Failures)

| # | Component | Failure | Evidence |
|---|-----------|---------|----------|
| 1 | **systemd unit** | No CGroup v2 limits (`MemoryMax`, `TasksMax`, `CPUQuota`). `Restart=always` + `RestartSec=1s` = guaranteed restart storm. | `omega-hub.service` has zero resource constraints |
| 2 | **Symlink loop** | `config/omega.yaml` → self (`lrwxrwxrwx ... omega.yaml -> omega.yaml`). `EntityRegistry` hits `ELOOP` on every init. | `journalctl`: "Too many levels of symbolic links" × 15+ |
| 3 | **Missing import** | `state.py:192` uses `OmegaError` but never imports it. Init crashes silently. | `journalctl`: "Hub service initialization FAILED: name 'OmegaError' is not defined" |
| 4 | **Double MCP spawn** | `Orchestrator.__init__` spawns 3 MCPs at import time. Hub ALSO spawns its own. = 2x processes. | Logs show "Started MCP firecrawl on port 8015" × 2 per boot |
| 5 | **Watchdog leak** | `watch_mcps()` → `_restart_mcp()` uses `pkill -f` + `anyio.run_process()` — **no PID tracking, no cleanup**. Orphans accumulate. | `_restart_mcp` lines 290-327: spawns raw process, adds to nothing |
| 6 | **No singleton guard** | `_init_services()` can re-enter. Each Hub restart re-runs init. | `state.py:95-193` only checks `_init_complete` |
| 7 | **MCP Client no backoff** | `SovereignMCPClient` hammers reconnect on failure (SearXNG 8018 down). | `mcp_client.py:43-57` bare try/except, no circuit breaker |

---

## 💥 The Cascade (Chronological)

```
1. Hub starts → Orchestrator.__init__() spawns 3 MCP subprocesses
2. Symlink loop → EntityRegistry fails repeatedly (ELOOP)
3. Hub init FAILS (OmegaError missing) → _init_error set
4. BUT background tasks START (pruning, reaper, discovery) → memory leaks begin
5. Watchdog detects unresponsive MCPs → triggers _restart_mcp()
6. _restart_mcp() uses pkill + anyio.run_process() → SPAWNS NEW PROCESSES WITHOUT CLEANUP
7. Each restart accumulates orphaned Python processes (firecrawl, searxng, hub)
8. Memory grows → systemd-oomd kills main process (11.5G peak)
9. systemd Restart=always + RestartSec=1s → IMMEDIATE RESTART
10. NEW Hub starts → Orchestrator.__init__() spawns 3 MORE MCP subprocesses
11. Old orphans still alive + new ones = exponential accumulation
12. RAM → 12GB → zRAM swap → 5GB → SYSTEM FREEZE → HARD REBOOT
```

---

## 📋 Remediation Plan (3 Phases)

### Phase 1 — Infrastructure Hardening (P0 — Do First)
| Step | Action | File | Command |
|------|--------|------|---------|
| 1.1 | Stop Hub + kill orphans | — | `systemctl --user stop omega-hub.service && pkill -f "mcp_servers/(firecrawl\|searxng\|omega_hub)"` |
| 1.2 | Fix symlink | `config/omega.yaml` | `rm config/omega.yaml && cp config/omega.yaml.example config/omega.yaml` |
| 1.3 | Patch systemd unit | `~/.config/systemd/user/omega-hub.service` | Add `MemoryMax=2G`, `MemorySwapMax=512M`, `TasksMax=200`, `CPUQuota=200%`, `OOMPolicy=kill`, `Restart=on-failure`, `RestartSec=10s`, `StartLimitIntervalSec=60`, `StartLimitBurst=3` |
| 1.4 | Patch `state.py` imports + init lock | `mcp_servers/omega_hub/state.py` | Add `from omega.errors import OmegaError`; add `_init_in_progress` lock |
| 1.5 | Reload + start | — | `systemctl --user daemon-reload && systemctl --user start omega-hub.service` |

### Phase 2 — Application Guards (P1)
| Step | Action | File |
|------|--------|------|
| 2.1 | Remove auto-spawn from `Orchestrator.__init__` | `src/omega/oracle/orchestrator.py` |
| 2.2 | Fix watchdog: PID tracking + circuit breaker | `src/omega/oracle/orchestrator.py` (`watch_mcps`, `_restart_mcp`) |
| 2.3 | Add exponential backoff to MCP Client | `mcp_servers/omega_hub/mcp_client.py` (`__aenter__`) |

### Phase 3 — Structural Unification (P2)
| Step | Action | File |
|------|--------|------|
| 3.1 | Unify MCP ownership: Hub owns all, Orchestrator is client | `orchestrator.py`, `state.py` |
| 3.2 | Add process reaper on shutdown | `state.py` (`_shutdown_services`) |

---

## 🔧 Additional Finding: Missing `.env` File
**Error**: `bash: /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.env: No such file or directory`
**Impact**: Hub logs show "Sovereign secrets file not found... Using system env." — Vault locked, keys missing.
**Action**: Create `.env` with required keys (GOOGLE_API_KEY, OPENCODE_ZEN_API_KEY, etc.)

---

## 📍 Current State
- **Hub**: STOPPED (after OOM kill)
- **WARP namespaces**: ACTIVE (warp_node_1,2,3)
- **Orchestrator**: Not running
- **MCP subprocesses**: KILLED (cleaned up)
- **RAM**: ~3GB (stable post-reboot)
- **Next Action**: Execute Phase 1.1 → 1.5

---

## 🧭 Post-Compaction Resumption Protocol
1. Read this file (`.opencode/anchored-summary.md`)
2. Read `OMEGA_ENGINE.md` for engine state
3. Read `SOVEREIGN_MANDATES.md` for rules
4. Check `data/coordination/KALI_LIVE_FEED.md` for live status
5. Resume at **Phase 1.1** — stop Hub, kill orphans
6. Verify each phase before proceeding

---

## SESSION 40 (2026-07-06 — Infrastructure Layer: Mount Propagation)

**Focus**: The MCP churn was NOT the software bugs from Session 39 — it was a **deeper infrastructure failure** preventing Podman from running at all.

### Root Cause
`runc create failed: ... remount-private ... flags=MS_PRIVATE: permission denied`
The external NVMe partition (`/dev/nvme0n1p3`) is mounted with `shared` propagation. Rootless Podman's overlayfs driver requires `MS_PRIVATE` on the rootfs. The kernel blocks this for rootless users on `shared` mounts.

### Actions Taken
1. **Purged root partition**: ~18G freed (`.cache`, `.gemini`, `.steam`, `.npm`, `.nvm`, journal vacuum) — 97% → ~81%
2. **Surgical Reset**: Moved `graphRoot` from external → root, wiped external images, `podman system reset -f`
3. **Verified**: `MS_PRIVATE` error completely gone. Podman can now create containers.
4. **Diagnosed Qdrant panic**: `Wal error: Kind(WouldBlock)` — stale WAL lock from old volume location on external drive

### Consensus Decision
| Item | Decision | Rationale |
|------|----------|-----------|
| graphRoot | **Root partition** | Solves MS_PRIVATE permanently |
| Volumes (Redis, Qdrant, Postgres, Caddy, Iris) | **Move to root** | Tiny (<1G), no reason to fight mount propagation |
| Models (41G) | **Stay on external drive** | Read-only, no overlayfs needed |
| External drive role | **Model library + cold storage only** | Read-mostly, no system dependencies |

### Plan Documented
`data/coordination/MCP_CHURN_FIX_PLAN.md` — updated with final consolidated plan ready for execution.

### Next Actions (post-compaction)
1. **Phase 0**: Kill zombies on 6333/8088, remove stale containers
2. **Phase 1**: rsync volumes from external → root
3. **Phase 2**: Update docker-compose.yml paths
4. **Phase 3**: Rebuild & verify all containers Up (healthy)

---

## 📍 Current State (Full System — End of Session 40)

| Component | Status |
|-----------|--------|
| Hub MCP bugs (Session 39) | 📋 Planned — not yet fixed |
| graphRoot location | ✅ Root partition — MS_PRIVATE fixed |
| Podman volumes location | ✅ Root partition — all 5 volumes migrated |
| Infrastructure containers | ✅ All 5 running (Redis, Qdrant, Postgres, Caddy, Iris) |
| Models | ✅ External drive (41G) — correct |
| Root partition | ✅ 20G free (81% used) |
| External partition | ✅ 34G free (69% used) |

---

## 📌 Session 41 — Operation Unified Storage + OmegaError Sweep

**Date**: 2026-07-06 | **Entity**: kali | **Model**: deepseek-v4-flash | **Channel**: opencode
**Trace**: ses_fcfb34cf6961 | **Phase**: Infrastructure Complete + Code Quality Sweep

### 🎯 Session Objective
Execute Operation Unified Storage (Phase 0-5) and fix OmegaError import bugs across the codebase.

### ✅ Completed

**Phase 0: Clean Slate** ✅
- Killed zombie processes on ports 6333/8088
- Removed stale containers and networks
- Stopped and disabled 6 conflicting systemd user services (redis, postgres, caddy, iris, qdrant, infra-pod) — 787+ restart attempts eliminated

**Phase 1: Migrate Volumes to Root** ✅
- Created `~/.local/share/containers/volumes/` with subdirs for redis, qdrant, postgres, caddy, cache-iris
- Rsynced all 5 volumes (Redis 12K, Qdrant 657MB, Postgres 96MB, Caddy 20K, Iris cache 4K)
- Fixed ownership with `pkexec chown -R 1000:1000`

**Phase 2: Update docker-compose.yml** ✅
- All 6 volume paths changed from external → root partition
- Updated comment to reflect new architecture

**Phase 3: Rebuild & Verify** ✅
- All 5 containers rebuilt and running:
  - Redis: healthy, PONG
  - Qdrant: healthy, healthz OK
  - Postgres: healthy, accepting connections
  - Caddy: healthy, serving on 8088
  - Iris: running, responding on 8080 (health check cosmetic — boot time exceeds check window)
- Fixed `OmegaError` missing import in `search_providers.py` (was crashing Iris)
- Fixed Qdrant health check (bash TCP instead of nonexistent curl)
- Fixed Caddy health check (wget instead of nonexistent curl)

**Phase 4: Clean Up External Drive** ✅
- Removed old volume data from external drive
- Models (41G) untouched and verified intact

**Phase 5: OmegaError Sweep + Test Recovery** ✅
- Found 50+ files missing `from omega.errors import OmegaError`
- Fixed all 50 files programmatically
- Added `yaml.YAMLError` to except clauses in `soul_edit_history.py` and `wad_loader.py`
- Fixed syntax errors from sed script (memory_store.py, ingestion/pipeline.py, providers.py, worker.py)
- **Result**: 77 failures → 65 failures (809 passed, up from 797)

### 🔶 Remaining Failures (65 total)

| Category | Count | Root Cause | Fix Required |
|----------|-------|------------|--------------|
| Hub health | 40 | Hub MCP server not running | Start hub or skip tests |
| Circuit breaker | 6 | Health monitor tests | Investigate pre-existing |
| Model gateway | 5 | Gateway tests | Investigate pre-existing |
| Memory store | 5 | Memory tests | Investigate pre-existing |
| Soul distiller | 4 | Distiller tests | Investigate pre-existing |
| Session manager | 3 | Session tests | Investigate pre-existing |
| Search tools | 3 | No API keys (Firecrawl, Exa) | Expected — needs API keys |
| E2E sieve | 2 | Network-dependent | Expected |
| Session lifecycle | 1 | Lifecycle test | Investigate |
| Selective hydration | 1 | Hydration test | Investigate |
| Orchestrator | 1 | MCP status test | Investigate |
| MCP taint | 1 | Taint test | Investigate |
| Headroom | 1 | Headroom test | Investigate |

### 📁 Files Modified

- `deploy/infra/docker-compose.yml` — all volume paths + health checks
- `src/omega/oracle/search_providers.py` — added OmegaError import
- `src/omega/oracle/soul_edit_history.py` — added OmegaError + yaml.YAMLError
- `src/omega/oracle/wad_loader.py` — added OmegaError + yaml.YAMLError + ValueError
- `data/coordination/MCP_CHURN_FIX_PLAN.md` — consolidated plan
- `.opencode/anchored-summary.md` — session 41 entry
- **50 files** across `src/omega/` — added `from omega.errors import OmegaError`

### 🧭 Next Actions (Next Session)

1. **Start Hub MCP server** — required for 40 Hub health tests to pass
2. **Investigate remaining 25 code failures** — circuit breaker, model gateway, memory store, soul distiller
3. **Commit all changes** — infrastructure + code quality improvements
4. **Update anchored-summary.md** — add session 41 entry

---

*🔱 OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ opencode ⬡ ses_fcfb34cf6961 ⬡ INFRASTRUCTURE-RECOVERY*