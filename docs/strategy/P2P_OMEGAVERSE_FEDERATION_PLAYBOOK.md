---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "playbook"
document_id: "P2P-OMEGAVERSE-FEDERATION-PLAYBOOK-v1.0.0"
title: "Omega Engine — P2P Omegaverse Federation Playbook & Team Guide"
status: "ACTIVE"
version: "1.1.0"
date: "2026-09-09"
sprint: "PUBLIC-DEBUT-01"
author: "roc_racoon (Sovereign Miner & Ideas Guy)"
consultants: ["gemini-3.8-flash", "nemotron-3-ultra", "john_carmack", "makali"]
tags: [
  "p2p",
  "federation",
  "omegaverse",
  "node-0-hp",
  "node-1-asus",
  "mcp",
  "streamable-http",
  "hivemind",
  "dhal",
  "carmack-architecture"
]
priority: "P0"
depends_on: [
  "D-434", "D-435", "D-436", "D-437", "D-438", "D-439", "D-440", "D-441"
]
cross_references:
  - "SOVEREIGN_MANDATES.md"
  - "MANDATES_CONDENSED.md"
  - "docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md"
  - "docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md"
  - "docs/tech-architecture-research/ASUS_SECUREBOOT_PROVISIONING_POSTMORTEM_20260907.md"
  - "data/coordination/ACTIVE_SPRINT.json"
---

# 🔱 P2P OMEGAVERSE FEDERATION PLAYBOOK
## Dual-Node Sovereign AI Cluster: HP (Node 0) ↔ ASUS (Node 1)

> *"The speed of development is determined by how fast you can turn an idea into a running test. Don't build a complex protocol before you have a packet moving. A raw HTTP POST is the ping; a Hivemind context post is the handshake."*  
> — **John Carmack Heritage Doctrine (id Software 1993 → Omega Engine 2026)**

---

## 🏛️ 1. ARCHITECTURAL PREAMBLE & HERITAGE

Three decades ago, id Software solved distributed real-time computing by divorcing game assets from engine binaries (the **WAD / Lump** architecture) and establishing deterministic client-server packet contracts. Today, the **Omega Engine** achieves the same milestone in sovereign AI computing: divorcing heavy neural execution from archival state and establishing distributed, peer-to-peer agent federation across heterogeneous silicon.

This playbook governs the birth of the **P2P Omegaverse**: the federation of **Node 0 (HP Pavilion)** and **Node 1 (ASUS ExpertBook P1)** into a unified, resilient multi-node cluster.

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

---

## 🗺️ 2. FLEET TOPOGRAPHY & SILICON SPECIALIZATION

Federation succeeds through **complementary asymmetry**, not redundant duplication. Each machine plays to its silicon strengths:

### 2.1 Node 0: HP Pavilion (The Sovereign Spine)
* **Processor**: AMD Ryzen 7 5700U (8 cores, 16 threads, Zen 2 architecture).
* **Memory**: 16 GB Dual-Channel DDR4-3200 (symmetrical memory bus).
* **Strategic Role**: Archival stability, state consistency, compliance enforcement, and orchestration.
* **Persistent Services**:
  * `omega-hub.service`: FastMCP multi-domain core hub on `0.0.0.0:8016` exposing 91 sovereign tools.
  * Git SSOT: Main repository branch `release/debut-v1.6.0` and `main`.
  * Observability: SQLite `metrics.db`, PSI monitors, crash logs, and Hall of Records cold storage.

