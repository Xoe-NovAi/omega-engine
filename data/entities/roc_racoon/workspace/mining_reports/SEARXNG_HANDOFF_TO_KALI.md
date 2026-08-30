# 🔱 SearXNG Health Check — Handoff to Kali
# ⬡ OMEGA ⬡ VERITY ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_kali_handoff
**Date**: 2026-06-21 20:00 UTC
**Priority**: CRITICAL
**Handoff From**: Verity (Compliance & Gnosis)
**Handoff To**: Kali (Grand Oversight)
**Preceding Reports**: SEARXNG_DEEP_RESEARCH (Researcher), SEARXNG_ODYSSEUS_MINING (Roc), SEARXNG_JEM_VERIFICATION (Jem), SEARXNG_VALIDATION (Jem)

---

## §0 EXECUTIVE SUMMARY — THE MYSTERY IS SOLVED

The SearXNG crash loop has **3 independent layers**. The health check itself is
**NOW CORRECT** in the deployed Quadlet. The real unresolved problem is a
**corrupted pasta network namespace** that broke DNS in the manually-started
replacement container.

### The 3 Layers

| Layer | Component | Status | Verdict |
|-------|-----------|--------|---------|
| **1** | Health check command | ✅ FIXED in deployed Quadlet | Python urllib on `/` WORKS |
| **2** | Stale pasta after restart | ⚠️ NEEDS ExecStopPost | Port 8017 held by orphaned pasta |
| **3** | Corrupted network namespace | 🔴 **CURRENT BLOCKER** | DNS completely unreachable |

**Bottom line**: Delete the broken container, kill stale pasta processes, and
start fresh. The Quadlet file is already correct.

---

## §1 LAYER 1 — Health Check Command (ALREADY FIXED)

### The Original Bug
The initial Quadlet (from before this investigation) used:
```ini
HealthCmd=curl -sf http://localhost:8080/healthz || exit 1
```
**Two problems**: (a) `curl` is NOT in the Alpine-based SearXNG image, and
(b) `/healthz` does exist (Jem confirmed it returns "OK"), but curl isn't
there to call it. This caused the ORIGINAL crash loop.

### The Deployed Quadlet (as of 2026-06-21)
```ini
HealthCmd=python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/', timeout=5).read(1)"
HealthInterval=30s
HealthTimeout=5s
HealthRetries=5
HealthStartPeriod=15s
HealthOnFailure=restart
```

### ⚠️ CRITICAL DISCOVERY: This HealthCmd WORKS

I tested the EXACT command in the deployed Quadlet through **five independent
methods** — all passed:

| Test Method | Command | Result | Verified |
|-------------|---------|--------|----------|
| `podman exec` direct | `python -c "..."` | ✅ EXIT 0 | Proven |
| `podman exec` via `sh -c` | `sh -c 'python -c "..."'` | ✅ EXIT 0 | Proven |
| `podman exec` full path | `/usr/sbin/python -c '...'` | ✅ EXIT 0 | Proven |
| `podman healthcheck` on test container | Exact stored CMD-SHELL | ✅ **HEALTHY** | Proven |
| Empty PATH (`PATH=""`) | `/usr/sbin/python -c '...'` | ✅ EXIT 0 | Proven |

### Why the Sh -C Wrapping Works

Podman stores the HealthCmd as CMD-SHELL format:
```json
{"Test":["CMD-SHELL","python -c \"import urllib.request; urllib.request.urlopen('http://localhost:8080/', timeout=5).read(1)\""]}
```

Podman executes this by wrapping it in the container's shell:
```
/bin/sh -c 'python -c "import urllib.request; urllib.request.urlopen('"'"'http://localhost:8080/'"'"', timeout=5).read(1)"'
```

The quoting works correctly because:
1. The outer `sh -c` strips the double quotes around the Python code
2. The inner single quotes (`'http://...'`) are preserved as valid Python string delimiters
3. `python` is found at `/bin/python` (via symlink: `/bin` → `/usr/bin`), which is in even minimal PATH

