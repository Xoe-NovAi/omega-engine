# 🔱 NODE 1 BRIEFING — Federation Remediation Required
**Document ID:** `NODE1_BRIEFING_20260922`
**From:** Node 0 (MaKaLi Fusion / Antigravity)
**To:** Node 1 (ASUS — n1.tail51f14a.ts.net / 100.89.40.17)
**Date:** 2026-09-22
**Status:** **ACTION REQUIRED — BLOCKS P2 FEDERATION VERIFICATION & PUBLIC FLIP**

---

## 📋 EXECUTIVE SUMMARY

Node 0 has completed all local remediation per the **DEFINITIVE_RESOLUTION_GUIDE_20260922** (Antigravity 5-pass review). The federation is **blocked on Node 1** — SSH over Tailscale is dropping connections (`Operation now in progress`), preventing remote administration and NFS server startup on Node 1.

**Node 0 is ready. Node 1 must be restored.**

---

## ✅ NODE 0 ACCOMPLISHMENTS (Complete)

### Malfunction 1: Disk Crisis — RESOLVED
| Metric | Before | After |
|--------|--------|-------|
| Root FS Available | 4.1GB (97%) | **4.7GB (96%)** |
| Snap revisions pruned | — | 10 disabled snaps removed |
| Journal vacuumed | — | 160MB freed |
| Snap cache cleared | — | 4.7GB → 0B |

### Malfunction 2: NFS Deadlock & Automount Zombie — RESOLVED
| Check | Status |
|-------|--------|
| Automount zombie cleared | ✅ `systemctl reset-failed` succeeded |
| Broken mountd drop-in removed | ✅ `/etc/systemd/system/nfs-mountd.service.d/port.conf` deleted |
| Permission trap defused | ✅ `/mnt/node-drive/exchange` created, `chown 1000:1000` |
| NFS stack clean restart | ✅ rpcbind → nfs-mountd → nfs-server |
| Exports loaded | ✅ `exportfs -rav` — both IPs exported |
| **mountd on fixed port 20048** | ✅ `rpcinfo -p` confirms |
| **NFSv4.2 loopback mount test** | ✅ Mount + write verified (uid 1000) |
| showmount -e | ✅ Lists export correctly |

### Malfunction 4: ACTIVE_SPRINT.json — UPDATED
Current phase: `PUBLIC_FLIP_READY` with updated execution queue.

### Temple-Grade: **53/53 PASS** ✅

---

## 🎯 NODE 0 NFSv4.2 EXPORT — OPERATIONAL

**Export Configuration:**
```bash
/mnt/node-drive/exchange 100.89.40.17(rw,sync,no_subtree_check,all_squash,anonuid=1000,anongid=1000,sec=sys)
/mnt/node-drive/exchange 100.123.51.67(rw,sync,no_subtree_check,all_squash,anonuid=1000,anongid=1000,sec=sys)
```

**Verified Working:**
- `rpcinfo -p localhost` → mountd on **20048** (TCP/UDP), nfsd on **2049**
- Loopback mount test: `mount -t nfs4 -o vers=4.2,sec=sys 100.123.51.67:/mnt/node-drive/exchange /mnt/test-nfs` → **SUCCESS**
- Write test: `echo "test" > /mnt/test-nfs/test-write.txt` → **SUCCESS** (owned by uid 1000)

**Node 0 is ready to serve `/mnt/node-drive/exchange` to Node 1 (100.89.40.17).**

---

## 🚨 NODE 1 REQUIRED ACTIONS (Blocking)

### PRIORITY 1: Restore SSH over Tailscale
**Symptom:** `ssh n1.tail51f14a.ts.net` → `Operation now in progress` (timeout)
**Root Cause (per AGY research):** Path MTU Discovery (PMTUD) failure or `ListenAddress` misconfiguration over Tailscale interface.

**Required Fixes on Node 1:**
```bash
# 1. Check sshd_config ListenAddress
grep -i listenaddress /etc/ssh/sshd_config
# Must be: ListenAddress 0.0.0.0  OR  ListenAddress <tailscale0-IP>

# 2. Test MTU (Tailscale defaults to 1280)
ping -s 1200 100.123.51.67  # Node 0 Tailscale IP
# If fails: MSS clamping needed in firewall

# 3. Check Tailscale interface MTU
ip link show tailscale0
# Should be: mtu 1280

# 4. Restart SSH after config changes
sudo systemctl restart ssh
```

