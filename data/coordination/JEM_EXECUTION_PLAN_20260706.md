# 🔱 JEM EXECUTION PLAN — Fleet Diagnostic Response
# ⬡ OMEGA ⬡ JEM ⬡ mimo-v2.5-free ⬡ opencode ⬡ TRC_EXECUTION ⬡ FLEET-RECOVERY

**Date**: 2026-07-06 23:15 ADT
**Requested by**: roc_racoon (diagnostic synthesis)
**Operator**: 1 human, 1 agent session
**Target**: P0 items complete tonight. P1 deferred to dedicated session.

---

## §1 THE CRITICAL PATH

The dependency graph is linear for P0. There is no parallelism — each step feeds the next.

```
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Fix Hub MemoryMax (2G → 4G)                           │
│  WHY: Hub is dead. 74 MCP tools unreachable. Everything downstream│
│        depends on this.                                          │
│  BLOCKS: Everything.                                             │
│  TIME: 2 min edit + 30s reload + 30s wait                       │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: Start Hub (systemctl --user start omega-hub.service)   │
│  WHY: After fixing memory, start it.                             │
│  BLOCKS: Step 3 (watchdog needs Hub running to know what to     │
│          restart).                                               │
│  TIME: 15-30s startup (12 singletons + 74 tools)                │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: Start MCP Watchdog                                     │
│  WHY: If Hub dies again, watchdog restarts it. Without this,    │
│        next OOM = dead Hub with no recovery.                     │
│  BLOCKS: Step 4 (ghost cleanup is cosmetic, not blocking)       │
│  TIME: 5s                                                       │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: Clean systemd ghosts                                   │
│  WHY: Cosmetic. Cleans `--failed` output. Reduces confusion.    │
│  BLOCKS: Nothing. Pure cleanup.                                  │
│  TIME: 10s                                                      │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 5: Verify Iris health                                     │
│  WHY: Iris reports unhealthy but endpoint returns 200 OK.        │
│        Likely a podman healthcheck config issue, not a real      │
│        problem. Document and move on.                            │
│  BLOCKS: Nothing. Cosmetic.                                      │
│  TIME: 2 min investigation + 5 min fix if needed                │
└─────────────────────────────────────────────────────────────────┘
```

---

## §2 STEP-BY-STEP EXECUTION

### STEP 1: Fix Hub MemoryMax (2G → 4G)

**What**: Edit `~/.config/systemd/user/omega-hub.service` line 13.
**Why**: The Hub loads 12 singletons + 74 MCP tools + 3 background loops into one Python process. 2GB is insufficient. Peak was 1.6GB + 512MB swap = no headroom for GC pauses or import spikes.

**Edit**:
```
MemoryMax=2G      →  MemoryMax=4G
MemorySwapMax=512M  →  MemorySwapMax=1G
MemoryHigh=1.5G    →  MemoryHigh=3G
```

**Also fix** (line 23):
```
StartLimitIntervalSec=60    → 移到 [Unit] section (this key is invalid in [Service] for systemd user mode)
```

**Corrected service file**:
```ini
[Unit]
Description=Omega Core Hub MCP Server
Documentation=https://github.com/Xoe-NovAi/omega-engine
After=network.target
StartLimitIntervalSec=60
StartLimitBurst=3

[Service]
CPUAffinity=0 2 4 6 8 10 12
Type=simple
WorkingDirectory=/home/arcana-novai/Documents/Xoe-NovAi/omega-engine
ExecStart=/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.venv/bin/python mcp_servers/omega_hub/server.py

MemoryMax=4G
MemorySwapMax=1G
MemoryHigh=3G
TasksMax=200
CPUQuota=200%
OOMPolicy=kill

Restart=on-failure
RestartSec=10s

Environment=PYTHONPATH=/home/arcana-novai/Documents/Xoe-NovAi/omega-engine:src
Environment=OMEGA_MCP_TRANSPORT=sse
Environment=OMEGA_MCP_PORT=8016
Environment=OMEGA_MCP_HOST=127.0.0.1
Environment=OPENBLAS_CORETYPE=ZEN

[Install]
WantedBy=default.target
```

**Risk**: Low. Memory limits are being relaxed, not tightened. If the Hub truly needs >4GB, it will OOM again — but that would indicate a memory leak, not a sizing issue.

