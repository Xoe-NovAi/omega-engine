# WARP Proxy Pool — Handoff Briefing for Roc
**Date**: 2026-07-22  
**From**: Kali / Cline session  
**To**: Roc (Roc Raccoon)  
**Subject**: Full handoff of W-1 (WARP Proxy Pool) fixes, current status, and remaining work  
**AP Token**: `AP-WARP-PROXY-POOL-v1.2.0`  

---

## §0 Executive Summary

The WARP proxy pool (`warp-proxy-pool` repo) was **broken out of the box** due to systemic bugs in the systemd unit files. We debugged, fixed, committed, and deployed all fixes. The pool is now **operational** on ports 8081, 8082, and 8083 with WARP=ON.

**What was delivered:**
1. Fixed all source unit files (`warp-node@.service`, `warp-reg@.service`, `warp-reg-svc@.service`)
2. Committed fixes to `warp-proxy-pool` git repo (7 commits)
3. Synced corrected units to host `/etc/systemd/system/`
4. Verified all 3 nodes live with `curl --socks5` tests
5. Created this briefing

**What still needs work:**
1. The `warp-node@.service` ExecStartPost `curl` health check can time out and leave services stuck in `activating`
2. Stale WARP registrations require manual deletion
3. Exit IP distribution is currently 2 unique IPs (8081 is unique, 8082/8083 share)
4. Need to validate the `fix_warp_ns_setup_and_restart.sh` script works end-to-end from a clean state

---
## §1 What Was Broken (Root Cause Analysis)

### 1.1 Bug #1: Unsupported `--config-dir` flag
**Files**: `warp-reg@.service`, `warp-node@.service`  
**Symptom**: `warp-cli` returned `error: unexpected argument '--config-dir' found`  
**Root cause**: The local `warp-cli` (2026.6.880.0) does not support the `--config-dir` flag  
**Fix**: Removed all `--config-dir /var/lib/cloudflare-warp-%i` flags

### 1.2 Bug #2: Bash arithmetic expansion in `ip netns exec`
**File**: `warp-node@.service`  
**Symptom**: `warp-cli proxy port 1))` error  
**Root cause**: `ip netns exec` does NOT invoke a shell; `$((8080 + %i))` was passed literally  
**Fix**: Wrapped in `/usr/bin/bash -c '...'` so bash expands arithmetic

### 1.3 Bug #3: `$${port}` double-expansion in curl test
**File**: `warp-node@.service`  
**Symptom**: Services stuck in `activating` forever  
**Root cause**: `$${port}` inside `bash -c '...'` expanded to `$PID{port}` instead of `$port`  
**Fix**: Changed to `${port}`

### 1.4 Bug #4: Read-only filesystem panic in `warp-svc`
**File**: `warp-reg-svc@.service`  
**Symptom**: `warp-svc` panicked with `Read-only file system`  
**Root cause**: `LOGS_DIRECTORY=/var/log/cloudflare-warp` + `ProtectSystem=strict`  
**Fix**: Changed `LOGS_DIRECTORY=/tmp`

### 1.5 Bug #5: Missing `daemon-reload` after syncing units
**File**: `scripts/fix_warp_ns_setup_and_restart.sh`  
**Symptom**: systemd warned "unit changed on disk, run daemon-reload"  
**Fix**: Added `sudo systemctl daemon-reload` after copying units

### 1.6 Bug #6: Stale WARP registrations
**Symptom**: `warp-reg@.service` failed with "Old registration is still around"  
**Root cause**: When `warp-node` fails after registration, stale state persists in `warp.db`  
**Fix**: Manual recovery with `warp-cli --accept-tos registration delete` (see §7.1)

### 1.7 Bug #7: Missing `warp-reg-svc@` in dependency chain
**Symptom**: `warp-reg@1.service` failed because `warp-reg-svc@1.service` wasn't running  
**Fix**: Script now starts `warp-reg-svc@1..3` before `warp-reg@1..3`

---
## §2 Git Commits Applied

