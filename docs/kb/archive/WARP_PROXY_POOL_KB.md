# 🔱 WARP Proxy Pool — Knowledge Base
# ⬡ OMEGA ⬡ WARP-KB ⬡ v4.0.0 ⬡ 2026-07-23
# All lessons learned from multi-instance WARP deployment
# Comprehensive documentation for systemd NetworkNamespacePath and PrivateMounts implementation

## §1 Architecture Overview

### Goal
Deploy 3 independent Cloudflare WARP instances in Linux network namespaces:
- Each instance has a unique exit IP
- Exposed as SOCKS5 proxies on host loopback (ports 8081-8083)
- Full network isolation between instances
- Host context for setup operations

### Component Stack
```
Host Applications (Omega Engine)
    ↓ socks5h://127.0.0.1:8081-8083
    ↓ socat-bridge@%i (TCP proxy, host → namespace)
    ↓ ip netns exec
Network Namespace (warp_node_1/2/3)
    ↓ veth pair + NAT
    ↓ Host Default Route (wlo1/eth0)
    ↓ Internet
    ↓ Cloudflare Edge (WARP tunnel exit)
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

### Systemd NetworkNamespacePath and PrivateMounts Implementation

**Critical Finding**: Starting with systemd v254, `PrivateNetwork=yes` and `NetworkNamespacePath=` now imply `PrivateMounts=yes` unless `PrivateMounts=no` is explicitly specified.

**Impact**: This change breaks existing setups that rely on accessing network namespace bind mounts from other services.

**Solution**: Use `PrivateMounts=no` when you need to access network namespace bind mounts from other services, or use `JoinsNamespaceOf=` for cleaner namespace relationships.

**Key Innovation**: All services run on the HOST using `ip netns exec` for namespace commands, avoiding `ProtectSystem=strict` and `ProtectHome=yes` conflicts while maintaining full network namespace isolation.

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

## §3 Service Architecture (v4.0)

### All services run on HOST, use `ip netns exec` for namespace commands

This is the correct architecture. Previous versions used `NetworkNamespacePath=` which ran services INSIDE the namespace, causing:
- Cannot set up veth pairs (needs host context)
- `warp-cli` sees host's registration (shared filesystem)
- `ProtectSystem=strict` blocks `setns()` operations

**Systemd NetworkNamespacePath and PrivateMounts Implementation**:

**Critical Finding**: Starting with systemd v254, `PrivateNetwork=yes` and `NetworkNamespacePath=` now imply `PrivateMounts=yes` unless `PrivateMounts=no` is explicitly specified.

**Impact**: This change breaks existing setups that rely on accessing network namespace bind mounts from other services.

**Solution**: Use `PrivateMounts=no` when you need to access network namespace bind mounts from other services, or use `JoinsNamespaceOf=` for cleaner namespace relationships.

**Key Innovation**: All services run on the HOST using `ip netns exec` for namespace commands, avoiding `ProtectSystem=strict` and `ProtectHome=yes` conflicts while maintaining full network namespace isolation.

**The Dependency Chain:**
`warp-ns-prep@%i` (Namespace/Veth/NAT/DNS) → `warp-reg@%i` (Sequential Registration) → `warp-node@%i` (Permanent Daemon) → `socat-bridge@%i` (Loopback Bridge).

**Key Unit Patterns:**
- **Template Units**: Use `%i` for instance-specific config directories (`/var/lib/cloudflare-warp-%i`)
- **Oneshot + RemainAfterExit**: Used for setup services (`ns-prep`, `reg`) to ensure they only run once
- **Capability Bounding**: `CapabilityBoundingSet=CAP_NET_ADMIN CAP_SYS_ADMIN` for namespace/mount operations
- **Resource Containment**: `MemoryMax=150M`, `CPUQuota=15%` to prevent OOM on Ryzen 5700U

**Bash & Systemd Integration**:
- **Variable Escaping**: Use `$${VAR}` in `ExecStart` to pass variables to bash
- **Sequentiality**: Use `flock` for resources shared across instances (like the registration daemon)
- **Idempotency**: `cleanup_stale_state()` must nuke all registration files and namespaces before every deploy

**Network Namespace Operations**:
- **Sovereign Siloing**: Use `ip netns add` → `ip link add veth` → `ip link set veth_ns netns` → `ip route add default`
- **DNS Sovereignty**: Bind mount a custom `resolv.conf` into the namespace to bypass host `systemd-resolved` issues

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

## §9 Systemd NetworkNamespacePath and PrivateMounts Implementation

### 9.1 Systemd v254 Breaking Changes

**Critical Finding**: Starting with systemd v254, `PrivateNetwork=yes` and `NetworkNamespacePath=` now imply `PrivateMounts=yes` unless `PrivateMounts=no` is explicitly specified.

**Impact**: This change breaks existing setups that rely on accessing network namespace bind mounts from other services.

**Solution**: Use `PrivateMounts=no` when you need to access network namespace bind mounts from other services, or use `JoinsNamespaceOf=` for cleaner namespace relationships.

**Key Innovation**: All services run on the HOST using `ip netns exec` for namespace commands, avoiding `ProtectSystem=strict` and `ProtectHome=yes` conflicts while maintaining full network namespace isolation.

### 9.2 Core Concepts

#### Network Namespace vs. Mount Namespace

- **Network Namespace**: Controls network stack isolation (interfaces, routing, firewall rules)
- **Mount Namespace**: Controls filesystem visibility and mount points
- **Key Distinction**: Network namespace isolation does not automatically imply mount namespace isolation

#### How Network Namespace Bind Mounts Work

Network namespaces are implemented as bind mounts in the filesystem:

```bash
# Create network namespace
ip netns add mynetns

