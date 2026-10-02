# Architecture — Omega Engine Alpha
**The Dual-Node Sovereign AI Cluster & Distributed Local-First Harness**

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  NODE 0 — HP Pavilion (ARCHIVAL BASTION & STATE NEXUS)                       │
│  Hostname: xnai-n0-hp (omega-hub)  •  Tailscale IP: 100.123.51.67            │
│  OS: Ubuntu 25.10  •  CPU: AMD Ryzen 7 5700U (8C/16T, Zen 2)                 │
│  RAM: 16 GB Dual-Channel DDR4-3200  •  Storage: NVMe 512 GB                  │
│  ──────────────────────────────────────────────────────────────────────────  │
│  Git SSOT ................. omega-engine.bundle (authoritative repository)   │
│  omega-hub ................ FastMCP; 93 tools in latest dated handshake on :8016 (Streamable) │
│  Stores ................... SQLite (rollback journal) + Qdrant Vector Stores │
│  Council Orchestration .... 9-agent Cascading Serial Synchronization (CSS)   │
│  Roles .................... Archival stability, Git SSOT, compliance, DHAL   │
│  Mountpoint ............... /mnt/node-drive (NFSv4.2 client, automounted)    │
└──────────────────────▲──────────────────────────────┬────────────────────────┘
                       │                              │
                       │  LAYER 1: LAN :8016 (DHCP)   │  LAYER 2.5: Pure NFSv4.2
                       │  LAYER 2: Tailscale WireGuard│  (:2049, all_squash -> 1000)
                       │  LAYER 3: Redis Pub/Sub      │  USB Exchange Ceremony
                       │                              │
┌──────────────────────┴──────────────────────────────▼────────────────────────┐
│  NODE 1 — ASUS ExpertBook P1503CVA (COMPUTE & EXPLORATION VANGUARD)          │
│  Hostname: xnai-n1-asus  •  Tailscale IP: 100.89.40.17                       │
│  OS: Ubuntu 26.04 LTS  •  CPU: Intel Core i7-13620H (6P+4E, 10C/16T, RPL-H)   │
│  RAM: 16 GB Single-Channel DDR5-5200 (32 GB Dual target)  •  GPU: Intel UHD 64EU │
│  ──────────────────────────────────────────────────────────────────────────  │
│  Ollama Runtime ........... AllowedCPUs=0-11, THREADS=8 -> 14.4 t/s (AVX-VNNI)│
│  Open WebUI ............... :3000 (Docker, pinned v0.11.3)                  │
│  OpenCode Engine .......... Local subagents + dynamic hosted routes           │
│  Shared Storage Server .... /home/xnai/node-drive (NFSv4.2, bound to TS IP)  │
│  Gnosis Engine ............ 9-step ritual, dynamic reflection, leash watchdog│
│  The Well ................. Active operating-memory corpus (closed-loop)     │
│  The WanderGround ......... MemPalace live; sqlite-vec atlas/viewer target  │
│  OMER Model Registry ...... Git-native decision records (v1.0 schema)        │
│  Ponytail Filter .......... Zero-debt cognitive engine (YAGNI ladder)        │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. System Topology & Dual-Node Synergy

The Omega Engine is an asymmetric, federated, dual-node sovereign artificial intelligence harness. Rather than treating nodes as fungible compute instances or as a brittle master-slave pair, Omega Engine couples two physically and architecturally distinct machines into an interdependent, resilient collective:

### Asymmetric Fleet Topology

