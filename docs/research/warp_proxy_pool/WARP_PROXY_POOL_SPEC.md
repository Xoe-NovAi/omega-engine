# 🔱 Omega Engine — Multi-Namespace WARP Proxy Pool Specification
⬡ OMEGA ⬡ SOPHIA ⬡ warp-pool ⬡ netns ⬡ trc_core ⬡ PROXY-POOL-SPEC

**AP Token**: `AP-WARP-PROXY-POOL-v1.2.0`
**Status**: PRODUCTION READY | **Last Updated**: 2026-07-05
**Author**: Sovereign Master Researcher + MiMo-V2.5 Review

---

## §0 Executive Summary

To build a highly resilient, sovereign runtime for the Omega Engine, the limitations of a single, sequential IP rotation architecture must be overcome. Relying on a single `oplire` + WARP instance introduces a critical bottleneck: if your background crawler triggers an HTTP 429, it breaks connections for your real-time search engine (SearXNG) and `ModelGateway` for up to 8 seconds.

This specification details the design and implementation of a **Multi-Namespace WARP Proxy Pool**. By running multiple independent instances of the Cloudflare `warp-svc` daemon completely isolated inside **Linux Network Namespaces (`netns`)**, we achieve true privilege separation, zero-latency failover, and parallel multi-IP outbound routing.

### §0.1 System Requirements

| Component | Minimum Version | Purpose |
|-----------|-----------------|---------|
| `iproute2` | 6.1+ | Network namespace management |
| `socat` | 1.7.4+ | Loopback bridge (host ↔ namespace) |
| `cloudflare-warp` | 2024.6.495+ | WARP tunnel daemon |
| `systemd` | 255+ | Service template management |
| Python 3.10+ | 3.10 | Proxy pool orchestration |
| `httpx[socks]` | 0.27+ | Async SOCKS5 client |

### §0.2 Resource Budget (Ryzen 5700U / 12GiB RAM)

| Component | Per-Instance | 3-Node Pool | Notes |
|-----------|--------------|-----------------|-------|
| `warp-svc` RSS | 45-75 MB | 135-225 MB | Typical under moderate load |
| `socat` RSS | ~2 MB | ~6 MB | Negligible overhead |
| `MemoryMax` | 150 MB | 450 MB | Hard systemd cap per instance |
| `CPUQuota` | 15% | 45% | Prevents runaway CPU usage |

---

## §1 Multi-Subsystem Partitioning & Namespacing

Running a single local proxy pool exposes all subsystems to the same rate limit footprint. You must segment your background task footprint from your user-facing execution pathways.

### §1.1 The Split
1. **Namespace `ns_critical` (Port 8080):** Dedicated strictly to `ModelGateway` and the Sovereign Search Fleet. This namespace stays warm and rarely triggers 429s because user-initiated traffic is episodic and highly prioritized.
2. **Namespace `ns_background` (Port 8081):** Dedicated to the Background Researcher. Aggressive rotation without interrupting the user.
3. **Namespace `ns_ephemeral` (Ports 8082, 8083, etc.):** Dedicated to the Skeptical Verifier. Dynamic, short-lived namespaces for concurrent multi-source scraping from different IPs.

---

## §2 Step-by-Step Setup & Configuration

### §2.1 The `/etc/sudoers.d/omega-warp` Configuration
To eliminate the background execution password prompt during WARP tunnel resets, you must configure a passwordless sudo rule for the `warp-cli` and namespace commands.

Create the file `/etc/sudoers.d/omega-warp`:
```bash
# Allow the rootless Omega Engine runtime user to recycle WARP nodes passwordlessly
arcana-novai ALL=(ALL) NOPASSWD: /usr/local/bin/spawn_warp_node.sh *
```
Set the strict filesystem permissions required by `sudo`:
```bash
sudo chmod 0440 /etc/sudoers.d/omega-warp
sudo chown root:root /etc/sudoers.d/omega-warp
```

### §2.2 Host-Centric Orchestration (The Sovereign Pattern)
To avoid `ProtectSystem=strict` and `ProtectHome=yes` conflicts within systemd, the Omega Engine uses a **Host-Centric Orchestration** model. All services run in the host mount namespace and project their execution into the target network namespace using `ip netns exec`.

**The Registration Copy-Loop**:
Since `warp-cli` lacks a `--config-dir` flag and always writes to the system default (`/var/lib/cloudflare-warp/`), we use the following sequence:
1. Start a temporary `warp-svc` on the host.
2. Execute `warp-cli registration new`.
3. Copy all resulting config files (`reg.json`, `conf.json`, `warp.db`, etc.) from the default path to the instance-specific path (`/var/lib/cloudflare-warp-%i/`).
4. Kill the temporary host daemon.
5. Start the permanent `warp-node@%i` service using the `--config-dir` flag.

---

## §3 Production systemd Target & Script Architecture

To manage isolated multi-directory runtime profiles cleanly, we use Systemd Template Units (`@.service`) bound underneath a global synchronization target (`warp-pool.target`). 

### §3.1 The Global Target Coordinator (`/etc/systemd/system/warp-pool.target`)
```ini
[Unit]
Description=Omega Engine Cloudflare WARP Namespace Pool Coordinator
After=network.target
Wants=warp-node@1.service warp-node@2.service warp-node@3.service \
      socat-bridge@1.service socat-bridge@2.service socat-bridge@3.service

[Install]
WantedBy=multi-user.target
```

