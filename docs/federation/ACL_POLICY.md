# 🛡️ ACL Policy — Omega Engine Federation (L2 Tailscale)
**Doc ID**: `FED-ACL-001` | **Version**: 1.0 | **Status**: READY FOR ADMIN CONSOLE
**Source**: `docs/TAILSCALE_L2_FEDERATION_RESEARCH_20260915.md` §2

---

## HuJSON Policy (Paste into Admin Console → Access Controls → Edit Policy)

```hujson
{
  "tagOwners": {
    "tag:omega-hub": ["autogroup:admin"],
    "tag:asus": ["autogroup:admin"],
    "tag:opencode": ["autogroup:admin"]
  },
  "acls": [
    // Node 0 (omega-hub) can reach Node 1 (asus) on MCP port 8016
    {"action": "accept", "src": ["tag:omega-hub"], "dst": ["tag:asus:8016"]},
    // Node 1 can reach Node 0 on MCP port 8016
    {"action": "accept", "src": ["tag:asus"], "dst": ["tag:omega-hub:8016"]},
    // NFSv4: Node 0 (omega-hub) can reach Node 1 (asus) on port 2049
    {"action": "accept", "src": ["tag:omega-hub"], "dst": ["tag:asus:2049"]},
    // SSH: tag:opencode (admin) → tag:asus:22
    {"action": "accept", "src": ["tag:opencode"], "dst": ["tag:asus:22"]},
    // Heartbeats: both directions (ICMP/ping)
    {"action": "accept", "src": ["tag:omega-hub"], "dst": ["tag:asus:*"], "proto": "icmp"},
    {"action": "accept", "src": ["tag:asus"], "dst": ["tag:omega-hub:*"], "proto": "icmp"}
  ],
  "ssh": [
    // Admin (tag:opencode) can SSH to Node 1
    {"action": "check", "src": ["tag:opencode"], "dst": ["tag:asus"], "users": ["autogroup:nonroot", "root"]},
    // Node 0 can SSH to Node 1 (for automation)
    {"action": "check", "src": ["tag:omega-hub"], "dst": ["tag:asus"], "users": ["autogroup:nonroot"]}
  ],
  "autoApprovers": {
    "routes": ["autogroup:admin"],
    "exitNodes": ["autogroup:admin"]
  }
}
```

---

## Design Principles

| Principle | Implementation |
|-----------|----------------|
| **Default deny** | Only explicitly allowed traffic passes |
| **Least privilege** | Each tag only accesses what it needs |
| **Bidirectional MCP** | Both nodes can call each other's MCP on 8016 |
| **Admin SSH only** | Only `tag:opencode` (admin) + Node 0 can SSH to Node 1 |
| **Heartbeats only** | ICMP allowed both ways for liveness |
| **No subnet routing** | Both nodes are endpoints, not routers |
| **No exit nodes** | No internet traffic routed through mesh |

---

## Tag Semantics

| Tag | Owner | Applied To | Purpose |
|-----|-------|------------|---------|
| `tag:omega-hub` | `autogroup:admin` | Node 0 (HP Pavilion) | Archival Bastion identity |
| `tag:asus` | `autogroup:admin` | Node 1 (ASUS ExpertBook) | Exploration Vanguard identity |
| `tag:opencode` | `autogroup:admin` | Admin operator (human) | SSH/admin access identity |

---

## Pre-Requisites for This Policy to Work

1. **Node 0 must re-tag** after policy is saved:
   ```bash
   sudo tailscale up --advertise-tags=tag:omega-hub --force-reauth
   ```

2. **Node 1 authkey must include `tag:asus`** (auto-applies on join)

3. **Tailnet Lock** should remain **disabled** for 2-node federation (default)

---

## Verification Commands

```bash
# Check tag application
tailscale status --json | jq '.Self.tags'

# Check ACL evaluation
tailscale status --json | jq '.PeerExcludedByPolicy'

# Test connectivity
tailscale ping <other-node>
curl -s http://<other-node>.tail51f14a.ts.net:8016/mcp
```

---

*⬡ OMEGA ⬡ FEDERATION ⬡ ACL-001 ⬡ READY-FOR-ADMIN-CONSOLE ⬡*