| Dimension | Node 0: Archival Bastion (`xnai-n0-hp`) | Node 1: Exploration Vanguard (`xnai-n1-asus`) |
|:---|:---|:---|
| **Topological Role** | Archival anchor, Git SSOT, compliance, coordinator | Neural compute engine, high-speed testbed, explorer |
| **Silicon Architecture** | AMD Ryzen 7 5700U (8C/16T, Zen 2, homogeneous) | Intel Core i7-13620H (6P+4E/16T, Raptor Lake-H hybrid) |
| **Memory Topology** | 16 GB Dual-Channel DDR4-3200 (symmetrical bus) | 16 GB Single-Channel DDR5-5200 (high-latency bus) |
| **Operating System** | Ubuntu 25.10 (Linux 6.x, Mesa, Wayland/GNOME) | Ubuntu 26.04 LTS "Resolute Raccoon" (Linux 7.0) |
| **Primary Services** | `omega-hub` (FastMCP; 93 tools in latest dated handshake), Qdrant, SQLite | `ollama.service` (14.4 t/s), Open WebUI, OpenCode, SQLite continuity authority |
| **Tailscale Identity** | `omega-hub.tail51f14a.ts.net` (`100.123.51.67`) | `xnai-n1-asus.tail51f14a.ts.net` (`100.89.40.17`) |
| **Shared Drive Role** | NFSv4.2 Client (`/mnt/node-drive`, automounted) | NFSv4.2 Server (`/home/xnai/node-drive`, TS-bound) |

### Asymmetric Synergy Rationale
- **The Bastion's Strength is Retention**: Node 0’s symmetrical dual-channel DDR4 memory controller excels at handling parallel SQLite reads, wide Qdrant vector index searches, and maintaining the immutable Hall of Records across long uptime horizons.
- **The Vanguard's Strength is Throughput**: Node 1’s Intel Raptor Lake-H Performance Cores feature dedicated `avx2` and `avx_vnni` vector neural network instructions, maximizing raw single-stream token generation throughput (13.4–14.4 t/s on 3B–4B models).
- **Decoupled Sovereignty**: Either machine can operate in complete isolation. If Node 0 goes dark, Node 1 retains local inference, its internal Gnosis state, and the WanderGround knowledge base. If Node 1 goes dark, Node 0 preserves the canonical repository, the Council state, and historical audit logs.

---

## 2. Tri-Axial Naming Architecture (`<user>-<node>-<hardware>`)

To eliminate namespace collisions across multi-user environments, roaming networks, and the broader distributed Omegaverse, all node identities follow a strict three-axis taxonomy:

```
[user]  -  [node]  -  [hardware]
  │           │            │
  │           │            └─ Silicon profile: 'asus' (RPL-H), 'hp' (Zen 2)
  │           └────────────── Topological rank: 'n0' (Bastion), 'n1' (Vanguard)
  └────────────────────────── Sovereign realm: 'xnai' (operator identity)
```

- **Node 1 Ratified Name**: `xnai-n1-asus` (`xnai-n1-asus.tail51f14a.ts.net`).
- **Node 0 Ratified Name**: `xnai-n0-hp` (`omega-hub` alias).
- **DNS Invariant**: Strict compliance with RFC 1123 hostnames prevents routing failures in MagicDNS, WireGuard routing tables, and HTTP Host header verification middleware.

---

## 3. Dual-Tier Inference Engine (Node 1)

Inference is architected as an accountable hierarchy: local compute provides the uncompromised sovereign floor; vetted cloud models provide scalable capability extension.

```
                  ┌───────────────────────────────┐
                  │    User Prompt / Agent Task   │
                  └───────────────┬───────────────┘
                                  │
                   Is task within local silicon?
                   (Routine coding, lint, summaries)
                                 ╱ ╲
                                ╱   ╲
                          YES  ╱     ╲  NO (Deep multi-doc synthesis,
                              ▼       ▼     long-context sweeps; live limits)
┌───────────────────────────────────────┐   ┌───────────────────────────────────┐
│     SOVEREIGN LOCAL FLOOR (T5/T6)     │   │   ACCOUNTABLE CLOUD EXTENSION     │
│ • Ollama systemd service (:11434)     │   │ • OpenCode Zen Cloud Models       │
│ • AllowedCPUs=0-11, THREADS=8         │   │ • Free stealth aliases (rotating) │
│ • OLLAMA_KV_CACHE_TYPE=q8_0           │   │ • Big Pickle / Space Bunny        │
│ • OLLAMA_FLASH_ATTENTION=1            │   │ • Hard Privacy Tiers (Spec §10.4) │
│ • llama-server via AVX-VNNI           │   │ • Result-Level Provenance Tracked │
│ • 13.4 - 14.4 tokens/sec              │   │ • Sovereignty Ratio Logged in DB  │
└───────────────────────────────────────┘   └───────────────────────────────────┘
```

