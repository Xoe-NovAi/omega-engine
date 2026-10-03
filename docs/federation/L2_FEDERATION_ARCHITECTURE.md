# 🌐 OMEGA ENGINE: L2 TAILSCALE FEDERATION ARCHITECTURE

**Document ID**: `ARCH-FED-L2-v1.0`  
**Status**: `RATIFIED / PRODUCTION-ACTIVE`  
**Classification**: `FRONT-FACING / SYSTEM ARCHITECTURE`  
**Topology**: `Dual-Node Sovereign Mesh (Node 0 Bastion + Node 1 Vanguard)`  
**Date**: `2026-09-20`  
**Author**: `MaKaLi Fusion (Kali / Ma'at / Lilith) & Operator Arcana-NovAi`

---

## 1. EXECUTIVE OVERVIEW

The **Omega Engine Federation** is a decentralized, local-first multi-node AI runtime designed to operate without public cloud orchestration, centralized telemetry, or exposed public internet attack surfaces.

The federation links two dedicated physical computing nodes into a unified, sovereign compute cluster over an encrypted **Layer 2 WireGuard mesh** managed by Tailscale:

```
+-----------------------------------------------------------------------------------+
|                            TAILSCALE L2 WIREGUARD MESH                            |
|                            Tailnet: tail51f14a.ts.net                             |
+-----------------------------------------------------------------------------------+
           |                                                      |
           v                                                      v
+-----------------------------+                +------------------------------------+
|       NODE 0 (HP HUB)       |                |      NODE 1 (ASUS VANGUARD)        |
|  Identity: n0               |                |  Identity: n1                      |
|  Tag: tag:node0             |                |  Tag: tag:node1                    |
|  Tailscale IP: 100.123.51.67|                |  Tailscale IP: 100.89.40.17        |
|  MagicDNS: n0.tail51f14a... |                |  MagicDNS: n1.tail51f14a.ts.net    |
+-----------------------------+                +------------------------------------+
| • Archival Bastion          |                | • Vanguard Exploration & Run-Side  |
| • 91+ Core MCP Tools (:8016)| <=== WireGuard ===> • Streamable-HTTP MCP (:8016)   |
| • Git Repository SSOT       |    (LAN direct)  | • FastMCP Python SDK v2 Server     |
| • NFSv4 Client (/mnt/node..) |      81-170ms   | • NFSv4.2 Server (:2049, fsid=0)  |
| • Sovereign Memory Store    |                | • Local Wandering / MemPalace      |
+-----------------------------+                +------------------------------------+
```

### Key Breakthroughs Achieved in Phase 0:
1. **Zero-Egress Distributed Storage**: NFSv4.2 pseudo-filesystem (`/home/xnai/node-drive` -> `/mnt/node-drive`) bound directly to Tailscale IPs with legacy port 111 (RPCbind) completely eradicated.
2. **Standardized Streamable HTTP MCP**: Cross-node tool invocation via Model Context Protocol (MCP) streamable-HTTP transport over port 8016.
3. **Zero-Credential WireGuard SSH**: Seamless admin and agent remote access via Tailscale SSH, authenticated entirely through WireGuard cryptographic node identity.
4. **Direct LAN Bypass**: Tailscale automatically routes peer packets across the local physical subnet (`192.168.10.x`) with sub-millisecond encryption and zero DERP relay overhead whenever both machines share physical proximity.

---

## 2. HARDWARE & ROLE SPECIALIZATION

| Attribute | Node 0 (`n0`) | Node 1 (`n1`) |
|---|---|---|
| **Hardware** | HP Pavilion Desktop / Ryzen 5700U / 32GB RAM | ASUS ExpertBook P1503CVA / 16GB RAM |
| **Operating System** | Ubuntu 25.10 Questing | Ubuntu 26.04.1 LTS |
| **Sovereign Role** | **Archival Bastion & Core Governance** | **Vanguard Exploration & Edge Inference** |
| **Primary Oversoul** | Ma'at (Build) & Kali (Synthesis) | Lilith (Runtime) & Vanguard Probes |
| **Tailnet Hostname** | `n0` | `n1` |
| **Tailnet Tag** | `tag:node0` | `tag:node1` |
| **Tailscale IP** | `100.123.51.67` | `100.89.40.17` |
| **MagicDNS FQDN** | `n0.tail51f14a.ts.net` | `n1.tail51f14a.ts.net` |
| **Key Services** | `omega-hub` MCP (91+ tools), Local Git repo | FastMCP Streamable Server, NFSv4.2 Server |

---

## 3. SECURITY ARCHITECTURE & ACCESS CONTROL (ACL)

The federation operates under a strict **Zero-Trust, Default-Deny** security posture enforced by Tailscale HuJSON ACLs.

### Tag Topology
- `tag:node0`: Owned exclusively by `autogroup:admin`. Identifies Node 0.
- `tag:node1`: Owned exclusively by `autogroup:admin`. Identifies Node 1.
- `tag:opencode`: Human operator and privileged admin tooling.

