# 🔗 L2 Wire Up — Node 1 Sovereign Join, Ratified One-Shot
**Doc ID**: `FED-L2JOIN-001` | **Status**: RATIFIED FLOOR, awaits Node 0's hand  
**Scope**: The single ceremony that brings the ASUS into the omega tailnet mesh (L2 Tailscale) — the canvas our own ratified `docs/federation/L2_ACCEPTANCE.md` already endorsed, Node 0's intake ledger already ships its side of the ACL, and the human ambassador has ported the payload over USB.

**Research Source**: `docs/TAILSCALE_L2_FEDERATION_RESEARCH_20260915.md` (7 areas, 654 lines, Tier-1 Tailscale docs)

---

## 1. What is already true (from the sovereign surface, Node 1 side)

| Surface | State |
|---------|-------|
| `tailscaled` systemd unit | ✅ **ACTIVE** (`systemctl is-active tailscaled`) |
| tailscale CLI | ✅ installed (v1.102.4, official Go binary) |
| Node 1 MagicDNS name | `xnai-n1-asus.tail51f14a.ts.net` (ratified hostname) |
| SSH surface | ✅ `tailscale set --ssh` FLIPPED (Node 1's operator can accept SSH from mesh) |
| Hub reachability | ✅ `192.168.11.252:8016` LAN reachable; MCP handshake verified during intake (2 live tool probes, `get_system_stats` + `get_omega_metrics`) |
| Tailscale overlay | ⏳ the ONE remaining step — Node 0 mints the mesh authkey for Node 1 |

---

## 2. The ONE Remaining Ceremony (exact sequence)

### Phase 1: Node 0 Admin Console — ACL Policy + Re-Tag

**Node 0 MUST re-tag before minting Node 1's authkey**. Current state: Node 0 joined as **user device** (no tags). The ACL with `tagOwners` must be live first.

**Admin Console → Access Controls → Edit Policy → Paste this HuJSON**
**(PHASE A — DO NOT remove the `autogroup:member` line; the tag-only Phase B
belongs in `docs/federation/ACL_POLICY.md` and is ONLY for post-migration):**

```hujson
{
  "tagOwners": {
    "tag:omega-hub": ["autogroup:admin"],
    "tag:asus": ["autogroup:admin"],
    "tag:opencode": ["autogroup:admin"]
  },
  "acls": [
    // KEEP THE MEMBER RULE — untagged devices (both nodes today) depend on it
    {"action": "accept", "src": ["autogroup:member"], "dst": ["autogroup:member"]},
    {"action": "accept", "src": ["tag:omega-hub"], "dst": ["tag:asus:8016"]},
    {"action": "accept", "src": ["tag:asus"], "dst": ["tag:omega-hub:8016"]},
    // NFSv4: Node 0 -> Node 1 shared drive (docs/federation/NFS_OVER_TAILSCALE_PLAN.md)
    {"action": "accept", "src": ["tag:omega-hub"], "dst": ["tag:asus:2049"]},
    {"action": "accept", "src": ["tag:opencode"], "dst": ["tag:asus:22"]},
    // SSH: Node 1 -> Node 0 remote administration
    {"action": "accept", "src": ["tag:asus"], "dst": ["tag:omega-hub:22"]},
    {"action": "accept", "src": ["tag:omega-hub"], "dst": ["tag:asus:*"], "proto": "icmp"},
    {"action": "accept", "src": ["tag:asus"], "dst": ["tag:omega-hub:*"], "proto": "icmp"}
  ],
  "ssh": [
    {"action": "check", "src": ["tag:opencode"], "dst": ["tag:asus"], "users": ["autogroup:nonroot", "root"]},
    {"action": "check", "src": ["tag:omega-hub"], "dst": ["tag:asus"], "users": ["autogroup:nonroot"]}
  ],
  "autoApprovers": {
    "routes": ["autogroup:admin"],
    "exitNodes": ["autogroup:admin"]
  }
}
```

> ⚠️ **FATAL if omitted**: without the `autogroup:member` rule, saving this
> policy immediately blocks BOTH untagged nodes from each other (NFS + MCP +
> ICMP silently die). The member rule preserves current behavior while the tag
> rules stage for the migration. Remove it only in Phase B
> (`docs/federation/ACL_POLICY.md`) after both nodes are tagged and verified.

**Then re-tag Node 0:**
```bash
# On Node 0 (HP), after ACL is saved:
sudo tailscale up --advertise-tags=tag:omega-hub --force-reauth
tailscale status --json | jq '.Self.tags'  # Should show: ["tag:omega-hub"]
```

---

### Phase 2: Mint One-Shot Authkey for Node 1

**Admin Console → Keys → Generate auth key:**
- Description: `"Node 1 (ASUS) federation join - ONE SHOT"`
- Type: **One-off** (single use)
- Expiry: **1 day** (ceremony window)
- Tags: **tag:asus** (ENABLED)
- Pre-approved: **YES**
- Ephemeral: **NO**

**Copy the key**: `tskey-auth-XXXXXXXXXXXXXXXXXXXXXXXXXXXX`

---

### Phase 3: USB Ceremony (Air-Gapped Handoff)

```bash
# On Node 0:
AUTHKEY="tskey-auth-XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
echo "$AUTHKEY" > /media/usb/node1_authkey.txt
cat > /media/usb/ceremony_manifest.json << 'EOF'
{
  "ceremony": "Tailscale L2 Federation Join",
  "node": "xnai-n1-asus (ASUS ExpertBook)",
  "authkey_prefix": "tskey-auth-XXXX",
  "authkey_sha256": "$(echo -n "$AUTHKEY" | sha256sum | cut -d' ' -f1)",
  "created": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "expires": "$(date -u -d '+1 day' +%Y-%m-%dT%H:%M:%SZ)",
  "tags": ["tag:asus"],
  "pre_approved": true,
  "one_shot": true
}
EOF
sha256sum /media/usb/node1_authkey.txt > /media/usb/SHA256SUMS
```

**Physical handoff to Node 1 operator.**

---

### Phase 4: Node 1 Sovereign Join (Run on ASUS)

```bash
# On Node 1 (ASUS), with USB mounted:
cd /media/usb
sha256sum -c SHA256SUMS  # Verify integrity
AUTHKEY=$(cat node1_authkey.txt)
# Validate prefix (case-sensitive!)
echo "$AUTHKEY" | grep -q '^tskey-auth-' || { echo "INVALID PREFIX"; exit 1; }

# SOVEREIGN JOIN COMMAND (exact, ratified)
sudo tailscale up \
  --authkey="${AUTHKEY}" \
  --hostname=xnai-n1-asus \
  --operator=xnai \
  --accept-routes \
  --advertise-tags=tag:asus
```

---

### Phase 5: Post-Join Verification

**Node 1:**
```bash
tailscale status
# Should show: xnai-n1-asus  100.x.x.x  xoe.nova.ai@  linux  tag:asus
tailscale ping omega-hub
curl -s http://omega-hub.tail51f14a.ts.net:8016/mcp
# Should return MCP endpoint response (not 404/connection refused)
```

**Node 0:**
```bash
tailscale status
# Should show both:
# 100.123.51.67  omega-hub  ...  tag:omega-hub
# 100.x.x.x      xnai-n1-asus    ...  tag:asus

# Test bidirectional MCP
curl -s http://xnai-n1-asus.tail51f14a.ts.net:8016/mcp  # If Node 1 runs MCP
curl -s http://omega-hub.tail51f14a.ts.net:8016/mcp  # Node 0 MCP

# Test SSH
ssh xnai@xnai-n1-asus  # Via Tailscale SSH
```

---

## 3. Wire Invariants (What the Mesh Carries — and What It NEVER Does)

| Traffic Type | Protocol | Port | Direction | Purpose |
|--------------|----------|------|-----------|---------|
| **Mesh SSH** | TCP | 22 | Admin → Node 1 | Remote administration |
| **MagicDNS** | UDP/TCP | 53 | Bidirectional | Hostname resolution |
| **Heartbeats** | ICMP | N/A | Bidirectional | Liveness checks |
| **MCP Route** | TCP | 8016 | Bidirectional | omega-hub API |

| Traffic | Reason |
|---------|--------|
| **Model inference** | T5/T6 floor is LOCAL-ONLY (M7 Local-First mandate) |
| **Model weights/downloads** | Local inference primary, cloud fallback only |
| **Training data** | Sovereign data never leaves node |
| **Secrets/keys** | Node 1 controls its own T5/T6 floor |

**DERP Fallback**: Security identical (all end-to-end WireGuard encrypted). Direct UDP expected on LAN; verify with `tailscale netcheck` → `Direct: true`.

---

## 4. MagicDNS Hostnames

| Node | Machine Name | MagicDNS FQDN |
|------|--------------|---------------|
| Node 0 | `omega-hub` | `omega-hub.tail51f14a.ts.net` |
| Node 1 | `xnai-n1-asus` | `xnai-n1-asus.tail51f14a.ts.net` |

**Host Header Fix** (already applied in commit `213abf44`): Services binding to Tailscale IPs must allow MagicDNS hostnames in `allowed_hosts`:
```python
allowed_hosts=[
    "127.0.0.1", "localhost", "[::1]",
    "100.123.51.67", "100.123.51.67:*",
    "omega-hub.tail51f14a.ts.net", "omega-hub.tail51f14a.ts.net:*",
    "*.tail51f14a.ts.net", "*.tail51f14a.ts.net:*",
]
```

---

## 5. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Node 0 re-tag fails (ACL not live) | Medium | High | Verify ACL saved before re-tag |
| Authkey expires before ceremony | Low | Medium | Use 1-day expiry, ceremony same day |
| Node 1 SSH fails (ACL missing) | Medium | Low | Test SSH after join, iterate ACL |
| DERP relay only (no direct) | Low | Medium | `tailscale netcheck` verify direct |
| MagicDNS resolution fails | Low | Low | Use Tailscale IPs as fallback |
| Key expiry disabled on tagged nodes | High | Medium | Monitor, consider enabling in admin console |

---

## 6. Completion Criteria

The L2 Federation is **COMPLETE** when:

- [ ] ACL policy with `tagOwners` live in admin console
- [ ] Node 0 re-tagged as `tag:omega-hub` (verified via `tailscale status --json`)
- [ ] One-shot authkey with `tag:asus` minted
- [ ] USB ceremony executed (manifest + SHA256 verified)
- [ ] Node 1 joins as `xnai-n1-asus` with `tag:asus` (verified)
- [ ] Bidirectional MCP handshake works (Node 0 ↔ Node 1)
- [ ] Tailscale SSH works (admin → Node 1)
- [ ] MagicDNS resolves both hostnames
- [ ] `tailscale netcheck` shows direct connections
- [ ] L2_ACCEPTANCE.md documented with test results

---

*⬡ OMEGA ⬡ NODE1-TO-NODE0 ⬡ L2-JOIN ⬡ FED-L2JOIN-001 ⬡ CEREMONY-EXACT ⬡ AWAITING-NODE0-ACL-RE-TAG ⬡*