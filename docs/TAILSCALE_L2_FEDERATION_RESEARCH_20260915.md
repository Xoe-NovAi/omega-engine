<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Tailscale L2 Federation Completion Research

**Session**: `ses_fd81c19dcffe1nkbPqFg5kRt2v` (Researcher-EIS standing)
**Date**: 2026-09-15
**AP Token**: `AP-RESEARCHER-TAILSCALE-L2-20260915-v1.0.0`
**Status**: COMPLETE — All 7 research areas covered

> **⚠️ 2026-09-21 SUPERSESSION NOTE**: This research predates the canonical
> tag ratification. **FED-ACL-001 v1.2 (`docs/federation/ACL_POLICY.md`) is the
> authoritative policy**; canonical tags are `tag:node0` / `tag:node1` /
> `tag:opencode`. Any `tag:omega-hub` / `tag:asus` / `tag:ollama-node` /
> `tag:searxng` references below are historical and must not be pasted.

---

## 📋 Executive Summary

This research identifies the **exact remaining gaps** to complete the Tailscale L2 Federation (C6 v1.1 / FED-L2-001) between Node 0 (HP / omega-hub) and Node 1 (ASUS / kali-n1).

### Current State

| Component | Node 0 (HP) | Node 1 (ASUS) |
|-----------|-------------|---------------|
| Tailscale installed | ✅ v1.102.4 | ✅ v1.102.4 |
| Tailnet joined | ✅ as `omega-hub` (user device) | ❌ NOT JOINED |
| Transport security | ✅ Updated for Tailscale IPs + MagicDNS | N/A |
| MCP handshake | ✅ Verified over Tailscale | ❌ Cannot test |
| ACL tags configured | ❌ NO (joined as user device) | ❌ Requires ACL first |
| Authkey for Node 1 | ❌ NOT MINTED | ❌ Awaiting Node 0 |

### The ONE Remaining Ceremony

```
Node 0 Admin Console → ACL Policy (with tagOwners) → Node 0 re-tags as tag:omega-hub
    → Mint one-shot authkey with tag:asus → USB transfer → Node 1 joins with tag:asus
```

### Key Finding: Node 0 Must Re-Tag

Node 0 currently joined as a **user device** (no tags). The ACL policy with `tagOwners` for `tag:omega-hub`, `tag:asus`, `tag:opencode` must be configured in the admin console **first**, then Node 0 must re-authenticate with `--advertise-tags=tag:omega-hub`, **then** mint the authkey for Node 1.

---

## 1️⃣ Tailscale Authkey Best Practices for Federation

### 1.1 One-Shot vs Reusable Authkeys