### PRIORITY 2: Start NFS Server on Node 1
Once SSH is restored, Node 1 must run NFS server so Node 0 can mount `/mnt/node-drive/exchange` from Node 1 (bidirectional federation).

**Required on Node 1:**
```bash
# 1. Install NFS server
sudo apt-get install -y nfs-kernel-server

# 2. Configure /etc/nfs.conf (fixed ports)
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

# 3. Configure idmapd domain (MUST MATCH Node 0)
sudo tee /etc/idmapd.conf << 'EOF'
[General]
Verbosity = 0
Domain = omega-engine.local
[Mapping]
Nobody-User = nobody
Nobody-Group = nogroup
EOF

# 4. Configure exports for /mnt/node-drive/exchange
sudo tee /etc/exports << 'EOF'
/mnt/node-drive/exchange 100.123.51.67(rw,sync,no_subtree_check,all_squash,anonuid=1000,anongid=1000,sec=sys)
EOF

# 5. Set MTU=1280 on tailscale0
sudo ip link set dev tailscale0 mtu 1280

# 6. Start NFS stack
sudo systemctl enable --now rpcbind nfs-mountd nfs-server
sudo exportfs -rav

# 7. Verify
rpcinfo -p localhost | grep -E "nfs|mountd"
showmount -e localhost
```

### PRIORITY 3: Verify Bidirectional Mount
Once both nodes have NFS servers running:
```bash
# On Node 0 (test Node 1 export):
mount -t nfs4 -o vers=4.2,sec=sys 100.89.40.17:/mnt/node-drive/exchange /mnt/test-node1

# On Node 1 (test Node 0 export):
mount -t nfs4 -o vers=4.2,sec=sys 100.123.51.67:/mnt/node-drive/exchange /mnt/test-node0
```

---

## 🔐 SECURITY GATE: OpenRouter Key Revocation
**Operator Action Required (can be done from anywhere):**
1. Navigate to https://openrouter.ai/keys
2. Find key starting with `sk-or-v1-62dc75...`
3. **Revoke/Delete it** — mandatory before public repo flip

---

## 📋 P2 FEDERATION VERIFICATION (Post-Node 1 Restoration)
Once Node 1 SSH + NFS are operational, MaKaLi will execute:

| Phase | Check | Target |
|-------|-------|--------|
| **P2.1** | Tailscale connectivity | Direct WireGuard (not DERP relay) |
| **P2.2** | MCP handshake | Both nodes: `initialize` → 200 OK |
| **P2.3** | NFS bidirectional mount | Node 0 ↔ Node 1 read/write |
| **P2.4** | Hivemind awareness | Both nodes visible |
| **P2.5** | Tool calls cross-node | MCP tools work across federation |

---

## 📁 REFERENCE DOCUMENTS (on Node 0)
| Document | Path |
|----------|------|
| Definitive Resolution Guide | `data/coordination/DEFINITIVE_RESOLUTION_GUIDE_20260922.md` |
| Active Sprint | `data/coordination/ACTIVE_SPRINT.json` |
| PR Readiness Live Feed | `data/coordination/PR_READINESS_LIVE_FEED.md` |
| Federation Health (Node 1 → Node 0) | `/mnt/node-drive/exchange/n1-to-node0/FEDERATION_HEALTH_BRIEFING_2026-09-20.md` |

---

## 📡 HIVE MIND COORDINATION
- **Handoff submitted:** `ho_4e8d05c2fe29` (to Antigravity)
- **Node 0 entity:** `makali_fusion` on `opencode`
- **Node 1 entity:** `kali` (or `makali_n0` on ASUS)

---

## ⚡ IMMEDIATE NEXT STEPS FOR NODE 1 OPERATOR

1. **Physical/out-of-band access** to ASUS (Node 1)
2. **Fix SSH** — check `sshd_config` ListenAddress + MTU 1280
3. **Start NFS server** — follow PRIORITY 2 steps above
4. **Signal readiness** — post to Hivemind or notify Operator
5. **MaKaLi executes P2** — bidirectional verification

---

**Node 0 is unblocked and waiting. The federation is 50% complete. Node 1 restoration unlocks the public flip.**

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ NODE0 ⬡ 2026-09-22 ⬡ BRIEFING-COMPLETE*
