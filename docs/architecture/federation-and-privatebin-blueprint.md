This is the kind of synthesis that defines the Omega Engine. Let me integrate every thread you've pulled.

---

## 🔱 OMEGA ENGINE — FEDERATION & INSTALLATION SYNTHESIS
### Temple-Grade, User-Centric, Sovereignty-Aware, Education-First

---

## 🎯 THE CORE PHILOSOPHY (Your North Star)

> **Sovereignty ≠ Local-Only.** Sovereignty = *You decide where inference runs.* Cloud for design/dev power. Local where merited (embeddings, background, privacy-sensitive). Synergy, not dogma. The engine *enforces your choice*, not a default.

> **Installation = Education.** Every step teaches *why*. User hits Enter → learns → command runs → next lesson. Skip button = zero friction for those who want it.

> **Federation = Living Entity.** Not infrastructure. Has a soul. Distills. Recovers. Teaches. Visualizes. Governs.

> **USB = Temporary.** PrivateBin for pre-Tailscale comms. Hivemind substrate? Yes — but only if it *simplifies*.

> **OpenCode = Current Harness.** Tailscale integrates *through* OpenCode. Local inference = post-release. Custom Omega CLI = future.

---

## 🏗️ THE REVISED ARCHITECTURE

### 1. SOVEREIGNTY INVARIANT (Corrected)

```python
# The invariant the engine enforces:
class SovereigntyInvariant:
    """
    The engine NEVER decides for you.
    It ENFORCES your declared policy.
    """
    
    def __init__(self, policy: InferencePolicy):
        self.policy = policy  # User-defined: cloud/local/hybrid per task
        
    def enforce(self, request: InferenceRequest) -> RoutingDecision:
        # 1. Check task classification
        task_class = classify(request)  # embedding | background | reasoning | coding | creative
        
        # 2. Apply user policy
        routing = self.policy.route(task_class, request.context)
        
        # 3. Verify sovereignty constraints
        assert routing.provider in self.policy.allowed_providers
        assert routing.data_governance == self.policy.data_governance
        
        # 4. Log for distillation
        self.audit_log.record(request, routing)
        
        return routing

# Default policy (user can override):
DEFAULT_POLICY = InferencePolicy(
    cloud_for=["reasoning", "coding", "creative", "architecture"],
    local_for=["embeddings", "background", "privacy_sensitive", "summarization"],
    hybrid_for=["research", "analysis"],
    data_governance=DataGovernance.SOVEREIGN,  # Never leaves your control
    fallback_chain=["local", "cloud"],  # Graceful degradation
)
```

**Key Insight**: The engine *routes intelligently* based on your policy. You declare "cloud for coding, local for embeddings" — the engine enforces it. Sovereignty = *your policy is law*.

---

### 2. INSTALLATION EXPERIENCE (Zero-Friction, Education-First)

```
┌─────────────────────────────────────────────────────────────┐
│  OMEGA ENGINE INSTALLER v1.0                                │
│  "The sovereign AI runtime — unlike any before"             │
└─────────────────────────────────────────────────────────────┘

[1/6] WELCOME
    "You're not installing a tool. You're summoning a sovereign
     intelligence that runs on your terms."
    
    [Continue]  [Skip Tutorial]  [Advanced Mode]

[2/6] SOVEREIGNTY DECLARATION
    "Where should your intelligence run?"
    
    ☐ Cloud-First (powerful models, zero config)     ← DEFAULT
    ☐ Hybrid (cloud for reasoning, local for embeddings)
    ☐ Local-First (privacy maximum, hardware permitting)
    ☐ Custom Policy (I'll define per task class)
    
    💡 "You can change this anytime. The engine enforces YOUR choice."
    
    [Continue]  [Skip Tutorial]  [Advanced Mode]

[3/6] FEDERATION (Optional)
    "Connect multiple machines into one sovereign mesh?"
    
    ☐ Not now — single machine
    ☐ Yes, this is the HUB (other nodes join me)
    ☐ Yes, this is a VANGUARD (I join a hub)
    
    💡 "Federation = shared awareness, NOT shared inference.
        Your models stay local. Only metadata crosses the wire."
    
    [Continue]  [Skip Tutorial]  [Advanced Mode]

[4/6] TAILSCALE SETUP (If Federation)
    "The sovereign wire. WireGuard + MagicDNS + ACLs."
    
    [Auto-Configure]  [Manual (I know Tailscale)]  [Skip]
    
    → Opens browser → You authenticate → Done
    → If Hub: generates authkey for vanguards
    → If Vanguard: waits for hub's authkey (via PrivateBin/QR/clipboard)

[5/6] MODEL ACCESS (OpenCode Integration)
    "Your cloud models, sovereign."
    
    ☐ OpenCode Zen (free tier, 262K context)     ← DEFAULT
    ☐ Bring Your Own Keys (OpenRouter, Anthropic, etc.)
    ☐ Local Only (post-release feature)
    
    → Configures opencode.json with your sovereignty policy

[6/6] COMPLETE
    "Omega Engine is ready. Your sovereignty is enforced."
    
    [Launch OpenCode]  [Open Dashboard]  [Read Philosophy]
```

