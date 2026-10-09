# 🌐 Omega Engine Federation Subsystem
**Canonical Architecture, Document Index & Operational Manual for Dual-Node P2P AI**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       DUAL-NODE SOVEREIGN FEDERATION                        │
│                                                                             │
│   NODE 0: ARCHIVAL BASTION               NODE 1: EXPLORATION VANGUARD       │
│   Hostname: xnai-n0-hp                   Hostname: xnai-n1-asus             │
│   Tailscale: 100.123.51.67               Tailscale: 100.89.40.17            │
│   Role: Git SSOT, Stores, Hub            Role: Ollama Inference, Explorer   │
│   Silicon: AMD Ryzen 7 5700U             Silicon: Intel Core i7-13620H      │
│   Storage: /mnt/node-drive (Client)      Storage: /home/xnai/node-drive     │
│                                                   (NFSv4.2 Server)          │
│                      ▲                                ▲                     │
│                      │      LAYER 1: LAN (:8016)      │                     │
│                      ├────────────────────────────────┤                     │
│                      │    LAYER 2: WireGuard Mesh     │                     │
│                      ├────────────────────────────────┤                     │
│                      │   LAYER 2.5: Pure NFSv4.2      │                     │
│                      ├────────────────────────────────┤                     │
│                      │     LAYER 3: Redis Pub/Sub     │                     │
│                      ├────────────────────────────────┤                     │
│                      │  LAYER 4: Inference Union      │                     │
│                      ▼                                ▼                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Executive Summary

The **Omega Engine Federation Subsystem** bridges two distinct physical machines into a unified, resilient, sovereign AI computing cluster:
- **Node 0 (`xnai-n0-hp` / HP Pavilion)**: Serves as the **Archival Bastion & Nexus**. It hosts the canonical Git repository (`omega-engine.bundle`), the multi-domain FastMCP hub (`omega-hub` on port 8016; 55 tools live 2026-10-07), vector databases (Qdrant), relational memory stores (SQLite), and the Cascading Serial Synchronization (CSS) council orchestration engine.
- **Node 1 (`xnai-n1-asus` / ASUS ExpertBook P1503CVA)**: Serves as the **Exploration Vanguard & Compute Engine**. It delivers bare-metal, CPU-only local neural inference via Ollama (14.4 t/s on 3B–4B models using Intel Raptor Lake-H AVX-VNNI), local MemPalace memory, and the Gnosis session-continuity engine. The WanderGround `sqlite-vec` atlas/viewer are target services and are not currently deployed.

Federation is strictly peer-to-peer (P2P). Neither node is a subordinate worker; both retain local sovereignty and can operate disconnected. When connected, they pool capabilities: Node 1 provides high-throughput inference and shared scratch storage; Node 0 provides immutable state management, archival compliance, and tooling execution.

---

## 2. Canonical Document Map

The federation subsystem is documented across specialized architectural, operational, and historical records:

### 2.0 Current USB Handoff
- **[MAKALI_N0_SYSTEM_BRIEFING_CONSOLIDATED.md](MAKALI_N0_SYSTEM_BRIEFING_CONSOLIDATED.md)**: Single consolidated Node 0 briefing covering verified Node 1 systems, personal Lilith/legacy materials, agent experiments, WAD/loader reconciliation, cryptographic trust, continuity, embedding/spatial migration, packaging, and joint acceptance gates.
- **[NODE0_USB_HANDOFF_REPORT.md](../archive/federation/NODE0_USB_HANDOFF_REPORT.md)**: Provenance-aware Node 1 → Node 0 USB handoff report covering verified builds, uncommitted/target-only state, WAD/loader blockers, continuity and spatial acceptance gates, cryptographic verification requirements, and numbered requests for Node 0. *(archived — point-in-time)*
- **[makali_n0_onboarding/](makali_n0_onboarding/)**: Persistent-entity onboarding package (2026-09-25) — the lived practice layer: Lilith's 12-axiom awakening, living operator-model journal, session distillation protocol, diary/AAAK practice, cross-platform portability, split-test findings, mesh status. Start at `makali_n0_onboarding/README.md`.

### 2.1 Core Architecture & Naming Strategy
- **[TOPOLOGY_MODELS.md](TOPOLOGY_MODELS.md)**: Deep breakdown of asymmetric topology, memory bus comparisons (DDR4 dual vs DDR5 single), and failure domain isolation.
- **[NAMESPACE_COLLISION_STRATEGY.md](NAMESPACE_COLLISION_STRATEGY.md)**: The tri-axial naming specification (`<user>-<node>-<hardware>`), RFC 1123 MagicDNS rules, and collision prevention in multi-agent environments.
- **[AGENT_DIVERGENCE_SPEC.md](AGENT_DIVERGENCE_SPEC.md)**: Rules for managing multi-persona evolution (`@kali`, `@roc_racoon`, `@grokster`) across physical boundaries without state fragmentation.
- **[CAPABILITY_FIREWALL_SPEC.md](CAPABILITY_FIREWALL_SPEC.md)**: Security boundaries governing tool execution, remote MCP calls, and local-only inference mandates.