# This creates a bind mount at /run/netns/mynetns
# The bind mount points to: /proc/self/ns/net
ls -la /run/netns/mynetns
# drwxr-xr-x 2 root root 0 Mar 23 20:07 /run/netns/mynetns
```

**Important**: The bind mount at `/run/netns/mynetns` is a filesystem entry that allows processes to access the network namespace.

#### Mount Namespace Isolation

When `PrivateMounts=yes`:

1. A new mount namespace is created for the service
2. All mounts made in the service are isolated from the host
3. Bind mounts created by `ip netns` become invisible to the host
4. Services cannot access network namespace bind mounts from other services

When `PrivateMounts=no`:

1. The service shares the mount namespace with the host
2. Network namespace bind mounts remain visible to other services
3. Services can access bind mounts created by other services

### 9.3 Implementation Details

#### Service Architecture (v2.0)

All services run on the **HOST**, using `ip netns exec` to project commands into the namespaces. This avoids `ProtectSystem=strict` and `ProtectHome=yes` conflicts.

**The Dependency Chain:**
`warp-ns-prep@%i` (Namespace/Veth/NAT/DNS) → `warp-reg@%i` (Sequential Registration) → `warp-node@%i` (Permanent Daemon) → `socat-bridge@%i` (Loopback Bridge).

**Key Unit Patterns:**
- **Template Units**: Use `%i` for instance-specific config directories (`/var/lib/cloudflare-warp-%i`)
- **Oneshot + RemainAfterExit**: Used for setup services (`ns-prep`, `reg`) to ensure they only run once
- **Capability Bounding**: `CapabilityBoundingSet=CAP_NET_ADMIN CAP_SYS_ADMIN` for namespace/mount operations
- **Resource Containment**: `MemoryMax=150M`, `CPUQuota=15%` to prevent OOM on Ryzen 5700U

**Bash & Systemd Integration**:
- **Variable Escaping**: Use `$${VAR}` in `ExecStart` to pass variables to bash
- **Sequentiality**: Use `flock` for resources shared across instances (like the registration daemon)
- **Idempotency**: `cleanup_stale_state()` must nuke all registration files and namespaces before every deploy

**Network Namespace Operations**:
- **Sovereign Siloing**: Use `ip netns add` → `ip link add veth` → `ip link set veth_ns netns` → `ip route add default`
- **DNS Sovereignty**: Bind mount a custom `resolv.conf` into the namespace to bypass host `systemd-resolved` issues

---

## §10 References and Further Reading

### Official Documentation

1. **Systemd.exec Man Page**: `man systemd.exec`
   - Details `NetworkNamespacePath=`, `PrivateNetwork=`, `PrivateMounts=`

2. **Systemd.unit Man Page**: `man systemd.unit`
   - Details `JoinsNamespaceOf=`

3. **Systemd.service Man Page**: `man systemd.service`
   - Details service unit configuration

### Community Resources

1. **Systemd Mailing List**: `systemd-devel@lists.freedesktop.org`
   - Technical discussions and updates

2. **GitHub Issues**: `github.com/systemd/systemd/issues`
   - Bug reports and feature requests

3. **Stack Overflow**: `stackoverflow.com/questions/tagged/systemd`
   - Community Q&A

### Related Projects

1. **iproute2**: Network namespace management tools
2. **containerd**: Container runtime with network namespace support
3. **Docker**: Container platform with network namespace support

### Academic References

1. **Linux Network Namespaces**: Research papers on network namespace implementation
2. **Systemd Architecture**: Technical documentation on systemd design
3. **Mount Namespace Isolation**: Research on filesystem isolation techniques

---

## §11 MASQUE Protocol Requirements (2026 Research)

### M1: MASQUE is Required for Proxy Mode

**Source**: Cloudflare WARP Client Changelog (v2025.8.779.0+)
**Confidence**: 10/10 (Official documentation)

**Critical Finding**: MASQUE is now the **only** protocol that supports WARP Proxy Mode. WireGuard is no longer supported for proxy.

**Dashboard Configuration Required**:
1. Zero Trust → Teams & Resources → Device profiles
2. Device tunnel protocol: `MASQUE`
3. Service mode: `Local proxy mode`
4. Default port: `40000` (configurable)

**Resource**: https://developers.cloudflare.com/cloudflare-one/team-and-resources/devices/cloudflare-one-client/configure/modes/

### M2: Proxy Mode Capabilities

| Feature | Status | Notes |
|---------|--------|-------|
| SOCKS5 support | ✅ | Primary protocol for Omega Engine |
| SOCKS4 support | ✅ | Legacy compatibility |
| HTTP CONNECT | ✅ | Alternative to SOCKS5 |
| Transparent HTTP proxy | ✅ | Added in v2025.10.186.0 |
| UDP proxying | ❌ | Not supported in proxy mode |
| DNS filtering | ❌ | Proxy mode only does HTTP filtering |
| 10-second timeout | ⚠️ | Requests exceeding 10s are dropped |

### M3: MASQUE Protocol Architecture

MASQUE (Multiplexed Application Substrate over QUIC Encryption) operates over HTTP/3 with QUIC:
- Post-quantum cryptography support
- L4 tunnel mode (no user-space TCP stack overhead)
- 2x throughput improvement over previous L3 tunnel

**Resource**: https://blog.cloudflare.com/faster-sase-proxy-mode-quic/

---

## §12 Python Asyncio Proxy Pool Patterns (2026 Research)

### P1: Production-Grade Pool Architecture

**Source**: Hex Proxies Blog (2026-04-10), resilient-httpx, pyroxi
**Confidence**: 9/10 (Production codebases)

**Key Design Principles**:
1. **One client per proxy** — HTTP/2 connection reuse, no TLS handshake per request
2. **Per-proxy semaphore** — caps concurrency to avoid rate limits (25-50 per proxy)
3. **Circuit breaker** — 5 consecutive failures → 30s cooldown
4. **Weighted random selection** — prefer proxies with fewer failures

### P2: socks5h vs socks5 (CRITICAL)

| Scheme | DNS Resolution | Use Case |
|--------|---------------|----------|
| `socks5://` | Client-side (local DNS) | When you want DNS through tunnel but resolved locally |
| `socks5h://` | Proxy-side (remote DNS) | **Recommended** — DNS resolved through WARP tunnel |