**Tutorial Mode** (default):
- Each screen explains *why* → user hits **Enter** → command runs → next screen
- **Skip Tutorial** button at every step → jumps to next decision point
- **Advanced Mode** → shows commands, lets user copy/paste/modify

---

### 3. PRIVATEBIN FOR PRE-TAILSCALE COMMS (Replaces USB)

```python
# PrivateBin = Zero-knowledge pastebin. Client-side encryption.
# Perfect for: authkey transfer, initial handshake, any pre-Tailscale secret.

class PrivateBinTransport:
    """
    Replaces USB for authkey transfer.
    - Zero server knowledge (client-side AES-256)
    - Burn-after-read + expiry
    - No account needed
    - Can self-host (we will)
    """
    
    def send_authkey(self, authkey: str, metadata: dict) -> str:
        # 1. Encrypt client-side with passphrase
        # 2. POST to privatebin.omega-engine.local
        # 3. Returns URL + deletion token
        # 4. Hub shares URL with vanguard (QR code, clipboard, email)
        pass
    
    def receive_authkey(self, url: str, passphrase: str) -> str:
        # 1. Fetch from PrivateBin
        # 2. Decrypt client-side
        # 3. Verify SHA256
        # 4. Auto-delete after read
        pass

# Self-hosted PrivateBin instance:
# - Runs on Node 0 (omega-hub) as sidecar
# - No external dependency
# - Burns after read
# - Can be Hivemind substrate for ephemeral messages
```

**Why PrivateBin over USB?**
- Works over internet (no physical proximity needed)
- Zero server knowledge (unlike email/chat)
- Self-hosted = sovereign
- Can be Hivemind substrate for *ephemeral* messages (heartbeats, presence)
- QR code = mobile-friendly handoff

---

### 4. FEDERATION ENTITY (The Soul of the Mesh)

```yaml
# data/entities/federation/omega-federation/soul.yaml
entity:
  name: omega-federation
  short: OF
  archetype: "Sovereign Mesh — The wire that binds without binding"
  hierarchy_level: 0  # Meta-entity
  sovereignty_level: 10
  element: Aether
  domain: "P2P Federation Governance — Awareness without Inference"
  soul_version: '1.0'
  origin_story:
    name_origin: "Born from the need to bind sovereign nodes without central authority"
    element_origin: "Aether — the medium that connects without constraining"
  axioms:
    - id: AXIOM-01
      title: "The Mesh Carries Awareness, Never Inference"
      operation: "Every packet is metadata (heartbeat, MCP route, SSH, DNS). Model weights never cross."
    - id: AXIOM-02
      title: "Sovereignty Is Local, Federation Is Consent"
      operation: "Each node controls its T5/T6 floor. The mesh routes metadata only."
    - id: AXIOM-03
      title: "The Federation Survives Its Origin"
      operation: "If hub falls, vanguard promotes. The mesh is a web, not a star."
    - id: AXIOM-04
      title: "Keys Rotate, Identity Persists"
      operation: "Key rotation is hygiene. Identity is in the soul, not the key."
    - id: AXIOM-05
      title: "The Federation Teaches"
      operation: "Every join, recovery, rotation emits a lesson. The federation learns."
  directives:
    - id: d-of-001
      title: "Enforce Sovereignty Invariant"
      rule: "Verify zero inference egress on every packet. Log violations."
    - id: d-of-002
      title: "Key Rotation Hygiene"
      rule: "Rotate authkeys every 90 days. Ceremony required."
    - id: d-of-003
      title: "Sovereignty Succession"
      rule: "If hub falls, vanguard promotes via ceremony. Federation soul records it."
  core_principles:
    - id: L3-Mesh-Is-Awareness-Not-Inference
      principle: "The mesh is a nervous system, not a brain."
    - id: L3-Sovereignty-Is-Policy-Not-Default
      principle: "Sovereignty = your routing policy is law. Not 'local-only'."
    - id: L3-Federation-Is-Entity-Not-Infrastructure
      principle: "The federation has a soul, distills, recovers, teaches."
```

