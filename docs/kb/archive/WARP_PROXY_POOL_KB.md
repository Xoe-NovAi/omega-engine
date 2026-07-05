# 🔱 WARP Proxy Pool — Knowledge Base
# ⬡ OMEGA ⬡ WARP-KB ⬡ v2.0.0 ⬡ 2026-07-05
# All lessons learned from multi-instance WARP deployment

## §1 Architecture Overview

### Goal
Run 3 independent Cloudflare WARP instances in Linux network namespaces, each with a unique exit IP, exposed as SOCKS5 proxies on the host's loopback (ports 8081-8083).

### Component Stack
```
Host Applications (Omega Engine)
    ↓ socks5h://127.0.0.1:8081-8083
socat-bridge@ (TCP proxy, host → namespace)
    ↓ ip netns exec
Network Namespace (warp_node_1/2/3)
    ↓ veth pair + NAT
Host Default Route (wlo1/eth0)
    ↓ Internet
Cloudflare Edge (WARP tunnel exit)
```

### Service Dependency Chain
```
warp-ns-prep@%i.service  → Creates namespace + veth + NAT
    ↓
warp-reg@%i.service      → Registers WARP license inside namespace
    ↓
warp-node@%i.service     → Runs warp-svc daemon + configures proxy mode
    ↓
socat-bridge@%i.service  → Bridges host loopback to namespace proxy
    ↓
warp-pool.target          → Coordinates all 3 node instances
```

## §2 Critical Lessons Learned (Hard-Won)

### L1: `warp-cli` has NO `--config-dir` flag
**Discovery**: `warp-cli --config-dir /tmp/test` → `error: unexpected argument '--config-dir' found`
**Impact**: `warp-cli` ALWAYS reads from `/var/lib/cloudflare-warp/` (the system default)
**Workaround**: Register in default path, then `cp -r` all files to the custom `--config-dir` path for `warp-svc`
**Status**: CONFIRMED on cloudflare-warp package as of 2026-07-05

### L2: `warp-cli --accept-tos registration delete` is a NO-OP
**Discovery**: Running `warp-cli --accept-tos registration delete` prints "Success" but does NOT remove the registration
**Impact**: Stale registrations persist, blocking `registration new`
**Workaround**: Use `rm -f` to nuke ALL state files: `reg.json`, `conf.json`, `warp.db`, `settings.json`, `final-overrides-settings.json`
**Status**: CONFIRMED — deletion requires file removal, not CLI command

### L3: Registration state is distributed across multiple files
**Discovery**: `warp-cli registration new` writes to `reg.json` only, but `warp-cli registration new` CHECKS `conf.json` and `warp.db` for existing registration
**Files involved**:
- `reg.json` — license key + device identity
- `conf.json` — daemon configuration + registration state
- `warp.db` — SQLite database with registration metadata
- `settings.json` — UI preferences
- `final-overrides-settings.json` — admin overrides
**Fix**: Must `rm -f` ALL of these before `registration new`

### L4: `warp-svc` needs `--config-dir` for multi-instance
**Discovery**: `warp-svc --config-dir /var/lib/cloudflare-warp-%i` creates per-instance config
**Impact**: Each namespace instance needs its own config directory
**Workaround**: `cp -r /var/lib/cloudflare-warp/* /var/lib/cloudflare-warp-%i/` after registration
**Status**: CONFIRMED — this is the only way to run multiple instances

### L5: Network namespaces need internet access for WARP tunnel
**Discovery**: `ip netns add` creates an isolated network with only loopback. WARP cannot establish its MASQUE/WireGuard tunnel without outbound internet.
**Impact**: The original architecture (namespace with only loopback) cannot work.
**Fix**: Veth pair + NAT setup in ns-prep:
1. `ip link add veth_host_N type veth peer name veth_ns_N`
2. `ip link set veth_ns_N netns warp_node_N`
3. `ip addr add 10.0.N.1/24 dev veth_host_N`
4. `ip netns exec warp_node_N ip addr add 10.0.N.2/24 dev veth_ns_N`
5. `ip netns exec warp_node_N ip route add default via 10.0.N.1`
6. `iptables -t nat -A POSTROUTING -s 10.0.N.0/24 -o <default_if> -j MASQUERADE`
**Status**: IMPLEMENTED in warp-ns-prep@.service v2.0