**Verification**:
```bash
systemctl --user daemon-reload
systemctl --user start omega-hub.service
sleep 10
ss -tlnp | grep 8016  # Should show listening
curl -s http://127.0.0.1:8016/health  # Should return JSON
```

---

### STEP 2: Start Hub and Verify

**What**: Start the Hub, wait for it to initialize all 12 singletons.
**Why**: Confirms the memory fix worked.

**Verification checklist**:
- [ ] Port 8016 is listening
- [ ] `curl -s http://127.0.0.1:8016/health` returns `{"status":"ok"}`
- [ ] `make mcp-check` shows Hub green
- [ ] Memory usage under 3GB (check with `systemctl --user show omega-hub.service --property=MemoryCurrent`)

**Risk**: Medium. If Hub fails to start, check `journalctl --user -u omega-hub.service -n 50` for the actual error. Possible causes:
- Import error (missing module)
- Port conflict (something else on 8016)
- Singleton initialization failure (Qdrant down, etc.)

**Fallback**: If 4G still isn't enough, check `journalctl --user -u omega-hub.service --since "5 min ago"` for memory spike patterns. May need to defer to P2 (lazy-load services).

---

### STEP 3: Start MCP Watchdog

**What**: `systemctl --user start omega-mcp-watchdog.service`
**Why**: The watchdog is the only auto-recovery mechanism. Without it, next OOM = dead Hub with manual restart required.

**Risk**: Low. The watchdog script exists at `scripts/mcp_watchdog.py`. It monitors port 8016 and restarts the Hub if it goes down.

**Verification**:
```bash
systemctl --user is-active omega-mcp-watchdog.service  # Should be "active"
```

---

### STEP 4: Clean systemd Ghosts

**What**: Reset all failed units that are not actually broken.

**Command** (copy-paste):
```bash
systemctl --user reset-failed \
  omega-belial.service \
  omega-belial.timer \
  warp-ns-prep@1.service warp-ns-prep@2.service warp-ns-prep@3.service \
  warp-reg@1.service warp-reg@2.service warp-reg@3.service \
  omega-infra-pod.service \
  omega-qdrant.service \
  2>/dev/null

# Also reset the two anonymous container healthcheck failures
# (these have long hash-based names — find them with):
systemctl --user list-units --state=failed --no-legend | grep -E '^[a-f0-9]{64}' | awk '{print $1}' | xargs -r systemctl --user reset-failed
```

**Why these are safe to reset**:
| Unit | Reason it's "failed" | Safe to reset? |
|------|---------------------|----------------|
| `omega-belial.service` | Unit file deleted, systemd still tracks | ✅ YES |
| `omega-belial.timer` | Same as above | ✅ YES |
| `warp-ns-prep@{1,2,3}` | Unit files deleted | ✅ YES |
| `warp-reg@{1,2,3}` | Unit files deleted | ✅ YES |
| `omega-infra-pod.service` | Containers are RUNNING, systemd saw exit-code=1 on stop | ✅ YES |
| `omega-qdrant.service` | Same lifecycle mismatch | ✅ YES |
| 2x healthcheck hashes | Podman healthcheck probe failures | ✅ YES |

**Risk**: Zero. These are all false failures. Resetting them just clears the state.

---

### STEP 5: Investigate Iris Health

**What**: The Iris container's health endpoint works (`curl :8080/health` → 200 OK) but podman reports unhealthy. No healthcheck is defined in the container config (confirmed via `podman inspect`).

**Likely cause**: The healthcheck was defined at `podman run` time via `--health-cmd` but isn't in the Quadlet/container config. Or the healthcheck state is stale from a previous run.

**Investigation**:
```bash
# Check actual health state
podman inspect infra_iris --format '{{.State.Health}}'

# If stale, recreate the container
podman rm -f infra_iris
podman run -d --name infra_iris \
  --health-cmd 'python3 -c "import urllib.request; urllib.request.urlopen(\"http://localhost:8080/health\")"' \
  --health-interval 30s \
  --health-timeout 5s \
  --health-retries 3 \
  -p 8080:8080 \
  infra_iris:latest
```

**Risk**: Low-Medium. Recreating the container requires confirming the run command matches the original. If unsure, document the issue and defer — the endpoint works, this is cosmetic.