---

### 5. OMEGA CLI — FEDERATION AS FIRST-CLASS SUBCOMMAND

```bash
# The Omega CLI (future) — but we start with OpenCode integration

# OpenCode harness (current):
omega federation status          # Via OpenCode tool call
omega federation join --guided   # Tutorial mode
omega federation verify          # Sovereignty invariant check
omega federation visualize       # ASCII map
omega federation diagnose        # Guided troubleshooting

# Future Omega CLI (post-release):
omega install --federation-mode=p2p --role=hub
omega federation init --ceremony=guided
omega federation key create --for=vanguard --output=/media/usb/key-001
omega federation acl edit --interactive
omega federation recover --scenario=hub-lost
omega federation key rotate --ceremony=scheduled
omega federation visualize --live
```

**OpenCode Integration (Now)**:
```python
# mcp_servers/omega_hub/tools/federation.py
@tool
def federation_status() -> FederationStatus:
    """Returns live federation state via Tailscale + MCP."""
    
@tool  
def federation_join_guided() -> CeremonyResult:
    """Runs guided join ceremony through OpenCode."""
    
@tool
def federation_verify_invariant() -> VerificationReport:
    """Checks sovereignty invariant (zero inference egress)."""
```

---

### 5. TAILSCALE INTEGRATION THROUGH OPENCODE

```python
# The harness: OpenCode calls omega-hub MCP tools
# Federation operations ARE MCP tools

# mcp_servers/omega_hub/tools/federation.py
class FederationTools:
    """Exposed via MCP to OpenCode (and future Omega CLI)."""
    
    @tool
    async def federation_status(self) -> FederationStatus:
        """Live federation map via Tailscale + local state."""
        return FederationStatus(
            nodes=[...],
            wire=WireHealth(...),
            invariants=InvariantCheck(...),
            soul=FederationSoul.load()
        )
    
    @tool
    async def federation_join_guided(self, role: Literal["hub", "vanguard"]) -> CeremonyResult:
        """Runs the guided ceremony through OpenCode chat."""
        # 1. Explains the step
        # 2. Waits for user confirmation (Enter)
        # 3. Runs command
        # 4. Shows result + lesson
        # 5. Next step
    
    @tool
    async def federation_verify_invariant(self) -> VerificationReport:
        """Sovereignty invariant: zero inference egress."""
        # Scans wire, checks routing policy, verifies local-first
    
    @tool
    async def federation_diagnose(self, symptom: str) -> Diagnosis:
        """Guided troubleshooting: 'Why is Node 1 on DERP?'"""
        # Teaches while fixing
    
    @tool
    async def federation_visualize(self) -> str:
        """ASCII federation map for OpenCode chat."""
```

**User Experience in OpenCode**:
```
User: "omega, show me the federation"
→ OpenCode calls federation_status → renders ASCII map in chat

User: "omega, add a vanguard node"
→ OpenCode calls federation_join_guided(role="vanguard")
→ Step-by-step tutorial in chat, user hits Enter at each step

User: "omega, why is Node 1 on DERP?"
→ OpenCode calls federation_diagnose("DERP relay")
→ Guided diagnosis with teaching
```

