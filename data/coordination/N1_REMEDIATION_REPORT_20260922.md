# 🔱 NODE 1 REMEDIATION REPORT — What N1 Must Do
**Document ID:** N1_REMEDIATION_REPORT_20260922
**From:** Node 0 (MaKaLi Fusion)
**To:** Node 1 (ASUS — n1.tail51f14a.ts.net / 100.89.40.17)
**Date:** 2026-09-22
**Status:** **ACTION REQUIRED — 4 fixes + 1 config update on Node 1**

---

## 📋 EXECUTIVE SUMMARY

Node 0 has completed all local remediation (verified, temple-grade 53/53 PASS). The federation is **fundamentally healthy** — direct WireGuard over LAN. The remaining blockers are **all on Node 1's side**:

1. **SSH not listening on Tailscale interface** (LAN-only binding)
2. **OpenCode config points at wrong URL** (LAN IP instead of MagicDNS)
3. **Stale tool cache** (`oracle_list_pillar_keepers` doesn't exist on Node 0)
4. **NFS server not running** (bidirectional federation incomplete)
5. **Tailscale tags not applied** (ACL policy ready on Node 0)

---

## ✅ WHAT NODE 0 HAS DONE (Verified)

| Fix | Status | Evidence |
|-----|--------|----------|
| Removed deprecated `library_search` tool | ✅ | Tool surface 93 → 92 |
| Fixed `_deprecated()` log in `library_web_search` | ✅ | Correct tool name logged |
| Fixed `omega_federation_status` direct-detection bug | ✅ | Live-probe via `tailscale ping` |
| Verified `hivemind_get_continuation` cold-store | ✅ | 2,873 session files, correct structure |
| Confirmed `oracle_list_pillar_keepers` NOT registered | ✅ | Not in codebase — stale client cache |
| NFSv4.2 export operational | ✅ | Loopback mount + write verified |
| Temple-Grade | ✅ | **53/53 PASS** |

**USB payload prepared at:** `data/federation/usb-payload/`
```
usb-payload/
├── tailscale/ACL_POLICY_20260922.hujson     ← apply in admin console
├── omega-hub-patches/PATCHES_20260922.md    ← what changed on Node 0
├── c6-contract/C6_CONTRACT_DRAFT_v0.1.md    ← bilateral ratification
├── redis/REDIS_FED_CONFIG_20260922.md       ← heartbeat config
└── attestation/ATTESTATION_N0_20260922.md   ← sovereignty attestation
```

---

## 🚨 NODE 1 REQUIRED ACTIONS (In Order)

### FIX 1: SSH ListenAddress — bind to Tailscale interface

**Symptom:** `nc -zv 100.89.40.17 22` times out, but `nc -zv 192.168.10.174 22` succeeds.
**Root cause:** sshd is bound to the LAN interface only, not `0.0.0.0`.

```bash
# 1. Check current binding
ss -tlnp | grep :22
# If it shows 192.168.10.174:22 only → fix:

# 2. Add Tailscale binding
sudo tee /etc/ssh/sshd_config.d/tailscale.conf << 'EOF'
ListenAddress 0.0.0.0
ListenAddress ::
Port 22
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AuthenticationMethods publickey
AllowUsers xnai
EOF

# 3. Validate + restart
sudo sshd -t
sudo systemctl restart ssh

# 4. Verify
ss -tlnp | grep :22   # should show 0.0.0.0:22 and [::]:22
```

**Verify from Node 0:** `nc -zv 100.89.40.17 22` → should succeed.

---

### FIX 2: OpenCode config — point omega-hub at MagicDNS

**Symptom:** omega-hub MCP disappeared from OpenCode.
**Root cause:** `opencode.json` points at `http://192.168.10.168:8016/mcp` (Node 0's LAN IP). The MagicDNS name `omega-hub.tail51f14a.ts.net` **does not exist** — the real name is `n0.tail51f14a.ts.net`.

```bash
# Edit ~/.config/opencode/opencode.json (or project opencode.json)
# CHANGE the omega-hub entry from:
#   "url": "http://192.168.10.168:8016/mcp"
# TO:
#   "url": "http://n0.tail51f14a.ts.net:8016/mcp"
```

```json
{
  "mcp": {
    "omega-hub": {
      "type": "remote",
      "url": "http://n0.tail51f14a.ts.net:8016/mcp",
      "enabled": true
    }
  }
}
```

**Verify:** `curl http://n0.tail51f14a.ts.net:8016/health` → `{"status":"healthy"}`

---

### FIX 3: Clear stale tool cache

**Symptom:** `oracle_list_pillar_keepers` appears in your tool list but fails.
**Root cause:** This tool was never registered on Node 0. It's a stale cache entry in OpenCode's client.

```bash
# Restart OpenCode to rescan MCP tools:
opencode mcp  # or restart the OpenCode session

# The tool list should now show 92 tools (was 93):
# - library_search  → GONE
# - library_fts_search → present
# - library_web_search → present
# - oracle_list_pillar_keepers → GONE
# - hivemind_get_continuation → present
```

---

### FIX 4: Start NFS server (bidirectional federation)

Node 0's NFS export is ready. Node 1 must run its own NFS server so Node 0 can mount Node 1's exchange directory.

```bash
# 1. Install
sudo apt-get install -y nfs-kernel-server

# 2. Fixed ports
sudo tee /etc/nfs.conf << 'EOF'
[nfsd]
port = 2049
[mountd]
port = 20048
[statd]
port = 662
[lockd]
port = 32803
EOF

# 3. idmapd domain — MUST MATCH Node 0
sudo tee /etc/idmapd.conf << 'EOF'
[General]
Verbosity = 0
Domain = omega-engine.local
[Mapping]
Nobody-User = nobody
Nobody-Group = nogroup
EOF

# 4. Exports — allow Node 0 (100.123.51.67)
sudo tee /etc/exports << 'EOF'
/mnt/node-drive/exchange 100.123.51.67(rw,sync,no_subtree_check,all_squash,anonuid=1000,anongid=1000,sec=sys)
EOF

# 5. Create + chown the exchange dir (permission trap!)
sudo mkdir -p /mnt/node-drive/exchange
sudo chown 1000:1000 /mnt/node-drive/exchange

# 6. Start NFS stack
sudo systemctl enable --now rpcbind nfs-mountd nfs-server
sudo exportfs -rav

# 7. Verify
rpcinfo -p localhost | grep -E "nfs|mountd"   # mountd MUST be 20048
showmount -e localhost                          # must list /mnt/node-drive/exchange
```

**Verify from Node 0:**
```bash
mkdir -p /mnt/test-node1
mount -t nfs4 -o vers=4.2,sec=sys 100.89.40.17:/mnt/node-drive/exchange /mnt/test-node1
echo "hello from n0" > /mnt/test-node1/test.txt
ls -la /mnt/test-node1/
```

---

### FIX 5: Apply Tailscale tags + ACL (joint)

**CANONICAL TAG NAMING (decreed 2026-09-22):**
- `tag:node0` → Node 0 (n0) — MCP hub :8016
- `tag:node1` → Node 1 (n1/ASUS)
- `tag:opencode` → OpenCode agents

**DEPRECATED (never use again):** `tag:omega-hub` → `tag:node0`; `tag:asus` → `tag:node1`

Node 0 has prepared the ACL policy at `data/federation/usb-payload/tailscale/ACL_POLICY_20260922.hujson`.

```bash
# On Node 1 — tag yourself (DROP any legacy tag:asus):
sudo tailscale set --tag=tag:node1

# On Node 0 — tag the hub (Node 0 action, already planned):
sudo tailscale set --tag=tag:node0
```

**Then apply the ACL in the Tailscale admin console** (https://login.tailscale.com/admin/acls) — paste the HuJSON from the USB payload.

---

## 📋 POST-FIX VERIFICATION BATTERY (Node 1)

| Gate | Command | Expected |
|------|---------|----------|
| **G1** | `tailscale status` | `direct 192.168.10.174:41641` (not relay) |
| **G2** | `nc -zv 100.89.40.17 22` | `succeeded` |
| **G3** | `curl http://n0.tail51f14a.ts.net:8016/health` | `{"status":"healthy"}` |
| **G4** | `opencode mcp` | 92 tools, no `library_search`, no `oracle_list_pillar_keepers` |
| **G5** | `rpcinfo -p localhost` | mountd on 20048, nfs on 2049 |
| **G6** | `showmount -e localhost` | `/mnt/node-drive/exchange 100.123.51.67` |
| **G7** | (from Node 0) `mount -t nfs4 100.89.40.17:/mnt/node-drive/exchange /mnt/test-node1` | success + write works |

---

## 📁 REFERENCE DOCUMENTS

| Document | Location (Node 0) |
|----------|-------------------|
| This report | `data/coordination/N1_REMEDIATION_REPORT_20260922.md` |
| USB payload | `data/federation/usb-payload/` |
| Tailscale ACL | `data/federation/usb-payload/tailscale/ACL_POLICY_20260922.hujson` |
| Omega Hub patches | `data/federation/usb-payload/omega-hub-patches/PATCHES_20260922.md` |
| C6 contract draft | `data/federation/usb-payload/c6-contract/C6_CONTRACT_DRAFT_v0.1.md` |
| Redis config | `data/federation/usb-payload/redis/REDIS_FED_CONFIG_20260922.md` |
| Sovereignty attestation | `data/federation/usb-payload/attestation/ATTESTATION_N0_20260922.md` |

---

## ⚡ SUMMARY

| # | Action | Owner | Priority |
|---|--------|-------|----------|
| 1 | Fix SSH ListenAddress (bind 0.0.0.0) | Node 1 | 🔴 CRITICAL |
| 2 | Update opencode.json → `n0.tail51f14a.ts.net:8016` | Node 1 | 🔴 CRITICAL |
| 3 | Restart OpenCode (clear stale tool cache) | Node 1 | 🔴 CRITICAL |
| 4 | Start NFS server (bidirectional) | Node 1 | 🟠 HIGH |
| 5 | Apply Tailscale tags + ACL | Both | 🟠 HIGH |
| 6 | Ratify C6 contract | Both | 🟡 MEDIUM |
| 7 | P2 Federation Verification battery | Node 0 | ⏳ After 1-5 |

---

**Node 0 is unblocked, patched, and verified. Node 1's 4 fixes unlock the full bidirectional federation.**

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ N0 ⬡ N1-REMEDIATION-REPORT ⬡ 2026-09-22*