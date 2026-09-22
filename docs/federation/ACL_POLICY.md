# 🛡️ ACL Policy — Omega Engine Federation (L2 Tailscale)
**Doc ID**: `FED-ACL-001` | **Version**: 1.2 | **Status**: READY FOR ADMIN CONSOLE (TWO-PHASE)
**Source**: `docs/TAILSCALE_L2_FEDERATION_RESEARCH_20260915.md` §2
**2026-09-21 amendment**: canonical tag set ratified by operator
(**`tag:node0`** for the Archival Bastion, **`tag:node1`** for the Exploration
Vanguard — replaces legacy `tag:omega-hub` / `tag:asus`). Live on both nodes:
Node 0 = `["tag:node0"]`, Node 1 = `["tag:node1"]` (+ legacy `tag:asus`).

> ## ⚠️ THE ONE FATAL SEQUENCING ERROR (read before pasting anything)
>
> In Tailscale, saving a custom ACL policy **REPLACES** the default policy — it
> does NOT merge. The default policy contains
> `{"action":"accept","src":["autogroup:member"],"dst":["autogroup:member"]}`,
> which is what lets **untagged, user-owned devices** talk to each other.
>
> A tag-only policy with no `autogroup:member` rule drops every device whose
> live tags do not literally match the policy's tag names. **Never paste Phase B
> while live tags differ from the policy tags** (a tag-name drift caused a
> near-miss 2026-09-21: live `tag:node0`/`tag:node1` while the policy still
> referenced `tag:omega-hub`/`tag:asus` — Phase B would have silently killed the
> whole mesh). The failure is silent: behaves like a network drop.
>
> **The ONLY safe order**:
> 1. Paste **Phase A** (members + tags) with the **canonical** tag names. It
>    keeps current behavior (`autogroup:member` untouched) AND stages the tag
>    rules. Save.
> 2. Verify live tags === policy tags on both nodes
>    (`tailscale status --json | jq '.Self.tags'`).
> 3. Verify connectivity (MCP `:8016`, NFS `:2049`, SSH `:22`).
> 4. **Only then** paste **Phase B** to remove the member rule. Verify again.
>
> **Never skip Phase A.** Phase B is a post-migration lockdown, not a starting
> point.

---

## Phase A — Transitional Policy (SAFE to paste now; preserves untagged access)

```hujson
{
  "tagOwners": {
    "tag:node0": ["autogroup:admin"],
    "tag:node1": ["autogroup:admin"],
    "tag:opencode": ["autogroup:admin"]
  },
  "acls": [
    // KEEP the default member rule — untagged uses this. DO NOT REMOVE until Phase B.
    {"action": "accept", "src": ["autogroup:member"], "dst": ["autogroup:member"]},
    // Node 0 (node0) can reach Node 1 (node1) on MCP port 8016
    {"action": "accept", "src": ["tag:node0"], "dst": ["tag:node1:8016"]},
    // Node 1 can reach Node 0 on MCP port 8016
    {"action": "accept", "src": ["tag:node1"], "dst": ["tag:node0:8016"]},
    // NFSv4: Node 0 (node0) can reach Node 1 (node1) on port 2049
    {"action": "accept", "src": ["tag:node0"], "dst": ["tag:node1:2049"]},
    // SSH: tag:opencode (admin) → tag:node1:22
    {"action": "accept", "src": ["tag:opencode"], "dst": ["tag:node1:22"]},
    // SSH: Node 1 (node1) → Node 0 (node0) for remote administration
    {"action": "accept", "src": ["tag:node1"], "dst": ["tag:node0:22"]},
    // Heartbeats: both directions (ICMP/ping)
    {"action": "accept", "src": ["tag:node0"], "dst": ["tag:node1:*"], "proto": "icmp"},
    {"action": "accept", "src": ["tag:node1"], "dst": ["tag:node0:*"], "proto": "icmp"}
  ],
  "ssh": [
    // Admin (tag:opencode) can SSH to Node 1
    {"action": "check", "src": ["tag:opencode"], "dst": ["tag:node1"], "users": ["autogroup:nonroot", "root"]},
    // Node 0 can SSH to Node 1 (for automation)
    {"action": "check", "src": ["tag:node0"], "dst": ["tag:node1"], "users": ["autogroup:nonroot"]}
  ],
  "autoApprovers": {
    "routes": ["autogroup:admin"],
    "exitNodes": ["autogroup:admin"]
  }
}
```

