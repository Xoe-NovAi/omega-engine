# 🔱 WARP Proxy Pool Deployment Documentation
# Systemd NetworkNamespacePath and PrivateMounts Implementation Guide
# Multi-Instance WARP Deployment for Omega Engine

**Version**: 4.0.0
**Last Updated**: 2026-07-23
**Author**: Kali (Sprint Coordinator)
**Status**: ACTIVE — All fixes applied, awaiting deployment verification

---

## Executive Summary

This document provides comprehensive guidance for deploying 3 independent Cloudflare WARP instances in Linux network namespaces, each with a unique exit IP, exposed as SOCKS5 proxies on the host's loopback (ports 8081-8083). This deployment addresses the "novel usage that people say can't be done" by implementing a sophisticated systemd-based architecture that overcomes systemd v254 breaking changes.

**Key Innovation**: All services run on the **HOST** using `ip netns exec` for namespace commands, avoiding `ProtectSystem=strict` and `ProtectHome=yes` conflicts while maintaining full network namespace isolation.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Systemd NetworkNamespacePath and PrivateMounts Implementation](#systemd-networknamespacepath-implementation)
3. [Service Architecture and Dependencies](#service-architecture)
4. [Critical Lessons Learned and Best Practices](#critical-lessons-learned)
5. [Deployment and Validation Procedures](#deployment-validation)
6. [Troubleshooting Guide](#troubleshooting-guide)
7. [Performance and Security Considerations](#performance-security)
8. [References and Further Reading](#references)

---

## 1. Architecture Overview

### 1.1 Goal

Deploy 3 independent Cloudflare WARP instances in Linux network namespaces:
- Each instance has a unique exit IP
- Exposed as SOCKS5 proxies on host loopback (ports 8081-8083)
- Full network isolation between instances
- Host context for setup operations

### 1.2 Component Stack

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

### 1.3 Service Dependency Chain

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

---

## 2. Systemd NetworkNamespacePath and PrivateMounts Implementation

### 2.1 Systemd v254 Breaking Changes

**Critical Finding**: Starting with systemd v254, `PrivateNetwork=yes` and `NetworkNamespacePath=` now imply `PrivateMounts=yes` unless `PrivateMounts=no` is explicitly specified.

**Impact**: This change breaks existing setups that rely on accessing network namespace bind mounts from other services.

**Solution**: Use `PrivateMounts=no` when you need to access network namespace bind mounts from other services, or use `JoinsNamespaceOf=` for cleaner namespace relationships.

**Key Innovation**: All services run on the **HOST** using `ip netns exec` for namespace commands, avoiding `ProtectSystem=strict` and `ProtectHome=yes` conflicts while maintaining full network namespace isolation.

### 2.2 Core Concepts

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

### 2.3 Implementation Details

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

## 3. Critical Lessons Learned and Best Practices

### 3.1 Critical Root Causes (The "Hard-Won" Truths)

| ID | Root Cause | Discovery | Sovereign Fix |
|----|-------------|-----------|----------------|
| **RC1** | `warp-cli` has NO `--config-dir` flag | `warp-cli --config-dir` → Error | Register in default path, then `cp -r` to custom path |
| **RC2** | `warp-cli --accept-tos registration delete` is a NO-OP | Running `warp-cli --accept-tos registration delete` prints "Success" but does NOT remove the registration | Use `rm -f` to nuke ALL state files: `reg.json`, `conf.json`, `warp.db`, `settings.json`, `final-overrides-settings.json` |
| **RC3** | Registration state is distributed across multiple files | `warp-cli registration new` writes to `reg.json` only, but `warp-cli registration new` CHECKS `conf.json` and `warp.db` for existing registration | Must `rm -f` ALL of these before `registration new` |
| **RC4** | `warp-svc` needs `--config-dir` for multi-instance | `warp-svc --config-dir /var/lib/cloudflare-warp-%i` creates per-instance config | Each namespace instance needs its own config directory |
| **RC5** | Network namespaces need internet access for WARP tunnel | `ip netns add` creates an isolated network with only loopback. WARP cannot establish its MASQUE/WireGuard tunnel without outbound internet. | Veth pair + NAT setup in ns-prep |
| **RC6** | `ProtectHome=yes` implies `PrivateTmp=yes` | systemd.exec man page: "Setting this to true implies PrivateTmp= and thus also creates a new mount namespace" | Remove `ProtectHome=yes` from ns-prep and warp-reg |
| **RC7** | `ProtectSystem=strict` breaks `ip netns exec` | `ProtectSystem=strict` makes the filesystem read-only, which can block `setns()` operations | Use `ip netns exec` from the HOST instead of `NetworkNamespacePath` |
| **RC8** | ExecStartPost warp-cli commands need `--accept-tos` | `warp-cli mode proxy`, `warp-cli proxy port`, `warp-cli connect` all require ToS acceptance in non-TTY mode | Add `--accept-tos` to ALL warp-cli commands in ExecStartPost |
| **RC9** | `ip netns add` creates empty files on failure | If `mount --bind` fails (e.g., due to PrivateMounts), `ip netns add` creates an empty file at `/var/run/netns/warp_node_N` | Check `file /var/run/netns/warp_node_N` for "nsfs" type. If empty, `rm -f` and recreate. |
| **RC10** | systemd `$$` escaping for bash variables | In systemd `ExecStart`, `${VAR}` is interpreted by systemd (not bash). To pass `${VAR}` to bash, use `$${VAR}`. | Use `$${port}` for bash variables in systemd ExecStart |
| **RC11** | Namespace bind mount validity check | Valid namespace bind mounts show as `nsfs` type in `/proc/self/mountinfo`. Invalid ones show as regular files. | `cat /proc/self/mountinfo | grep warp_node` → should show `nsfs nsfs rw` with unique net IDs |
| **RC12** | StartLimitBurst needs headroom for deploy cycles | Deploy script's cleanup/start cycle can trigger 5+ restarts within 60s, hitting `StartLimitBurst=5` | Increase to `StartLimitBurst=10` |

### 3.2 Key Implementation Patterns

#### Pattern 1: Host-Based Service Architecture

**Why**: Avoids `ProtectSystem=strict` and `ProtectHome=yes` conflicts

**How**:
```ini
# All services run on HOST
[Service]
Type=simple
PrivateMounts=no  # Allows access to /run/netns/warp_node_%i

ExecStart=/usr/bin/service-that-needs-host-context
```

#### Pattern 2: Sequential Registration

**Why**: Prevents race conditions in WARP registration

**How**:
```ini
# warp-reg@%i.service
[Unit]
Description=WARP Registration Service %i
After=warp-ns-prep@%i.service
Requires=warp-ns-prep@%i.service

[Service]
Type=oneshot
RemainAfterExit=yes
PrivateMounts=no

ExecStart=/usr/bin/flock -x /run/warp-reg-global.lock \
    /usr/bin/warp-cli --accept-tos registration new \
    --config-dir /var/lib/cloudflare-warp-%i \
    --license-key ${LICENSE_KEY}
```

#### Pattern 3: Namespace Setup with Host Context

**Why**: Veth pairs and NAT setup require host context

**How**:
```ini
# warp-ns-prep@%i.service
[Unit]
Description=Network Namespace Setup %i

[Service]
Type=oneshot
RemainAfterExit=yes
PrivateMounts=no

ExecStart=/usr/bin/ip netns add warp_node_%i
ExecStart=/usr/bin/ip link add veth_host_%i type veth peer name veth_ns_%i
ExecStart=/usr/bin/ip link set veth_ns_%i netns warp_node_%i
ExecStart=/usr/sbin/ip addr add 10.0.%i.1/24 dev veth_host_%i
ExecStart=/usr/sbin/ip netns exec warp_node_%i ip addr add 10.0.%i.2/24 dev veth_ns_%i
ExecStart=/usr/sbin/ip netns exec warp_node_%i ip route add default via 10.0.%i.1
ExecStart=/usr/sbin/iptables -t nat -A POSTROUTING -s 10.0.%i.0/24 -o wlo1 -j MASQUERADE
```

---

## 4. Deployment Checklist

### 4.1 Pre-deployment

1. [ ] Verify cloudflare-warp is installed: `which warp-cli warp-svc`
2. [ ] Verify iproute2: `ip netns list` works
3. [ ] Verify socat: `which socat`
4. [ ] Stop host WARP daemon: `sudo systemctl stop warp-svc` (if running)
5. [ ] Remove host WARP registration: `sudo rm -f /var/lib/cloudflare-warp/{reg,conf,settings,final-overrides-settings}.json /var/lib/cloudflare-warp/warp.db`

### 4.2 Deployment

```bash
sudo ./scripts/deploy_warp_pool.sh
```

### 4.3 Post-deployment verification

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

---

## 5. Troubleshooting Guide

### 5.1 Common Error Matrix

| Error | Cause | Fix |
|-------|-------|-----|
| `Unable to connect to daemon` | `warp-svc` not running | Start `warp-svc` before `warp-cli` |
| `Address already in use` | Socket conflict | Stop host `warp-svc`; use `flock` |
| `Old registration is still around` | Daemon memory state | `warp-cli settings reset` |
| `Permission denied` (logs) | Log dir not writable | `LOGS_DIRECTORY=/var/log/cloudflare-warp` |
| `DNS timeout` | No resolver in namespace | Bind mount `resolv.conf` |
| `Invalid argument` (ns) | Failed bind mount (ProtectHome) | Remove `ProtectHome=yes` from ns-prep, recreate namespace |

### 5.2 Error-Specific Solutions

#### "Old registration is still around"

- **Cause**: `reg.json` removed but `conf.json`/`warp.db` still present
- **Fix**: `rm -f /var/lib/cloudflare-warp/{reg,conf,warp.db,settings,final-overrides-settings}.json`

#### "Please accept the WARP Terms of Service"

- **Cause**: `warp-cli` command missing `--accept-tos` flag
- **Fix**: Add `--accept-tos` to ALL `warp-cli` commands

#### "Cannot open network namespace: Permission denied"

- **Cause**: Service running inside namespace but needs host context
- **Fix**: Remove `NetworkNamespacePath=`, use `ip netns exec` from host

#### "Cannot open network namespace: Invalid argument"

- **Cause**: Namespace file exists but is empty (failed bind mount)
- **Fix**: Remove `ProtectHome=yes` from ns-prep, recreate namespace

#### "Cannot open network namespace: No such file or directory"

- **Cause**: Namespace doesn't exist (ns-prep failed)
- **Fix**: Check ns-prep journal: `journalctl -u warp-ns-prep@1.service`

#### warp-node hits StartLimitBurst

- **Cause**: Multiple restart cycles within 60s
- **Fix**: Increase `StartLimitBurst=10` in warp-node service

#### WARP tunnel establishes but no internet

- **Cause**: Namespace lacks outbound route (missing veth + NAT)
- **Fix**: Verify veth pair exists, NAT rule present, IP forwarding enabled

---

## 6. Performance and Security Considerations

### 6.1 Resource Budget (Ryzen 5700U)

- **Memory**: ~50-100MB per `warp-svc` instance. Total pool ≈ 300MB
- **CPU**: Low idle; spikes during tunnel establishment
- **Sovereignty**: `socks5h://` forces DNS through the tunnel, eliminating local DNS leaks

### 6.2 Security Model

- **Namespace isolation**: Each WARP instance runs in its own network namespace
- **Veth pairs**: Isolated L2 connectivity between host and namespace
- **NAT**: MASQUERADE for outbound traffic (no inbound from internet)
- **No capabilities retained**: Services drop capabilities after oneshot execution
- **No telemetry**: All traffic stays local or goes through WARP tunnel

### 6.3 Sovereign-Siloing

Adapted from `[id-soft: doom-1993]` to ensure one node's failure cannot crash others. Each instance operates as a sovereign entity with:

- Independent network stack
- Separate configuration state
- Isolated DNS resolution
- Unique exit IP

---

## 7. References and Further Reading

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

*Last Updated: 2026-07-23*
*Version: 4.0.0*
*Author: Kali (Sprint Coordinator)*
*Status: ACTIVE — All fixes applied, awaiting deployment verification*