```
ec88eaf fix(warp-node): wrap proxy port command in bash for arithmetic expansion
4cc68c2 fix(warp-node): remove --config-dir flag (not supported by local warp-cli)
e7565e2 fix(warp-reg): remove --config-dir flag (not supported by all warp-cli versions)
dd34d20 fix(warp): remove SystemCallFilter from warp-node@.service
7a29e23 fix(warp): bridge unit port templating + SystemCallFilter for socat
d7e135d fix(warp-node): correct bash variable expansion in curl test line
bd09104 fix(warp-node): make curl SOCKS test non-blocking
```

## §3 Current Live State

As of last verification:

| Port | Status | Exit IP | WARP |
|------|--------|---------|------|
| 8081 | WORKING | 104.28.204.4 | ON |
| 8082 | WORKING | 104.28.236.4 | ON |
| 8083 | WORKING | 104.28.236.4 | ON |

Note: 8082 and 8083 share an exit IP. Normal for WARP location-based assignment.

### Service status
- `warp-ns-prep@1..3`: active
- `warp-reg-svc@1..3`: active  
- `warp-reg@1..3`: active
- `warp-node@1..3`: may be stuck in `activating` due to curl test timeout (non-blocking fix applied)
- `warp-bridge@1..3`: check per-node

---
## §4 What Roc Needs To Do Next

### 4.1 Immediate: Verify & stabilize
1. Run the fix script to ensure clean state:
   ```bash
   cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
   bash scripts/fix_warp_ns_setup_and_restart.sh
   ```

2. Verify all 3 exit IPs:
   ```bash
   for port in 8081 8082 8083; do
     echo -n "Port $port: "
     curl --socks5 127.0.0.1:$port -s https://1.1.1.1/cdn-cgi/trace | grep ip=
   done
   ```

3. Check service states:
   ```bash
   for svc in warp-ns-prep@1 warp-ns-prep@2 warp-ns-prep@3 \
             warp-reg-svc@1 warp-reg-svc@2 warp-reg-svc@3 \
             warp-reg@1 warp-reg@2 warp-reg@3 \
             warp-node@1 warp-node@2 warp-node@3 \
             warp-bridge@1 warp-bridge@2 warp-bridge@3; do
     echo "$svc: $(systemctl is-active $svc 2>/dev/null || echo unknown)"
   done
   ```

### 4.2 Short-term: Fix the `warp-node` curl test blocker
The non-blocking fix has been committed but may still cause services to stay in `activating`. Options:

**Option A**: Remove the curl test entirely and let `validate_warp_pool.py` handle health checks

**Option B**: Make the curl test non-fatal with `timeout 15` and `|| true`

### 4.3 Short-term: Fix stale registration handling
Add a pre-cleanup step in `warp-reg@.service` ExecStartPre:
```ini
ExecStartPre=/usr/bin/bash -c 'set -e; NS="warp_node_%i"; ip netns exec "$NS" /usr/bin/warp-cli --accept-tos registration delete 2>/dev/null || true'
```

### 4.4 Medium-term: Validate script improvements
The `validate_warp_pool.py` script should:
1. Check port listening status on host
2. Check SOCKS5 connectivity through each port
3. Extract and compare exit IPs
4. Report node count, healthy count, degraded count
5. Auto-recycle nodes with stale registrations

### 4.5 Documentation updates needed
1. `docs/research/warp_proxy_pool/WARP_PROXY_POOL_SPEC.md` — update §3.2/§3.3 with actual working unit contents
2. `docs/research/warp_proxy_pool/INTEGRATION_GUIDE.md` — add troubleshooting section for the 5 bugs
3. `docs/research/warp_proxy_pool/VALIDATION_STRATEGY.md` — document exit IP verification method
4. `scripts/fix_warp_ns_setup_and_restart.sh` — update docstring comments

---
## §5 Runbook for Restarting the Pool