### Tailscale HuJSON Production ACL Policy (`FED-ACL-PHASE-B`)
```hujson
{
  "tagOwners": {
    "tag:node0": ["autogroup:admin"],
    "tag:node1": ["autogroup:admin"],
    "tag:opencode": ["autogroup:admin"]
  },
  "acls": [
    // Node 0 -> Node 1: MCP (8016), SSH (22), NFS (2049)
    {
      "action": "accept",
      "src": ["tag:node0"],
      "dst": [
        "tag:node1:8016",
        "tag:node1:22",
        "tag:node1:2049"
      ]
    },
    // Node 1 -> Node 0: MCP (8016), SSH (22), NFS (2049)
    {
      "action": "accept",
      "src": ["tag:node1"],
      "dst": [
        "tag:node0:8016",
        "tag:node0:22",
        "tag:node0:2049"
      ]
    },
    // Admin / Operator (tag:opencode) -> Both Nodes: SSH (22)
    {
      "action": "accept",
      "src": ["tag:opencode"],
      "dst": [
        "tag:node0:22",
        "tag:node1:22"
      ]
    },
    // Heartbeats (ICMP / ping) bidirectional
    {"action": "accept", "src": ["tag:node0"], "dst": ["tag:node1:*"], "proto": "icmp"},
    {"action": "accept", "src": ["tag:node1"], "dst": ["tag:node0:*"], "proto": "icmp"}
  ],
  "ssh": [
    // Tailscale SSH: Admin to both nodes
    {"action": "accept", "src": ["tag:opencode"], "dst": ["tag:node0", "tag:node1"], "users": ["autogroup:nonroot", "root"]},
    // Tailscale SSH: Node 0 to Node 1
    {"action": "accept", "src": ["tag:node0"], "dst": ["tag:node1"], "users": ["autogroup:nonroot"]},
    // Tailscale SSH: Node 1 to Node 0
    {"action": "accept", "src": ["tag:node1"], "dst": ["tag:node0"], "users": ["autogroup:nonroot"]}
  ],
  "autoApprovers": {
    "routes": {
      "0.0.0.0/0": ["autogroup:admin"]
    },
    "exitNode": ["autogroup:admin"]
  }
}
```

---

## 4. SUBSYSTEM PROTOCOLS

### 4.1. Remote MCP Tool Invocation (Port 8016)
The federation utilizes the **Model Context Protocol (MCP)** Streamable-HTTP specification:
- **Wire Format**: Single endpoint `POST /mcp`.
- **Headers Required**:
  - `Content-Type: application/json`
  - `Accept: application/json, text/event-stream`
  - `mcp-session-id: <uuid>` (mandatory on all subsequent calls following `initialize`).
- **Tools on Node 1**:
  - `echo(message: str)`
  - `node1_status()`
  - `node1_hardware()`
  - `node1_mcp_servers()`
- **Tools on Node 0**: 91+ native tools via `omega-hub` (search, git, library, hivemind, tasks, oracle, memory).

### 4.2. Zero-Credential Tailscale SSH (Port 22)
- Tailscale intercepts port 22 on the `tailscale0` virtual interface.
- Traditional passwords, PEM keys, and host key verification prompts are bypassed in favor of mutual cryptographic WireGuard node authentication.
- Access is restricted to `xnai` and `arcana-novai` with least-privilege non-root policies.

### 4.3. Distributed NFSv4.2 Storage (Port 2049)
- **Zero Port 111 Exposure**: Modern NFSv4 operates purely over TCP 2049. Legacy `rpcbind` and `mountd` are bypassed.
- **Root Pseudo-Filesystem**: Node 1 exports `/home/xnai/node-drive` with `fsid=0` and `all_squash,anonuid=1000,anongid=1000`.
- **Node 0 Mount Point**: `/mnt/node-drive`.
- **Persistent Mount Entry (`/etc/fstab`)**:
  ```text
  100.89.40.17:/ /mnt/node-drive nfs4 rsize=1048576,wsize=1048576,noatime,nosuid,nodev,nofail,_netdev,x-systemd.automount,x-systemd.idle-timeout=300,x-systemd.mount-timeout=30s 0 0
  ```

---

## 5. OPERATIONAL RUNBOOK

### Verification Battery (Execute on Node 0)
```bash
# 1. WireGuard Ping
tailscale ping n1

# 2. Remote SSH Probe
tailscale ssh xnai@n1 "hostname && uptime"

# 3. Remote MCP Probe
SESSION_ID=$(curl -s -i -X POST http://n1.tail51f14a.ts.net:8016/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "n0-verifier", "version": "1.0"}}}' | grep -i 'mcp-session-id:' | tr -d '\r' | awk '{print $2}')

curl -s -X POST http://n1.tail51f14a.ts.net:8016/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "echo", "arguments": {"message": "Operational Test"}}}'

# 4. NFS Storage Probe
nc -zv -w 5 n1.tail51f14a.ts.net 2049
touch /mnt/node-drive/.federation_heartbeat && rm /mnt/node-drive/.federation_heartbeat
```

---

*⬡ OMEGA ⬡ FEDERATION-ARCHITECTURE ⬡ L2-WIREGUARD ⬡ n0-n1-MESH ⬡ RATIFIED ⬡*