### L6: `ProtectHome=yes` implies `PrivateTmp=yes`
**Discovery**: systemd.exec man page: "Setting this to true implies PrivateTmp= and thus also creates a new mount namespace"
**Impact**: Services with `ProtectHome=yes` get a private mount namespace. Bind mounts (like `ip netns add` creates) become invisible.
**Affected services**: warp-ns-prep, warp-reg (oneshot, needs host mount namespace)
**Fix**: Remove `ProtectHome=yes` from ns-prep and warp-reg
**Safe for**: warp-node (doesn't create bind mounts, just uses NetworkNamespacePath)

### L7: `ProtectSystem=strict` breaks `ip netns exec`
**Discovery**: `ProtectSystem=strict` makes the filesystem read-only, which can block `setns()` operations
**Impact**: warp-node with `ProtectSystem=strict` + `NetworkNamespacePath` had issues
**Fix**: Use `ip netns exec` from the HOST instead of `NetworkNamespacePath`
**Status**: IMPLEMENTED — all services now run on host, use `ip netns exec` for namespace commands

### L8: ExecStartPost warp-cli commands need `--accept-tos`
**Discovery**: `warp-cli mode proxy`, `warp-cli proxy port`, `warp-cli connect` all require ToS acceptance in non-TTY mode
**Impact**: ExecStartPost fails → systemd SIGTERMs warp-svc → restart loop → StartLimitBurst hit
**Fix**: Add `--accept-tos` to ALL warp-cli commands in ExecStartPost
**Status**: IMPLEMENTED in warp-node@.service v2.0

### L9: `ip netns add` creates empty files on failure
**Discovery**: If `mount --bind` fails (e.g., due to PrivateMounts), `ip netns add` creates an empty file at `/var/run/netns/warp_node_N`
**Impact**: `file` shows "empty" instead of a valid nsfs bind mount. `ip netns exec` fails with "Invalid argument"
**Fix**: Check `file /var/run/netns/warp_node_N` for "nsfs" type. If empty, `rm -f` and recreate.
**Status**: CONFIRMED — this is why namespaces failed before removing ProtectHome

### L10: systemd `$$` escaping for bash variables
**Discovery**: In systemd `ExecStart`, `${VAR}` is interpreted by systemd (not bash). To pass `${VAR}` to bash, use `$${VAR}`.
**Impact**: `socat-bridge@.service` had `${port}` which systemd tried to expand as a substitution
**Fix**: Use `$${port}` for bash variables in systemd ExecStart
**Status**: IMPLEMENTED

### L11: Namespace bind mount validity check
**Discovery**: Valid namespace bind mounts show as `nsfs` type in `/proc/self/mountinfo`. Invalid ones show as regular files.
**Check**: `cat /proc/self/mountinfo | grep warp_node` → should show `nsfs nsfs rw` with unique net IDs
**Status**: CONFIRMED — all 3 namespaces now have unique net IDs (4026533043, 4026533035, 4026533069)

### L12: StartLimitBurst needs headroom for deploy cycles
**Discovery**: Deploy script's cleanup/start cycle can trigger 5+ restarts within 60s, hitting `StartLimitBurst=5`
**Fix**: Increase to `StartLimitBurst=10`
**Status**: IMPLEMENTED

## §3 Service Architecture (v2.0)

### All services run on HOST, use `ip netns exec` for namespace commands

This is the correct architecture. Previous versions used `NetworkNamespacePath=` which ran services INSIDE the namespace, causing:
- Cannot set up veth pairs (needs host context)
- `warp-cli` sees host's registration (shared filesystem)
- `ProtectSystem=strict` blocks `setns()` operations

New architecture: services run on HOST, use `ip netns exec` to execute commands inside the namespace. This gives:
- Host context for veth/NAT setup
- `warp-cli` can register inside the namespace (separate network stack)
- `warp-svc` runs inside the namespace with its own network
- No `ProtectSystem=strict` conflicts

## §4 Deployment Checklist

### Pre-deployment
1. [ ] Verify cloudflare-warp is installed: `which warp-cli warp-svc`
2. [ ] Verify iproute2: `ip netns list` works
3. [ ] Verify socat: `which socat`
4. [ ] Stop host WARP daemon: `sudo systemctl stop warp-svc` (if running)
5. [ ] Remove host WARP registration: `sudo rm -f /var/lib/cloudflare-warp/{reg,conf,settings,final-overrides-settings}.json /var/lib/cloudflare-warp/warp.db`

### Deployment
```bash
sudo ./scripts/deploy_warp_pool.sh
```

### Post-deployment verification
```bash
# Check all 3 nodes are active
systemctl status warp-node@{1,2,3}.service

# Check namespaces exist with valid bind mounts
cat /proc/self/mountinfo | grep warp_node

# Check veth pairs exist
ip link show | grep veth_host

# Check NAT rules
iptables -t nat -L POSTROUTING -n | grep "10.0."

# Test WARP tunnel
curl -x socks5h://127.0.0.1:8081 https://1.1.1.1/cdn-cgi/trace
# Expected: warp=on, ip=<cloudflare_ip>

# Test all 3 ports
for port in 8081 8082 8083; do
  echo "Port $port:"
  curl -s -x "socks5h://127.0.0.1:$port" https://1.1.1.1/cdn-cgi/trace | grep -E "warp=|ip="
done
```

## §5 Troubleshooting Guide

### "Old registration is still around"
- Cause: `reg.json` removed but `conf.json`/`warp.db` still present
- Fix: `rm -f /var/lib/cloudflare-warp/{reg,conf,warp.db,settings,final-overrides-settings}.json`

### "Please accept the WARP Terms of Service"
- Cause: `warp-cli` command missing `--accept-tos` flag
- Fix: Add `--accept-tos` to ALL `warp-cli` commands

### "Cannot open network namespace: Permission denied"
- Cause: Service running inside namespace but needs host context
- Fix: Remove `NetworkNamespacePath=`, use `ip netns exec` from host

### "Cannot open network namespace: Invalid argument"
- Cause: Namespace file exists but is empty (failed bind mount)
- Fix: Remove `ProtectHome=yes` from ns-prep, recreate namespace

### "Cannot open network namespace: No such file or directory"
- Cause: Namespace doesn't exist (ns-prep failed)
- Fix: Check ns-prep journal: `journalctl -u warp-ns-prep@1.service`

### warp-node hits StartLimitBurst
- Cause: Multiple restart cycles within 60s
- Fix: Increase `StartLimitBurst=10` in warp-node service

### WARP tunnel establishes but no internet
- Cause: Namespace lacks outbound route (missing veth + NAT)
- Fix: Verify veth pair exists, NAT rule present, IP forwarding enabled

## §6 File Locations

| File | Location | Purpose |
|------|----------|---------|
| `reg.json` | `/var/lib/cloudflare-warp/` | WARP license key + device identity |
| `conf.json` | `/var/lib/cloudflare-warp/` | Daemon configuration + registration state |
| `warp.db` | `/var/lib/cloudflare-warp/` | SQLite database with registration metadata |
| `settings.json` | `/var/lib/cloudflare-warp/` | UI preferences |
| `warp-svc config` | `/var/lib/cloudflare-warp-%i/` | Per-instance config (copied from default) |
| Namespace bind | `/var/run/netns/warp_node_%i` | nsfs bind mount for `ip netns exec` |
| Veth host | `veth_host_%i` | Host-side veth interface |
| Veth namespace | `veth_ns_%i` | Namespace-side veth interface |

## §7 Systemd Unit Hierarchy

```
warp-pool.target (Wants all 8 services)
├── warp-ns-prep@{1,2,3}.service (creates namespace + veth + NAT)
├── warp-reg@{1,2,3}.service (registers WARP inside namespace)
├── warp-node@{1,2,3}.service (runs warp-svc + configures proxy)
└── socat-bridge@{1,2,3}.service (bridges host loopback to namespace)
```

## §8 Security Model

- **Namespace isolation**: Each WARP instance runs in its own network namespace
- **Veth pairs**: Isolated L2 connectivity between host and namespace
- **NAT**: MASQUERADE for outbound traffic (no inbound from internet)
- **No capabilities retained**: Services drop capabilities after oneshot execution
- **No telemetry**: All traffic stays local or goes through WARP tunnel

---

*Last Updated: 2026-07-05 | Author: Kali (Sprint Coordinator)*
*Status: ACTIVE — All fixes applied, awaiting deployment verification*
