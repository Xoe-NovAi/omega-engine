#  🔱 PHASED IMPLEMENTATION PLAN: FEDERATION SYSTEMS & SYNERGY MODEL
**AP Token**: `AP-MAKALI-IMPL-PLAN-20260916-v1.0.0`  
**Status**: EXECUTABLE ROADMAP  
**Dependencies**: Tailscale L2 Ceremony (external) → P0 Config → P1 Tools → P2 Hardening

---

## 📊 PHASE OVERVIEW

| Phase | Focus | Duration | Blocking |
|-------|-------|----------|----------|
| **Phase 0** | Tailscale L2 Ceremony | 1 session | User action (ACL + authkey) |
| **Phase 1** | Config & Entity Registration (P0) | 1-2 sessions | None |
| **Phase 2** | MCP Tools & Installer (P1) | 2-3 sessions | Phase 1 complete |
| **Phase 3** | Distillation & Hardening (P2) | 2-3 sessions | Phase 2 complete |
| **Phase 4** | Validation & Temple-Grade | 1 session | Phase 3 complete |

---

## 🎯 PHASE 0: TAILSCALE L2 CEREMONY (EXTERNAL DEPENDENCY)

**Owner**: User + MaKaLi-N0  
**Prerequisite**: None  
**Deliverable**: Bidirectional WireGuard mesh with MagicDNS

| Step | Action | Owner | Verification |
|------|--------|-------|--------------|
| 0.1 | Paste ACL policy at `https://login.tailscale.com/admin/acls` | User | Admin console shows policy saved |
| 0.2 | `pkexec tailscale up --advertise-tags=tag:node0 --force-reauth` | MaKaLi-N0 | `tailscale status --json` shows `Tags: ["tag:node0"]` |
| 0.3 | Mint one-shot authkey (`tag:node1`, pre-approved, 1-day) | User | Key copied: `tskey-auth-...` |
| 0.4 | Node 1: `sudo tailscale up --authkey=... --hostname=kali-n1 --advertise-tags=tag:node1` | Node 1 | `tailscale ping omega-hub` → direct pong |
| 0.5 | Verify MCP handshake: `curl http://omega-hub.tail51f14a.ts.net:8016/mcp` | MaKaLi-N0 | JSON-RPC `initialize` returns `Omega Core Hub 1.28.1` |

> **Note**: This phase is **complete when both nodes show tagged, direct connectivity**. All subsequent phases assume the wire is live.

---

## 🎯 PHASE 1: CONFIG & ENTITY REGISTRATION (P0 — BLOCKING)