### Full restart (clean from zero)
```bash
# 1. Stop everything
sudo systemctl stop warp-bridge@1 warp-bridge@2 warp-bridge@3
sudo systemctl stop warp-node@1 warp-node@2 warp-node@3
sudo systemctl stop warp-reg@1 warp-reg@2 warp-reg@3
sudo systemctl stop warp-reg-svc@1 warp-reg-svc@2 warp-reg-svc@3
sudo systemctl stop warp-ns-prep@1 warp-ns-prep@2 warp-ns-prep@3

# 2. Clean up old state
for i in 1 2 3; do
  pkexec ip netns exec warp_node_$i /usr/bin/warp-cli --accept-tos registration delete 2>/dev/null || true
done
pkexec rm -rf /var/lib/cloudflare-warp-{1,2,3}/*

# 3. Run the fix script
bash scripts/fix_warp_ns_setup_and_restart.sh

# 4. Verify
for port in 8081 8082 8083; do
  echo -n "Port $port: "
  curl --socks5 127.0.0.1:$port -s https://1.1.1.1/cdn-cgi/trace | grep ip=
done
```

### Recycling individual nodes (for new exit IPs)
```bash
pkexec ip netns exec warp_node_1 /usr/bin/warp-cli --accept-tos registration delete
sudo systemctl restart warp-reg@1 warp-node@1 warp-bridge@1
curl --socks5 127.0.0.1:8081 -s https://1.1.1.1/cdn-cgi/trace | grep ip=
```

---
## §6 Key Technical Insights for Roc

### 6.1 `ip netns exec` does NOT invoke a shell
This is the #1 confusion source. systemd `ExecStart` lines run the binary directly. If you need shell features (arithmetic expansion, pipes, &&), you MUST use `/bin/bash -c '...'`.

### 6.2 `$$` in systemd unit single-quoted strings
Inside `ExecStartPost=/usr/bin/bash -c '...'`, `$$` does NOT mean literal `$`. It means bash PID expansion. Use `${var}` syntax carefully.

### 6.3 `warp-cli` version differences
The local `warp-cli` (2026.6.880.0) does NOT accept `--config-dir`. Always test `warp-cli --help` on target host.

### 6.4 Stale registration behavior
When `warp-svc` dies uncleanly, `warp.db` retains the registration. Delete is required, AND `--accept-tos` flag must be present.

### 6.5 `ProtectSystem=strict` + `LOGS_DIRECTORY`
systemd makes `/var/log` read-only under `ProtectSystem=strict`. If a Rust/Go service tries to create log files there, it will crash.

## §7 Links & References

| Resource | Path |
|----------|------|
| Source repo | `../warp-proxy-pool/` |
| Systemd units (host) | `/etc/systemd/system/warp-*` |
| Fix script | `scripts/fix_warp_ns_setup_and_restart.sh` |
| Spec doc | `docs/research/warp_proxy_pool/WARP_PROXY_POOL_SPEC.md` |
| Integration guide | `docs/research/warp_proxy_pool/INTEGRATION_GUIDE.md` |
| Validation script | `docs/research/warp_proxy_pool/validate_warp_pool.sh` |
| This briefing | `docs/strategy/archive/2026-07-22/WARP_PROXY_POOL_HANDOFF_ROC_20260722.md` |

## §8 Open Questions for Roc

1. Should the `warp-node@.service` curl test be removed entirely, or made robust with `timeout 15`?
2. Should stale registration cleanup happen in `warp-reg@.service` ExecStartPre, or a separate maintenance unit?
3. Do we need 8 nodes for 8 OCZ accounts, or is 3 sufficient with rotation?
4. Should the Python pool manager handle exit-IP diversity automatically?
5. Does `warp-reg-svc@.service` still need `ReadWritePaths=/var/log/cloudflare-warp` if `LOGS_DIRECTORY=/tmp`?

---

*Briefing prepared by Kali + Cline — 2026-07-22 21:55 ADT*  
*🔱 OMEGA ⬡ WARP-POOL ⬡ HANDOFF ⬡ ROC ⬡ SOVEREIGN*