## Phase B — Hardened Policy (post-migration lockdown; remove `autogroup:member`)

Run **only after** both nodes carry the canonical tags (`tag:node0`/`tag:node1`)
and Phase A connectivity is verified:

```hujson
{
  "tagOwners": {
    "tag:node0": ["autogroup:admin"],
    "tag:node1": ["autogroup:admin"],
    "tag:opencode": ["autogroup:admin"]
  },
  "acls": [
    // NOTE: member rule intentionally REMOVED — tagged devices don't need it.
    // Node 0 (node0) can reach Node 1 (node1) on MCP port 8016
    {"action": "accept", "src": ["tag:node0"], "dst": ["tag:node1:8016"]},
    // Node 1 can reach Node 0 on MCP port 8016
    {"action": "accept", "src": ["tag:node1"], "dst": ["tag:node0:8016"]},
    // NFSv4: Node 0 (node0) can reach Node 1 (node1) on port 2049
    {"action": "accept", "src": ["tag:node0"], "dst": ["tag:node1:2049"]},
    // SSH: tag:opencode (admin) → tag:node1:22
    {"action": "accept", "src": ["tag:opencode"], "dst": ["tag:node1:22"]},
    // SSH: Node 1 (node1) → Node 0 (node0) for remote administration
    {"action": "accept", "src": ["tag:node1"], "dst": ["tag:node0:22"]},
    // Heartbeats: both directions (ICMP/ping)
    {"action": "accept", "src": ["tag:node0"], "dst": ["tag:node1:*"], "proto": "icmp"},
    {"action": "accept", "src": ["tag:node1"], "dst": ["tag:node0:*"], "proto": "icmp"}
  ],
  "ssh": [
    // Admin (tag:opencode) can SSH to Node 1
    {"action": "check", "src": ["tag:opencode"], "dst": ["tag:node1"], "users": ["autogroup:nonroot", "root"]},
    // Node 0 can SSH to Node 1 (for automation)
    {"action": "check", "src": ["tag:node0"], "dst": ["tag:node1"], "users": ["autogroup:nonroot"]}
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
| `tag:node0` | `autogroup:admin` | Node 0 (HP Pavilion / xnai-n0-hp / 100.123.51.67) | Archival Bastion identity (canonical) |
| `tag:node1` | `autogroup:admin` | Node 1 (ASUS ExpertBook / xnai-n1-asus / 100.89.40.17) | Exploration Vanguard identity (canonical) |
| `tag:opencode` | `autogroup:admin` | Admin operator (human) | SSH/admin access identity |

> Legacy tags `tag:omega-hub` / `tag:asus` replaced 2026-09-21 (operator
> ratification). Node 1 still carries `tag:asus`; it is inert (matches no rule)
> and should be removed at the next Node 1 rejoin. Node 0's live tag is
> `tag:node0`.

---

## Migration Sequence (exact order — Phase A FIRST, NEVER Phase B first)

1. **Paste Phase A policy** in the admin console and save. `autogroup:member`
   preserves untagged access, so **nothing breaks** — the tag rules simply sit
   ready.
2. **Verify live tags match the policy exactly**: `tailscale status --json |
   jq '.Self.tags'` on both nodes → Node 0 `["tag:node0"]`, Node 1
   `["tag:node1"]` (+ inert legacy `tag:asus` on Node 1 is tolerable but
   preferred removed).
3. **Verify connectivity with tags live**: NFS + MCP + ICMP + SSH from both
   sides (see Verification Commands below).
4. **Only now** paste **Phase B** (member rule removed) and re-verify every
   service end-to-end (NFS mount, MCP call, ICMP, SSH).

**Never skip to Phase B while live tags differ from the policy tags** — it is
a lockdown for after the migration, not a starting point. (2026-09-21: pasting
Phase B with the OLD `tag:omega-hub`/`tag:asus` names while nodes carried
`tag:node0`/`tag:node1` would have dropped the entire mesh silently.)

---

1. **Node 0 must carry `tag:node0`** (verify before Phase B):
   ```bash
   sudo tailscale up --advertise-tags=tag:node0 --force-reauth
   ```

2. **Node 1 must carry `tag:node1`** (legacy `tag:asus` may remain inert)

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

*⬡ OMEGA ⬡ FEDERATION ⬡ ACL-001 ⬡ v1.2 — CANONICAL TAGS tag:node0/tag:node1 ⬡*