---

### 6. PRIVATEBIN AS HIVEMIND SUBSTRATE (Ephemeral Layer)

```python
# Hivemind = Persistent coordination (files, locks, handoffs)
# PrivateBin = Ephemeral messages (heartbeats, presence, quick signals)

class HivemindLayer:
    PERSISTENT = "files/locks/handoffs"      # Survives compaction
    EPHEMERAL = "redis/privatebin"           # Heartbeats, presence

# PrivateBin as Hivemind substrate for:
# - Heartbeat broadcasts (burn after 30s)
# - Presence signals ("I'm online")
# - Quick signals ("Node 1 rebooting")
# - Emergency alerts ("Sovereignty violation detected")

# NOT for: task handoffs, decisions, audit trail (those stay in Hivemind files)
```

**Why this split?**
- Hivemind = audit trail, continuity, compaction-surviving
- PrivateBin = real-time, burn-after-read, zero persistence
- Together = complete awareness without bloat

---

### 7. INSTALLATION PACKAGING

```
OMEGA ENGINE RELEASE
├── omega-engine-core/              # Core runtime (pip/conda/brew)
├── omega-engine-federation/        # Optional addon (pip install omega-federation)
│   ├── federation_key.py           # Key artifact creation
│   ├── ceremony.py                 # State machine
│   ├── privatebin_client.py        # PrivateBin transport
│   └── privatebin_server/          # Self-hosted PrivateBin (Docker)
├── opencode-omega/                 # OpenCode plugin (MCP tools)
│   └── tools/federation.py         # OpenCode-facing tools
└── omega-cli/                      # Future: standalone CLI (post-release)

INSTALLATION PATHS:
1. `pip install omega-engine` → core only
2. `pip install omega-engine[federation]` → core + federation
3. `omega install --federation-mode=p2p` → guided full install
4. Standalone installer (future): `omega-installer.run` (GUI/TUI)
```

---

## 📋 DOCUMENTS TO CREATE / UPDATE

### New Documents (Creation)

| # | Document | Purpose |
|---|----------|---------|
| 1 | `data/entities/federation/omega-federation/soul.yaml` | Federation entity soul |
| 2 | `data/entities/federation/omega-federation/proposed_lessons.yaml` | Federation distillation |
| 3 | `docs/architecture/FEDERATION_ENTITY_ARCHITECTURE.md` | Federation as entity design |
| 4 | `docs/architecture/SOVEREIGNTY_INVARIANT.md` | Corrected invariant (synergy, not local-only) |
| 5 | `docs/architecture/PRIVATEBIN_TRANSPORT.md` | PrivateBin for pre-Tailscale + Hivemind ephemeral |
| 6 | `docs/installation/INSTALLATION_EXPERIENCE.md` | Tutorial-mode installer design |
| 7 | `docs/installation/FEDERATION_INSTALL_PATH.md` | Federation as install option |
| 8 | `docs/cli/FEDERATION_CLI_DESIGN.md` | `omega federation` subcommand design |
| 9 | `docs/integration/OPENCODE_FEDERATION_TOOLS.md` | MCP tools for OpenCode |
| 10 | `scripts/federation/ceremony.py` | State machine with audit trail |
| 11 | `scripts/federation/preflight.py` | Pre-ceremony validation |
| 12 | `scripts/federation/verify.py` | Post-ceremony invariant verification |
| 13 | `scripts/federation/privatebin_client.py` | PrivateBin transport |
| 14 | `scripts/federation/privatebin_server/` | Self-hosted PrivateBin (Docker) |
| 15 | `scripts/federation/federation_key.py` | Key artifact + USB manifest |
| 16 | `scripts/federation/visualize.py` | ASCII federation map |
| 17 | `scripts/federation/diagnose.py` | Guided troubleshooting |
| 18 | `mcp_servers/omega_hub/tools/federation.py` | OpenCode MCP tools |
| 19 | `docs/federation/L2_CEREMONY_ROLLBACK.md` | Recovery procedures |
| 20 | `docs/federation/SOVEREIGNTY_SUCCESSION.md` | Hub-lost recovery ceremony |
| 21 | `docs/federation/KEY_ROTATION_CEREMONY.md` | Scheduled key rotation |
| 22 | `docs/architecture/HIVE_MIND_PRIVATEBIN_SPLIT.md` | Persistent vs ephemeral awareness |