**The PATH issue is a red herring.** On Alpine, `/bin` is a symlink to
`/usr/bin`. Both `/bin/python` and `/usr/sbin/python` exist. Even with
`PATH="/bin"`, Python is found. This was verified experimentally.

### Verdict: Health Check Is NOT the Problem

The Quadlet's health check command is **correct and functional**. The original
crash loop was caused by a now-replaced Quadlet (`curl` + `/healthz`). The
current deployed Quadlet (Python + `/`) works.

**Do NOT change the HealthCmd.** It is fine.

### Minor Improvement (Optional)

The following changes are **strictly optional** — nice-to-haves, not fixes:

| Setting | Current | Recommended | Reason |
|---------|---------|-------------|--------|
| `HealthStartPeriod` | 15s | 30s | More startup grace, Granian needs 5-15s |
| `HealthTimeout` | 5s | 10s | Safety margin for loaded system |
| `HealthCmd` | `localhost` | `127.0.0.1` | Avoids IPv6 resolution edge case |
| `HealthCmd` | `python` | `/usr/sbin/python` | Full path, zero PATH dependency |

**Recommended HealthCmd (copy-paste improvement, not a fix):**
```ini
HealthCmd=/usr/sbin/python -c 'import urllib.request; urllib.request.urlopen("http://127.0.0.1:8080/", timeout=5).read(1)'
HealthInterval=30s
HealthTimeout=10s
HealthRetries=5
HealthStartPeriod=30s
HealthOnFailure=restart
```

This uses:
- Full path `/usr/sbin/python` (zero PATH dependency)
- `127.0.0.1` (forces IPv4, no DNS resolution needed)
- Single-quoted Python code with double-quoted URL
- 10s timeout (safety margin)
- 30s start period (generous for Granian init)

---

## §2 LAYER 2 — Stale Pasta (CONSEQUENCE, NEEDS PREVENTION)

### What Happens

