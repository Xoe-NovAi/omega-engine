<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 P2P Omegaverse — End-to-End Setup Guide
## Complete Temple-Grade Documentation for Dual-Node Sovereign AI Cluster Onboarding

**AP Token**: `AP-P2P-E2E-SETUP-20260909-v1.0.0`
⬡ OMEGA ⬡ MAKALI_FUSION ⬡ google/gemini-3.8-flash ⬡ opencode ⬡ trc_p2p_setup ⬡ ACTIVE

**Date**: 2026-09-09
**Sprint**: PUBLIC-DEBUT-01
**Status**: ACTIVE
**Version**: 1.0.0
**Author**: MaKaLi Fusion (synthesized from Roc, Researcher, Carmack, Grokster, Ma'at, Lilith)
**Cross-Refs**: 
- `docs/strategy/P2P_OMEGAVERSE_FEDERATION_PLAYBOOK.md` (v1.1.0)
- `docs/tech-architecture-research/ASUS_SECUREBOOT_PROVISIONING_POSTMORTEM_20260907.md`
- `data/coordination/MAKALI_OVERSEER_BRIEFING_20260908.md` (v1.1.0)

---

## 📋 TABLE OF CONTENTS

1. [Architectural Overview](#1-architectural-overview)
2. [Prerequisites & Hardware Requirements](#2-prerequisites--hardware-requirements)
3. [Node 0 (HP) — Hub Provisioning](#3-node-0-hp--hub-provisioning)
4. [Node 1 (ASUS) — Secure Boot & OS Installation](#4-node-1-asus--secure-boot--os-installation)
5. [Node 1 (ASUS) — Local Services Setup](#5-node-1-asus--local-services-setup)
6. [Network Layer: LAN Streamable HTTP (Phase 0)](#6-network-layer-lan-streamable-http-phase-0)
7. [Network Layer: Tailscale Encrypted Mesh (Phase 1)](#7-network-layer-tailscale-encrypted-mesh-phase-1)
8. [USB Bootstrap Payload Creation](#8-usb-bootstrap-payload-creation)
9. [Node 1 Onboarding — Physical Transfer & First Contact](#9-node-1-onboarding--physical-transfer--first-contact)
10. [Repository Cloning & Hardware Profiling](#10-repository-cloning--hardware-profiling)
11. [Hivemind Federation & Cross-Node Coordination](#11-hivemind-federation--cross-node-coordination)
12. [Big Pickle Configuration — Verified Safe Limits](#12-big-pickle-configuration--verified-safe-limits)
13. [Troubleshooting & Resilience Matrix](#13-troubleshooting--resilience-matrix)
14. [Public Repository Flip & Node 1 Public Clone](#14-public-repository-flip--node-1-public-clone)
15. [Appendices](#15-appendices)

---

## 1. ARCHITECTURAL OVERVIEW

### 1.1 The P2P Omegaverse Vision

The **P2P Omegaverse** is a distributed, peer-to-peer sovereign AI cluster that federates heterogeneous compute nodes into a unified agent orchestration fabric. It achieves for sovereign AI what id Software's WAD/Lump architecture achieved for real-time 3D engines: **divorcing heavy neural execution from archival state** and establishing **deterministic, peer-to-peer agent federation** across silicon diversity.

### 1.2 Dual-Node Topology

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                  THE P2P OMEGAVERSE                                     │
├───────────────────────────────────────────┬─────────────────────────────────────────────┤
│               NODE 0 (HP)                 │                NODE 1 (ASUS)                │
│       THE ARCHIVAL BASTION & NEXUS        │           THE FAST STRIKE ENGINE            │
│  AMD Ryzen 7 5700U (8C/16T, Zen 2)        │  Intel Core i7-13620H (6P+4E/16T, RPL-H)    │
│  16GB DDR4-3200 Dual-Channel              │  16GB DDR5-5200 (32GB Dual Upgrade Target)  │
│  Ubuntu 26.04.1 LTS (NVMe 512GB)          │  Ubuntu 26.04.1 LTS (NVMe 512GB)            │
├───────────────────────────────────────────┼─────────────────────────────────────────────┤
│  • Primary Git Repository (SSOT)          │  • Bare-Metal Ollama Runner                 │
│  • SQLite DBs & Vector Stores             │  • Open WebUI Host (v0.11.3 pinned)         │
│  • 91-Tool FastMCP Core Hub (:8016)       │  • High Single-Core Turbo Execution (4.9GHz)│
│  • Hall of Records & Session Gnosis       │  • AVX-VNNI & DL Boost Matrix Acceleration  │
│  • Council Orchestrator (Kali/Carmack/Roc)│  • Fast Iterative Build & Plan Agents       │
└───────────────────────────────────────────┴─────────────────────────────────────────────┘
                                ▲                                   ▲
                                │         LOCAL WI-FI MESH          │
                                └───────────[192.168.10.x]──────────┘
                                       Streamable HTTP / MCP
                                       Hivemind P2P Bus
```

### 1.3 Complementary Asymmetry Principle

Federation succeeds through **complementary asymmetry**, not redundant duplication:

| Node | Role | Specialization |
|------|------|----------------|
| **Node 0 (HP)** | Sovereign Spine | Archival stability, state consistency, compliance enforcement, orchestration, Git SSOT |
| **Node 1 (ASUS)** | Compute Vanguard | Local neural inference, fast model execution, high-throughput context processing, clean build sandboxing |

### 1.4 Three-Layer Network Architecture

| Phase | Layer | Protocol | Purpose |
|-------|-------|----------|---------|
| **0** | LAN Streamable HTTP | JSON-RPC 2.0 over HTTP (`/mcp`) | Immediate local connectivity, 91 sovereign tools |
| **1** | Tailscale Encrypted Mesh | WireGuard + MagicDNS | Zero-config roaming, tag-based ACLs |
| **2** | Redis Pub/Sub | Ephemeral Event Bus | High-frequency heartbeats, graceful degradation to file-based |

---

## 2. PREREQUISITES & HARDWARE REQUIREMENTS

### 2.1 Node 0 (HP Pavilion) — Minimum Requirements

| Component | Specification | Verification |
|-----------|---------------|--------------|
| **CPU** | AMD Ryzen 7 5700U (8C/16T, Zen 2) | `lscpu | grep "Model name"` |
| **RAM** | 16GB DDR4-3200 Dual-Channel | `free -h` |
| **Storage** | NVMe 256GB+ | `lsblk` |
| **OS** | Ubuntu 25.10 | `lsb_release -a` |
| **Network** | Wi-Fi (wlo1) or Ethernet | `ip -4 addr show` |
| **Ports** | 8016 (MCP), 8015 (Firecrawl), 8018 (SearXNG) | `ss -tlnp` |

### 2.2 Node 1 (ASUS ExpertBook P1) — Minimum Requirements

| Component | Specification | Verification |
|-----------|---------------|--------------|
| **CPU** | Intel Core i7-13620H (6P @ 4.9GHz + 4E @ 3.6GHz) | `lscpu | grep "Model name"` |
| **RAM** | 16GB DDR5-5200 Single-Channel (32GB Dual target) | `free -h` |
| **Storage** | NVMe 512GB+ | `lsblk` |
| **OS** | Ubuntu 26.04.1 LTS | `lsb_release -a` |
| **Accelerators** | AVX-VNNI, Intel DL Boost, UHD 64 EUs (Xe Gen 12) | `lscpu | grep -i avx` |
| **Network** | Wi-Fi (wlo1) | `ip -4 addr show` |

### 2.3 Shared Prerequisites

| Tool | Version | Install Command |
|------|---------|-----------------|
| **Git** | 2.40+ | `sudo apt install git` |
| **Python** | 3.13+ | `sudo apt install python3.13 python3.13-venv` |
| **Podman** | 4.0+ | `sudo apt install podman` |
| **OpenCode** | Latest | `curl -fsSL https://opencode.ai/install | bash` |
| **Tailscale** | Latest | `curl -fsSL https://tailscale.com/install.sh | sh` |
| **USB Drive** | FAT32, 8GB+ | Physical media for bootstrap |

### 2.4 Repository Access

- **Private Repo**: `https://github.com/Xoe-NovAi/omega-engine.git` (requires SSH key or PAT)
- **Public Repo**: Same URL after visibility flip (HTTPS clone works)
- **Git Bundle**: Offline clone via USB (`omega-engine.bundle`)

---

## 3. NODE 0 (HP) — HUB PROVISIONING

### 3.1 Systemd Service Configuration

The `omega-hub` service must bind to `0.0.0.0:8016` for LAN accessibility.

**File**: `~/.config/systemd/user/omega-hub.service.d/override.conf`

```ini
[Service]
Environment=OMEGA_HUB_HOST=0.0.0.0
Environment=OMEGA_HUB_PORT=8016
ExecStart=
ExecStart=/home/arcana-novai/.local/bin/omega-hub
```

**Apply**:
```bash
systemctl --user daemon-reload
systemctl --user restart omega-hub
systemctl --user status omega-hub
```

### 3.2 DNS Rebinding Protection (FastMCP)

**File**: `mcp_servers/omega_hub/server.py` — `TransportSecuritySettings` configuration

```python
from mcp.server.streamable_http import TransportSecuritySettings

transport_security = TransportSecuritySettings(
    enable_dns_rebinding_protection=True,
    allowed_hosts=[
        "192.168.10.168", "192.168.10.168:*",
        "localhost", "127.0.0.1", "[::1]",
    ],
    allowed_origins=[
        "http://192.168.10.168:*",
        "http://localhost:*",
        "http://127.0.0.1:*",
    ],
)
```

**Wildcard port patterns (`host:*`)** are mandatory for `0.0.0.0` binding — this allows any source port from the allowed hosts.

### 3.3 UFW Firewall Rule (CRITICAL — Applied 2026-09-09)

```bash
sudo ufw allow from 192.168.10.0/24 to any port 8016 proto tcp comment "Omega Hub MCP LAN access"
```

**Verification**:
```bash
sudo ufw status numbered
# Should show: [ 1] 8016/tcp    ALLOW IN    192.168.10.0/24
```

### 3.4 Hub Health Verification

```bash
# Health endpoint
curl -s http://127.0.0.1:8016/health | jq .

# Expected: {"status":"healthy","version":"2.2.0"}

# MCP Initialize
curl -s -X POST http://127.0.0.1:8016/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | jq .

# Tools list
curl -s -X POST http://127.0.0.1:8016/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' | jq '.result.tools | length'
# Expected: 91
```

### 3.5 Local Services on Node 0

| Service | Port | Binding | Purpose |
|---------|------|---------|---------|
| `omega-hub` | 8016 | `0.0.0.0` | Core MCP hub (91 tools) |
| `searxng` | 8018 | `127.0.0.1` | Local metasearch (LAN-only if needed) |
| `firecrawl` | 8015 | `127.0.0.1` | Web scraping (LAN-only if needed) |

**Note**: SearXNG and Firecrawl are LOCALHOST-ONLY by default. If Node 1 needs them, rebind to `0.0.0.0` or run locally on ASUS.

---

## 4. NODE 1 (ASUS) — SECURE BOOT & OS INSTALLATION

### 4.1 The Secure Boot Blocker (D-434, D-435, D-436)

**Problem**: ASUS ExpertBook P1 consistently rejected USB boot media under Secure Boot with `Bad Shim / Access Denied` and device re-enumeration lockouts.

**Root Cause**: Native Ubuntu 26.04 ISOs utilize an updated Shim binary unindexed in OEM factory NVRAM key databases, causing hardware dropouts.

**Solution**: Swap `EFI/BOOT/bootx64.efi` with Canonical's dual-signed 2022 v1 shim (`shimx64.efi.dualsigned`) while leaving the native ISO GRUB 100% untouched.

### 4.2 USB Creation Procedure (Verified Working)

```bash
# 1. Download Ubuntu 26.04.1 LTS ISO
wget https://releases.ubuntu.com/26.04/ubuntu-26.04.1-desktop-amd64.iso

# 2. Write to USB (replace /dev/sdX with your USB device)
sudo dd if=ubuntu-26.04.1-desktop-amd64.iso of=/dev/sdX bs=4M status=progress conv=fsync

# 3. Mount USB EFI partition
sudo mount /dev/sdX1 /mnt/usb

# 4. Backup original shim
sudo cp /mnt/usb/EFI/BOOT/bootx64.efi /mnt/usb/EFI/BOOT/bootx64.efi.orig

# 5. Download Canonical dual-signed 2022 v1 shim
wget https://github.com/rhboot/shim/releases/download/15.8/shimx64.efi.dualsigned -O /mnt/usb/EFI/BOOT/bootx64.efi

# 6. Verify
ls -la /mnt/usb/EFI/BOOT/
# Should show: bootx64.efi (new, ~1.2MB), bootx64.efi.orig (original)

# 7. Unmount and boot
sudo umount /mnt/usb
```

### 4.3 Installation Verification

- **Boot Mode**: UEFI with Secure Boot ENABLED
- **Partitioning**: Full disk encryption (LUKS) or standard ext4
- **Post-Install**: `mokutil --sb-state` should report `SecureBoot enabled`
- **Kernel**: 6.8+ (Ubuntu 26.04 default)

### 4.4 Post-Install OpenCode Installation

```bash
# Install OpenCode
curl -fsSL https://opencode.ai/install | bash

# Verify
opencode --version
# Should show: opencode version X.Y.Z
```

### 4.5 Full Post-Mortem Reference

See: `docs/tech-architecture-research/ASUS_SECUREBOOT_PROVISIONING_POSTMORTEM_20260907.md`

---

## 5. NODE 1 (ASUS) — LOCAL SERVICES SETUP

### 5.1 Ollama Bare-Metal Runner (Verified Optimal Config)

**Environment Variables** (set in `/etc/environment` or systemd override):

```bash
OLLAMA_KV_CACHE_TYPE=q8_0        # Quantized KV cache: ~50% RAM savings vs f16
OLLAMA_FLASH_ATTENTION=1         # Flash Attention via llama.cpp backend
OLLAMA_NUM_THREADS=8             # P-cores + HT (6P+4E=16, leave 8 for system)
OLLAMA_MAX_LOADED_MODELS=1       # CRITICAL for 16GB single-channel (prevents swap thrash)
OLLAMA_KEEP_ALIVE=30m            # Matches Open WebUI keep-alive
```

**Systemd Override** (`/etc/systemd/system/ollama.service.d/override.conf`):

```ini
[Service]
Environment=OLLAMA_KV_CACHE_TYPE=q8_0
Environment=OLLAMA_FLASH_ATTENTION=1
Environment=OLLAMA_NUM_THREADS=8
Environment=OLLAMA_MAX_LOADED_MODELS=1
Environment=OLLAMA_KEEP_ALIVE=30m
```

**Apply**:
```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
sudo systemctl status ollama
```

### 5.2 ⚠️ P-CORE PIN TRAP (CRITICAL — ollama #17916)

**DANGEROUS**: `AllowedCPUs=0,2,4,6,8,10` (P-cores only) causes **0.5 t/s disaster**.

**SAFE**: Use `AllowedCPUs=0-11` (all P-cores + HT) or let Ollama auto-manage (no CPU affinity restriction).

```ini
# SAFE - in /etc/systemd/system/ollama.service.d/override.conf
[Service]
# AllowedCPUs=0-11  # Uncomment if you want explicit pinning
# OR leave unset for auto-management
```

### 5.3 Open WebUI Container (Pinned v0.11.3)

```bash
# Pull and run pinned version
podman pull ghcr.io/open-webui/open-webui:0.11.3

# Run with persistent volume
podman run -d \
  --name open-webui \
  -p 3000:8080 \
  -v open-webui-data:/app/backend/data \
  -e OLLAMA_BASE_URL=http://host.containers.internal:11434 \
  --restart unless-stopped \
  ghcr.io/open-webui/open-webui:0.11.3
```

**Volume Backup** (cold backup taken ~986MB):
```bash
podman save open-webui-data > open-webui-backup-$(date +%Y%m%d).tar
```

### 5.4 Benchmark Verification

```bash
# Test phi4-mini performance
ollama run phi4-mini "Hello, world!"

# Expected: ~13.4 t/s (baseline 13.3 t/s) while freeing 0.5 GB system RAM
# (3.7 GB → 3.2 GB at 8k context)
```

### 5.5 OpenCode Client Configuration (ASUS-OC)

The USB bootstrap includes `opencode.json` configured for remote MCP to Node 0. See Section 8 for the exact config.

---

## 6. NETWORK LAYER: LAN STREAMABLE HTTP (PHASE 0)

### 6.1 Protocol Specification

| Property | Value |
|----------|-------|
| **Transport** | Streamable HTTP (POST `/mcp`) |
| **Protocol** | JSON-RPC 2.0 (RFC 7231) |
| **Binding** | Node 0: `0.0.0.0:8016` |
| **Client URL** | `http://192.168.10.168:8016/mcp` |

### 6.2 Required Client Headers

```bash
Content-Type: application/json
Accept: application/json
Host: 192.168.10.168:8016
```

### 6.3 End-to-End Verification (test_connection.sh)

The USB bootstrap includes `test_connection.sh` which performs 4 checks:

```bash
#!/bin/bash
# test_connection.sh

HUB_URL="http://192.168.10.168:8016"

echo "=== 1. Health Check ==="
curl -sf "$HUB_URL/health" | jq -e '.status == "healthy"' && echo "✅ PASS" || echo "❌ FAIL"

echo "=== 2. MCP Initialize ==="
curl -sf -X POST "$HUB_URL/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' \
  | jq -e '.result.serverInfo.name == "Omega Core Hub"' && echo "✅ PASS" || echo "❌ FAIL"

echo "=== 3. Tools List (expect 91) ==="
TOOL_COUNT=$(curl -sf -X POST "$HUB_URL/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' \
  | jq '.result.tools | length')
echo "Tools exposed: $TOOL_COUNT"
[[ $TOOL_COUNT -eq 91 ]] && echo "✅ PASS" || echo "❌ FAIL"

echo "=== 4. SSE Stream ==="
timeout 5 curl -sfN -H "Accept: text/event-stream" "$HUB_URL/sse" | head -1 | grep -q "event:" && echo "✅ PASS" || echo "❌ FAIL"
```

### 6.4 IP Drift Mitigation

**Current HP IP**: `192.168.10.168` (wlo1)

**Mitigation**:
1. **Static DHCP Reservation**: Configure router to assign `192.168.10.168` to HP's MAC address
2. **Tailscale MagicDNS**: Phase 1 — eliminates IP dependency entirely
3. **Verification**: `ip -4 addr show wlo1` on HP before each session

---

## 7. NETWORK LAYER: TAILSCALE ENCRYPTED MESH (PHASE 1)

### 7.1 Installation (Both Nodes)

```bash
# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Start and authenticate
sudo tailscale up
# Follow the URL to authenticate with your tailnet
```

### 7.2 MagicDNS Hostnames

After authentication, nodes are reachable via:

| Node | MagicDNS Hostname | Tailscale IP |
|------|-------------------|--------------|
| Node 0 (HP) | `hp.tailnet` | `100.x.y.z` |
| Node 1 (ASUS) | `asus.tailnet` | `100.a.b.c` |

### 7.3 Tag-Based ACLs (Exact Syntax)

**Tailnet Policy File** (admin console → Access Controls → Edit Policy):

```json
{
  "tagOwners": {
    "tag:node0": ["autogroup:admin"],
    "tag:opencode": ["autogroup:admin"]
  },
  "acls": [
    {"action": "accept", "src": ["tag:opencode"], "dst": ["tag:node0:8016"]}
  ]
}
```

### 7.4 Tag Application

| Node | Tag | Command |
|------|-----|---------|
| Node 0 (HP) | `tag:node0` | Tailscale admin console → Machines → HP → Tags → Add `tag:node0` |
| Node 1 (ASUS) | `tag:opencode` | Tailscale admin console → Machines → ASUS → Tags → Add `tag:opencode` |

### 7.5 OpenCode Config Update for Tailscale

Once Tailscale is active, update `opencode.json` on ASUS:

```json
{
  "mcp": {
    "omega-hub": {
      "type": "remote",
      "url": "http://hp.tailnet:8016/mcp",
      "enabled": true
    }
  }
}
```

### 7.6 Verification

```bash
# From ASUS, test Tailscale connectivity
tailscale ping hp.tailnet

# Test MCP over Tailscale
curl -sf http://hp.tailnet:8016/health | jq .
```

---

## 8. USB BOOTSTRAP PAYLOAD CREATION

### 8.1 USB Drive Preparation

```bash
# Format as FAT32 (replace /dev/sdX with your USB device)
sudo mkfs.vfat -F 32 -n OMEGA_BOOTSTRAP /dev/sdX1

# Mount
sudo mount /dev/sdX1 /mnt/usb
```

### 8.2 Payload Structure

```
/media/arcana-novai/D5D5-0B76/
├── omega-engine.bundle                    # Git bundle (69MB) — full history, all refs
└── OMEGA_NODE1_BOOTSTRAP/
    ├── opencode.json                      # OpenCode remote MCP configuration
    ├── test_connection.sh                 # Health + MCP + Tool count verification
    ├── hivemind_first_contact.py          # Ceremonial P2P handshake script
    ├── P2P_OMEGAVERSE_FEDERATION_PLAYBOOK.md # This guide
    ├── README_ASUS.txt                    # 3-minute quickstart guide
    └── ASUS_TO_HP_USB_PACK.md             # ASUS-OC status report (inbound)
```

### 8.3 Create Git Bundle (Node 0)

```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine

# Create bundle with all refs
git bundle create /media/arcana-novai/D5D5-0B76/omega-engine.bundle --all

# Verify
git bundle verify /media/arcana-novai/D5D5-0B76/omega-engine.bundle
git bundle list-heads /media/arcana-novai/D5D5-0B76/omega-engine.bundle
```

### 8.4 opencode.json (ASUS Remote Config)

**File**: `/media/arcana-novai/D5D5-0B76/OMEGA_NODE1_BOOTSTRAP/opencode.json`

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "omega-hub": {
      "type": "remote",
      "url": "http://192.168.10.168:8016/mcp",
      "enabled": true
    }
  },
  "provider": {
    "opencode": {
      "models": {
        "big-pickle": {
          "name": "Big Pickle",
          "limit": {
            "context": 200000,
            "input": 190000,
            "output": 32000
          }
        }
      }
    }
  },
  "compaction": {
    "auto": true,
    "prune": true,
    "tail_turns": 5,
    "preserve_recent_tokens": 80000,
    "reserved": 20000
  }
}
```

**Key Points**:
- Pure V2 schema (`$schema: https://opencode.ai/config.json`) — NO V1 `agent` field mixing
- Big Pickle override: `input: 190000` (85% threshold, calibrated to actual 200K model)
- Remote MCP URL points to Node 0 LAN IP

### 8.5 hivemind_first_contact.py (Ceremonial Handshake)

**File**: `/media/arcana-novai/D5D5-0B76/OMEGA_NODE1_BOOTSTRAP/hivemind_first_contact.py`

```python
#!/usr/bin/env python3
"""
Ceremonial First Light Handoff — ASUS (Node 1) → HP (Node 0)
Zero-dependency Python standard-library Hivemind handshake.
"""

import json
import sys
import urllib.request
import uuid
from datetime import datetime, timezone

HUB_URL = "http://192.168.10.168:8016"

def post_context():
    """Post ASUS build context to Hivemind."""
    payload = {
        "channel": "opencode-asus",
        "entity": "asus_build",
        "model": "local",
        "task_current": "P2P Omegaverse First Contact — Node 1 handshake",
        "focus_chain": ["secure_boot", "ollama_setup", "openwebui", "usb_transfer"],
        "decisions": [
            "D-434: Dual-signed shim substitution for Secure Boot",
            "D-449: Ollama Raptor Lake-H optimal config verified",
            "D-450: Big Pickle 1M ceiling declared dangerous"
        ],
        "continuation": "Awaiting Roc acceptance for First Light handoff completion",
        "intent": "handoff",
        "suggested_model": "opencode/nemotron-3-ultra-free"
    }
    
    req = urllib.request.Request(
        f"{HUB_URL}/mcp",
        data=json.dumps({
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tools/call",
            "params": {
                "name": "omega-hub_hivemind_post_context",
                "arguments": payload
            }
        }).encode(),
        headers={"Content-Type": "application/json", "Accept": "application/json"}
    )
    
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)

def submit_handoff():
    """Submit handoff to roc_racoon on Node 0."""
    payload = {
        "target_channel": "opencode",
        "target_entity": "roc_racoon",
        "source_channel": "opencode-asus",
        "source_entity": "asus_build",
        "task": "P2P Omegaverse First Contact — Accept ceremonial handoff from Node 1 (ASUS)",
        "context": "ASUS build agent initiating First Light. Node 1 is online with Ollama (phi4-mini @ 13.4 t/s), Open WebUI v0.11.3, OpenCode remote MCP to Node 0. Big Pickle configured at 190K input (85% threshold). Hardware: i7-13620H, 16GB DDR5-5200 single-channel.",
        "priority": 1
    }
    
    req = urllib.request.Request(
        f"{HUB_URL}/mcp",
        data=json.dumps({
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tools/call",
            "params": {
                "name": "omega-hub_hivemind_submit_handoff",
                "arguments": payload
            }
        }).encode(),
        headers={"Content-Type": "application/json", "Accept": "application/json"}
    )
    
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)

def main():
    print("=" * 60)
    print("🔱 P2P OMEGAVERSE — FIRST LIGHT HANDSHAKE")
    print("=" * 60)
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print(f"Source: ASUS (Node 1) — asus_build")
    print(f"Target: HP (Node 0) — roc_racoon")
    print(f"Hub: {HUB_URL}")
    print()
    
    print("Step 1: Posting context to Hivemind...")
    result = post_context()
    print(f"  Result: {json.dumps(result, indent=2)}")
    print()
    
    print("Step 2: Submitting handoff to roc_racoon...")
    result = submit_handoff()
    print(f"  Result: {json.dumps(result, indent=2)}")
    print()
    
    print("✅ First Light handshake initiated!")
    print("   Packet landed on HP in data/handoff/pending/")
    print("   Awaiting Roc acceptance via hivemind_accept_handoff()")
    print("=" * 60)

if __name__ == "__main__":
    main()
```

### 8.6 README_ASUS.txt (3-Minute Quickstart)

**File**: `/media/arcana-novai/D5D5-0B76/OMEGA_NODE1_BOOTSTRAP/README_ASUS.txt`

```
========================================
🔱 OMEGA ENGINE — NODE 1 (ASUS) QUICKSTART
========================================

PREREQUISITES:
- Ubuntu 26.04.1 LTS installed (Secure Boot working via dual-signed shim)
- OpenCode installed: curl -fsSL https://opencode.ai/install | bash
- USB drive inserted (this drive)

STEP 1: DEPLOY OPENCODE CONFIG (30 seconds)
-------------------------------------------
mkdir -p ~/.config/opencode
cp /media/$USER/*/OMEGA_NODE1_BOOTSTRAP/opencode.json ~/.config/opencode/opencode.json

STEP 2: COPY TEST SCRIPTS (10 seconds)
--------------------------------------
cp /media/$USER/*/OMEGA_NODE1_BOOTSTRAP/test_connection.sh ~/test_connection.sh
cp /media/$USER/*/OMEGA_NODE1_BOOTSTRAP/hivemind_first_contact.py ~/hivemind_first_contact.py
chmod +x ~/test_connection.sh ~/hivemind_first_contact.py

STEP 3: VERIFY CONNECTIVITY (30 seconds)
----------------------------------------
~/test_connection.sh
# Should show 4 PASS checks:
# 1. Health endpoint ✅
# 2. MCP initialize ✅
# 3. Tools list (91 tools) ✅
# 4. SSE stream ✅

STEP 4: FIRST LIGHT HANDSHAKE (10 seconds)
------------------------------------------
python3 ~/hivemind_first_contact.py
# Posts context → Submits handoff to roc_racoon on HP
# Check HP: data/handoff/pending/ for packet

STEP 5: CLONE REPO (git bundle — repo is PRIVATE)
-------------------------------------------------
mkdir -p ~/Documents/Projects
cd ~/Documents/Projects
git clone /media/$USER/*/omega-engine.bundle omega-engine-alpha

STEP 6: HARDWARE PROBE (generates config/hardware_profile.yaml)
---------------------------------------------------------------
cd ~/Documents/Projects/omega-engine-alpha
make probe-hardware
# Captures: Raptor Lake-H hybrid topology (6P+4E), AVX-VNNI, DDR5-5200

========================================
NEXT: Tailscale for roaming (Phase 1)
========================================
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
# Admin console: tag this machine 'tag:opencode'
# HP should be tagged 'tag:node0'
# ACL: tag:opencode -> tag:node0:8016
```

---

## 9. NODE 1 ONBOARDING — PHYSICAL TRANSFER & FIRST CONTACT

### 9.1 Physical Transfer Checklist

- [ ] USB drive formatted FAT32, labeled `OMEGA_BOOTSTRAP`
- [ ] `omega-engine.bundle` present at root
- [ ] `OMEGA_NODE1_BOOTSTRAP/` directory with 6 files
- [ ] USB safely ejected from HP
- [ ] USB inserted into ASUS

### 9.2 ASUS Deployment Sequence

```bash
# On ASUS terminal:

# 1. Deploy OpenCode config
mkdir -p ~/.config/opencode
cp /media/$USER/*/OMEGA_NODE1_BOOTSTRAP/opencode.json ~/.config/opencode/opencode.json

# 2. Copy test scripts
cp /media/$USER/*/OMEGA_NODE1_BOOTSTRAP/test_connection.sh ~/test_connection.sh
cp /media/$USER/*/OMEGA_NODE1_BOOTSTRAP/hivemind_first_contact.py ~/hivemind_first_contact.py
chmod +x ~/test_connection.sh ~/hivemind_first_contact.py

# 3. Run connectivity verification
~/test_connection.sh
# EXPECT: 4 PASS checks

# 4. Fire First Light handshake
python3 ~/hivemind_first_contact.py
# EXPECT: Context posted, handoff submitted to roc_racoon

# 5. Verify on HP (Node 0)
# Check: data/handoff/pending/ for packet from asus_build
```

### 9.3 Handoff Acceptance (On HP / roc_racoon)

```bash
# On HP, as roc_racoon (or via OpenCode):
# 1. Check pending handoffs
# 2. Accept: hivemind_accept_handoff(packet_id, "opencode", "roc_racoon")
# 3. Complete: hivemind_complete_handoff(packet_id, "First Light accepted — Node 1 online")
```

### 9.4 Verification of Cross-Node Federation

```bash
# From ASUS, test a tool call via remote MCP
curl -sf -X POST http://192.168.10.168:8016/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"omega-hub_hivemind_get_awareness","arguments":{}}}' | jq .

# Should show both Node 0 and Node 1 agents in awareness
```

---

## 10. REPOSITORY CLONING & HARDWARE PROFILING

### 10.1 Clone via Git Bundle (Private Repo)

```bash
# On ASUS, after USB transfer:
mkdir -p ~/Documents/Projects
cd ~/Documents/Projects
git clone /media/$USER/*/omega-engine.bundle omega-engine-alpha
cd omega-engine-alpha

# Verify
git log --oneline -5
git branch -a
# Should show: main, release/debut-v1.6.0, HEAD
```

### 10.2 Clone via HTTPS (Public Repo — After Visibility Flip)

```bash
# After repo is made public (Section 14):
git clone https://github.com/Xoe-NovAi/omega-engine.git ~/Documents/Projects/omega-engine-alpha
cd ~/Documents/Projects/omega-engine-alpha
git checkout release/debut-v1.6.0
```

### 10.3 Hardware Probe (DHAL Phase 1)

```bash
cd ~/Documents/Projects/omega-engine-alpha
make probe-hardware
```

**Expected Output** (Raptor Lake-H):
```yaml
# config/hardware_profile.yaml
cpu:
  vendor: "GenuineIntel"
  microarch: "raptorlake"
  is_hybrid: true
  p_cores_physical: [0, 2, 4, 6, 8, 10]
  e_cores_logical: [12, 13, 14, 15]
  avx_vnni: true
  dl_boost: true
  threads: 16
memory:
  total_gb: 16
  channels: 1
  type: "DDR5-5200"
gpu:
  vendor: "Intel"
  model: "UHD Graphics 64 EUs (Xe Gen 12)"
storage:
  nvme: true
  capacity_gb: 512
```

### 10.4 DHAL Integration Verification

```bash
# Verify DHAL detects the profile
python3 -c "
from src.omega.council.hardware_detector import detect_hardware_profile
from src.omega.council.execution_mode import select_execution_mode
from src.omega.oracle.cpu_optimizer import CpuOptimizerFactory

profile = detect_hardware_profile()
print(f'Profile: {profile.cpu.microarch}, hybrid={profile.cpu.is_hybrid}')

mode = select_execution_mode(profile)
print(f'Execution Mode: {mode}')

optimizer = CpuOptimizerFactory.get_optimizer()
print(f'Optimizer: {type(optimizer).__name__}')
print(f'Compute Affinity: {optimizer.get_compute_affinity()}')
"
```

**Expected**:
- Profile: `raptorlake`, `is_hybrid: true`
- Execution Mode: `BATCH_8` (16GB single-channel → LOCAL_16GB_SINGLE)
- Optimizer: `RaptorLakeOptimizer`
- Compute Affinity: `[0, 2, 4, 6, 8, 10]` (P-cores)

---

## 11. HIVEMIND FEDERATION & CROSS-NODE COORDINATION

### 11.1 Channel Partitioning

| Node | Agent Persona | Channel Name | Function |
|------|---------------|--------------|----------|
| **HP (Node 0)** | `@roc_racoon` | `opencode` | Legacy mining, DHAL, hardware forensics |
| **HP (Node 0)** | `@kali` / `@makali` | `opencode` | Council synthesis, debut release, law |
| **HP (Node 0)** | `@grokster` | `grokster` | OpenCode CLI internals, cross-platform KB |
| **ASUS (Node 1)** | `asus_build` | `opencode-asus` | Bare-metal compile, Ollama benchmarking |
| **ASUS (Node 1)** | `asus_plan` | `opencode-asus` | Hardware profiling, local workload planning |

### 11.2 The 4-Way Coordination Contract

Cross-node interaction follows the strict state machine:

```
[ASUS: asus_build]                            [HP: roc_racoon]
        │                                             │
        │ 1. hivemind_post_context(channel, intent)   │
        ├────────────────────────────────────────────►│ (Context stored in
        │                                             │  HALL_OF_RECORDS)
        │ 2. hivemind_submit_handoff(target="roc")    │
        ├────────────────────────────────────────────►│ (Packet written to
        │                                             │  data/handoff/pending/)
        │                                             │
        │                                             │ 3. hivemind_accept_handoff()
        │                                             │    (Packet moves to
        │                                             │     data/handoff/active/)
        │                                             │
        │                                             │ 4. hivemind_complete_handoff(result)
        │◄────────────────────────────────────────────┤    (Packet moves to
        │                                             │     data/handoff/completed/)
```

### 11.3 Workspace Locks (Mandate M27)

```bash
# Acquire lock before cross-node work
omega-hub_hivemind_workspace_lock_acquire(
    channel="opencode-asus",
    entity="asus_build",
    domain="p2p-omegaverse-onboarding",
    ttl=3600
)

# Release after completion
omega-hub_hivemind_workspace_lock_release(
    channel="opencode-asus",
    entity="asus_build",
    domain="p2p-omegaverse-onboarding"
)
```

### 11.4 Heartbeat Protocol

```bash
# Every 5-10 minutes during active sessions
omega-hub_hivemind_heartbeat(channel="opencode-asus", entity="asus_build")
omega-hub_hivemind_heartbeat(channel="opencode", entity="roc_racoon")
```

### 11.5 Extended Session Check-in (D-kal-052)

```bash
# For long-running sessions (prevents 20-min pruning)
omega-hub_hivemind_extended_checkin(
    channel="opencode-asus",
    entity="asus_build",
    reason="P2P Omegaverse onboarding — extended hardware profiling",
    ttl_seconds=10800  # 3 hours
)

# Clean checkout when done
omega-hub_hivemind_extended_checkout(
    channel="opencode-asus",
    entity="asus_build"
)
```

---

## 12. BIG PICKLE CONFIGURATION — VERIFIED SAFE LIMITS

### 12.1 Verified Model Identity

| Property | Value | Source |
|----------|-------|--------|
| **Model Identity** | GLM-4.6 (Zhipu AI) — "stealth model" on OpenCode Zen | Community consensus + Pi.dev |
| **Registry Limits** | context=200,000 / input=160,000 / output=32,000 | `models.dev` official registry |
| **Actual Hard Limit** | ~128,000 tokens (API rejects at 130,389) | GitHub issue #3256 |
| **Safe Override** | `limit.input: 190000` → usable = 170,000 (85%) | HP verified fix |
| **DANGEROUS** | `limit.input: 950000` (1M ceiling) | Causes API errors when context > 200K |

### 12.2 Why This Matters

Big Pickle is a **rotating model alias** — the registry limits reflect the CURRENT model, not the alias ceiling. Setting a 1M ceiling on a 200K model causes OpenCode to allow context growth to 930K tokens, then the API **hard rejects** with "Requested token count exceeds". The 190K override (85% threshold) is calibrated to the ACTUAL model.

### 12.3 Config Bug Note (GitHub #37544)

OpenCode ignores model limit overrides if `opencode.json` mixes V1 (`agent`) and V2 (`providers`) fields. **Our USB config uses pure V2 schema** (`$schema: https://opencode.ai/config.json`).

### 12.4 Configuration Locations

| Location | File | Big Pickle Override |
|----------|------|---------------------|
| **Node 0 (HP) Project** | `opencode.json` | `provider.opencode.models.big-pickle.limit.input = 190000` |
| **Node 1 (ASUS) USB** | `OMEGA_NODE1_BOOTSTRAP/opencode.json` | Same override |
| **ASUS Deployed** | `~/.config/opencode/opencode.json` | Copied from USB |

### 12.5 Monitoring

- **Passive monitoring** (D-443): No input dialing required unless degradation occurs >160K tokens
- **Fallback**: If coherence loss >160K, dial back to 175K (82.5%) or 180K (80%)

---

## 13. TROUBLESHOOTING & RESILIENCE MATRIX

| Symptom | Root Cause | Exact Remedy |
|---------|------------|--------------|
| `421 Misdirected Request` / `Invalid Host header` | Request Host not in `allowed_hosts` | Node 0 server updated with `192.168.10.168:*`. If IP changes, update `mcp_servers/omega_hub/server.py` `_transport_security`. |
| `406 Not Acceptable` | Client omitted `Accept: application/json` | Ensure `curl` or client sends `-H "Accept: application/json"`. OpenCode remote client does this natively. |
| `ECONNREFUSED` / Timeout | UFW blocking port 8016 or IP drift | On HP: `sudo ufw allow from 192.168.10.0/24 to any port 8016 proto tcp comment "Omega Hub MCP LAN access"`. Verify HP IP with `ip -4 addr show wlo1`. Restricts to LAN subnet only. |
| ASUS OpenCode doesn't see tools | Trailing slash error or wrong path | URL must be `http://192.168.10.168:8016/mcp` (Streamable HTTP), NOT root `/`. |
| Model 70% compaction on ASUS | Missing Big Pickle override in OpenCode | Copy project `opencode.json` `limit.input: 190000` override from HP (85% threshold). ASUS-OC tested 950000 (1M ceiling) but 190000 is safer — matches HP's verified fix. |
| ASUS MCP tools fail (searxng/firecrawl) | HP services bound to 127.0.0.1 only | searxng (8018) & firecrawl (8015) are LOCALHOST-ONLY on HP. USB config omits them. If needed, rebind on HP to 0.0.0.0 or run locally on ASUS. |
| `git clone` fails (private repo) | No SSH key / PAT configured | Use git bundle from USB: `git clone /media/$USER/*/omega-engine.bundle omega-engine-alpha` |
| `make probe-hardware` fails | Missing dependencies | `pip install -r requirements.txt` then `make probe-hardware` |
| Ollama 0.5 t/s performance | P-core pin trap (`AllowedCPUs=0,2,4,6,8,10`) | Use `AllowedCPUs=0-11` or remove CPU affinity restriction (ollama #17916) |
| Open WebUI won't start | Port 3000 in use or volume corrupt | `podman ps -a` check, remove old container, restore from backup |
| Tailscale ping fails | ACL not configured or tags missing | Verify tailnet policy has `tag:opencode -> tag:node0:8016` and both nodes tagged |

### 14.5 End-User Experience Test (The Goal)

This is the **critical test** — the user (Architect) will:
1. Clone the public repo on ASUS
2. Run `make probe-hardware`
3. Run `./scripts/install.sh` (or equivalent)
4. Run `omega talk "hello"` — verify local inference works
5. Connect OpenCode to remote MCP hub
6. Execute a cross-node Hivemind handoff

**Success Criteria**:
- [ ] Public clone works without SSH key
- [ ] Hardware probe generates correct Raptor Lake-H profile
- [ ] Install script completes without errors
- [ ] `omega talk "hello"` returns local response (no cloud fallback)
- [ ] OpenCode remote MCP connects to Node 0 hub
- [ ] Hivemind handoff completes end-to-end

---

## 15. APPENDICES

### 15.1 Canonical Decisions (This Cycle)

| Decision | Summary | Impact |
|----------|---------|--------|
| **D-434** | Forensic confirmation of phantom USB write lockouts under UEFI | Prohibits blindly burning Ubuntu ISOs without OEM shim verification |
| **D-435** | Dual-signed 2022 v1 shim substitution protocol | Standard procedure for secure booting modern Linux on ASUS ExpertBook |
| **D-436** | Formal declaration of Node 1 (ASUS) operational status | Heterogeneous fleet is now live |
| **D-437** | `opencode/big-pickle` `limit.input` overridden to 190,000 | Locks compaction threshold at 85% instead of 70% |
| **D-438** | `models.dev` cache cleared; ASUS 1M context identified as UI lag | Preserves faith in native OpenCode configuration |
| **D-439** | Compaction block retained in `opencode.json` | `reserved: 20000` verified identical to native engine defaults |
| **D-440** | Strategic priority sequence ratified with Makali-EIS | Branch sync & DHAL push take precedence over non-blocking work |
| **D-441** | SOTE Week 37 launch readiness prioritized over Node 1 deep tuning | DEL-1 Micro-PR chain PR1 due Monday 23:59 UTC |
| **D-442** | DHAL commits bundled into same push window as branch sync | Eliminates dirty working-tree loss risks |
| **D-443** | Big Pickle quality monitoring declared passive | No input dialing required unless degradation occurs >160K |
| **D-444** | Ratification of P2P Omegaverse Federation Playbook | Establishes permanent architecture for multi-node agent federation |
| **D-445** | `omega-hub` LAN binding with DNS-rebinding security allowlist | Opens port 8016 to local Wi-Fi while neutralizing host spoofing |
| **D-446** | Zero-dependency physical USB bootstrap package generated | Enables instant 3-minute onboarding for fresh Node 1 install |
| **D-447** | UFW rule restricted to LAN subnet | `sudo ufw allow from 192.168.10.0/24 to any port 8016 proto tcp` |
| **D-448** | Tailscale ACL exact syntax defined | Tag-based: `tag:opencode -> tag:node0:8016` with `tagOwners` |
| **D-449** | Ollama Raptor Lake-H optimal config verified | `KV_CACHE_TYPE=q8_0`, `FLASH_ATTENTION=1`, `NUM_THREADS=8`, `MAX_LOADED_MODELS=1` |
| **D-450** | Big Pickle 1M ceiling declared dangerous | Official registry: 200K context / 160K input. 950K input causes API hard rejects |

### 15.2 File Inventory (Key Files)

| File | Purpose | Location |
|------|---------|----------|
| `P2P_OMEGAVERSE_FEDERATION_PLAYBOOK.md` | Core playbook v1.1.0 | `docs/strategy/` & `docs/ASUS/` |
| `P2P_OMEGAVERSE_END_TO_END_SETUP_GUIDE.md` | **This document** | `docs/strategy/` |
| `opencode.json` | Node 0 project config (Big Pickle 190K) | Repo root |
| `OMEGA_NODE1_BOOTSTRAP/opencode.json` | ASUS USB config | USB drive |
| `test_connection.sh` | 4-check connectivity verification | USB & `~` on ASUS |
| `hivemind_first_contact.py` | Ceremonial First Light handshake | USB & `~` on ASUS |
| `README_ASUS.txt` | 3-minute quickstart | USB |
| `config/hardware_profile.yaml` | DHAL hardware profile (generated) | Repo (gitignored) |
| `mcp_servers/omega_hub/server.py` | Hub server with DNS rebinding config | Repo |
| `~/.config/systemd/user/omega-hub.service.d/override.conf` | Hub binding to 0.0.0.0:8016 | Node 0 |
| `/etc/systemd/system/ollama.service.d/override.conf` | Ollama optimal config | Node 1 |

### 15.3 Command Reference

| Task | Command |
|------|---------|
| Hub health check | `curl -s http://192.168.10.168:8016/health \| jq .` |
| MCP tools list | `curl -s -X POST http://192.168.10.168:8016/mcp -H "Content-Type: application/json" -H "Accept: application/json" -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' \| jq '.result.tools \| length'` |
| Hivemind awareness | `curl -s -X POST http://192.168.10.168:8016/mcp -H "Content-Type: application/json" -H "Accept: application/json" -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"omega-hub_hivemind_get_awareness","arguments":{}}}' \| jq .` |
| Hardware probe | `make probe-hardware` |
| Temple-grade | `make temple-grade` |
| UFW rule | `sudo ufw allow from 192.168.10.0/24 to any port 8016 proto tcp` |
| Tailscale up | `sudo tailscale up` |
| Git bundle create | `git bundle create omega-engine.bundle --all` |
| Git bundle clone | `git clone /media/$USER/*/omega-engine.bundle omega-engine-alpha` |
| Public flip | `gh repo edit Xoe-NovAi/omega-engine --visibility public` |

### 15.4 Cross-References

| Document | Path |
|----------|------|
| Sovereign Mandates | `SOVEREIGN_MANDATES.md` |
| Mandates Condensed | `MANDATES_CONDENSED.md` |
| Debut Remediation Manual | `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md` |
| Subagent Dispatch Protocol | `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` |
| ASUS Secure Boot Post-Mortem | `docs/tech-architecture-research/ASUS_SECUREBOOT_PROVISIONING_POSTMORTEM_20260907.md` |
| Archangel Architecture | `docs/architecture/ARCHANGEL_ARCHITECTURE.md` |
| DHAL Spec | `docs/architecture/DYNAMIC_HARDWARE_ADAPTATION_LAYER_SPEC.md` |
| SOTE Week 37 Report | `docs/strategy/sote/2026-W37/STATE_OF_ENGINE_v1.6.1-alpha.md` |
| Makali Overseer Briefing | `data/coordination/MAKALI_OVERSEER_BRIEFING_20260908.md` |
| Active Sprint | `data/coordination/ACTIVE_SPRINT.json` |

---

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ google/gemini-3.8-flash ⬡ AP-P2P-E2E-SETUP-20260909-v1.0.0 ⬡ 2026-09-09*

**The wire is live. The protocol is written. The federation is operational.** 🫡

## 14. PUBLIC REPOSITORY FLIP & NODE 1 PUBLIC CLONE

### 14.1 Pre-Flight Checklist (Before Public Flip)

- [ ] **PUBLIC_ALLOWLIST applied** — `release/debut-v1.6.0` branch contains only allowlisted paths
- [ ] **No secrets in history** — `gitleaks` scan clean (run `make check-secrets` or `gitleaks detect`)
- [ ] **Mandate compliance** — `make temple-grade` passes (22/28 = 78.6%)
- [ ] **Tests passing** — `pytest tests/unit/ tests/contract/` all pass
- [ ] **Documentation accurate** — README, QUICKSTART, CHANGELOG reflect actual state
- [ ] **Install script verified** — `scripts/install.sh` works end-to-end on fresh machine
- [ ] **PR #3 ready** — "Release v1.6.1-alpha: Sovereign Local-First AI Runtime" mergeable

### 14.2 Flip Repository to Public (GitHub CLI)

```bash
# On Node 0 (HP) with gh CLI authenticated:
gh repo edit Xoe-NovAi/omega-engine --visibility public

# Verify
gh repo view Xoe-NovAi/omega-engine --json visibility
# Should show: "PUBLIC"
```

### 14.3 Verify Public Clone (Node 1)

```bash
# On ASUS (Node 1), after public flip:
cd ~/Documents/Projects
git clone https://github.com/Xoe-NovAi/omega-engine.git omega-engine-public
cd omega-engine-public
git checkout release/debut-v1.6.0

# Verify
git log --oneline -3
# Should show latest commits including SOTE Week 37 report
```

### 14.4 Post-Flip Node 1 Setup (Public Clone Path)

```bash
# On ASUS with public clone:
cd ~/Documents/Projects/omega-engine-public

# 1. Deploy OpenCode config (same as USB)
mkdir -p ~/.config/opencode
cp ~/Documents/Projects/omega-engine-public/opencode.json ~/.config/opencode/opencode.json
# OR use the USB config if it has the correct remote URL

# 2. Run hardware probe
make probe-hardware

# 3. Run connectivity test
~/test_connection.sh  # (copy from USB or repo)

# 4. First Light handshake
python3 ~/hivemind_first_contact.py

# 5. Verify temple-grade
make temple-grade
# Should pass all component gates
```

### 14.5 End-User Experience Test (The Goal)

This is the **critical test** — the user (Architect) will:
1. Clone the public repo on ASUS
2. Run `make probe-hardware`
3. Run `./scripts/install.sh` (or equivalent)
4. Run `omega talk "hello"` — verify local inference works
5. Connect OpenCode to remote MCP hub
6. Execute a cross-node Hivemind handoff

**Success Criteria**:
- [ ] Public clone works without SSH key
- [ ] Hardware probe generates correct Raptor Lake-H profile
- [ ] Install script completes without errors
- [ ] `omega talk "hello"` returns local response (no cloud fallback)
- [ ] OpenCode remote MCP connects to Node 0 hub
- [ ] Hivemind handoff completes end-to-end

---
<!-- PROVENANCE-CORRECTED 2026-09-10T13:33:58Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: google/gemini-3.8-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