**Decision gate**: If the fix takes >5 minutes, document and defer to P1. The Iris endpoint is functional.

---

## §3 RISK REGISTER

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| Hub still OOMs at 4G | LOW | HIGH | Check `journalctl` for memory spike. May need lazy-loading (P2). |
| Hub fails to start (import error) | LOW | HIGH | `journalctl --user -u omega-hub.service -n 50` for root cause. |
| Watchdog script has bugs | LOW | MED | Check `journalctl --user -u omega-mcp-watchdog.service -n 20`. |
| Iris recreation breaks something | LOW | MED | Don't recreate unless confident. Document and defer. |
| Root disk fills during session | LOW | HIGH | 82% = 25GB free. Safe for tonight. Address in P2. |
| `StartLimitIntervalSec` fix breaks restart | LOW | MED | Move to `[Unit]` is correct per systemd docs. Test with `systemctl --user restart omega-hub.service`. |

---

## §4 RESOURCE ALLOCATION

**Operator**: 1 human, available tonight.
**Time budget**: ~30 minutes for all P0 items.

| Step | Time | Operator | Can Fail? |
|------|------|----------|-----------|
| Fix Hub service file | 2 min | Agent (edit) | No |
| daemon-reload + start | 1 min | Agent (bash) | No |
| Verify Hub alive | 2 min | Agent (bash) | No |
| Start watchdog | 5s | Agent (bash) | No |
| Clean ghosts | 10s | Agent (bash) | No |
| Iris investigation | 5 min | Agent (bash) | Yes (defer) |
| **TOTAL** | **~12 min** | | |

The 30-minute budget includes buffer for debugging if something unexpected happens.

---

## §5 VERIFICATION PROTOCOL

After all P0 steps complete, run this verification suite:

```bash
# 1. Hub alive
ss -tlnp | grep 8016 && echo "✅ Hub port listening" || echo "❌ Hub port NOT listening"

# 2. Hub health
curl -s http://127.0.0.1:8016/health | python3 -c "import sys,json; d=json.load(sys.stdin); print('✅ Hub health OK' if d.get('status')=='ok' else '❌ Hub unhealthy')" 2>/dev/null || echo "❌ Hub health endpoint unreachable"

# 3. Watchdog alive
systemctl --user is-active omega-mcp-watchdog.service && echo "✅ Watchdog active" || echo "❌ Watchdog not running"

# 4. Ghost units cleaned
FAILED=$(systemctl --user list-units --state=failed --no-legend 2>/dev/null | wc -l)
echo "Failed units remaining: $FAILED (target: 0)"

# 5. Memory usage
systemctl --user show omega-hub.service --property=MemoryCurrent 2>/dev/null

# 6. Iris (cosmetic)
curl -s http://localhost:8080/health && echo "✅ Iris endpoint OK" || echo "❌ Iris unreachable"

# 7. Full fleet status
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

**Success criteria**:
- Hub responding on 8016
- Watchdog active
- 0 failed systemd units
- All 5 containers running

---

## §6 P1 ITEMS (DEFERRED — Dedicated Session)

These are important but not blocking tonight. Document for next session:

| # | Item | Effort | Value |
|---|------|--------|-------|
| 5 | `make fleet-status` aggregate command | 30 min | Single-command system view |
| 6 | Caddy `/status` HTML dashboard | 2 hr | Visual monitoring |
| 7 | Fix systemd lifecycle (ExecStopPost) | 1 hr | Eliminates false failures |
| 8 | Lazy-load Hub services | 2 hr | 30-40% memory reduction |
| 9 | Metrics dashboard | 4 hr | Historical visibility |
| 10 | Disk cleanup | 1 hr | Prevents disk-full emergencies |

---

## §7 META-PRINCIPLE

> **The fix isn't more code. It's wiring what exists.**

Every P0 item is a configuration change, not a code change. The system was built correctly in isolation. The gaps are between the layers:
- Hub was built → memory limit was wrong
- Watchdog was built → it wasn't running
- Ghost units were cleaned up → systemd still tracked them
- Iris works → podman says it doesn't

Tonight's work is plumbing, not architecture.

---

*⬡ OMEGA ⬡ JEM ⬡ mimo-v2.5-free ⬡ opencode ⬡ TRC_EXECUTION ⬡ FLEET-RECOVERY*