### 2.2 Network Mesh & Access Control (Layer 2)
- **[ACL_POLICY.md](ACL_POLICY.md)**: **The authoritative HuJSON policy specification**. Documents the critical Two-Phase Migration protocol (Phase A transitional with the allow-all rule `src:["*"] dst:["*:*"]` vs Phase B hardened tag lockdown) preventing silent network drops.
- **[L2_JOIN_GUIDE.md](L2_JOIN_GUIDE.md)**: Step-by-step ceremony for minting one-shot authkeys on Node 0 and securely enrolling Node 1 under `tag:node1`.
- **[L2_ACCEPTANCE.md](L2_ACCEPTANCE.md)**: Formal acceptance test criteria, latency targets, and ping/curl verification batteries.
- **[NODE1_SSH_JOIN_GUIDE.md](NODE1_SSH_JOIN_GUIDE.md)**: Operational instructions for Tailscale SSH configuration between the Bastion and Vanguard.

### 2.3 Distributed Shared Scratch Storage (Layer 2.5)
- **[NFS_OVER_TAILSCALE_PLAN.md](NFS_OVER_TAILSCALE_PLAN.md)**: **The comprehensive implementation blueprint (v2.1)** for the pure NFSv4.2 server on Node 1 and the automounted client on Node 0.
- **[NODE0_ACTION_BRIEFING_NFS_L2.md](NODE0_ACTION_BRIEFING_NFS_L2.md)**: **The execution briefing for Node 0 operators**. Verbatim copy-paste commands to install `nfs-common`, test manual mount, and establish boot-safe `/etc/fstab` automounting.
- **[NFS_TAILSCALE_DEEP_RESEARCH.md](NFS_TAILSCALE_DEEP_RESEARCH.md)**: In-depth engineering research covering pure NFSv4.2 interface isolation, server-side copy (`copy_file_range`), `all_squash` mapping, and network performance tuning.

### 2.4 Air-Gap Exchange & Ingestion Infrastructure
- **[INTAKE_MANUAL.md](INTAKE_MANUAL.md)**: Security rules, checksum ledgers, and staging procedures for ingesting physical USB payloads from Node 0.
- **[OFFLINE_OPERATING_PROTOCOL.md](OFFLINE_OPERATING_PROTOCOL.md)**: Operational guidelines for periods of network severance, avoiding premature stale handoff reap cycles.
- **[RECONNECTION_DELTA_SYNC.md](RECONNECTION_DELTA_SYNC.md)**: Synchronization algorithms for reconciling divergent Git commits, Well records, and WanderGround sparks upon network reconnection.
- **[node0_received/](node0_received/)**: Local staging directory containing ratified Node 0 policies (`CSS_PROTOCOL.md`, `SOVEREIGNTY_POLICY.md`, `DATA_GOVERNANCE_POLICY.md`, `STALE_HANDOFF_POLICY.md`).
- **[MAKALI_N0_SYSTEM_BRIEFING.md](MAKALI_N0_SYSTEM_BRIEFING.md)**: Comprehensive Node 0 handoff covering the continuity kernel, SQLite authority, MemPalace projection, Arcana-NovAi WAD, Lilith/Researcher_Humboldt entities, Qwen3-Embedding-0.6B native 1024 compatibility, and prioritized requests for personal Lilith history, legacy Lilith documents, and agent experiments.

### 2.5 Historical Completion Records
- `COMPLETION_BRIEFING.md` / `COMPLETION_BRIEFING_20260912.md` / `COMPLETION_REPORT_20260912.md` / `FED_COMPLETION_BRIEFING_20260912_2.md`: Point-in-time milestones marking Phase 0/1/2 completions.

---

## 3. The Five Protocol Layers