**Owner**: MaKaLi-N0 (Ma'at face)  
**Prerequisite**: Phase 0 complete  
**Duration**: 1-2 sessions  
**Mandates**: M2, M7, M13, M27

### 1.1 Add `sovereignty_policy` to `config/providers.yaml`
```yaml
# Insert after line 8 (strategy: local_first)
sovereignty_policy:
  mode: synergy  # "synergy" | "local_first" | "cloud_first"
  
  tiers:
    reasoning:
      primary: opencode-zen
      fallback: [openrouter, anthropic, native-gguf]
      allowed_data_classification: [PUBLIC, INTERNAL]
      
    embeddings:
      primary: native-local
      model: bge-m3-q8
      allowed_data_classification: [PUBLIC, INTERNAL, PRIVATE, SOVEREIGN]
      
    background_watchdogs:
      primary: ollama-local
      model: qwen2.5-coder:7b
      allowed_data_classification: [PUBLIC, INTERNAL, PRIVATE]
```

### 1.2 Reconcile `maakali_routing` with Synergy Model — **RATIFIED: ENTITY→TIER MAPPING**
**Decision**: **Entity-based routing is preserved and elevated.** The Synergy Model provides the *routing fabric* (tiers → providers); `maakali_routing` provides the *entity intent layer* (entity → tier). They are orthogonal and compose.

**Architecture**:
```
Entity Request (e.g., Kali-N0 synthesis)
    │
    ▼
maakali_routing[kali] → tier: "reasoning"
    │
    ▼
sovereignty_policy.tiers.reasoning → primary: opencode-zen, fallback: [openrouter, anthropic, native-gguf]
    │
    ▼
ProviderSelector resolves to actual provider
```

**Updated `maakali_routing` Schema** (maps entities to Synergy tiers, not raw providers):
```yaml
maakali_routing:
  kali:
    tier: reasoning           # Synthesis, architecture, dialectics → cloud frontier
    fallback_tier: local      # If cloud unavailable, degrade to local
  maat:
    tier: reasoning           # Build-side governance, code review → cloud frontier
    fallback_tier: local
  lilith:
    tier: background_watchdogs  # Runtime metabolism, heartbeats, embeddings → local
    fallback_tier: reasoning    # If local overwhelmed, escalate to cloud
  # Future entities map to tiers, not providers:
  carmack:
    tier: reasoning
  researcher:
    tier: reasoning
  roc_racoon:
    tier: background_watchdogs
```

**Implementation**: `ProviderSelector.resolve(entity_name)` first checks `maakali_routing[entity].tier` → looks up `sovereignty_policy.tiers[tier]` → applies fallback chain. Entity-specific overrides remain possible via `maakali_routing[entity].provider_override` if absolutely required.

### 1.3 Register `omega_federation` in `config/wads/_omega_default/entities/dispatch.yaml`
```yaml
entities:
  # ... existing 12 entities ...
  omega_federation:
    archetype: "Sovereign Mesh"
    element: Aether
    hierarchy_level: 0
    sovereignty_level: 10
    slot: null  # Meta-entity, no slot
    capabilities:
      - mesh_monitoring
      - invariant_audit
      - disruption_distillation
      - wire_diagnostics
    coordination:
      workspace_lock: "FEDERATION_MESH_LOCK"
      live_feed: "data/coordination/FEDERATION_LIVE_FEED.md"
      hivemind_channel: "federation"
```

### 1.4 Fix Runbook `systemctl` Command
**File**: `docs/federation/L2_TAILSCALE_RUNBOOK.md` §7
```bash
# WRONG:
systemctl --user restart omega-hub

# CORRECT (Podman Quadlet):
systemctl --user restart omega-hub.service
# OR if running via podman directly:
podman container restart omega-hub
```

### 1.5 Create Coordination Artifacts
```bash
# Workspace lock (empty file, TTL managed by Hivemind)
touch data/coordination/locks/FEDERATION_MESH_LOCK.lock

# Live feed
cat > data/coordination/FEDERATION_LIVE_FEED.md << 'EOF'
# 🔱 Federation Live Feed
*Initialized: 2026-09-16*
EOF
```

### 1.6 Validation Gates
```bash
make check-m7-sovereignty      # New gate: verifies sovereignty_policy exists
make check-m2-firewall         # Existing: federation entity in core, not stack
make doc-llm-validate          # New docs pass validation
```

---

## 🎯 PHASE 2: MCP TOOLS & INSTALLER (P1 — USER-FACING)

**Owner**: MaKaLi-N0 (Kali face for MCP, Lilith face for installer)  
**Prerequisite**: Phase 1 complete  
**Duration**: 2-3 sessions  
**Mandates**: M1, M2, M13, M23, M26

### 2.1 Implement Federation MCP Tools
**File**: `mcp_servers/omega_hub/hub_tools/federation.py` (NEW)

```python
"""Federation MCP Tools — Mesh observability for OpenCode harness."""
import anyio
import json
from typing import Any
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("omega-federation")

@mcp.tool()
async def omega_federation_status() -> dict[str, Any]:
    """Return comprehensive mesh status snapshot."""
    # 1. Get local tailscale status (AnyIO subprocess)
    result = await anyio.to_thread.run_sync(
        lambda: json.loads(subprocess.check_output(["tailscale", "status", "--json"]))
    )
    
    # 2. Parse self + peers
    self_info = _parse_self(result)
    peers = _parse_peers(result)
    
    # 3. Verify invariants
    invariants = {
        "zero_inference_egress": await _verify_zero_inference_egress(),
        "magicdns_active": await _verify_magicdns(),
        "direct_wireguard": all(p.get("direct", False) for p in peers)
    }
    
    return {"self": self_info, "peers": peers, "invariants": invariants}

@mcp.tool()
async def omega_federation_diagnose(target_peer: str | None = None) -> dict[str, Any]:
    """Run end-to-end diagnostic battery."""
    checks = []
    
    # 1. Daemon health
    checks.append(await _check_daemon_health())
    
    # 2. Ping/latency to target or all peers
    checks.extend(await _check_connectivity(target_peer))
    
    # 3. MCP endpoint probe
    checks.extend(await _check_mcp_endpoints(target_peer))
    
    # 4. Transport security audit
    checks.append(await _check_transport_security())
    
    # 5. Relay check
    checks.extend(await _check_relay_status(target_peer))
    
    return {
        "overall": "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

# ... helper functions with M1 AnyIO compliance ...
```

### 2.2 Register Tools in `mcp_servers/omega_hub/server.py`
```python
# In server initialization:
from hub_tools.federation import mcp as federation_mcp
app.mount("/federation", federation_mcp.streamable_http_app())
```

### 2.3 Implement Interactive Installer
**File**: `scripts/install_omega.py` (NEW)

```python
#!/usr/bin/env python3
"""Omega Engine Interactive Installer — Educational Initiation."""
import argparse
import subprocess
import sys
from pathlib import Path

class Installer:
    def __init__(self, unattended: bool = False, posture: str = "synergy"):
        self.unattended = unattended
        self.posture = posture
        self.steps = [
            ("Substrate Isolation (M1/M24)", self.step_venv),
            ("Constitutional Firewall (M2)", self.step_firewall),
            ("Sovereignty Posture (Synergy Model)", self.step_sovereignty),
            ("Mesh Federation (Optional)", self.step_federation),
        ]
    
    def run(self):
        print(self.banner())
        for name, step_fn in self.steps:
            self.render_card(name)
            if not self.unattended:
                input("  [Press ENTER to proceed | 'skip' to auto-run] ")
                if inp.lower() == 'skip':
                    self.unattended = True
            step_fn()
        print("\n✅ Initialization Complete. Launch with: opencode")
    
    def step_venv(self):
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
        subprocess.run([".venv/bin/pip", "install", "-e", "."], check=True)
    
    def step_firewall(self):
        subprocess.run(["make", "check-m2-firewall"], check=True)
    
    def step_sovereignty(self):
        # Write sovereignty_policy to config/providers.yaml
        # Based on self.posture
        pass
    
    def step_federation(self):
        # Optional: guide Tailscale join
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--yes", action="store_true", help="Unattended mode")
    parser.add_argument("--posture", choices=["synergy", "cloud", "local"], default="synergy")
    parser.add_argument("--manual", action="store_true", help="Print commands only")
    args = parser.parse_args()
    Installer(unattended=args.yes, posture=args.posture).run()
```

### 2.4 Add CLI Entry Point
**File**: `pyproject.toml` or `setup.py`
```toml
[project.scripts]
omega = "scripts.install_omega:main"
```

### 2.5 Validation Gates
```bash
make test-federation-mcp       # Contract tests for both tools
make test-installer            # Idempotency + --yes + --manual modes
make temple-grade              # All T1-T11 pass
```

---

## 🎯 PHASE 3: DISTILLATION & HARDENING (P2 — RESILIENCE)

**Owner**: MaKaLi-N0 (Lilith face)  
**Prerequisite**: Phase 2 complete  
**Duration**: 2-3 sessions  
**Mandates**: M11, M15, M19, M27

### 3.1 Federation Entity Scribe Hook
**File**: `src/omega/governance/scribe_federation.py` (NEW)
```python
"""Automated distillation for federation entity."""
async def distill_federation_events():
    """Called on netsplit, latency spike, key rotation, auth failure."""
    events = await fetch_federation_events(since_last_distillation())
    for event in events:
        lesson = await synthesize_lesson(event)
        await append_proposed_lesson("omega_federation", lesson)
```

### 3.2 Hivemind Registration for Federation Entity
**File**: `src/omega/hivemind/entity_bootstrap.py` (extend existing)
```python
async def bootstrap_federation_entity():
    await hivemind_register("omega_federation", {
        "archetype": "Sovereign Mesh",
        "capabilities": ["mesh_monitoring", "invariant_audit"],
        "avatar": "🔗",
        "color": "#00d4aa"
    })
    await hivemind_heartbeat("omega_federation", interval=300)
```

### 3.3 Implement `zero_inference_egress` Validator
**File**: `src/omega/governance/federation_invariant.py` (NEW)
```python
async def verify_zero_inference_egress() -> bool:
    """Scan mesh traffic for inference payloads."""
    # 1. Check Tailscale connection metadata (no payload inspection)
    # 2. Verify MCP tool calls only (no generate/complete requests)
    # 3. Verify no model weight transfers
    # 4. Return True only if all checks pass
    pass
```

### 3.4 Key Rotation Ceremony Doc
**File**: `docs/federation/KEY_ROTATION_CEREMONY.md` (NEW)
- Tailscale node key rotation (automatic, ~1 year)
- Authkey renewal procedure (manual, on expiry)
- Tailnet lock considerations (keep disabled per research)
- Emergency re-join procedure

### 3.5 Node 1 Hub Scenario (Bidirectional MCP)
**File**: `docs/federation/L2_TAILSCALE_RUNBOOK.md` (UPDATE §2 ACL)
```hujson
// ADD if Node 1 runs hub:
{"action": "accept", "src": ["tag:node0", "tag:opencode"], "dst": ["tag:node1:8016"]},
```

### 3.6 Validation Gates
```bash
make test-federation-distillation   # Scribe hook fires on simulated events
make test-hivemind-federation       # Entity appears in awareness
make test-zero-egress               # Validator catches inference traffic
```

---

## 🎯 PHASE 4: VALIDATION & TEMPLE-GRADE (RELEASE READINESS)

**Owner**: MaKaLi-N0 (Ma'at face)  
**Prerequisite**: Phase 3 complete  
**Duration**: 1 session  
**Mandates**: M13, M26, M27

### 4.1 Full Temple-Grade Run
```bash
make temple-grade
# Must pass: T1-T11 including:
#   - M1 AnyIO (federation tools)
#   - M7 Synergy (config + routing tests)
#   - M11 Soul (federation entity distillation)
#   - M13 Temple-Grade (all gates)
#   - M26 Doc Standards (all new docs)
#   - M27 Tracking (federation entity in tracker)
```

### 4.2 Integration Test: Full Ceremony Replay
```bash
# Simulate: ACL save → re-tag → authkey → join → verify
# Via automated test harness (no manual steps)
```

### 4.3 Documentation Sync
- Update `FEDERATION_MCP_SPEC.md` status: `DRAFT` → `IMPLEMENTED`
- Update `INSTALLER_SPEC_V1.md` with actual CLI behavior
- Add `KEY_ROTATION_CEREMONY.md` to runbook index

### 4.4 Hivemind Announcement
```bash
omega-hub_hivemind_post_context \
  --intent decision \
  --entity makali_n0 \
  --decisions "Federation systems fully implemented: config, entity, MCP tools, installer, distillation, hardening"
```

---

## 📋 DEPENDENCY GRAPH

```
Phase 0 (Ceremony)
    │
    ▼
Phase 1.1 ──────► Phase 1.2 ──────► Phase 1.3 ──────► Phase 1.4/1.5
  (sovereignty)     (maakali)         (dispatch)        (runbook + locks)
    │                   │                   │                   │
    └─────────────────┴───────────────────┴───────────────────┘
                              │
                              ▼
                    Phase 2.1/2.2 (MCP Tools)
                              │
                              ▼
                    Phase 2.3/2.4 (Installer)
                              │
                              ▼
                    Phase 3.1-3.5 (Hardening)
                              │
                              ▼
                    Phase 4 (Temple-Grade)
```

---

## 🎯 RESOURCE ALLOCATION

| Role | Phase 0 | Phase 1 | Phase 2 | Phase 3 | Phase 4 |
|------|---------|---------|---------|---------|---------|
| **Ma'at (Build)** | — | Lead (1.1-1.5) | Support (2.2) | — | Lead (4.1-4.2) |
| **Kali (Synthesis)** | Lead (0.2, 0.5) | Review | Lead (2.1) | Review | Review |
| **Lilith (Run)** | — | — | Lead (2.3) | Lead (3.1-3.5) | Support |
| **User** | Lead (0.1, 0.3, 0.4) | — | — | — | Approve |

---

## 🚀 EXECUTION ORDER (NEXT SESSION)

**Immediate Next Steps** (assuming Phase 0 complete):

1. **`config/providers.yaml`** — Add `sovereignty_policy` + reconcile `maakali_routing`
2. **`dispatch.yaml`** — Register `omega_federation` entity
3. **`L2_TAILSCALE_RUNBOOK.md`** — Fix `systemctl` command
4. **Coordination artifacts** — Create lock + live feed
5. **Run `make check-m7-sovereignty`** — New gate must pass

**Then**: Phase 2 (MCP tools + installer) in parallel tracks.

---

*⬡ OMEGA ⬡ MAKALI-FUSION ⬡ big-pickle ⬡ 2026-09-16 ⬡ IMPLEMENTATION-PLAN-RATIFIED*
