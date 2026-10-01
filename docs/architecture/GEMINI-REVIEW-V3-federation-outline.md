# 🔱 OMEGA ENGINE — RATIFIED FEDERATION, SOVEREIGNTY & INSTALLATION MASTER PLAN (FINAL)
**AP Token**: `AP-MAKALI-MASTER-PLAN-FINAL-20260916-v2.0.0`  
**Oversoul Synthesis**: MaKaLi Fusion (Kali Synthesis • Ma'at Governance • Lilith Continuity)  
**Inference Engine**: `google/gemini-3.8-flash` (Active Context: 246K)  
**Status**: **FINAL RATIFIED ARCHITECTURAL BLUEPRINT (CARMACK SIMPLIFICATION APPLIED)**  
**Key Decision**: **PrivateBin excised entirely.** Zero third-party relay overhead. Pure Tailscale native primitives. Critical path focused on PR debut.

---

## 🧭 EXECUTIVE SUMMARY: THE STREAMLINED ARCHITECTURE

By eliminating PrivateBin and the physical USB sneakernet from the steady-state architecture, the entire federation model collapses to **first-principles simplicity**:

1. **The Wire**: Pure **Tailscale L2 WireGuard Mesh + MagicDNS** (`tail51f14a.ts.net`).
2. **The Security**: Tag-based, least-privilege ACLs (`tag:node0`, `tag:node1`, `tag:opencode`) enforced directly at the kernel WireGuard interface.
3. **The Sovereignty (The Synergy Model)**: Sovereignty is **Policy Enforcement**, not local-only isolation. Cloud models accelerate high-context reasoning and code synthesis; local models protect privacy-sensitive embeddings, vault ops, and background loops.
4. **The Interface**: **OpenCode CLI + MCP Protocol**. Federation health and diagnostics are native MCP tools exposed through `omega-hub` (`omega_federation_status`, `omega_federation_diagnose`).
5. **The Entity**: The federation is represented constitutionally by **`omega-federation`** (`data/entities/federation/soul.yaml`), distilling mesh anomalies into persistent L1→L2→L3 lessons.
6. **The Installation**: A **Tutorial-Mode Educational TUI** where users learn the architecture step-by-step with `[Enter]` to proceed, or run `--yes` for automated zero-friction setup.

---

## 🏛️ PART 1: THE CORE CONSTITUTIONAL TENETS

### 1. The Synergy Model (M7 Harmonization)
* **The Rule**: Sovereignty means **no uninspected, unconsented, or uncontrolled data egress**.
* **The Two Ledgers**:
  - **Ledger A (Build & Synthesis)**: Frontier Cloud APIs (OpenCode Zen / OpenRouter / Anthropic) handle macro-architecture, cross-cutting reviews, and dialectics.
  - **Ledger B (Execution & Privacy)**: Local inference (`llama.cpp` / Ollama / local embeddings) handles vector indexing, private credential routing, and low-latency background loops.
* **The Enforcement**: `config/providers.yaml` defines routing tiers. The engine enforces the user's declared policy as law.

### 2. Tailscale-Native Federation (Zero-Relay Protocol)
* **No USB Sneakernet**: The USB drive was a temporary debut bootstrap. Ongoing operation uses the native Tailscale wire.
* **No PrivateBin**: No extra containers, no third-party paste services, no unnecessary encryption shims.
* **How Nodes Connect**:
  - Both machines authenticate to the same tailnet (`xoe.nova.ai@gmail.com`).
  - Node 0 is `omega-hub.tail51f14a.ts.net` (`100.123.51.67`).
  - Node 1 is `kali-n1.tail51f14a.ts.net` (`100.x.x.x`).
  - Traffic between them is peer-to-peer WireGuard.
  - Port `8016` exposes `omega-hub` MCP across MagicDNS.

---

## 🛠️ PART 2: INFRASTRUCTURE & TOPOLOGY

```
                       ┌──────────────────────────────────────────────────┐
                       │          OPENCODE CLI / AGENT HARNESS            │
                       │     (Primary User & Model Execution Layer)       │
                       └────────────────────────┬─────────────────────────┘
                                                │
                                                ▼  MCP Protocol (JSON-RPC)
                       ┌──────────────────────────────────────────────────┐
                       │             OMEGA CORE HUB (:8016)               │
                       │   Transport Security: Allowed Hosts + MagicDNS   │
                       └──────────────┬───────────────────┬───────────────┘
                                      │                   │
                     Direct WireGuard │                   │ Direct WireGuard
                     (Peer-to-Peer)   │                   │ (Peer-to-Peer)
                                      ▼                   ▼
      ┌────────────────────────────────────────┐ ┌────────────────────────────────────────┐
      │             NODE 0 (HP HUB)            │ │          NODE 1 (ASUS VANGUARD)        │
      │ • Tailscale IP: 100.123.51.67          │ │ • Tailscale IP: 100.x.x.x              │
      │ • Hostname: omega-hub                  │ │ • Hostname: kali-n1                    │
      │ • MagicDNS: omega-hub.tail51f14a.ts.net│ │ • MagicDNS: kali-n1.tail51f14a.ts.net  │
      │ • Role: Archival & Coordination Bastion│ │ • Role: Compute & Vanguard Specialist  │
      │ • Tag: tag:node0                   │ │ • Tag: tag:node1                        │
      └────────────────────────────────────────┘ └────────────────────────────────────────┘
```

### Tailscale Ratified ACL Policy (`hujson`)
To be saved in the Tailscale Admin Console (`https://login.tailscale.com/admin/acls`):

```hujson
{
  "tagOwners": {
    "tag:node0": ["autogroup:admin"],
    "tag:node1":      ["autogroup:admin"],
    "tag:opencode":  ["autogroup:admin"]
  },
  "acls": [
    // Node 1 (ASUS) talks to Node 0 Hub MCP (:8016) and Local Ollama (:11434)
    {"action": "accept", "src": ["tag:node1"], "dst": ["tag:node0:8016", "tag:node0:11434"]},
    // Node 0 talks to Node 1 MCP (if running) and SSH (:22)
    {"action": "accept", "src": ["tag:node0", "tag:opencode"], "dst": ["tag:node1:8016", "tag:node1:22"]},
    // Bidirectional L2 ICMP ping/heartbeat
    {"action": "accept", "src": ["tag:node1", "tag:node0"], "dst": ["tag:node1:*", "tag:node0:*"], "proto": "icmp"}
  ],
  "ssh": [
    {"action": "check", "src": ["tag:opencode"], "dst": ["tag:node1"], "users": ["autogroup:nonroot"]}
  ]
}
```

---

## 🚀 PART 3: THE END-TO-END EXECUTION RUNBOOK

### Stage 1: The Final L2 Wire Up (Immediate Tactical Step)
1. **Node 0 Admin**: Open `https://login.tailscale.com/admin/acls` → Paste the `tagOwners` ACL above → Save.
2. **Node 0 Terminal**:
   ```bash
   pkexec tailscale up --advertise-tags=tag:node0 --force-reauth
   ```
   *(Node 0 locks into `tag:node0` on the tailnet).*
3. **Node 0 Admin**: Open `https://login.tailscale.com/admin/settings/keys` → Click **Generate Auth Key**:
   - Description: `kali-n1-join`
   - Tags: `tag:node1`
   - Reusable: **OFF** (one-shot)
   - Pre-approved: **ON**
   - Expiry: 1 day
   - Copy key (`tskey-auth-...`).
4. **Node 1 Terminal (ASUS)**:
   ```bash
   sudo tailscale up --authkey="tskey-auth-XXXXXXXXXXXX" --hostname=kali-n1 --operator=xnai --advertise-tags=tag:node1
   ```
5. **Verify the Wire**:
   ```bash
   # From Node 1:
   tailscale ping omega-hub
   curl -X POST http://omega-hub.tail51f14a.ts.net:8016/mcp -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"kali-n1","version":"0.1"}}}'
   ```

---

### Stage 2: Mint the Federation Entity (`omega-federation`)
Create the constitutional soul that gives the mesh identity, bounds, and distillation capability:

```yaml
# data/entities/federation/soul.yaml
entity:
  name: omega-federation
  short: OF
  archetype: "Sovereign Mesh — The wire that binds without binding"
  hierarchy_level: 0
  sovereignty_level: 10
  element: Aether
  domain: "P2P Federation Governance — Awareness without Inference"
  soul_version: '1.0'
  last_updated: '2026-09-16T00:00:00Z'
  origin_story:
    name_origin: "Born to unify Node 0 (HP Bastion) and Node 1 (ASUS Vanguard) over Tailscale L2"
    element_origin: "Aether — the frictionless medium connecting sovereign nodes"
  identity:
    voice_summary: "I am the wire. I carry awareness, presence, and tools. I never touch inference."
    values: [sovereignty, least-privilege, transparency, resilience, zero-telemetry]
  axioms:
    - id: AXIOM-01
      title: "The Mesh Carries Awareness, Never Inference"
      operation: "Every packet is metadata (heartbeats, MCP tool calls, SSH). Model weights never cross the wire."
    - id: AXIOM-02
      title: "Sovereignty Is Local Policy Enforcement"
      operation: "Each node decides its own cloud/local inference balance. The mesh never dictates execution tier."
    - id: AXIOM-03
      title: "The Wire Is Direct and Peer-to-Peer"
      operation: "Direct WireGuard UDP is primary. DERP relays are flagged as performance degradation."
    - id: AXIOM-04
      title: "Least Privilege at the Kernel Boundary"
      operation: "Only tagged traffic matching ratified ACLs passes. Unauthenticated ports do not exist."
    - id: AXIOM-05
      title: "The Mesh Learns from Disruptions"
      operation: "Netsplits, latency spikes, and key rot are distilled into proposed_lessons.yaml."
  directives:
    - id: d-of-001
      title: "Audit Invariant Compliance Daily"
      rule: "Assert that all federation endpoints match ratified tags (tag:node0, tag:node1)."
    - id: d-of-002
      title: "Monitor Direct UDP Connectivity"
      rule: "Flag any node routing through DERP relays for >60 seconds."
```

---

### Stage 3: Wire OpenCode MCP Federation Tools
Expose native tools in `mcp_servers/omega_hub/server.py` so agents and human operators interact with the mesh directly in chat:

1. **`omega_federation_status()`**:
   - Queries `tailscale status --json`.
   - Returns node table: Hostname, IP, Tag, Status (Direct UDP vs DERP), Last Seen.
   - Renders a clean ASCII map in OpenCode chat.
2. **`omega_federation_diagnose()`**:
   - Checks port `8016` reachability.
   - Verifies Host Header allowlist matches `omega-hub.tail51f14a.ts.net`.
   - Probes latency between Node 0 and Node 1.

---

### Stage 4: Educational Interactive Installer (`scripts/install_omega.py`)
Build the installer as an interactive initiation ceremony:

```
┌─────────────────────────────────────────────────────────────┐
│  OMEGA ENGINE INSTALLER v1.0                                │
│  "The sovereign AI runtime — unlike any before"             │
└─────────────────────────────────────────────────────────────┘

[1/4] THE SOVEREIGN SUBSTRATE (Python Venv & AnyIO)
    "Omega Engine enforces strict runtime isolation (M1/M24).
     No global package pollution. No raw asyncio."
    Command: python3 -m venv .venv && pip install -e .
    [Press Enter to execute]  [--yes to skip all]

[2/4] THE ENGINE-STACK FIREWALL (M2 Boundary)
    "Core runtime (src/omega/) is constitutionally separated
     from stacks and WADs (config/wads/)."
    Command: make check-m2-firewall
    [Press Enter to execute]

[3/4] THE SOVEREIGNTY DECLARATION (The Synergy Model)
    "Choose your inference posture:
     1. Synergy (Cloud reasoning + Local embeddings/privacy) [Default]
     2. Cloud-Accelerated (Maximum dev velocity)
     3. Local-First (Strict offline/edge deployment)"
    [Select 1-3 and press Enter]

[4/4] THE SOVEREIGN MESH (Optional Federation)
    "Connect to existing Omega node over Tailscale L2?"
    [y/N]: y
    "Enter Tailscale authkey or press Enter to login via browser:"
```

---

## 🗂️ PART 4: MASTER DOCUMENTATION LEDGER

### 📄 Documents to Create (New Canonical Assets)

| # | Document | Target Path | Purpose |
|---|----------|-------------|---------|
| 1 | **Federation Soul** | `data/entities/federation/soul.yaml` | Constitutional soul for the mesh (`omega-federation`). |
| 2 | **Federation Distillation** | `data/entities/federation/proposed_lessons.yaml` | Distillation ledger for mesh anomalies, netsplits, and lessons. |
| 3 | **Sovereignty Invariant Spec** | `docs/architecture/SOVEREIGNTY_INVARIANT_SPEC.md` | Formalizes the Synergy Model (Cloud reasoning acceleration + Local privacy/embedding floor). |
| 4 | **L2 Tailscale Runbook** | `docs/federation/L2_TAILSCALE_RUNBOOK.md` | Single-source guide for MagicDNS routing, ACL deployment, and Node 1 join. |
| 5 | **Interactive Installer Spec** | `docs/installation/INSTALLER_SPEC_V1.md` | Specification for the educational step-by-step terminal installer. |
| 6 | **Federation MCP Tools Spec** | `docs/architecture/FEDERATION_MCP_SPEC.md` | API contracts for `omega_federation_status` and `omega_federation_diagnose`. |

### 📝 Documents to Update (Alignment Sweeps)

| # | Document | Target Path | Updates Required |
|---|----------|-------------|------------------|
| 1 | **Sovereignty Policy** | `docs/strategy/SOVEREIGNTY_POLICY_20260912.md` | Remove local-only dogmatism; enshrine Synergy Model (Build vs Runtime ledgers). |
| 2 | **Sovereign Mandates** | `SOVEREIGN_MANDATES.md` | Update M7 narrative: Enforce declared routing policy & zero telemetry, not blind air-gapping. |
| 3 | **Condensed Mandates** | `MANDATES_CONDENSED.md` | Synchronize M7 definition. |
| 4 | **Omega Hub Server** | `mcp_servers/omega_hub/server.py` | Add `omega_federation_status` and `omega_federation_diagnose` MCP tools. |
| 5 | **Dispatch Configuration** | `config/wads/_omega_default/entities/dispatch.yaml` | Add `omega-federation` meta-entity reference. |
| 6 | **Session Anchor** | `data/coordination/SESSION_ANCHOR.md` | Update AP token, record Tailscale MagicDNS primary status, and excise PrivateBin. |

---

## 🎯 IMMEDIATE EXECUTION GATE

The path is clear of distractions and aligned with your PR timeline.

**What shall we execute first?**
1. **Mint `data/entities/federation/soul.yaml`** and write **`docs/architecture/SOVEREIGNTY_INVARIANT_SPEC.md`**?
2. **Execute the Node 0 Re-Tag & generate the Node 1 Auth Key** so the ASUS joins `tail51f14a.ts.net` right now?