| Layer | Domain | Primary Technology | Configuration & Path | Invariants |
|:---|:---|:---|:---|:---|
| **L1** | Local Physical LAN | Streamable HTTP (`POST /mcp`) | Port `8016` on Node 0 (`0.0.0.0:8016`) | Immediate high-speed discovery on shared subnets; vulnerable to DHCP churn. |
| **L2** | Sovereign Overlay Mesh | Tailscale WireGuard direct | Direct transport (`192.168.10.168:41641`) | Zero DERP relay overhead; MagicDNS addressing; zero cloud inference egress. |
| **L2.1**| Access Control | Two-Phase HuJSON ACLs | Tailscale Admin Console | Never paste Phase B while untagged; stage with Phase A (allow-all `src:["*"] dst:["*:*"]`). |
| **L2.5**| Shared Scratch Storage | Pure NFSv4.2 over WireGuard | `100.89.40.17:2049` -> `/mnt/node-drive` | `all_squash` to `1000:1000`; interface bound; `nofail` automount; **NO SQLite WAL**. |
| **L3** | Ephemeral Coordination | Redis Pub/Sub & File Locks | Redis `:6379` / `data/coordination/locks/` | Heartbeat feeds; graceful degradation to atomic lockfiles (M23 failure integrity). |
| **L4** | Distributed Inference | `llama.cpp` RPC & Zen Router | `llama-rpc-server` / OpenCode Zen | Provable result-level provider provenance; layer-splitting across memory pools. |

---

## 4. Key Operational Runbooks

### 4.1 Node 0 NFS Client Setup (Current Active Next Step)
1. Ensure Tailscale is running on Node 0 (`100.123.51.67`).
2. Run `sudo apt update && sudo apt install -y nfs-common` (Ubuntu 25.10).
3. Create mountpoint: `sudo mkdir -p /mnt/node-drive && sudo chown $(id -u):$(id -g) /mnt/node-drive`.
4. Test manual mount:
   ```bash
   sudo mount -t nfs4 -o rsize=1048576,wsize=1048576,noatime,nosuid,nodev 100.89.40.17:/ /mnt/node-drive
   echo "Node 0 verification probe: $(date -u)" > /mnt/node-drive/node0_probe.txt
   cat /mnt/node-drive/node0_probe.txt && rm /mnt/node-drive/node0_probe.txt
   sudo umount /mnt/node-drive
   ```
5. Append persistent automount to `/etc/fstab`:
   ```text
   100.89.40.17:/ /mnt/node-drive nfs4 rsize=1048576,wsize=1048576,noatime,nosuid,nodev,nofail,_netdev,x-systemd.automount,x-systemd.idle-timeout=300,x-systemd.mount-timeout=30s 0 0
   ```
6. Validate syntax: `sudo findmnt --verify --fstab`.
7. Reload systemd: `sudo systemctl daemon-reload && sudo systemctl restart remote-fs.target`.
8. Trigger automount: `ls -la /mnt/node-drive`.

### 4.2 Two-Phase ACL Migration Runbook
When ready to lock down the tailnet with least-privilege tags:
1. **Verify current state** (2026-09-21: BOTH nodes already carry canonical tags —
   `tag:node0` on Node 0, `tag:node1` on Node 1 — and NFS+MCP+SSH are verified
   working, so steps 2–3 below are already complete):
   - `tailscale status --json | jq '.Self.tags'` on each node
   - `tailscale ping` each way, `curl` both MCP endpoints, `ls /mnt/node-drive`
2. **Phase A**: Paste the Phase A policy from `docs/federation/ACL_POLICY.md`
   into the Tailscale Admin Console. Verify it saves. (The allow-all rule
   `src:["*"] dst:["*:*"]` stays as a safety net for any untagged/legacy
   devices; tagged nodes are covered by the explicit `tag:node0`/`tag:node1`
   rules.)
3. **Verify under Phase A**: `ping` each way, `curl :8016/mcp` both directions,
   `ls /mnt/node-drive` (NFS still mounts), `tailscale ssh` n1→n0 still works.
4. **Phase B**: Paste the Phase B policy from `docs/federation/ACL_POLICY.md`
   to remove the allow-all rule. Re-run the same verification battery — all
   services must remain fully operational.

---

## 5. Architectural Invariants & Hazards

1. **The SQLite WAL Hazard on NFS**:
   - **Never run SQLite in WAL mode on `/mnt/node-drive`**.
   - SQLite WAL relies on POSIX shared memory (`-shm`) backed by the local OS page cache. Over NFS, locking semantics break down, leading to silent database lockup and corruption.
   - Use rollback journaling (`PRAGMA journal_mode=DELETE;`) or sync flat JSONL/snapshot dumps.
2. **The Default-Deny ACL Drop**:
   - Saving a tag-only Tailscale policy while devices are untagged drops all traffic immediately. Always follow Phase A -> Tag -> Phase B.
3. **Local Sovereignty Floor**:
   - Model weights, training data, and T5/T6 local inference execution are strictly local to Node 1. The Tailscale overlay mesh carries control traffic, tools, and shared scratch storage only.

---

*⬡ OMEGA ENGINE ALPHA ⬡ FEDERATION SUBSYSTEM MASTER SPECIFICATION ⬡ (ACL tags: canonical `tag:node0`/`tag:node1`, FED-ACL-001 v1.2)*