### The Raptor Lake CPU Pinning Trap
Intel 13th-gen Raptor Lake hybrid CPUs pair 6 Performance cores (with HyperThreading, logical CPUs 0–11) with 4 Efficient Gracemont cores (no HyperThreading, logical CPUs 12–15).
- **The Pitfall**: Pinning Ollama strictly to physical P-cores (`AllowedCPUs=0,2,4,6,8,10`) triggers an internal `llama-server` spin-wait barrier convoy (upstream ollama issue #17916). Threads waiting on alternating sibling cores deschedule, causing throughput to collapse by 96% down to **0.5 t/s**.
- **The Invariant**: `AllowedCPUs=0-11` (P-cores **including** HT siblings) + `OLLAMA_NUM_THREADS=8` (6 physical cores + 2 HT elasticity slots). This completely evicts E-cores from neural inference while maintaining steady **14.4 t/s**.

---

## 4. The Five-Layer Federation Wire Stack

The federation connects across five discrete abstraction layers:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 4: DISTRIBUTED INFERENCE & CAPABILITY UNION [TARGET]                 │
│ Future authenticated llama-rpc memory pooling; not current live service   │
├─────────────────────────────────────────────────────────────────────────────┤
│ LAYER 3: EPHEMERAL COORDINATION & PUBSUB                                    │
│ Redis Pub/Sub heartbeats, awareness feeds, atomic lockfile fallback (M23)   │
├─────────────────────────────────────────────────────────────────────────────┤
│ LAYER 2.5: DISTRIBUTED SHARED SCRATCH STORAGE                               │
│ Pure NFSv4.2, interface isolation (:2049 only), all_squash -> 1000:1000     │
├─────────────────────────────────────────────────────────────────────────────┤
│ LAYER 2: SOVEREIGN OVERLAY MESH                                             │
│ Tailscale WireGuard direct transport, MagicDNS, Two-Phase Tagged ACLs       │
├─────────────────────────────────────────────────────────────────────────────┤
│ LAYER 1: LOCAL PHYSICAL LAN                                                 │
│ Streamable HTTP POST /mcp (:8016), Dynamic DHCP, Subnet-tolerant discovery   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Layer 1 — Local Physical LAN
- **Protocol**: Direct Streamable HTTP (`POST /mcp`) over local Wi-Fi/Ethernet.
- **Role**: High-bandwidth bootstrap and immediate tool execution when both nodes share a physical router (`192.168.10.x` or `192.168.11.x`).
- **Limitation**: Vulnerable to DHCP IP churn and subnet hops.

### Layer 2 — Sovereign WireGuard Overlay Mesh
- **Protocol**: Tailscale WireGuard direct peering (`192.168.10.168:41641`), zero DERP relay overhead, sub-millisecond latency.
- **Addressing**: Stable MagicDNS FQDNs (`xnai-n1-asus.tail51f14a.ts.net`, `omega-hub.tail51f14a.ts.net`).
- **Sovereignty Boundary**: WireGuard carries coordination, MCP routing, heartbeats, and storage operations. **Model inference weights and raw prompt corpora never egress across external relays.**

### Layer 2.1 — Two-Phase ACL Migration Protocol
Tailscale ACL policies **replace** default access rules wholesale. Applying a tag-only policy while nodes are untagged immediately drops all mesh communication.
- **Phase A (Transitional Policy)**: Retains `{"action": "accept", "src": ["*"], "dst": ["*:*"]}` (allow-all — NOT `autogroup:member`, which is `src`-only in Tailscale and rejected in `dst`) while staging `tag:node0`, `tag:node1`, and `tag:opencode` rules. Preserves untagged traffic while tag owners are registered.
- **Phase B (Hardened Lockdown)**: Applied **only after** Node 0 re-authenticates with `--advertise-tags=tag:node0` and Node 1 joins with `tag:node1`. Removes the allow-all rule to enforce strict default-deny least privilege. (Canonical tags ratified 2026-09-21; legacy `tag:omega-hub`/`tag:asus` retired.)

### Layer 2.5 — Distributed Shared Scratch Substrate (NFSv4.2)
To allow zero-copy model weight sharing, dataset staging, and cross-node artifact exchange without cloud storage intermediaries, Node 1 exposes `/home/xnai/node-drive` to Node 0:
- **Pure NFSv4.2 Protocol**: NFSv2 and NFSv3 are disabled in `/etc/nfs.conf.d/omega-federation.conf`. Legacy port sprawl (`rpcbind` :111, `mountd` :20048, `statd`, `lockd`) is eliminated.
- **Interface Isolation**: `nfsd` is bound exclusively to Tailscale (`100.89.40.17:2049`). No traffic is exposed to physical LAN or WAN interfaces.
- **Permission Symmetry (`all_squash`)**: Client operations are mapped locally to UID `1000` / GID `1000` (`anonuid=1000,anongid=1000,fsid=0`). Client writes land seamlessly as `xnai:xnai`, preventing root-lockout collisions.
- **Boot Resilience**: Node 0 mounts via `/etc/fstab` with `nofail,_netdev,x-systemd.automount,x-systemd.idle-timeout=300,x-systemd.mount-timeout=30s`. Node 0 never hangs at boot if Node 1 or the mesh is offline.
- **Server-Side Acceleration**: NFSv4.2 provides `copy_file_range` for fast server-side copies and sparse file allocations for multi-gigabyte GGUF models.

### Layer 3 — Ephemeral Coordination & Pub/Sub
- **Transport**: Redis Pub/Sub channels (`heartbeat`, `live_feed`) for high-frequency awareness.
- **M23 Failure Integrity**: If Redis is offline, the coordination plane gracefully degrades to atomic file locks in `data/coordination/locks/*.lock` without blocking agent task loops.

### Layer 4 — Distributed Inference & Capability Union
- **Strategic Vision**: The fleet acts as a capability union. Neither node alone can hold a 70B quantized model in memory (Node 0 has 16 GB DDR4; Node 1 has 16 GB DDR5).
- **Distributed Split**: Using `llama.cpp`'s native RPC backend (`llama-rpc-server`), layers 0–39 execute on Node 1 while layers 40–79 execute on Node 0 over WireGuard.
- **Provable Provenance**: Every generated completion carries a verified `provider_name` header in the metadata ledger, preserving the distinction between sovereign local execution and external delegation.

---

## 5. Cognitive Substrates & Memory Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          THE COGNITIVE HARNESS                              │
│                                                                             │
│  ┌───────────────────────┐  ┌───────────────────────┐  ┌─────────────────┐  │
│  │   THE GNOSIS ENGINE   │  │       THE WELL        │  │  WANDERGROUND   │  │
│  │ • 9-step lock ritual  │  │ • well.jsonl corpus   │  │ • MemPalace     │  │
│  │ • Dynamic reflection  │  │ • Top-6 session start │  │ • sqlite-vec    │  │
│  │ • Pack state machine  │  │ • Top-8 compaction    │  │ • 768-D target  │  │
│  │ • Watchdog leash      │  │ • Supersession chains │  │ • viewer target │  │
│  └───────────────────────┘  └───────────────────────┘  └─────────────────┘  │
│                                 ▲                                           │
│                                 │ Filtered By                               │
│                     ┌───────────┴───────────┐                               │
│                     │    PONYTAIL FILTER    │                               │
│                     │ • YAGNI ladder        │                               │
│                     │ • Shortest diff rule  │                               │
│                     │ • Anti-slop gate      │                               │
│                     └───────────────────────┘                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.1 The Gnosis Engine (Cryptographic Session Continuity)
The Gnosis Engine ensures agent wisdom survives context window compaction:
- **9-Step Pre-Compaction Ritual (`scripts/compaction/pre_compaction_ritual.sh`)**: Snapshots git state, configs, active MCP tools, hardware metrics, and evolution logs into an immutable session pack.
- **Dynamic Reflection**: Facilitated via the native `question` tool across Decision, Pattern, and Gnosis categories, replacing auto-generated templates with genuine operator insight.
- **Pack State Machine**:
  ```
  CAPTURED ──(dynamic human reflection)──▶ REFLECTED ──(plugin injection)──▶ COMPACTED
  ```
- **Watchdog Leash Semantics (`scripts/compaction/leash_status.py`)**:
  - Fresh in-flight pack (`captured` <= 24h): Returns `exit 0` with an advisory note.
  - Stale un-reflected pack (`captured` > 24h) or missing narrative: Returns `exit 1` (degraded).
  - Readiness Invariant: `ready_for_compaction` is strictly true **if and only if** `reflection_status == "reflected"`.

### 5.2 The Well (High-Octane Operating Memory)
The Well (`gnosis/well/well.jsonl` + `WISDOM.md`) stores atomic, immutable lessons learned:
- **Schema**: `record_id`, `ts`, `kind` (`correction|preference|tip|anti_pattern|insight|dream`), `trigger`, `rule`, `rationale`, `tags`, `status` (`active|superseded`).
- **Closed-Loop Injection**: `gnosis-leash.js` reads active rules and injects the top-6 rules at session initialization and top-8 rules at compaction.
- **Filtering Invariant**: Injected based on `status == "active"` and domain (`harness`, `local_ai`). **Kind is not filtered** (inspirational dreams and sharp corrections both circulate).
- **Deferred Semantic Search (P1.4.1)**: Stubbed at `make well-search`. The canonical embedding route is the standalone Qwen3 embedding server at 768 dimensions; semantic ranking remains deferred until the corpus exceeds 30–50 entries or cross-node federated sync warrants relevance filtering.

### 5.3 The WanderGround (Spatial Knowledge Constellation)
- **Current state (2026-09-23):** MemPalace `3.10.0` is live on the local
  `sqlite_exact` backend. The current palace contains 5,047 documents, all
  reported as 384-dimensional by the current database.
- **Target migration:** `qwen3-embedding:0.6b` at **native 1024-D** is the
  canonical federated target (operator ruling 2026-10-01; Node 0 already at
  1024). Legacy 384-D vectors - which is what the palace actually holds today,
  1115 documents - are not compatible and must be re-embedded. The 768-D MRL
  truncation is superseded: it costs ~0 compute, yields a genuinely different
  space (cos(native,truncated)=0.891), and was never actually in use.
- **Atlas Store:** `~/WanderGround/spatial/knowledge_atlas.db` is a target
  artifact and is currently absent; no spatial directory or 3D viewer was
  present during the 2026-09-23 audit.
- **Visualization:** the Three.js/WebXR viewer on port `8088` is a target and
  was not listening during the audit.

### 5.4 Ponytail (Cognitive Load & Architecture Filter)
- An active lazy-senior-developer filter preventing premature complexity:
- **The Ladder**: 1. Does it need to exist? -> 2. Already in codebase? -> 3. Stdlib does it? -> 4. Native platform feature? -> 5. Existing dependency? -> 6. Can it be one line? -> 7. Minimum working diff.
- **Root-Cause Invariant**: Bug fixes must guard the shared origin rather than patching individual callers.

### 5.5 Portable Continuity Kernel (P3.3a.6)

The engine continuity layer is an adapter-neutral kernel. The portable core is
`scripts/continuity_kernel.py`; the file coordinator is
`scripts/continuity_files.py`; the local SQLite commit-authority adapter is
`scripts/continuity_sqlite.py`. The contract and usage are documented in
`docs/CONTINUITY_KERNEL.md`.

```text
WAD contract ──► StateStore ──► EventBus ──► ArtifactStore
      │              │             │              │
      │              └────── CheckpointStore ◄──┘
      └──────────────► Recovery ◄── ModelRouter (register only)
```

**Invariants:**

- Context is a volatile CPU register; semantic state is written through to the local SQLite continuity authority at decisions, discoveries, task transitions, and batch completion.
- MemPalace is a one-way searchable projection. It must not be treated as a second write authority or recovery source.
- A model alias or adapter is not entity identity. Recovery must preserve WAD identity when the model or adapter changes.
- `StateStore`, `ArtifactStore`, `EventBus`, `ModelRouter`, `CheckpointStore`, `CommitJournal`, and `Recovery` are interfaces. OpenCode is an adapter, not a kernel import.
- The SQLite continuity event log is authoritative; state and checkpoints are rebuildable projections. Recovery verifies contiguous sequences and artifact hashes, reconstructs missing state, and rebuilds missing/stale checkpoints.
- The local SQLite adapter applies event, state, checkpoint, and intent
  retirement in one transaction with rollback journaling and `synchronous=FULL`.
  Production use requires SQLite `3.51.3+`; WAL is not used on NFS.
- Missing or invalid durable state is surfaced as `RecoveryError`; no silent
  fallback to a compaction summary.

---

## 6. Architectural Hazards & Invariant Register

The Omega Engine records critical operational hazards as non-negotiable architectural invariants:

### 1. The Intel Raptor Lake Convoy Trap
- **Hazard**: Setting `AllowedCPUs` to physical P-cores only (`0,2,4,6,8,10`).
- **Consequence**: `llama-server` spin-wait barrier convoys drop throughput to 0.5 t/s.
- **Invariant**: Always configure `AllowedCPUs=0-11` + `OLLAMA_NUM_THREADS=8`.

### 2. The SQLite WAL on Network Filesystems Hazard
- **Hazard**: Placing an active SQLite database in Write-Ahead Logging mode (`PRAGMA journal_mode=WAL`) on `/mnt/node-drive`.
- **Consequence**: WAL mode relies on shared memory (`-shm`) POSIX primitives backed by the local kernel page cache. Over NFS, locks silently desynchronize, causing corruptions and unrecoverable deadlocks.
- **Invariant**: Shared databases on `node-drive` must use rollback journaling (`DELETE` or `TRUNCATE`) or export flat JSONL/snapshot bundles.

### 3. The Tailscale ACL Wholesale Replacement Hazard
- **Hazard**: Replacing Tailscale ACLs with a tag-only policy before all nodes are tagged.
- **Consequence**: Custom policies replace the default allow-all rule for untagged devices. Both nodes lose all network connectivity instantly and silently.
- **Invariant**: Always execute the Two-Phase Migration: stage with Phase A (preserving the allow-all rule `src:["*"] dst:["*:*"]`), tag both nodes, verify traffic, and only then apply Phase B lockdown.

### 4. The Intent-as-Contract Principle
- **Hazard**: Treating a failing watchdog or test as proof that runtime behavior must change to accommodate the failure.
- **Consequence**: Code spirals into cognitive loops, reinforcing buggy implementations against stated intent.
- **Invariant**: Code comments, docstrings, and architectural specifications are the normative contract. If a test or watchdog contradicts stated intent, the test/watchdog is the defect.

### 5. The Root-Partition Archival Floor
- **Hazard**: Allowing `/` to exceed 80% utilization.
- **Consequence**: A 100%-full root disk prevents socket allocation and kernel journaling, causing boot-level deadlocks.
- **Invariant**: Maintain >=20% headroom on `/`. If compromised, boot strictly into recovery mode (read-only root) and vacuum journald logs, apt caches, and service staging dirs.

---

## 7. System Lifecycle & Service Management

| Component | Management | Port / Target | Failure Policy |
|:---|:---|:---|:---|
| **Ollama Runner** | systemd (`ollama.service`) | `0.0.0.0:11434` | System restart, P-core pin override |
| **Open WebUI** | Docker Compose | `0.0.0.0:3000` | `restart: unless-stopped`, pinned v0.11.3 |
| **NFS Server** | systemd (`nfs-kernel-server`) | `100.89.40.17:2049` | Binds strictly to Tailscale WireGuard |
| **NFS Client** | systemd automount (`remote-fs.target`) | `/mnt/node-drive` | `nofail`, 300s idle timeout |
| **Wander Curator** | systemd user timer (`wander-curator.timer`)| 30-min cadence | Systemd linger enabled (survives logout)|
| **Gnosis Watchdog** | CLI / CI (`scripts/compaction/leash_status.py`)| Pre-commit & Make | Non-zero exit blocks dirty compaction |
| **Node 0 Hub** | FastMCP daemon (`omega-hub`) | `0.0.0.0:8016` | LAN + MagicDNS host header tolerant |

---

*⬡ OMEGA ENGINE ALPHA ⬡ CANONICAL ARCHITECTURE SPECIFICATION ⬡ RATIFIED*
