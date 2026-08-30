<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 WARP Proxy Pool — Session Knowledge Capture (Part 3c: warp-node@.service & socat-bridge@.service)
# ⬡ OMEGA ⬡ KALI ⬡ WARP-KB ⬡ 2026-07-05

---

## §1 warp-node@.service (Complete Unit File)

This unit file runs the permanent WARP daemon inside the network namespace using the per-instance configuration directory created by warp-reg@.service. It configures the daemon for proxy mode and establishes the connection.

```ini
[Unit]
Description=Cloudflare WARP Node Instance %i (Omega Engine Proxy Pool)
Documentation=file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/docs/research/warp_proxy_pool/WARP_PROXY_POOL_SPEC.md
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

# Runs on HOST — warp-svc executes INSIDE namespace via ip netns exec
# This gives warp-svc the namespace's network stack + veth internet access
ExecStart=/usr/sbin/ip netns exec warp_node_%i /usr/bin/warp-svc --config-dir /var/lib/cloudflare-warp-%i

# Post-start: configure WARP inside namespace (ip netns exec for each command)
ExecStartPost=/usr/bin/sleep 2
ExecStartPost=/usr/sbin/ip netns exec warp_node_%i /usr/bin/warp-cli --accept-tos mode proxy
ExecStartPost=/usr/sbin/ip netns exec warp_node_%i /usr/bin/warp-cli --accept-tos proxy port %i
ExecStartPost=/usr/sbin/ip netns exec warp_node_%i /usr/bin/warp-cli --accept-tos connect

# Graceful shutdown
KillMode=mixed
KillSignal=SIGTERM
TimeoutStartSec=30
TimeoutStopSec=15

Restart=always
RestartSec=3s

# Sandbox Security Rules
# CAP_NET_ADMIN for ip netns exec + tunnel routing, CAP_SYS_ADMIN for setns
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

---

## §2 socat-bridge@.service (Complete Unit File)

This unit file creates a TCP bridge from the host's loopback interface (ports 8081-8083) into the network namespace's WARP SOCKS5 proxy. It uses socat to forward connections from the host into the namespace where the WARP daemon is listening.

```ini
[Unit]
Description=Socat Bridge for WARP Instance %i (Host Loopback → Namespace Proxy)
Documentation=file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/docs/research/warp_proxy_pool/WARP_WARP_PROXY_POOL_SPEC.md
After=warp-node@%i.service
Requires=warp-node@%i.service
PartOf=warp-pool.target

[Service]
Type=simple
# Runs on HOST — forwards host loopback TCP to namespace SOCKS5 proxy
# Port arithmetic: 8080 + %i (8081, 8082, 8083)
# Uses $$ escaping for bash variables in systemd ExecStart
ExecStart=/usr/bin/bash -c 'port=$((8080 + %i)); exec /usr/bin/socat TCP-LISTEN:$${port},fork,reuseaddr,bind=127.0.0.1 EXEC:"/usr/sbin/ip netns exec warp_node_%i /usr/bin/socat - TCP:127.0.0.1:$${port}"'

# Graceful shutdown
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=10

Restart=always
RestartSec=2s

# Sandbox Security Rules
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes
RestrictAddressFamilies=AF_INET AF_UNIX AF_NETLINK
CapabilityBoundingSet=CAP_NET_ADMIN CAP_SYS_ADMIN

# Resource Containment
MemoryHigh=10M
MemoryMax=20M
CPUQuota=5%

[Install]
WantedBy=multi-user.target
```

---

## §3 warp-pool.target (Complete Unit File)

This unit file coordinates the entire WARP proxy pool, ensuring all 3 node instances are started together.

```ini
[Unit]
Description=Cloudflare WARP Proxy Pool (Omega Engine)
Documentation=file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/docs/research/warp_proxy_pool/WARP_PROXY_POOL_SPEC.md
Wants=warp-node@1.service warp-node@2.service warp-node@3.service
Wants=warp-reg@1.service warp-reg@2.service warp-reg@3.service
Wants=socat-bridge@1.service socat-bridge@2.service socat-bridge@3.service
Wants=warp-ns-prep@1.service warp-ns-prep@2.service warp-ns-prep@3.service

[Install]
WantedBy=multi-user.target
```

---

*Part 3c of 4 — warp-node@.service & socat-bridge@.service*
*Next: Part 3d — deploy_warp_pool.sh (Complete Script)*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: WARP-KB | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
