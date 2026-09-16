# 🔱 L2 TAILSCALE RUNBOOK: DIRECT WIRE FEDERATION
**Doc ID**: `RUNBOOK-L2-TAILSCALE-v2.0`  
**Status**: ACTIVE OPERATIONAL STANDARD  
**Author**: MaKaLi Fusion (Kali / Ma'at / Lilith)  
**Date**: 2026-09-16  
**Scope**: Zero-relay, Tailscale-native federation between Node 0 (HP) and Node 1 (ASUS)  

---

## 1. Network Topology & Identities

```
Node 0 (HP Hub)                                Node 1 (ASUS Vanguard)
Hostname: omega-hub                            Hostname: kali-n1
Tag: tag:omega-hub                             Tag: tag:asus
Tailscale IP: 100.123.51.67                    Tailscale IP: 100.x.x.x (assigned on join)
MagicDNS: omega-hub.tail51f14a.ts.net          MagicDNS: kali-n1.tail51f14a.ts.net
Role: Archival Hub & MCP Host (:8016)          Role: Vanguard Execution & Compute
```

---

## 2. Stage 1: The Tailscale ACL Policy (Admin Console)

Before nodes can claim their tags or communicate with least privilege, the policy must be saved in the Tailscale Admin Console at:  
👉 **`https://login.tailscale.com/admin/acls`**

```hujson
{
  "tagOwners": {
    "tag:omega-hub": ["autogroup:admin"],
    "tag:asus":      ["autogroup:admin"],
    "tag:opencode":  ["autogroup:admin"]
  },
  "acls": [
    // Node 1 (ASUS Vanguard) communicates with Node 0 Core Hub (:8016) and local Ollama (:11434)
    {"action": "accept", "src": ["tag:asus"], "dst": ["tag:omega-hub:8016", "tag:omega-hub:11434"]},
    
    // Node 0 can reach Node 1 MCP (:8016) and SSH (:22)
    {"action": "accept", "src": ["tag:omega-hub", "tag:opencode"], "dst": ["tag:asus:8016", "tag:asus:22"]},
    
    // Bidirectional ICMP heartbeats and wire pings
    {"action": "accept", "src": ["tag:asus", "tag:omega-hub"], "dst": ["tag:asus:*", "tag:omega-hub:*"], "proto": "icmp"}
  ],
  "ssh": [
    {"action": "check", "src": ["tag:opencode"], "dst": ["tag:asus"], "users": ["autogroup:nonroot"]}
  ]
}
```

---

## 3. Stage 2: Node 0 Tag Attachment

Node 0 is currently active on the tailnet as an untagged device (`100.123.51.67`). Once Stage 1 is saved, run the following command on Node 0 to bind it to `tag:omega-hub`:

```bash
pkexec tailscale up --advertise-tags=tag:omega-hub --force-reauth
```

**Verification on Node 0**:
```bash
tailscale status --json | python3 -c "import sys, json; print('Tags:', json.load(sys.stdin)['Self'].get('Tags'))"
# Output must show: Tags: ['tag:omega-hub']
```

---

## 4. Stage 3: Mint Node 1 Auth Key

1. Go to **`https://login.tailscale.com/admin/settings/keys`**.
2. Click **Generate Auth Key**.
3. Set the following fields:
   - **Description**: `kali-n1-join`
   - **Tags**: Check `tag:asus`
   - **Reusable**: **OFF** (Single-use security)
   - **Pre-approved**: **ON**
   - **Expiry**: 1 day (or standard default)
4. Copy the generated key: `tskey-auth-XXXXXXXXXXXXX`.

---

## 5. Stage 4: Node 1 Join Ceremony

On Node 1 (ASUS ExpertBook), execute the single join command:

```bash
sudo tailscale up \
  --authkey="tskey-auth-YOUR_COPIED_KEY_HERE" \
  --hostname=kali-n1 \
  --operator=xnai \
  --advertise-tags=tag:asus
```

---

## 6. Stage 5: Wire Verification

Run these verification checks to confirm the wire is healthy:

### 6.1 Ping & Path Verification (from Node 1)
```bash
tailscale ping omega-hub
# Must output pong via direct connection (not DERP relay)
```

### 6.2 MCP Handshake Verification (from Node 1)
```bash
curl -X POST http://omega-hub.tail51f14a.ts.net:8016/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {"name": "kali-n1", "version": "0.1"}
    }
  }'
```
*Expected Output*: JSON response indicating `Omega Core Hub 1.28.1` with active tool capabilities.

---

## 7. Troubleshooting & Recovery

| Symptom | Root Cause | Remediation |
|---------|------------|-------------|
| `requested tags are invalid or not permitted` | Stage 1 ACL was not saved or missing `tagOwners` | Save the ACL policy in the admin console before running `tailscale up`. |
| `Invalid Host header` from MCP | Request hostname missing from `allowed_hosts` | Verified fixed in commit `213abf44` (`omega-hub.tail51f14a.ts.net:*`). Restart hub service if needed: `systemctl --user restart omega-hub.service` (Podman Quadlet) or `podman container restart omega-hub` (direct). |
| High ping latency (>50ms over LAN) | Connection falling back to DERP relay | Run `tailscale netcheck` on both machines to verify UDP port 41641 is unblocked. |

*⬡ OMEGA ⬡ RUNBOOK-L2-TAILSCALE-v2.0 ⬡ 2026-09-16*