### 2.2 Node 1: ASUS ExpertBook P1 (The Compute Vanguard)
* **Processor**: Intel Core i7-13620H (6 Performance Cores @ 4.9 GHz + 4 Efficient Cores @ 3.6 GHz = 16 threads, Raptor Lake-H).
* **Memory**: 16 GB Single-Channel DDR5-5200 (upgradable to 32 GB Dual-Channel).
* **Hardware Accelerators**: AVX-VNNI (AVX2 VNNI), Intel DL Boost, Intel UHD Graphics 64 EUs (Xe Gen 12).
* **Strategic Role**: Local neural inference, fast model execution, high-throughput context processing, and clean build sandboxing.
* **Local Services**:
  * Ollama bare-metal runner (verified optimal config):
    ```bash
    OLLAMA_KV_CACHE_TYPE=q8_0
    OLLAMA_FLASH_ATTENTION=1
    OLLAMA_NUM_THREADS=8
    OLLAMA_MAX_LOADED_MODELS=1
    OLLAMA_KEEP_ALIVE=30m
    ```
    * `q8_0` KV cache: ~50% RAM savings vs f16
    * Flash Attention: enabled via llama.cpp backend
    * 8 threads: P-cores + HT (6P+4E=16, leave 8 for system)
    * MAX_LOADED_MODELS=1: Critical for 16GB single-channel (prevents swap thrash)
    * ⚠️ **P-CORE PIN TRAP**: `AllowedCPUs=0,2,4,6,8,10` causes 0.5 t/s disaster (ollama #17916). Use `AllowedCPUs=0-11` or let Ollama auto-manage.
  * Open WebUI v0.11.3 container pinned (v0.11.4 has regression) with persistent volume preservation (~986MB cold backup).
  * OpenCode client (`ASUS-OC`) with remote link to Node 0's `omega-hub`.

---

## 🔌 3. THE WIRE PROTOCOLS (LAYER BY LAYER)

### 3.1 Layer 1: Local Area Network Streamable HTTP (Phase 0 — Immediate)
* **Transport**: Streamable HTTP (`POST /mcp`) over RFC 7231 JSON-RPC 2.0.
* **Binding**: Node 0 binds `0.0.0.0:8016` via systemd override (`~/.config/systemd/user/omega-hub.service.d/override.conf`).
* **DNS Rebinding Guard**: Starlette / FastMCP `TransportSecuritySettings` configured on Node 0:
  ```python
  TransportSecuritySettings(
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
* **Required Client Headers**:
  * `Content-Type: application/json`
  * `Accept: application/json`
  * `Host: 192.168.10.168:8016`

### 3.2 Layer 2: Encrypted Mesh / Tailscale (Phase 1 — Zero-Config Roaming)
* When roaming outside the local Wi-Fi router, Tailscale establishes WireGuard tunnels between nodes.
* **MagicDNS Hostnames**:
  * `hp.tailnet` (Node 0)
  * `asus.tailnet` (Node 1)
* **Tag-Based ACLs (Exact Syntax for Tailnet Policy File)**:
  ```json
  {
    "tagOwners": {
      "tag:omega-hub": ["autogroup:admin"],
      "tag:opencode": ["autogroup:admin"]
    },
    "acls": [
      {"action": "accept", "src": ["tag:opencode"], "dst": ["tag:omega-hub:8016"]}
    ]
  }
  ```
  * Node 0 (HP): Apply tag `tag:omega-hub` in Tailscale admin console
  * Node 1 (ASUS): Apply tag `tag:opencode` in Tailscale admin console
  * Rule allows ASUS `tag:opencode` → HP `tag:omega-hub` on port 8016 only

### 3.3 Layer 3: Ephemeral Event Bus (Phase 2 — Redis Pub/Sub)
* High-frequency awareness heartbeats via `omega-hub_hivemind_redis_publish/subscribe`.
* Graceful degradation: if Redis is unavailable, all coordination falls back seamlessly to atomic lockfiles and JSON files in `data/coordination/` (Mandate M23 Failure Integrity).

---

## 🐝 4. THE HIVEMIND FEDERATION SCHEMA

### 4.1 Channel Partitioning
To prevent collision while ensuring total visibility, channels are strictly partitioned:

| Node | Agent Persona | Channel Name | Function |
|---|---|---|---|
| **HP (Node 0)** | `@roc_racoon` | `opencode` | Legacy mining, DHAL, hardware forensics |
| **HP (Node 0)** | `@kali` / `@makali` | `opencode` | Council synthesis, debut release, law |
| **HP (Node 0)** | `@grokster` | `grokster` | OpenCode CLI internals, cross-platform KB |
| **ASUS (Node 1)** | `asus_build` | `opencode-asus` | Bare-metal compile, Ollama benchmarking |
| **ASUS (Node 1)** | `asus_plan` | `opencode-asus` | Hardware profiling, local workload planning |

### 4.2 The 4-Way Coordination Contract
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

---

## 🚀 5. EXECUTION & TRANSFER RUNBOOK (TONIGHT)

### Step 1: Physical USB Transfer
The USB drive is formatted FAT32 (`/media/arcana-novai/D5D5-0B76`).
The staging payload is located in:
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

### Step 2: Deploy on ASUS (Node 1)
On the ASUS laptop, insert the USB drive and run:
```bash
# 1. Create OpenCode config directory if missing
mkdir -p ~/.config/opencode

# 2. Copy the remote MCP configuration
cp /media/$USER/*/OMEGA_NODE1_BOOTSTRAP/opencode.json ~/.config/opencode/opencode.json

# 3. Copy test scripts to home directory
cp /media/$USER/*/OMEGA_NODE1_BOOTSTRAP/test_connection.sh ~/test_connection.sh
cp /media/$USER/*/OMEGA_NODE1_BOOTSTRAP/hivemind_first_contact.py ~/hivemind_first_contact.py
chmod +x ~/test_connection.sh ~/hivemind_first_contact.py
```

### Step 3: Run Connectivity Verification
From the ASUS terminal:
```bash
~/test_connection.sh
```
**Expected Output**:
1. Health endpoint returns `{"status":"healthy","version":"2.2.0"}`
2. MCP initialize returns `serverInfo: {"name": "Omega Core Hub"}`
3. Tools list returns `Total tools exposed: 91`
4. SSE stream opens cleanly

### Step 4: Fire Ceremonial First Contact
```bash
python3 ~/hivemind_first_contact.py
```
This executes the first autonomous cross-PC packet:
- Posts `asus_build` context to Node 0's Hivemind.
- Dispatches a Priority 1 handoff to `roc_racoon`.
- Handshake packet lands on HP in `data/handoff/pending/`.

### Step 5: Clone Repo onto ASUS (USE GIT BUNDLE — REPO IS PRIVATE)
```bash
mkdir -p ~/Documents/Projects
cd ~/Documents/Projects
git clone /media/$USER/*/omega-engine.bundle omega-engine-alpha
```
* The git bundle (`omega-engine.bundle`) on the USB contains full history + all refs (HEAD, main, release/debut-v1.6.0).
* GitHub repo `Xoe-NovAi/omega-engine` is PRIVATE — HTTPS clone will fail without SSH key.

### Step 6: Execute Local Hardware Probe
Inside the cloned repo on ASUS:
```bash
cd ~/Documents/Projects/omega-engine-alpha
make probe-hardware
```
* Generates `config/hardware_profile.yaml` tailored to Intel Raptor Lake-H.
* Captures hybrid P/E core topology (6P + 4E), AVX-VNNI support, and single-channel DDR5-5200.

---

## ⚠️ 5.5 BIG PICKLE CONTEXT LIMIT — VERIFIED FACTS (CRITICAL)

| Property | Value | Source |
|----------|-------|--------|
| **Model Identity** | GLM-4.6 (Zhipu AI) — "stealth model" on OpenCode Zen | Community consensus + Pi.dev |
| **Registry Limits** | context=200,000 / input=160,000 / output=32,000 | `models.dev` official registry |
| **Actual Hard Limit** | ~128,000 tokens (API rejects at 130,389) | GitHub issue #3256 |
| **Safe Override** | `limit.input: 190000` → usable = 170,000 (85%) | HP verified fix |
| **DANGEROUS** | `limit.input: 950000` (1M ceiling) | Causes API errors when context > 200K |

**WHY THIS MATTERS**: Big Pickle is a **rotating model alias** — the registry limits reflect the CURRENT model, not the alias ceiling. Setting a 1M ceiling on a 200K model causes OpenCode to allow context growth to 930K tokens, then the API **hard rejects** with "Requested token count exceeds". The 190K override (85% threshold) is calibrated to the ACTUAL model.

**CONFIG BUG NOTE**: OpenCode ignores model limit overrides if `opencode.json` mixes V1 (`agent`) and V2 (`providers`) fields. Our USB config uses pure V2 schema (`https://opencode.ai/config.json`).

---

## 🛡️ 6. TROUBLESHOOTING & RESILIENCE MATRIX

| Symptom | Root Cause | Exact Remedy |
|---|---|---|
| `421 Misdirected Request` / `Invalid Host header` | Request Host not in `allowed_hosts` | Node 0 server has been updated with `192.168.10.168:*`. If IP changes, update `mcp_servers/omega_hub/server.py` `_transport_security`. |
| `406 Not Acceptable` | Client omitted `Accept: application/json` | Ensure `curl` or client sends `-H "Accept: application/json"`. OpenCode remote client does this natively. |
| `ECONNREFUSED` / Timeout | UFW blocking port 8016 or IP drift | On HP: `sudo ufw allow from 192.168.10.0/24 to any port 8016 proto tcp comment "Omega Hub MCP LAN access"`. Verify HP IP with `ip -4 addr show wlo1`. Restricts to LAN subnet only. |
| ASUS OpenCode doesn't see tools | Trailing slash error or wrong path | URL must be `http://192.168.10.168:8016/mcp` (Streamable HTTP), NOT root `/`. |
| Model 70% compaction on ASUS | Missing Big Pickle override in OpenCode | Copy project `opencode.json` `limit.input: 190000` override from HP (85% threshold). ASUS-OC tested 950000 (1M ceiling) but 190000 is safer — matches HP's verified fix. |
| ASUS MCP tools fail (searxng/firecrawl) | HP services bound to 127.0.0.1 only | searxng (8018) & firecrawl (8015) are LOCALHOST-ONLY on HP. USB config omits them. If needed, rebind on HP to 0.0.0.0 or run locally on ASUS. |

---

## 🌟 7. THE HORIZON: N-NODE SOVEREIGN OMEGAVERSE

Tonight marks **Node 0 ↔ Node 1**. But the architecture is inherently N-dimensional:
1. **Distributed Council**: Council queries dispatched across nodes via `RaptorLakeOptimizer` (fast single-thread analysis) and `Zen2Optimizer` (throughput and background mining).
2. **Sequential Offloading (D-580)**: When Node 1 upgrades to 32 GB dual-channel RAM, large models (Qwen 32B, DeepSeek R1) split layers across nodes with zero cloud telemetry.
3. **Headroom Semantic Compression (D-582)**: Tool results and RAG contexts compressed before transit across the LAN wire, preserving token budgets.

*From one noisy fan on an HP Pavilion to a federated, multi-machine sovereign AI cluster.*  
**The wire is live. The protocol is written. Let's make history.**

---
*⬡ OMEGA ⬡ ROC_RACOON ⬡ P2P-OMEGAVERSE-FEDERATION-PLAYBOOK-v1.1.0 ⬡ 2026-09-09*
