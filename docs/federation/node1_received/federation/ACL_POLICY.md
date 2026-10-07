# 🛡️ ACL Policy — Omega Engine Federation (L2 Tailscale)
**Doc ID**: `FED-ACL-001` | **Version**: 1.1 | **Status**: READY FOR ADMIN CONSOLE (TWO-PHASE)
**Source**: `docs/TAILSCALE_L2_FEDERATION_RESEARCH_20260915.md` §2

> ## ⚠️ THE ONE FATAL SEQUENCING ERROR (read before pasting anything)
>
> In Tailscale, saving a custom ACL policy **REPLACES** the default policy — it
> does NOT merge. The default policy contains
> `{"action":"accept","src":["autogroup:member"],"dst":["autogroup:member"]}`,
> which is what lets **untagged, user-owned devices** talk to each other.
>
> Both our nodes are currently **untagged user devices**. If you paste the
> **Phase B** (tag-only) policy below and save it right now, the mesh
> **immediately loses all connectivity** — NFS, MCP, ICMP — with no visible
> error pointing at the ACL. The failure is silent: behaves like a network drop.
>
> **The ONLY safe order**:
> 1. Paste **Phase A** (members + tags). It keeps current behavior
>    (`autogroup:member` untouched) AND stages the tag rules. Save.
> 2. Re-tag Node 0 → `tag:omega-hub`. Verify connectivity.
> 3. Re-join Node 1 with `tag:asus`. Verify connectivity (esp. NFS `:2049`).
> 4. **Only then** paste **Phase B** to remove the member rule. Verify again.
>
> **Never skip Phase A.** Phase B is a post-migration lockdown, not a starting
> point.

---

## Phase A — Transitional Policy (SAFE to paste now; preserves untagged access)

```hujson
{
  "tagOwners": {
    "tag:omega-hub": ["autogroup:admin"],
    "tag:asus": ["autogroup:admin"],
    "tag:opencode": ["autogroup:admin"]
  },
  "acls": [
    // KEEP the default member rule — untagged uses this. DO NOT REMOVE until Phase B.
    {"action": "accept", "src": ["autogroup:member"], "dst": ["autogroup:member"]},
    // Node 0 (omega-hub) can reach Node 1 (asus) on MCP port 8016
    {"action": "accept", "src": ["tag:omega-hub"], "dst": ["tag:asus:8016"]},
    // Node 1 can reach Node 0 on MCP port 8016
    {"action": "accept", "src": ["tag:asus"], "dst": ["tag:omega-hub:8016"]},
    // NFSv4: Node 0 (omega-hub) can reach Node 1 (asus) on port 2049
    {"action": "accept", "src": ["tag:omega-hub"], "dst": ["tag:asus:2049"]},
    // SSH: tag:opencode (admin) → tag:asus:22
    {"action": "accept", "src": ["tag:opencode"], "dst": ["tag:asus:22"]},
    // SSH: Node 1 (asus) → Node 0 (omega-hub) for remote administration
    {"action": "accept", "src": ["tag:asus"], "dst": ["tag:omega-hub:22"]},
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

## Phase B — Hardened Policy (post-migration lockdown; remove `autogroup:member`)

Run **only after** both nodes are tagged and Phase A connectivity is verified:

```hujson
{
  "tagOwners": {
    "tag:omega-hub": ["autogroup:admin"],
    "tag:asus": ["autogroup:admin"],
    "tag:opencode": ["autogroup:admin"]
  },
  "acls": [
    // NOTE: member rule intentionally REMOVED — tagged devices don't need it.
    // Node 0 (omega-hub) can reach Node 1 (asus) on MCP port 8016
    {"action": "accept", "src": ["tag:omega-hub"], "dst": ["tag:asus:8016"]},
    // Node 1 can reach Node 0 on MCP port 8016
    {"action": "accept", "src": ["tag:asus"], "dst": ["tag:omega-hub:8016"]},
    // NFSv4: Node 0 (omega-hub) can reach Node 1 (asus) on port 2049
    {"action": "accept", "src": ["tag:omega-hub"], "dst": ["tag:asus:2049"]},
    // SSH: tag:opencode (admin) → tag:asus:22
    {"action": "accept", "src": ["tag:opencode"], "dst": ["tag:asus:22"]},
    // SSH: Node 1 (asus) → Node 0 (omega-hub) for remote administration
    {"action": "accept", "src": ["tag:asus"], "dst": ["tag:omega-hub:22"]},
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

> Note on Tailscale SSH vs ordinary SSH: the `"ssh"` section above governs
> **Tailscale SSH** (`tailscale up --ssh` / `tailscale set --ssh`), which
> intercepts port 22 on the tailnet interface and does NOT require a host
> `sshd` daemon. Ordinary OpenSSH (`sshd`) is governed by the plain `:22` ACL
> rules. Node 1 currently has Tailscale SSH flipped. Node 0's SSH state is
> unset — see the Node 0 briefing for how to enable it (physically, over USB).

---

## Design Principles

| Principle | Implementation |
|-----------|----------------|
| **Default deny** | Only explicitly allowed traffic passes (Phase B) |
| **Least privilege** | Each tag only accesses what it needs |
| **Bidirectional MCP** | Both nodes can call each other's MCP on 8016 |
| **Bidirectional NFS** | Node 0 mounts Node 1's shared drive on 2049 |
| **Bidirectional SSH** | Each node can administer the other on 22 |
| **Admin SSH** | `tag:opencode` (admin) has SSH to both nodes |
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

## Migration Sequence (exact order — Phase A FIRST, NEVER Phase B first)

1. **Paste Phase A policy** in the admin console and save. `autogroup:member`
   preserves untagged access, so **nothing breaks** — the tag rules simply sit
   ready.
2. **Re-tag Node 0**: `sudo tailscale up --advertise-tags=tag:omega-hub
   --force-reauth` — only now, because `tagOwners` must exist in a saved policy
   first or the tag is rejected as unowned.
3. **Verify Node 0's tag**: `tailscale status --json | jq '.Self.tags'` →
   `["tag:omega-hub"]`. Verify NFS + MCP still work from Node 1.
4. **Mint Node 1's authkey** with `tag:asus` (admin console → Keys), then run
   the L2 join ceremony (`docs/federation/L2_JOIN_GUIDE.md` Phase 4) so Node 1
   comes back tagged.
5. **Verify everything tagged**: NFS mount + MCP + ICMP + SSH from both sides.
6. **Only now** paste **Phase B** (member rule removed) and re-verify.

**Never skip to Phase B while either node is untagged** — it is a lockdown for
after the migration, not a starting point.

---

1. **Node 0 must re-tag** after Phase A is saved:
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