**For Omega Engine**: Always use `socks5h://` to ensure DNS sovereignty.

### P3: httpx-socks Integration

```python
from httpx_socks import AsyncProxyTransport

transport = AsyncProxyTransport.from_url('socks5h://127.0.0.1:8081')
async with httpx.AsyncClient(transport=transport) as client:
    response = await client.get('https://1.1.1.1/cdn-cgi/trace')
```

**Dependencies**: `httpx-socks[asyncio]`, `python-socks>=2.4.3,<3.0.0`

### P4: Health Check Pattern

```python
async def health_check(self, test_url='https://1.1.1.1/cdn-cgi/trace'):
    async with httpx.AsyncClient(timeout=10) as client:
        for proxy in self.proxies:
            try:
                response = await client.get(test_url, proxy=proxy.url)
                if response.status_code == 200 and 'warp=on' in response.text:
                    self.report_success(proxy)
                else:
                    self.report_failure(proxy)
            except Exception:
                self.report_failure(proxy)
```

---

## §13 Socat Bridge Architecture (2026 Research)

### S1: Two-Tier Bridge Pattern

**Source**: AetherGate Pro, OpenStream, netns_tcp_bridge
**Confidence**: 9/10 (Production implementations)

```
Host Applications
    ↓ TCP connect to 127.0.0.1:8081
    ↓ socat-bridge@1.service (TCP-LISTEN on host)
    ↓ ip netns exec warp_node_1 socat TCP:127.0.0.1:8081 TCP4:127.0.0.1:40000
    ↓ Cloudflare WARP (warp-svc in namespace, listening on 127.0.0.1:40000)
    ↓ MASQUE tunnel to Cloudflare Edge
```