**Source**: [Tailscale Auth Keys Docs](https://tailscale.com/docs/features/access-control/auth-keys), [Secure Auth Keys](https://tailscale.com/docs/features/access-control/auth-keys/how-to/secure-auth-keys)

| Property | One-Off (Single-Use) | Reusable |
|----------|---------------------|----------|
| Use count | 1 device only | Multiple devices |
| Auto-revocation | ✅ After use | ❌ Manual only |
| Security | **HIGH** — stolen key useless after use | **LOW** — stolen key = unlimited devices |
| Best for | **Air-gapped ceremonies, CI/CD, servers** | Auto-scaling groups (with key vault) |

**Recommendation**: **ONE-SHOT AUTHKEY** for Node 1 federation ceremony. This is a sovereign join — one device, one key, one use.

### 1.2 Ephemeral vs Pre-Authorized Flags

| Flag | Purpose | Federation Use |
|------|---------|----------------|
| `Ephemeral` | Auto-remove authkey after device goes offline | ❌ NOT for Node 1 (permanent node) |
| `Pre-approved` | Auto-authorize device if device approval enabled | ✅ **REQUIRED** — bypasses manual approval |
| `Tags` | Auto-tag devices using the key | ✅ **REQUIRED** — applies `tag:asus` to Node 1 |

**Critical**: For tagged devices, the authkey **must** have `Tags` enabled with `tag:asus`. Node 1 will automatically assume the tag identity.

### 1.3 Tag Propagation via Authkeys

**Source**: [Tailscale Tags Docs](https://tailscale.com/kb/1068/tags)

> "However, if you use tags with an auth key, after a device logs in as the user who generated the auth key, the device assumes the identity of the auth key's tags."

**Mechanism**:
1. Admin creates authkey with `Tags: tag:asus` + `Pre-approved: true` + `One-off: true`
2. Node 1 runs `sudo tailscale up --authkey=tskey-auth-... --advertise-tags=tag:asus`
3. Node 1 **automatically receives `tag:asus` identity** — no manual tagging needed
4. ACL policies referencing `tag:asus` immediately apply

### 1.4 Authkey Expiry Management for Air-Gapped Ceremonies

**Source**: [Tailscale Key Expiry](https://tailscale.com/docs/features/access-control/key-expiry)

- Authkeys expire **1-90 days** (configurable at creation)
- **Node keys** (different from authkeys) expire **180 days** default
- **Tagged devices**: Key expiry **disabled by default** — persists until re-auth
- **Air-gap recommendation**: Create authkey with **1-day expiry** (ceremony window), use immediately

**Ceremony Protocol**:
```
Day 0: Node 0 admin → Create one-shot authkey (1-day expiry, tag:asus, pre-approved)
Day 0: USB transfer (SHA256 ledgered)
Day 0: Node 1 joins → authkey auto-revoked after use
Day 0: Verify Node 1 appears as `kali-n1` with `tag:asus`
```

---

## 2️⃣ ACL Policy Configuration for P2P Federation

### 2.1 tagOwners Best Practices

**Source**: [Tailscale ACL Tags](https://tailscale.com/kb/1068/acl-tags), [Tailnet Policy File](https://tailscale.com/docs/features/tailnet-policy-file.md)

```hujson
{
  "tagOwners": {
    "tag:omega-hub": ["autogroup:admin"],
    "tag:asus": ["autogroup:admin"],
    "tag:opencode": ["autogroup:admin"]
  }
}
```

**Key Principles**:
- `autogroup:admin` = all admins can manage these tags (simplest for 2-node federation)
- For larger fleets: specific users/groups per tag
- **Tag owners** = who can APPLY the tag (via authkey or admin console)
- **ACLs** = what tagged devices CAN ACCESS

### 2.2 Least-Privilege ACL Design for Mesh SSH + MCP + Heartbeats

**Source**: [ACL Policy Examples](https://tailscale.com/docs/reference/examples/acls), [Restrict by Purpose](https://tailscale.com/kb/1192/acl-samples)

```hujson
{
  "acls": [
    // Node 0 (omega-hub) can reach Node 1 (asus) on MCP port 8016
    {"action": "accept", "src": ["tag:omega-hub"], "dst": ["tag:asus:8016"]},
    // Node 1 can reach Node 0 on MCP port 8016
    {"action": "accept", "src": ["tag:asus"], "dst": ["tag:omega-hub:8016"]},
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

**Principle**: Default deny. Only allow:
- MCP (8016) bidirectional
- SSH (22) from admin → Node 1
- ICMP heartbeats bidirectional
- Nothing else

### 2.3 MagicDNS Name Resolution

**Source**: [MagicDNS Docs](https://tailscale.com/docs/features/magicdns)

- **Enabled by default** for tailnets created after Oct 2022
- Device hostname → `hostname.tailnet-suffix.ts.net`
- Our tailnet suffix: `tail51f14a.ts.net`
- Node 0: `omega-hub.tail51f14a.ts.net` ✅
- Node 1 (after join): `kali-n1.tail51f14a.ts.net` (or `asus.tailnet` per Node 1's ratified ACL)

**Resolution**: Works automatically within tailnet. No external DNS needed.

---

## 3️⃣ Tailscale MagicDNS & DNS Rebinding Protection

### 3.1 MagicDNS with Custom Hostnames

**Source**: [MagicDNS Docs](https://tailscale.com/kb/1081/magicdns)

- Machine name = DNS label (sanitized: lowercase, hyphens only)
- Full FQDN: `machine-name.tailnet-suffix.ts.net`
- Our tailnet: `tail51f14a.ts.net`
- Node 0 machine name: `omega-hub` → `omega-hub.tail51f14a.ts.net`
- Node 1 machine name: `kali-n1` → `kali-n1.tail51f14a.ts.net`

### 3.2 DNS Rebinding Protection & Host Header Validation

**Source**: [DNS Rebinding Protection](https://tailscale.com/kb/1195/dns-rebinding), [NousResearch Issue #74664](https://github.com/NousResearch/hermes-agent/issues/74664)

**The Problem**: Services binding to Tailscale IPs (100.x.x.x) receive `Host: friendly-name` headers from browsers, but middleware rejects non-matching Host headers.

**Our Fix** (already applied in commit `213abf44`):
```python
# mcp_servers/omega_hub/server.py
_transport_security = TransportSecuritySettings(
    allowed_hosts=[
        "127.0.0.1", "localhost", "[::1]",
        # Tailscale L2 federation
        "100.123.51.67", "100.123.51.67:*",
        "omega-hub.tail51f14a.ts.net", "omega-hub.tail51f14a.ts.net:*",
        "*.tail51f14a.ts.net", "*.tail51f14a.ts.net:*",
    ],
    allowed_origins=[
        "http://192.168.10.168:*",
        "http://localhost:*", "http://127.0.0.1:*",
        "http://100.123.51.67:*",
        "http://omega-hub.tail51f14a.ts.net:*",
        "http://*.tail51f14a.ts.net:*",
    ],
)
```

**Why this works**: MagicDNS is **not affected by DNS rebinding protection** because it resolves entirely within the Tailscale client (no external DNS involved). The host header issue is a **service-side middleware problem**, fixed by allowing the MagicDNS hostnames in `allowed_hosts`.

### 3.3 Host Header Patterns for Federation Services

| Service Bind | Browser Host Header | Must Allow in `allowed_hosts` |
|--------------|---------------------|-------------------------------|
| `0.0.0.0:8016` | `omega-hub.tail51f14a.ts.net` | `omega-hub.tail51f14a.ts.net` |
| `0.0.0.0:8016` | `100.123.51.67` | `100.123.51.67` |
| `0.0.0.0:8016` | `kali-n1.tail51f14a.ts.net` | `*.tail51f14a.ts.net` (wildcard) |

---

## 4️⃣ Node 0 Re-Tagging Procedure

### 4.1 Current State: User Device (No Tags)

Node 0 joined via interactive login (or `--reset` to bypass tag error). It has **user-based identity**, not tag-based.

### 4.2 Re-Tag Procedure

**Source**: [Tailscale Tags - Apply Tag](https://tailscale.com/kb/1068/tags)

**Prerequisite**: ACL policy with `tagOwners` for `tag:omega-hub` must be **live in admin console**.

**Steps**:
```bash
# 1. Verify ACL is live (admin console → Access Controls → Policy)
# 2. Re-authenticate Node 0 with tag
sudo tailscale up --advertise-tags=tag:omega-hub --force-reauth
```

**What happens**:
- Generates **new node key** (Tailscale IP **does not change**)
- Device identity shifts from user → `tag:omega-hub`
- Key expiry **disabled by default** for tagged devices
- ACL policies for `tag:omega-hub` immediately apply

**Timing**: Tag change propagates within seconds. Verify with `tailscale status --json | grep -A5 tags`.

### 4.3 Interaction with Existing Identity

- **Cannot remove all tags** — tagged device must have ≥1 tag
- **Cannot use `--advertise-tags` with authkey** — must generate new authkey with updated tags
- **User device → tagged device**: Requires `--force-reauth` (generates new node key)

---

## 5️⃣ Air-Gapped Authkey Handoff Ceremony

### 5.1 Ceremony Design

**Threat Model**: Authkey in shell history = unauthorized device enrollment. Mitigation: one-shot + USB + SHA256 ledger.

### 5.2 Step-by-Step Protocol

```
┌─────────────────────────────────────────────────────────────────┐
│  TAILSCALE L2 FEDERATION CEREMONY (AIR-GAPPED)                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  NODE 0 (HP)                                                    │
│  ────────────────────────────────────────────────────────────  │
│  1. Admin Console → Access Controls → Keys → Generate auth key │
│     • Description: "Node 1 (ASUS) federation join - ONE SHOT"  │
│     • Type: One-off (single use)                                │
│     • Expiry: 1 day (ceremony window)                          │
│     • Tags: tag:asus (ENABLED)                                  │
│     • Pre-approved: YES                                         │
│     • Ephemeral: NO                                             │
│     → COPY KEY: tskey-auth-XXXXXXXXXXXXXXXXXXXXXXXXXXXX        │
│                                                                 │
│  2. Create ceremony manifest (JSON)                             │
│     {                                                           │
│       "ceremony": "Tailscale L2 Federation Join",              │
│       "node": "kali-n1 (ASUS ExpertBook)",                     │
│       "authkey_prefix": "tskey-auth-XXXX",                     │
│       "authkey_sha256": "sha256(full_key)",                    │
│       "created": "2026-09-15T...",                             │
│       "expires": "2026-09-16T...",                             │
│       "tags": ["tag:asus"],                                     │
│       "pre_approved": true,                                     │
│       "one_shot": true                                          │
│     }                                                           │
│                                                                 │
│  3. Write manifest + authkey to USB (encrypted or plaintext)   │
│     echo "$AUTHKEY" > /media/usb/node1_authkey.txt             │
│     cat manifest.json > /media/usb/ceremony_manifest.json      │
│     sha256sum /media/usb/node1_authkey.txt > /media/usb/SHA256 │
│                                                                 │
│  4. Physical handoff to Node 1 operator                        │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  NODE 1 (ASUS)                                                  │
│  ────────────────────────────────────────────────────────────  │
│  1. Verify USB integrity                                        │
│     sha256sum -c SHA256                                         │
│                                                                 │
│  2. Read authkey                                                │
│     AUTHKEY=$(cat /media/usb/node1_authkey.txt)                │
│                                                                 │
│  3. SOVEREIGN JOIN COMMAND (exact, ratified)                   │
│     sudo tailscale up \                                         │
│       --authkey="${AUTHKEY}" \                                  │
│       --hostname=kali-n1 \                                      │
│       --operator=xnai \                                         │
│       --accept-routes \                                         │
│       --advertise-tags=tag:asus                                 │
│                                                                 │
│  4. Verify join                                                 │
│     tailscale status                                            │
│     # Should show: kali-n1  100.x.x.x  xoe.nova.ai@  linux  tag:asus  │
│                                                                 │
│  5. Test MCP handshake                                          │
│     curl -s http://omega-hub.tail51f14a.ts.net:8016/mcp        │
│     # Should return MCP endpoint response (not 404/connection refused) │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 tskey-auth Prefix Validation

**Source**: [Tailscale Auth Keys](https://tailscale.com/docs/features/access-control/auth-keys)

> "Tailscale-generated auth keys are case-sensitive."

- All authkeys have prefix `tskey-auth-` (lowercase)
- **Validation**: `echo "$AUTHKEY" | grep -q '^tskey-auth-'` before use
- Case-sensitive: `TSKEY-AUTH-` will fail

### 5.4 Post-Join Verification Steps

```bash
# 1. Verify identity
tailscale status --json | jq '.Self.tags'  # Should include "tag:asus"

# 2. Verify connectivity to Node 0
tailscale ping omega-hub
curl -s http://omega-hub.tail51f14a.ts.net:8016/mcp

# 3. Verify MagicDNS
ping kali-n1.tail51f14a.ts.net  # From Node 0
ping omega-hub.tail51f14a.ts.net  # From Node 1

# 4. Verify SSH (from Node 0, if tag:opencode configured)
ssh xnai@kali-n1  # Should work via Tailscale SSH

# 5. Verify ACL enforcement
# Try to access non-allowed port → should fail
```

---

## 6️⃣ Federation Wire Invariants

### 6.1 What the Mesh Carries (ONLY)

| Traffic Type | Protocol | Port | Direction | Purpose |
|--------------|----------|------|-----------|---------|
| **Mesh SSH** | TCP | 22 | Admin → Node 1 | Remote administration |
| **MagicDNS** | UDP/TCP | 53 | Bidirectional | Hostname resolution |
| **Heartbeats** | ICMP | N/A | Bidirectional | Liveness checks |
| **MCP Route** | TCP | 8016 | Bidirectional | omega-hub API |

### 6.2 What NEVER Egresses Over Mesh

| Traffic | Reason |
|---------|--------|
| **Model inference** | T5/T6 floor is LOCAL-ONLY (M7 Local-First mandate) |
| **Model weights/downloads** | Local inference primary, cloud fallback only |
| **Training data** | Sovereign data never leaves node |
| **Secrets/keys** | Node 1 controls its own T5/T6 floor |

### 6.3 DERP Fallback Behavior

**Source**: [Tailscale Connection Types](https://tailscale.com/docs/reference/connection-types.md), [DERP Servers](https://tailscale.com/kb/1232/derp-servers)

| Connection Type | Latency | When Used |
|-----------------|---------|-----------|
| **Direct (UDP)** | Lowest (~1-5ms LAN, ~20-50ms WAN) | NAT traversal succeeds |
| **Peer Relay** | Low-Medium | Direct fails, peer relay available |
| **DERP Relay** | Highest (~50-200ms) | Last resort, hard NAT |

**Our Setup**: Both nodes on LAN (192.168.11.x) + Tailscale mesh → **Direct UDP expected**.

**Verification**:
```bash
# Check connection type
tailscale netcheck
# Look for: "Direct: true" or "DERP: <region>"
```

**DERP Regions**: Tailscale auto-selects nearest DERP home. For US East: typically `nyc`, `bos`, `iad`.

### 6.4 UDP Direct vs Relayed

- **Direct**: UDP hole-punching via DERP side-channel (STUN-like)
- **Relayed**: WireGuard packets encapsulated in TLS to DERP server
- **Security**: **Identical** — all end-to-end WireGuard encrypted. DERP cannot decrypt.
- **Performance**: Direct = 10-100x throughput vs DERP

---

## 7️⃣ Additional Gaps & Blind Spots Identified

### 7.1 Tailnet Lock (Not Yet Configured)

**Source**: [Tailnet Lock](https://tailscale.com/docs/features/tailnet-lock)

- **What**: Trust-on-first-use — new nodes require admin approval even with valid authkey
- **Impact**: If enabled, Node 1 authkey join would still require admin approval
- **Current**: Likely **disabled** (default for personal/small tailnets)
- **Recommendation**: Keep disabled for 2-node federation; enable when fleet grows >5 nodes

### 7.2 Device Posture Requirements

**Source**: [Tailnet Policy - Postures](https://tailscale.com/docs/features/tailnet-policy-file.md)

- Can require: OS version, Tailscale version, auto-update enabled, disk encryption
- **Recommendation**: Add posture check for Node 1 (ASUS) — require Linux + auto-update
- Example:
```hujson
"postures": {
  "posture:linux-auto-update": [
    "node:os == 'linux'",
    "node:tsAutoUpdate == true"
  ]
},
"defaultSrcPosture": ["posture:linux-auto-update"]
```

### 7.3 Key Expiry for Tagged Devices

**Critical Finding**: Tagged devices have **key expiry disabled by default**. This means:
- Node 1 (`tag:asus`) will **never require re-auth** unless manually triggered
- Node 0 (`tag:omega-hub`) after re-tag will also have expiry disabled
- **Risk**: If device compromised, attacker has persistent access
- **Mitigation**: Monitor `tailscale status --json` for `KeyExpiryDisabled: true`; consider enabling expiry for tagged devices in admin console

### 7.4 SSH Key Management

**Source**: [Tailscale SSH](https://tailscale.com/kb/1153/tailscale-ssh)

- Tailscale SSH uses **short-lived certificates** (not persistent keys)
- Certificate issued per-session by coordination server
- **No SSH key distribution needed** — ACL controls access
- **Audit trail**: All SSH sessions logged in admin console

### 7.5 Subnet Routing (Not Needed)

- We do **NOT** need subnet routers — both nodes are endpoints
- `--accept-routes` in Node 1 join command is harmless but unnecessary
- `--advertise-routes` not used

### 7.6 Exit Nodes (Not Needed)

- We do **NOT** route internet traffic through either node
- `--advertise-exit-node` not used
- `autoApprovers.exitNodes` in ACL not needed

### 7.7 IPv6 Considerations

- Tailscale provides **dual-stack** (IPv4 100.x.x.x + IPv6 fd7a:...)
- MagicDNS resolves both A and AAAA records
- **No action needed** — works automatically

### 7.8 Monitoring & Observability Gaps

| Gap | Recommendation |
|-----|----------------|
| No automated alerting for Node 1 offline | Add `tailscale status` cron + alert on missing `kali-n1` |
| No latency monitoring | `tailscale ping` cron + log RTT |
| No DERP usage alerting | `tailscale netcheck` cron → alert if `Direct: false` |
| No authkey audit log | Admin console → Keys page shows all authkey usage |

---

## 🎯 ACTIONABLE RECOMMENDATIONS (Exact Commands)

### Phase 1: ACL Policy Configuration (Node 0 Admin Console)

```bash
# 1. Open admin console: https://login.tailscale.com/admin/machines
# 2. Go to "Access Controls" → "Edit Policy"
# 3. Paste the following HuJSON policy:
```

```hujson
{
  "tagOwners": {
    "tag:omega-hub": ["autogroup:admin"],
    "tag:asus": ["autogroup:admin"],
    "tag:opencode": ["autogroup:admin"]
  },
  "acls": [
    {"action": "accept", "src": ["tag:omega-hub"], "dst": ["tag:asus:8016"]},
    {"action": "accept", "src": ["tag:asus"], "dst": ["tag:omega-hub:8016"]},
    {"action": "accept", "src": ["tag:opencode"], "dst": ["tag:asus:22"]},
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

### Phase 2: Node 0 Re-Tag

```bash
# On Node 0 (HP), after ACL is saved:
sudo tailscale up --advertise-tags=tag:omega-hub --force-reauth

# Verify
tailscale status --json | jq '.Self.tags'
# Should show: ["tag:omega-hub"]
```

### Phase 3: Mint Authkey for Node 1

```bash
# Admin Console → Keys → Generate auth key:
#   Description: "Node 1 (ASUS) federation join - ONE SHOT"
#   Type: One-off
#   Expiry: 1 day
#   Tags: tag:asus (ENABLED)
#   Pre-approved: YES
#   Ephemeral: NO
# COPY: tskey-auth-XXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### Phase 4: USB Ceremony

```bash
# On Node 0:
AUTHKEY="tskey-auth-XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
echo "$AUTHKEY" > /media/usb/node1_authkey.txt
cat > /media/usb/ceremony_manifest.json << 'EOF'
{
  "ceremony": "Tailscale L2 Federation Join",
  "node": "kali-n1 (ASUS ExpertBook)",
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

### Phase 5: Node 1 Join (Run on ASUS)

```bash
# On Node 1 (ASUS), with USB mounted:
cd /media/usb
sha256sum -c SHA256SUMS  # Verify integrity
AUTHKEY=$(cat node1_authkey.txt)
# Validate prefix
echo "$AUTHKEY" | grep -q '^tskey-auth-' || { echo "INVALID PREFIX"; exit 1; }

# SOVEREIGN JOIN COMMAND
sudo tailscale up \
  --authkey="${AUTHKEY}" \
  --hostname=kali-n1 \
  --operator=xnai \
  --accept-routes \
  --advertise-tags=tag:asus

# Verify
tailscale status
tailscale ping omega-hub
curl -s http://omega-hub.tail51f14a.ts.net:8016/mcp
```

### Phase 6: Post-Ceremony Verification (Node 0)

```bash
# On Node 0:
tailscale status
# Should show both:
# 100.123.51.67  omega-hub  ...  tag:omega-hub
# 100.x.x.x      kali-n1    ...  tag:asus

# Test bidirectional MCP
curl -s http://kali-n1.tail51f14a.ts.net:8016/mcp  # If Node 1 runs MCP
curl -s http://omega-hub.tail51f14a.ts.net:8016/mcp  # Node 0 MCP

# Test SSH
ssh xnai@kali-n1  # Via Tailscale SSH
```

---

## 📚 Citations & Sources

| Area | Sources (Tier) |
|------|----------------|
| Authkey best practices | [1] Tailscale Docs (Tier 1), [2] Secure Auth Keys (Tier 1), [3] learn_tailscale (Tier 2) |
| ACL policy / tagOwners | [4] Tailnet Policy File (Tier 1), [5] ACL Tags (Tier 1), [6] ACL Examples (Tier 1) |
| MagicDNS / DNS rebinding | [7] MagicDNS (Tier 1), [8] DNS Rebinding (Tier 1), [9] NousResearch #74664 (Tier 2) |
| Re-tagging procedure | [10] Apply Tags (Tier 1), [11] Tags Docs (Tier 1) |
| Air-gapped ceremony | [12] Secure Auth Keys (Tier 1), [13] Node Keys (Tier 1) |
| Wire invariants / DERP | [14] Connection Types (Tier 1), [15] DERP Servers (Tier 1), [16] Performance (Tier 1) |

---

## ⚠️ Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Node 0 re-tag fails (ACL not live) | Medium | High | Verify ACL saved before re-tag |
| Authkey expires before ceremony | Low | Medium | Use 1-day expiry, ceremony same day |
| Node 1 SSH fails (ACL missing) | Medium | Low | Test SSH after join, iterate ACL |
| DERP relay only (no direct) | Low | Medium | `tailscale netcheck` verify direct |
| MagicDNS resolution fails | Low | Low | Use Tailscale IPs as fallback |
| Key expiry disabled on tagged nodes | High | Medium | Monitor, consider enabling in admin console |

---

## ✅ Completion Criteria

The L2 Federation is **COMPLETE** when:

- [ ] ACL policy with `tagOwners` live in admin console
- [ ] Node 0 re-tagged as `tag:omega-hub` (verified via `tailscale status --json`)
- [ ] One-shot authkey with `tag:asus` minted
- [ ] USB ceremony executed (manifest + SHA256 verified)
- [ ] Node 1 joins as `kali-n1` with `tag:asus` (verified)
- [ ] Bidirectional MCP handshake works (Node 0 ↔ Node 1)
- [ ] Tailscale SSH works (admin → Node 1)
- [ ] MagicDNS resolves both hostnames
- [ ] `tailscale netcheck` shows direct connections
- [ ] L2_ACCEPTANCE.md documented with test results

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ TAILSCALE-L2-RESEARCH-COMPLETE ⬡ 2026-09-15 ⬡ 7/7 AREAS COVERED ⬡ CEREMONY-READY*