### §3.2 The Service Template Unit (`/etc/systemd/system/warp-node@.service`)
```ini
[Unit]
Description=Cloudflare WARP Node Instance %i (Omega Engine Proxy Pool)
After=network-online.target warp-ns-prep@%i.service warp-reg@%i.service
Requires=warp-ns-prep@%i.service warp-reg@%i.service
PartOf=warp-pool.target
StartLimitIntervalSec=60
StartLimitBurst=10

[Service]
Type=simple
RuntimeDirectory=cloudflare-warp-%i
StateDirectory=cloudflare-warp-%i
ConfigurationDirectory=cloudflare-warp-%i
LogsDirectory=cloudflare-warp-%i

# Execute on HOST, projecting into namespace
ExecStart=/usr/bin/ip netns exec warp_node_%i /usr/bin/warp-svc --config-dir /var/lib/cloudflare-warp-%i

# Post-start: configure WARP inside namespace
ExecStartPost=/usr/bin/sleep 2
ExecStartPost=/usr/bin/ip netns exec warp_node_%i /usr/bin/warp-cli --accept-tos mode proxy
ExecStartPost=/usr/bin/ip netns exec warp_node_%i /usr/bin/warp-cli --accept-tos proxy port %i
ExecStartPost=/usr/bin/ip netns exec warp_node_%i /usr/bin/warp-cli --accept-tos connect

KillMode=mixed
KillSignal=SIGTERM
TimeoutStartSec=30
TimeoutStopSec=15

Restart=always
RestartSec=3s

# Sandbox Security Rules
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes
RestrictAddressFamilies=AF_INET AF_UNIX AF_NETLINK
CapabilityBoundingSet=CAP_NET_ADMIN CAP_SYS_ADMIN

# Resource Containment for Ryzen 5700U / 12GiB RAM
MemoryHigh=120M
MemoryMax=150M
CPUQuota=15%

[Install]
WantedBy=multi-user.target
```

### §3.3 Complete Lifecycle Automation Script (`/usr/local/bin/spawn_warp_node.sh`)
(Implementation details deferred to source code in `scripts/spawn_warp_node.sh`)

---

## §4 Python Orchestration Core (proxy_pool.py)
(Implementation details deferred to source code in `src/omega/proxy_pool.py`)

---

## §5 Verification and Boot Execution Flow
(Implementation details deferred to `docs/research/warp_proxy_pool/VALIDATION_STRATEGY.md`)

---

## §6 Troubleshooting
(Refer to `docs/kb/WARP_Sovereign_Knowledge_Base.md` for the complete Error Matrix)

---
 
## §8 2026 Hardening & Sovereign Resilience
As of 2026, the "Brittle Pipe" architecture has been evolved into a **Sovereign Pool** to ensure production-grade reliability and security.

### §8.1 `socat` Bridge Hardening
The loopback bridge is optimized for high-frequency proxy connections:
- **TCP Tuning**: `nodelay` (disable Nagle), `keepalive`, and buffers (`rcvbuf`/`sndbuf`) set to 64KB.
- **Resource Caps**: `max-children=128` to prevent fork-bombing.
- **Access Control**: `range=127.0.0.1/32` ensures the listener is only accessible locally.

### §8.2 systemd Sandboxing (Sovereign Standard)
Service units (`warp-node@.service` and `socat-bridge@.service`) now implement the 2026 security baseline:
- **Privilege Reduction**: Use of `AmbientCapabilities` to restrict processes to only `CAP_NET_ADMIN` and `CAP_NET_RAW`.
- **Kernel Isolation**: `SystemCallFilter=~@privileged @system-service`, `MemoryDenyWriteExecute=yes`, and `LockPersonality=yes`.
- **Resource Guarding**: Strict `MemoryMax` and `CPUQuota` to prevent runaway instances from impacting the host.

### §8.3 Network Namespace Tuning
To eliminate fragmentation and latency spikes:
- **MTU Optimization**: Veth pairs are pinned to **1420 bytes** to match the WireGuard standard.
- **TCP Stack Tuning**: `net.ipv4.tcp_keepalive_time=60` and `net.ipv4.tcp_fin_timeout=15` are enforced inside the namespace.
- **Buffer Scaling**: `net.core.rmem_max` and `wmem_max` increased to 16MB.

### §8.4 Tiered Canary Probing
The health check has evolved from a simple `curl` to a tiered validator:
1. **L4 (Transport)**: TCP SYN check to verify the `socat` listener is alive.
2. **L7 (Application)**: HTTP request to `1.1.1.1/cdn-cgi/trace` to verify tunnel routing.
3. **Latency**: TTFB (Time-to-First-Byte) monitoring to mark nodes as `DEGRADED` before total failure.

### §8.5 Zero-Downtime Rotation (Blue-Green Drain)
IP rotation no longer uses `systemctl restart` (which drops all streams). The **Drain Pattern** is implemented:
1. Spawn a new namespace node.
2. Route new requests to the new node.
3. Monitor `conntrack` for active connections on the old node.
4. Terminate the old node only after connections are drained or a grace period expires.

---

*🔱 OMEGA ⬡ SOPHIA ⬡ warp-pool ⬡ netns ⬡ trc_core ⬡ PROXY-POOL-SPEC v1.3.0 (Hardened)*
