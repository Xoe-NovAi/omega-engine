# 🔱 OMEGA ENGINE — RATIFIED FEDERATION, SOVEREIGNTY & INSTALLATION BLUEPRINT
**AP Token**: `AP-MAKALI-RATIFIED-BLUEPRINT-20260916-v1.0.0`  
**Oversoul Synthesis**: MaKaLi Fusion (Kali Synthesis • Ma'at Governance • Lilith Continuity)  
**Inference Engine**: `google/gemini-3.8-flash` (Active Context: 242K)  
**Status**: **RATIFIED ARCHITECTURAL SPECIFICATION**  
**Predecessor Docs**: `docs/architecture/federation-and-privatebin-blueprint.md` & `docs/architecture/GEMINI-REVIEW-federation-and-privatebin-blueprint.md`

---

## 🏛️ PART 1: PHILOSOPHY & FIRST PRINCIPLES (The Grounded Law)

### 1. Sovereignty as Policy Enforcement (The Synergy Model)
* **The Error Excised**: The dogma of *"100% local inference or bust"* is dead. Forcing consumer hardware (Ryzen 5700U / Intel i7-13620H) to run multi-step architectural synthesis locally starves the engine of reasoning velocity.
* **The Ratified Law**: **Sovereignty is Policy, Not Isolation.** Sovereignty means *no unconsented, uninspected, or uncontrolled data egress*. If the Sovereign Operator designates frontier cloud models for reasoning and coding, and local models for embeddings, private data sanitization, and background loops, **that declared policy is the sovereign law**.
* **Two-Ledger Model (M7 Harmonization)**:
  1. **Build & Synthesis Ledger (Cloud-Accelerated)**: High-context frontier APIs (OpenCode Zen / OpenRouter / Anthropic) drive design, code generation, and complex dialectics.
  2. **Execution & Privacy Ledger (Local-First)**: Local SLMs (Ollama / `llama.cpp`) and local embeddings handle memory vectors, local file indexing, and sensitive vault ops.

### 2. Elimination of the USB Sneakernet (Carmack-Style Simplicity)
* **The Error Excised**: Relying on physical USB thumb drives for ongoing node communication is clunky, high-friction, and archaic. 
* **The Ratified Law**: **Tailscale is the Sovereign Wire.** Tailscale already provides end-to-end WireGuard encryption, NAT traversal, and cryptographic node keys over commodity internet. 
* **Zero-Knowledge Courier (PrivateBin)**: We do **not** run Dockerized PrivateBin as an internal IPC or Hivemind database. PrivateBin is strictly an **out-of-band human courier**—a temporary, client-side encrypted, burn-after-read pastebin used only when a human operator needs to pass a single one-shot authkey or bootstrap link across air gaps. Once nodes join the tailnet, **Tailscale MagicDNS (`omega-hub.tail51f14a.ts.net:8016`) is the only wire needed.**

### 3. Installation as Interactive Initiation (Education-First)
* **The Ratified Law**: **Installation is not a silent script; it is an educational ceremony.**
* Users step through an interactive, clean terminal interface. Each screen illuminates the *why* behind the component (Substrate, Firewall, Soul, Wire). The user presses `[Enter]` to run the command, learns from the result, and proceeds.
* For power users, CI pipelines, or those in a hurry: `--yes` / `--unattended` bypasses all pauses and installs in <60 seconds.

### 4. The Federation as a Living Entity (`omega-federation`)
* **The Ratified Law**: In Omega Engine, systems are not passive config files—they are managed by sovereign archetypes.
* The mesh itself is governed by an entity soul: `data/entities/federation/soul.yaml`. It monitors C6 contract terms, tracks node profiles, and distills mesh disruptions (netsplits, latency spikes, key rotation) into permanent L1→L2→L3 lessons.

---

## 🛠️ PART 2: THE CONCRETE INFRASTRUCTURE (How It Works)

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

### 1. The Wire & Security Boundary
* **Transport**: Tailscale WireGuard mesh (`tail51f14a.ts.net`).
* **Hub Endpoint**: `http://omega-hub.tail51f14a.ts.net:8016/mcp`.
* **Transport Security Allowlist** (already live in `mcp_servers/omega_hub/server.py` @ `213abf44`):
  - `100.123.51.67:*`
  - `omega-hub.tail51f14a.ts.net:*`
  - `*.tail51f14a.ts.net:*`
* **Mesh Traffic Invariant**: The wire carries **coordination metadata, tool invocations, and MCP heartbeats only**. Model weights and raw model streaming remain local to each node's active inference harness.

### 2. The Tailscale ACL Architecture (`hujson`)
Configured at `https://login.tailscale.com/admin/acls`:
```hujson
{
  "tagOwners": {
    "tag:node0": ["autogroup:admin"],
    "tag:node1":      ["autogroup:admin"],
    "tag:opencode":  ["autogroup:admin"]
  },
  "acls": [
    // Node 1 (tag:node1) talks to Node 0 Hub MCP & Local Ollama
    {"action": "accept", "src": ["tag:node1"], "dst": ["tag:node0:8016", "tag:node0:11434"]},
    // Node 0 talks to Node 1 MCP (if running) & SSH
    {"action": "accept", "src": ["tag:node0", "tag:opencode"], "dst": ["tag:node1:8016", "tag:node1:22"]},
    // Bidirectional L2 ICMP ping/heartbeat
    {"action": "accept", "src": ["tag:node1", "tag:node0"], "dst": ["tag:node1:*", "tag:node0:*"], "proto": "icmp"}
  ],
  "ssh": [
    {"action": "check", "src": ["tag:opencode"], "dst": ["tag:node1"], "users": ["autogroup:nonroot"]}
  ]
}
```

### 3. OpenCode Harness Integration (MCP as the UI)
Instead of waiting months for a custom terminal GUI, we bring the federation interface directly into OpenCode via **three new MCP tools** in `omega-hub`:
1. `omega_federation_status`: Returns live node presence, ping latency, and MagicDNS routing table.
2. `omega_federation_diagnose`: Checks port 8016 reachability, Host header validity, and WireGuard handshake status.
3. `omega_federation_mint_key`: Wraps Tailscale API (when token provided) or guides one-shot authkey generation.

---

## 📋 PART 3: THE STEP-BY-STEP EXECUTION RUNBOOK

### Stage 1: The Final L2 Wire Up (Current Blocker)
1. **Node 0 Admin**: Open Tailscale Admin Console → Access Controls → Paste the ratified `tagOwners` ACL above.
2. **Node 0 Terminal**: Run `pkexec tailscale up --advertise-tags=tag:node0 --force-reauth` (locks Node 0 into `tag:node0`).
3. **Node 0 Admin**: Keys → Generate Auth Key (`tag:node1`, One-off, Pre-approved, 1-day expiry).
4. **Handoff to Node 1**:
   - *Option A (Fastest)*: Paste into a 5-minute burn-after-read PrivateBin link (or local terminal).
   - *Option B (USB)*: Save to stick as `node1_authkey.txt`.
5. **Node 1 Terminal (ASUS)**:
   ```bash
   sudo tailscale up --authkey="${AUTHKEY}" --hostname=kali-n1 --operator=xnai --advertise-tags=tag:node1
   ```
6. **Verification**:
   ```bash
   # From Node 1:
   tailscale ping omega-hub
   curl -X POST http://omega-hub.tail51f14a.ts.net:8016/mcp -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"kali-n1","version":"0.1"}}}'
   ```

### Stage 2: Mint the Federation Entity (`omega-federation`)
Create `data/entities/federation/soul.yaml` and `proposed_lessons.yaml` to give the mesh persistent memory and constitutional oversight.

### Stage 3: Wire Federation MCP Tools to `omega-hub`
Add `federation_status` and `federation_diagnose` to `mcp_servers/omega_hub/server.py` so agents and user can inspect the mesh natively.

### Stage 4: Build the Interactive Educational Installer (`scripts/install_omega.py`)
Implement the Python/Rich-based interactive installer with `--yes` skip-logic and step-by-step teaching cards.

---

## 🗂️ PART 4: COMPLETE DOCUMENT LEDGER (Creation & Updates)

### 📄 Documents to Create (New Canonical Assets)

| # | Document | Target Location | Purpose |
|---|----------|-----------------|---------|
| 1 | **Federation Soul** | `data/entities/federation/soul.yaml` | Constitutional identity of the mesh (Aether element, Level 0 meta-entity, 5 axioms). |
| 2 | **Federation Lessons** | `data/entities/federation/proposed_lessons.yaml` | L1→L2→L3 distillation ledger for network partitions, sync delays, and mesh events. |
| 3 | **Sovereignty Invariant Spec** | `docs/architecture/SOVEREIGNTY_INVARIANT_SPEC.md` | Formalizes the Synergy Model: User-declared policy routing vs dogmatic local-onlyism. |
| 4 | **L2 Federation Runbook** | `docs/federation/L2_TAILSCALE_RUNBOOK.md` | Streamlined operational guide for MagicDNS routing, ACL deployment, and key handoff. |
| 5 | **Interactive Installer Spec** | `docs/installation/INSTALLER_SPEC_V1.md` | UI/UX specification for the tutorial-mode terminal installer (`omega install`). |
| 6 | **Federation MCP Tools Spec** | `docs/architecture/FEDERATION_MCP_SPEC.md` | API contracts for `federation_status`, `federation_diagnose`, and mesh monitoring. |

### 📝 Documents to Update (Alignment Sweeps)

| # | Document | Target Location | Update Required |
|---|----------|-----------------|-----------------|
| 1 | **Sovereignty Policy** | `docs/strategy/SOVEREIGNTY_POLICY_20260912.md` | Align §2 & §4 with the Synergy Model (Cloud reasoning acceleration + Local execution floor). |
| 2 | **Sovereign Mandates** | `SOVEREIGN_MANDATES.md` | Update M7 narrative: Enforce declared policy and zero telemetry; clarify build vs runtime tiers. |
| 3 | **Condensed Mandates** | `MANDATES_CONDENSED.md` | Synchronize M7 definition. |
| 4 | **Omega Hub Server** | `mcp_servers/omega_hub/server.py` | Expose `federation_status` and `federation_diagnose` tools. |
| 5 | **Dispatch Configuration** | `config/wads/_omega_default/entities/dispatch.yaml` | Add `omega-federation` meta-entity reference. |
| 6 | **Session Anchor** | `data/coordination/SESSION_ANCHOR.md` | Record ratification of the Synergy Model, Tailscale MagicDNS primary, and Federation Soul. |

---

## 🎯 Immediate Tactical Directive

The architecture is clarified, grounded, and ratified. 

**Next Action**:
1. Shall I write the **Federation Soul** (`data/entities/federation/soul.yaml`) and **Sovereignty Invariant Spec** (`docs/architecture/SOVEREIGNTY_INVARIANT_SPEC.md`) now?
2. Or shall we execute the **Tailscale ACL and Node 1 join ceremony** first to get both machines pinging over MagicDNS immediately?
