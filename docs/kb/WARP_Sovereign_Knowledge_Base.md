# 🔱 Omega Engine — WARP Proxy Pool Sovereign Knowledge Base
# ⬡ OMEGA ⬡ KALI ⬡ WARP-KB ⬡ v3.0.0 ⬡ 2026-07-05
# The definitive record of the Multi-Namespace WARP Deployment.

---

## §1 Architecture & Root Causes

### 1.1 Executive Summary
**Goal**: Deploy 3 independent Cloudflare WARP instances in Linux network namespaces, each with a unique exit IP, exposed as SOCKS5 proxies on host loopback (ports 8081-8083).

**The Sovereign Design**:
Host Applications (Omega Engine) $\rightarrow$ `socks5h://127.0.0.1:8081-8083` $\rightarrow$ `socat-bridge@` (Host $\rightarrow$ Namespace) $\rightarrow$ Network Namespace (`warp_node_1/2/3`) $\rightarrow$ Veth Pair + NAT $\rightarrow$ Host Default Route $\rightarrow$ Cloudflare Edge.

### 1.2 Critical Root Causes (The "Hard-Won" Truths)
| ID | Root Cause | Discovery | Sovereign Fix |
|----|-------------|-----------|----------------|
| **RC1** | `warp-cli` lacks `--config-dir` | `warp-cli --config-dir` $\rightarrow$ Error | Register at default path $\rightarrow$ `cp -r` to custom path |
| **RC2** | Daemon-Centric IPC | `warp-cli` needs `warp-svc` | Start temporary `warp-svc` on host for registration |
| **RC3** | Socket Conflicts | Multiple daemons fight for `/run/cloudflare-warp/warp_service` | Stop host `warp-svc` before registration; use `flock` for serialization |
| **RC4** | Persistent Daemon State | `rm -rf` files $\neq$ clean slate | `warp-cli --accept-tos settings reset` before registration |
| **RC5** | Log Permissions | `warp-svc` cannot write to default logs | `LOGS_DIRECTORY=/var/log/cloudflare-warp` + `chmod 755` |
| **RC6** | Namespace DNS Void | No resolver in new namespace | Bind mount `/etc/netns/warp_node_%i/resolv.conf` with `1.1.1.1` |
| **RC7** | NAT Volatility | `ExecStop` removed MASQUERADE rules | Move NAT setup to deploy script's `enable_and_start_pool()` |
| **RC8** | Registration Race | Parallel `warp-reg` conflict on host daemon | `flock -x /run/warp-reg-global.lock` for strict serialization |

---

## §2 Implementation Patterns

### 2.1 Systemd Service Architecture (v2.0)
All services run on the **HOST**, using `ip netns exec` to project commands into the namespaces. This avoids `ProtectSystem=strict` and `ProtectHome=yes` conflicts.

**The Dependency Chain:**
`warp-ns-prep@%i` (Namespace/Veth/NAT/DNS) $\rightarrow$ `warp-reg@%i` (Sequential Registration) $\rightarrow$ `warp-node@%i` (Permanent Daemon) $\rightarrow$ `socat-bridge@%i` (Loopback Bridge).

**Key Unit Patterns:**
- **Template Units**: Use `%i` for instance-specific config directories (`/var/lib/cloudflare-warp-%i`).
- **Oneshot + RemainAfterExit**: Used for setup services (`ns-prep`, `reg`) to ensure they only run once.
- **Capability Bounding**: `CapabilityBoundingSet=CAP_NET_ADMIN CAP_SYS_ADMIN` for namespace/mount operations.
- **Resource Containment**: `MemoryMax=150M`, `CPUQuota=15%` to prevent OOM on Ryzen 5700U.

### 2.2 Bash & Systemd Integration
- **Variable Escaping**: Use `$${VAR}` in `ExecStart` to pass variables to bash.
- **Sequentiality**: Use `flock` for resources shared across instances (like the registration daemon).
- **Idempotency**: `cleanup_stale_state()` must nuke all registration files and namespaces before every deploy.

### 2.3 Network Namespace Operations
- **Sovereign Siloing**: Use `ip netns add` $\rightarrow$ `ip link add veth` $\rightarrow$ `ip link set veth_ns netns` $\rightarrow$ `ip route add default`.
- **DNS Sovereignty**: Bind mount a custom `resolv.conf` into the namespace to bypass host `systemd-resolved` issues.

---

## §3 Debugging & Forensic Toolkit

### 3.1 Inspection Commands
| Goal | Command |
|------|----------|
| **Namespace List** | `ip netns list` |
| **Namespace IP** | `ip netns exec warp_node_1 ip addr show` |
| **Namespace Route** | `ip netns exec warp_node_1 ip route show` |
| **Namespace DNS** | `ip netns exec warp_node_1 cat /etc/resolv.conf` |
| **Bridge Status** | `ss -tlnp | grep 8081` |
| **Tunnel Trace** | `curl -x socks5h://127.0.0.1:8081 https://1.1.1.1/cdn-cgi/trace` |

### 3.2 Common Error Matrix
| Error | Cause | Fix |
|-------|-------|-----|
| `Unable to connect to daemon` | `warp-svc` not running | Start `warp-svc` before `warp-cli` |
| `Address already in use` | Socket conflict | Stop host `warp-svc`; use `flock` |
| `Old registration is still around` | Daemon memory state | `warp-cli settings reset` |
| `Permission denied` (logs) | Log dir not writable | `LOGS_DIRECTORY=/var/log/cloudflare-warp` |
| `DNS timeout` | No resolver in namespace | Bind mount `resolv.conf` |
| `Invalid argument` (ns) | Failed bind mount (ProtectHome) | Remove `ProtectHome=yes` from prep units |

---

## §4 Deployment & Validation

### 4.1 The Deployment Flow
1. **Cleanup**: Stop all services $\rightarrow$ Nuke registration files $\rightarrow$ Delete namespaces.
2. **Deploy**: Copy units $\rightarrow$ `systemctl daemon-reload` $\rightarrow$ `systemctl start warp-pool.target`.
3. **NAT**: Apply `iptables -t nat -A POSTROUTING -s 10.0.i.0/24 -o <default_if> -j MASQUERADE`.
4. **Wait**: Poll `systemctl is-active` for all nodes (up to 300s).

### 4.2 Validation Scenarios
- **Isolation**: `ss -tlnp` inside `warp_node_1` must not show ports from `warp_node_2`.
- **Connectivity**: `curl -x socks5h://...` must return `warp=on`.
- **Rotation**: `recycle` node $\rightarrow$ verify `ip=` change in `cdn-cgi/trace`.
- **Recovery**: Kill `socat` bridge $\rightarrow$ trigger `recycle` $\rightarrow$ verify port returns to `LISTENING`.

---

## §5 Performance & Security

### 5.1 Resource Budget (Ryzen 5700U)
- **Memory**: ~50-100MB per `warp-svc` instance. Total pool $\approx$ 300MB.
- **CPU**: Low idle; spikes during tunnel establishment.
- **Sovereignty**: `socks5h://` forces DNS through the tunnel, eliminating local DNS leaks.

### 5.2 Security Model
- **Privilege Separation**: `spawn_warp_node.sh` is the only root-privileged entry point (via sudoers).
- **Network Siloing**: Each instance is in a separate `netns`; no inbound access from the internet.
- **Sovereign-Siloing**: Adapted from `[id-soft: doom-1993]` to ensure one node's failure cannot crash others.

---

*Last Updated: 2026-07-05 | Author: Kali (Sprint Coordinator)*
*Status: ACTIVE — Consolidated Master Knowledge Base*