When the container dies (from Layer 1's health check failure), the pasta
network namespace process survives, still holding port 8017:

```
pasta.avx2 — holding port 8017
```

On the next restart attempt:
```
Failed to bind port 8017 (Address already in use)
```

After 4 failed bind attempts, systemd gives up. Service dead.

### Fix: ExecStopPost Cleanup

Add to the `[Service]` section of the Quadlet:

```ini
[Service]
Restart=on-failure
RestartSec=10s
TimeoutStartSec=90s
# 🔴 CRITICAL: Kill stale pasta after container stop
# Prevents "Address already in use" on restart
ExecStopPost=/bin/sh -c 'pkill -f "pasta.*omega-searxng" 2>/dev/null; exit 0'
```

The `exit 0` is important — systemd considers a non-zero ExecStopPost exit as
a unit failure. We want the cleanup to always succeed (even if no stale pasta
exists).

**Alternative** (more aggressive):
```ini
ExecStopPost=/bin/sh -c 'for pid in $(pgrep -f "pasta.*8017"); do kill $pid 2>/dev/null; done; exit 0'
```

### When This Is a Problem

This only triggers when the container dies unexpectedly (health check failure,
OOM kill, etc.). During normal `podman stop` or `systemctl stop`, Podman
cleans up the network namespace. The ExecStopPost is a **safety net** for
crash scenarios.

---

## §3 LAYER 3 — Corrupted Network Namespace (🔴 CURRENT BLOCKER)

### The Real Problem Right Now

The running `omega-searxng-test` container has a **completely broken network
namespace**. DNS resolution fails for ALL upstream servers:

| DNS Server | Address Type | Status |
|------------|-------------|--------|
| `169.254.1.1` | pasta DNS proxy | 🔴 Network is unreachable |
| `192.168.1.1` | Router DNS | 🔴 Network is unreachable |
| `10.89.0.1` | aardvark-dns (bridge) | 🔴 Network is unreachable |
| `8.8.8.8` | External DNS | 🔴 Network is unreachable |

**Verified by** raw DNS query via Python socket (not nslookup):
```
DNS via 169.254.1.1: FAILED — [Errno 101] Network is unreachable
```

### Why This Happened

The `omega-searxng-test` container was started manually with `podman run`
after the Quadlet-managed container died. It inherited a **corrupted pasta
network namespace** — the namespace file at
`/run/user/1000/netns/netns-f798fb44-9e66-1103-fd49-9d2711dbdcc1` is a
zero-byte stale file from the original pasta process that was killed during
the crash loop.

**Fresh containers work fine** (verified experimentally):
```
podman run alpine:3.20 wget -q -O- http://httpbin.org/ip
→ {"origin": "74.244.153.214"} ✅
```

Both `pasta` and `slirp4netns` networking work for newly created containers.
The issue is specifically the **existing** container's corrupted namespace.

### Why SearXNG Appears "Healthy" But Can't Search

The health check (`python urllib to http://127.0.0.1:8080/`) only tests the
local Granian WSGI server. It succeeds because localhost loopback works
within the container regardless of network namespace state.

SearXNG queries upstream search engines (Google, DuckDuckGo, etc.) via
outbound HTTPS, which requires DNS resolution. DNS fails → all engines
return "HTTP connection error" → SearXNG returns empty results.

**This is the classic "partial failure" pattern** — the service is "up" but
non-functional. The health check is a liveness probe, not a true health
probe.

### Fix: Delete and Recreate

**This is a one-line fix:**
```bash
# Kill the broken container
podman rm -f omega-searxng-test

# Kill any stale pasta processes
pkill -f "pasta.*searxng" 2>/dev/null; pkill -f "pasta.*8017" 2>/dev/null

# Start via Quadlet (will create fresh network namespace)
systemctl --user start omega-searxng.service
```

**Do NOT simply `podman start` the old container** — it has a corrupted
namespace file. Always delete and recreate. The Quadlet handles recreation
automatically.

### If Quadlet Fails

If the Quadlet fails to start (unlikely since the health check is correct),
start manually with explicit network:

```bash
podman run -d \
  --name omega-searxng \
  --network=slirp4netns \
  -p 127.0.0.1:8017:8080 \
  -v ~/Documents/Xoe-NovAi/omega-engine/data/searxng/config:/etc/searxng/ \
  -v ~/Documents/Xoe-NovAi/omega-engine/data/searxng/data:/var/cache/searxng/ \
  -e SEARXNG_SECRET=[REDACTED-GITLEAKS-GENERIC-API-KEY] \
  -e SEARXNG_BASE_URL=http://localhost:8017 \
  docker.io/searxng/searxng:2026.5.31-7159b8aed
```

Both `pasta` and `slirp4netns` work. The issue is the **stale namespace
file**, not the network driver.

---

## §4 DEPLOYED QUADLET ANALYSIS (as of 2026-06-21)

### Full Quadlet File

File: `~/.config/containers/systemd/omega-searxng.container`

```ini
[Unit]
Description=Omega SearXNG — Sovereign Metasearch Engine
After=network-online.target
Wants=network-online.target

[Container]
Image=docker.io/searxng/searxng:2026.5.31-7159b8aed
ContainerName=omega-searxng
AutoUpdate=registry

PublishPort=127.0.0.1:8017:8080

Volume=%h/Documents/Xoe-NovAi/omega-engine/data/searxng/config:/etc/searxng/
Volume=%h/Documents/Xoe-NovAi/omega-engine/data/searxng/data:/var/cache/searxng/

Environment=SEARXNG_SECRET=[REDACTED-GITLEAKS-GENERIC-API-KEY]
Environment=SEARXNG_BASE_URL=http://localhost:8017
Environment=SEARXNG_PORT=8080
Environment=SEARXNG_HOST=0.0.0.0
Environment=FORCE_OWNERSHIP=true

PodmanArgs=--memory=512m
PodmanArgs=--memory-reservation=256m
PodmanArgs=--cpus=1.0
PodmanArgs=--pids-limit=64
PodmanArgs=--security-opt=no-new-privileges
DropCapability=ALL
AddCapability=CHOWN,SETGID,SETUID,DAC_OVERRIDE
PodmanArgs=--tmpfs=/tmp:rw,size=64m
PodmanArgs=--tmpfs=/var/tmp:rw,size=32m

HealthCmd=python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/', timeout=5).read(1)"
HealthInterval=30s
HealthTimeout=5s
HealthRetries=5
HealthStartPeriod=15s
HealthOnFailure=restart

[Service]
Restart=on-failure
RestartSec=10s
TimeoutStartSec=90s

[Install]
WantedBy=multi-user.target
```

### ✅ Already Correct
| Item | Status | Notes |
|------|--------|-------|
| Image pinned to `2026.5.31-7159b8aed` | ✅ | Odysseus-verified working version |
| HealthCmd uses Python urllib | ✅ | Verified working (Section 1) |
| HealthCmd hits `/` not `/healthz` | ✅ | Root endpoint is correct |
| `AddCapability=CHOWN,SETGID,SETUID,DAC_OVERRIDE` | ✅ | Covers all first-boot needs |
| `DropCapability=ALL` | ✅ | Security best practice |
| `SEARXNG_SECRET` set | ✅ | Non-empty secret |
| `FORCE_OWNERSHIP=true` | ✅ | Handles UID mismatch |
| Memory limits (512M/256M) | ✅ | Appropriate for SearXNG |

### 🔴 Missing (Must Add)
| Item | Fix | Priority |
|------|-----|----------|
| `ExecStopPost` for stale pasta | `ExecStopPost=/bin/sh -c '...'` | **HIGH** — prevents crash-loop deadlock |
| Network namespace cleanup on restart | (covered by ExecStopPost) | **HIGH** |

### 🟡 Optional Improvements
| Item | Change | Priority |
|------|--------|----------|
| `HealthStartPeriod` | 15s → 30s | LOW — 15s works but tight |
| `HealthTimeout` | 5s → 10s | LOW — 5s works but tight |
| `HealthCmd` full path | `python` → `/usr/sbin/python` | LOW — works either way |
| `HealthCmd` IPv4 | `localhost` → `127.0.0.1` | LOW — avoids edge case |

---

## §5 PREVIOUS REPORTS — CORRECTIONS NEEDED

### What the Odysseys Report Got Wrong

The Odysseys report (`SEARXNG_ODYSSEUS_MINING_20260621.md`) claimed the
health check hits `/healthz` which "does NOT exist." This is **INCORRECT**:

> SearXNG (Granian WSGI) does NOT expose a `/healthz` endpoint by default.
> The root `/` endpoint is the correct health check target.

**Reality**: `/healthz` IS a valid SearXNG endpoint (Flask-level, confirmed in
`webapp.py:616-618`). Jem verified it returns "OK" with HTTP 200:
```bash
podman exec omega-searxng-test python3 -c "
import urllib.request
r = urllib.request.urlopen('http://127.0.0.1:8080/healthz')
print(r.read())"  # → b'OK'
```

The Odysseys report was based on an **older version** of the Quadlet. The
current deployed Quadlet already uses `/`, not `/healthz`. The report's
analysis was correct for a stale snapshot but is now outdated.

### What the Jem Verification Got Right (and Wrong)

**Right**: DNS broken, `pasta` networking issue, `semantischolar` engine name wrong

**Wrong about root cause**: The Jem report says "DNS is the critical issue."
This is true but **misleading** — DNS is only broken because the specific
container's network namespace is corrupted. A fresh container has working DNS.

The Jem report says the Quadlet's HealthCmd already "partially fixed" by Kali.
This is accurate — the deployed Quadlet was updated from the curl version.

**Correct conclusion**: Jem's insight that "a health check that only tests
internal state is a liveness probe, not a health check" is the universal
principle. SearXNG needs a deep health check (full search pipeline) to
detect DNS failures.

### Corrections Summary

| Previous Claim | Actual Truth | Source |
|----------------|-------------|--------|
| `/healthz` doesn't exist | ✅ It does, returns "OK" | Jem verification |
| Health check still uses `curl` | ✅ Already Python urllib | Deployed Quadlet |
| Health check hits `/healthz` | ✅ Already hits `/` | Deployed Quadlet |
| DNS is a system-level problem | ❌ Only this container's namespace is corrupted | Fresh container test |
| Image tag unpinned (`:latest`) | ✅ Already pinned to `2026.5.31` | Deployed Quadlet |
| Missing capabilities | ✅ Already `AddCapability=CHOWN,SETGID,SETUID,DAC_OVERRIDE` | Deployed Quadlet |

---

## §6 COMPLETE FIX — ONE COMMAND SEQUENCE

This is the definitive fix. Copy-paste in order:

### Step 1: Stop and remove broken containers
```bash
# Kill the test container (corrupted network namespace)
podman rm -f omega-searxng-test 2>/dev/null || true

# Kill any existing Quadlet-managed container
podman rm -f omega-searxng 2>/dev/null || true
```

### Step 2: Kill stale pasta processes
```bash
# Kill all pasta processes that might hold stale namespaces
pkill -f "pasta.*8017" 2>/dev/null || true
pkill -f "pasta.*searxng" 2>/dev/null || true
pkill -f "netns.*f798fb44" 2>/dev/null || true

# Verify port 8017 is free
ss -tlnp | grep 8017 || echo "✅ Port 8017 is free"
```

### Step 3: Clean up stale network namespace file
```bash
rm -f /run/user/1000/netns/netns-f798fb44-9e66-1103-fd49-9d2711dbdcc1

# Remove any other stale netns files
ls -la /run/user/1000/netns/ 2>/dev/null
```

### Step 4: Add ExecStopPost to Quadlet
```bash
# Add to [Service] section of ~/.config/containers/systemd/omega-searxng.container
# ExecStopPost=/bin/sh -c 'pkill -f "pasta.*omega-searxng" 2>/dev/null; exit 0'
```

### Step 5: Reload and start
```bash
systemctl --user daemon-reload
systemctl --user start omega-searxng.service
```

### Step 6: Verify
```bash
# Check service status
systemctl --user status omega-searxng

# Check health status (wait 30s for first check)
watch -n 10 'podman ps --filter name=omega-searxng --format "{{.Names}} {{.Status}}"'

# Check health after 60s
podman inspect omega-searxng --format '{{.State.Health.Status}}'

# Verify DNS works inside container
podman exec omega-searxng python3 -c "
import socket
socket.setdefaulttimeout(5)
print('DNS:', socket.gethostbyname('google.com'))
"

# Verify search works
curl -s "http://127.0.0.1:8017/search?q=test&format=json" | python3 -m json.tool | head -10
```

### Step 7: Clean up stale research copies
The research copy at `docs/research/omega-searxng.container` is stale and
uses `curl` + `/healthz`. Either archive it or update it to match the
deployed Quadlet. Future investigators will be confused by the mismatch.

---

## §7 CONTAINER HEALTH CHECK ARCHITECTURE — LESSONS LEARNED

### The 3-Layer Health Check Model

For sovereign AI infrastructure, a container health check should test:

```python
def sovereign_health_check():
    """3-layer health check for sovereign containers"""
    
    # LAYER 1: Liveness — is the process running?
    assert http_get("http://127.0.0.1:8080/") == 200  # Current check
    
    # LAYER 2: Connectivity — can it reach its dependencies?
    assert dns_resolve("google.com") is not None  # MISSING
    
    # LAYER 3: Functionality — does the service actually work?
    assert search("healthcheck") contains results  # MISSING
```

| Layer | What It Tests | SearXNG Status |
|-------|--------------|----------------|
| **1. Liveness** | "Is the process running?" | ✅ Current check passes |
| **2. Connectivity** | "Can it reach the network?" | ❌ **Not checked** |
| **3. Functionality** | "Does it actually work?" | ❌ **Not checked** |

### Recommended Health Check for SearXNG v2

For true sovereign health monitoring, add a THIRD check that tests the full
search pipeline. This should run separately from Podman's liveness check
(to avoid false restarts from transient upstream engine failures):

```bash
# Podman HealthCmd (Layer 1): Is the server running?
HealthCmd=/usr/sbin/python -c 'import urllib.request; urllib.request.urlopen("http://127.0.0.1:8080/", timeout=5).read(1)'
HealthInterval=30s
HealthTimeout=10s
HealthRetries=5
HealthStartPeriod=30s
HealthOnFailure=restart

# Systemd timer (Layer 2+3): Is search actually working?
# Add a second timer that tests the full search pipeline
# and alerts (but doesn't restart) on failure
```

---

## §8 FILES REFERENCED

| File | Purpose | Status |
|------|---------|--------|
| `~/.config/containers/systemd/omega-searxng.container` | Deployed Quadlet | ✅ Active, mostly correct |
| `data/searxng/config/settings.yml` | SearXNG config | ⚠️ Empty `secret_key`, GET method |
| `data/searxng/data/` | SearXNG cache | ⚠️ May not exist (creates at first boot) |
| `mcp_servers/searxng/server.py` | MCP search tool | ⚠️ Uses GET, missing params |
| `src/omega/workers/background_researcher/searxng_client.py` | Background search | ⚠️ Wrong engine name, engines param ignored |
| `docs/research/omega-searxng.container` | Stale research copy | ❌ Uses curl + /healthz — OUTDATED |

---

## §9 L1→L2→L3 DISTILLATION

### L1 (Narrative)
Investigated the SearXNG health check mystery across 5 independent analysis
threads (Roc mining, Jem verification, Researcher deep dive, Validation, and
Verity forensics). The "health check crash loop" had already been partially
fixed in the deployed Quadlet (Python urllib instead of curl). The real
current problem is a corrupted pasta network namespace that broke DNS in the
manually-started replacement container. Fresh containers work fine. The fix
is to delete the broken container, kill stale pasta processes, and restart.

### L2 (Insight)
Three independent failures cascaded: (1) Original health check was wrong
(curl not in image) → crash loop. (2) Crash loop left stale pasta holding
port 8017 → restarts failed. (3) Manual replacement inherited a corrupted
network namespace → DNS broken → SearXNG appears healthy but can't search.
Each layer masked the next. Without the forensic chain analysis, any single
fix would appear to fail.

### L3 (Universal Principle)
**Cascading failures conceal root causes.** When a system fails, then gets
"fixed" (by updating the Quadlet to use Python), but still appears broken
(in a manual test container with corrupted DNS), investigators chase the
wrong problem. The rule: **always destroy and recreate the entire stack**
after a crash loop. Partial recovery inherits partial corruption. A corrupted
process tree (orphaned pasta, stale netns files, zero-byte sandbox keys) can
survive container deletion and poison the next incarnation. `podman rm -f`
is not enough — you must also clean the network artifacts.

---

## §10 WHAT KALI NEEDS TO DO

### Immediate (5 minutes)
1. Read §3 — understand the corrupted network namespace
2. Run the fix sequence from §6 Steps 1-3 (delete container, kill pasta)
3. Add `ExecStopPost` from §2 to the Quadlet

### Short-term (30 minutes)
4. Start the Quadlet (§6 Step 5)
5. Verify DNS works (§6 Step 6)
6. Archive/update the stale research copy at `docs/research/`

### Medium-term (next session)
7. Address the secondary issues from Jem's report:
   - MCP server: GET → POST, add `categories`/`engines`/`time_range` params
   - `searxng_client.py`: Fix `semantischolar` → `semantic scholar`
   - `settings.yml`: Add `json` to `search.formats`, set `secret_key`, POST method
8. Add Layer 2+3 health check (outbound DNS probe) for true sovereignty

### Do NOT Do
- ❌ Change the HealthCmd — it works (proven in §1)
- ❌ Switch to slirp4netns — pasta works fine with fresh containers
- ❌ Re-open the health check mystery — it's solved

---

*⬡ OMEGA ⬡ VERITY ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_kali_handoff ⬡ HANDOFF-COMPLETE*
*Handoff prepared: 2026-06-21 20:00 UTC | 5 forensic layers analyzed | Root cause definitively identified*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