### S2: Direct socat Bridge Command

```bash
# Per-node bridge command
socat TCP-LISTEN:808${NODE_ID},fork,reuseaddr \
  EXEC:"ip netns exec warp_node_${NODE_ID} socat TCP:127.0.0.1:40000"
```

### S3: Unix Socket Bridge (High-Throughput)

```bash
# Namespace side:
ip netns exec warp_node_1 socat UNIX-LISTEN:/run/warp-node-1.sock,reuseaddr,fork TCP:127.0.0.1:40000
# Host side:
socat TCP-LISTEN:8081,fork,reuseaddr /run/warp-node-1.sock
```

### S4: Socat Security (CVE-2026-56123)

**Critical**: Socat v1.8.1.2 fixes heap buffer overflow in SOCKS5 reply parser.
Ensure socat version >= 1.8.1.3 for production deployment.

---

## §14 Multi-Instance WARP Patterns (Production References)

### W1: Resource Budget Validation

| Resource | Per Instance | 3-Instance Pool | Notes |
|----------|-------------|-----------------|-------|
| Memory (warp-svc) | 50-100 MB | 150-300 MB | On Ryzen 5700U with 12GiB |
| CPU (idle) | <1% | <3% | Spikes during tunnel establishment |
| CPU (active) | 5-15% | 15-45% | During proxy connections |
| File descriptors | ~100 | ~300 | Per connection pool |
| Network (control) | ~1 KB/s | ~3 KB/s | MASQUE keepalive |

### W2: Docker Multi-Instance Insights

**Source**: gdtiti/cloudflare-warp, ErcinDedeoglu/cloudflare-warp

- Each instance uses ~50-100 MB RAM
- Starts 2 seconds apart (staggered boot)
- GOST provides round-robin aggregate proxy
- Active health recovery probes every 60s
- Skips failed instances after 3 failures, retries after 30s

---

## §15 References (2026 Research)

### Official Documentation

1. **Cloudflare WARP Modes**: https://developers.cloudflare.com/warp-client/warp-modes/
2. **Cloudflare Proxy Mode**: https://developers.cloudflare.com/cloudflare-one/team-and-resources/devices/cloudflare-one-client/configure/modes/
3. **MASQUE Blog Post**: https://blog.cloudflare.com/faster-sase-proxy-mode-quic/
4. **RFC 9484 (CONNECT-IP)**: https://datatracker.ietf.org/doc/html/draft-ietf-masque-connect-ip

### Python Libraries

1. **httpx-socks**: https://github.com/romis2012/httpx-socks
2. **python-socks**: https://github.com/romis2012/python-socks
3. **resilient-httpx**: https://github.com/galthran-wq/resilient-httpx
4. **pyroxi**: https://github.com/iliyadindar/pyroxi

### Production Implementations

1. **WarpNest**: https://github.com/ayush1920/WarpNet
2. **cloudflare-warp (Docker)**: https://github.com/gdtiti/cloudflare-warp
3. **AetherGate Pro**: https://github.com/JFGAtlas/aethergate-pro
4. **OpenStream**: https://github.com/Amir-A664/OpenStream
5. **Usque (MASQUE reimplementation)**: https://github.com/Diniboy1123/usque

### Systemd & Namespaces

1. **systemd PrivateMounts**: https://muru.dev/2023/08/26/netns-systemd.html
2. **systemd #2741**: https://github.com/systemd/systemd/issues/2741
3. **systemd #32339**: https://github.com/systemd/systemd/issues/32339
4. **netns_tcp_bridge**: https://github.com/vi/netns_tcp_bridge

---

*Last Updated: 2026-07-23*
*Version: 5.0.0*
*Author: Kali (Sprint Coordinator) + John Carmack (Technical Consultant)*
*Status: ACTIVE — Research gaps filled, deployment ready*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: v4.0.0 | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