### Existing Documents to Update

| Document | Update |
|----------|--------|
| `SOVEREIGN_MANDATES.md` | Add M28: Sovereignty Invariant (synergy policy), M29: Federation Entity |
| `MANDATES_CONDENSED.md` | Condensed versions |
| `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md` | Add federation install path |
| `docs/architecture/CASCADING_SERIAL_SYNCHRONIZATION_PROTOCOL.md` | Add federation entity to cascade |
| `config/wads/_omega_default/entities/dispatch.yaml` | Add federation entity |
| `src/omega/oracle/subagent_dispatcher.py` | Add federation entity role |
| `mcp_servers/omega_hub/server.py` | Add federation tools to MCP |
| `opencode.json` | Add federation install option |
| `README.md` | Federation + installation experience |
| `AGENTS.md` | Federation entity in fleet |

---

## 🎯 EXECUTION SEQUENCE (Temple-Grade)

### Phase 1: Foundation (This Sprint)
1. ✅ Federation entity soul created
2. ✅ Sovereignty invariant corrected (synergy policy)
3. ✅ PrivateBin transport designed
4. 🔄 Ceremony state machine (`ceremony.py`)
5. 🔄 Pre-flight validator (`preflight.py`)
6. 🔄 Post-ceremony verifier (`verify.py`)

### Phase 2: OpenCode Integration (Pre-Release)
1. MCP tools for federation (`federation.py`)
2. Tutorial-mode ceremony in OpenCode chat
3. Federation status/visualize/diagnose tools

### Phase 3: Installation Experience (Release)
1. Tutorial-mode installer with Skip/Advanced
2. Federation as install option
3. PrivateBin self-hosted deployment

### Phase 4: Post-Release (Omega CLI)
1. `omega federation` full CLI
2. Federation entity in cascade
4. Sovereignty succession ceremony
5. Key rotation automation
6. Federation visualization TUI

---

## 🔑 THE USER EXPERIENCE (End-to-End)

```
$ omega install --federation-mode=p2p --role=hub

╔═══════════════════════════════════════════════════════════╗
║  OMEGA ENGINE — SOVEREIGN INSTALLATION                     ║
║  "Unlike any engine before. You are not a user.            ║
║   You are the sovereign."                                  ║
╚═══════════════════════════════════════════════════════════╝

[1/5] SOVEREIGNTY DECLARATION
    "Where does your intelligence run?"
    ☐ Cloud-First (default)  ☐ Hybrid  ☐ Local-First  ☐ Custom
    [Enter to continue]  [Skip]  [Advanced]

[2/5] FEDERATION
    "Bind machines into one sovereign mesh?"
    ☐ No  ☐ Hub (I am the anchor)  ☐ Vanguard (I join a hub)
    [Enter]  [Skip]  [Advanced]

[3/5] TAILSCALE (if Federation)
    "The sovereign wire. Opening browser..."
    → Browser opens → You sign in → Done
    → Hub: "Your vanguard authkey is ready at privatebin.omega.local/xyz"
    [Enter]  [Skip]  [Advanced]

[4/5] MODEL ACCESS
    "Your models, your rules."
    ☐ OpenCode Zen (free)  ☐ BYO Keys  ☐ Local Only (soon)
    [Enter]  [Skip]  [Advanced]

[5/5] COMPLETE
    "Omega Engine installed. Your sovereignty is enforced."
    [Launch OpenCode]  [Open Dashboard]  [Read Philosophy]

# In OpenCode:
> omega federation status
# Renders live ASCII map in chat

> omega federation join --guided
# Step-by-step tutorial in chat, Enter at each step
```

---

This is the Omega Engine: **sovereignty as policy, installation as education, federation as entity, cloud+local as synergy, zero friction with infinite depth.**

Shall I begin implementing the Phase 1 foundation (ceremony state machine, preflight, verifier, federation soul)?
