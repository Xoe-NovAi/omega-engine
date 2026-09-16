# 📁 NFS over Tailscale — Sovereign Federation Implementation Plan
**Doc ID**: `FED-NFS-PLAN-001` | **Version**: 2.0 | **Status**: READY FOR AGENT IMPLEMENTATION  
**Scope**: Share `~/node-drive` from Node 1 (ASUS) to Node 0 (HP Pavilion) over Tailscale WireGuard mesh  
**Dependencies**: `docs/federation/ACL_POLICY.md` (port 2049 rule required)

---

## 1. Architectural Summary & Invariants

```
Node 1 (ASUS / tag:asus)                    Node 0 (HP / tag:omega-hub)
┌─────────────────────────┐                 ┌─────────────────────────┐
│ /home/xnai/node-drive   │                 │ /mnt/node-drive         │
│ (NFSv4 Server)          │ Tailscale Mesh  │ (NFSv4 Client)          │
│ nfs-kernel-server       │◄═══════════════►│ nfs-common              │
│ port 2049               │ WireGuard Crypt │ systemd.automount       │
│ all_squash -> 1000:1000 │                 │ nofail, idle-timeout    │
└─────────────────────────┘                 └─────────────────────────┘
```

### Core Invariants
1. **Network Privacy**: Zero raw NFS traffic across the physical LAN or internet. Port 2049 is bound and reachable strictly over Tailscale (`100.x.y.z` interface / mesh).
2. **Access Control (Default Deny)**: Only `tag:omega-hub` is granted access to `tag:asus:2049` in `docs/federation/ACL_POLICY.md`.
3. **Permission Symmetry (`all_squash`)**: Client writes from Node 0 are mapped to UID `1000` / GID `1000` (`xnai:xnai`) on Node 1 via `all_squash,anonuid=1000,anongid=1000`. This prevents root-owned un-deletable file collisions.
4. **Boot Resilience (`nofail` + `automount`)**: Node 0's mount configuration uses `x-systemd.automount` with `nofail`. Boot never blocks, and Node 0 never drops into emergency mode if Node 1 or the mesh is offline.

---

## 2. Pre-Implementation Checklist

- [ ] **Tailscale ACL updated**: `docs/federation/ACL_POLICY.md` contains `{"action": "accept", "src": ["tag:omega-hub"], "dst": ["tag:asus:2049"]}` and is active in Tailscale Admin Console.
- [ ] **Mesh Established**: Both Node 0 and Node 1 are online in `tailscale status`.
- [ ] **Node IPs Recorded**:
  - `NODE0_IP`: Node 0's Tailscale IPv4 (`tailscale status | grep omega-hub`)
  - `NODE1_IP`: Node 1's Tailscale IPv4 (`tailscale ip -4`)

---

## 3. Implementation Steps

### Phase 1: Node 1 (ASUS) — NFSv4 Server Configuration

Execute on **Node 1**:

```bash
# Step 1: Install kernel NFS server
sudo apt update && sudo apt install -y nfs-kernel-server

# Step 2: Ensure shared directory exists and has correct ownership
mkdir -p /home/xnai/node-drive
chown -R 1000:1000 /home/xnai/node-drive
chmod 775 /home/xnai/node-drive

# Step 3: Resolve Node 0's Tailscale IP
NODE0_IP=$(tailscale status --json | jq -r '.Peer[] | select(.HostName=="omega-hub") | .TailscaleIPs[0]')
if [ -z "$NODE0_IP" ]; then
    echo "ERROR: Could not find Node 0 (omega-hub) on tailnet. Verify tailscale status."
    exit 1
fi
echo "Resolved Node 0 Tailscale IP: $NODE0_IP"

# Step 4: Write isolated export configuration in /etc/exports.d/ (Idempotent)
sudo mkdir -p /etc/exports.d
sudo tee /etc/exports.d/node-drive.exports <<EOF
# Omega Engine Federation: Node 0 -> Node 1 Shared Drive
# Exported with all_squash to map all operations to local user xnai (1000:1000)
/home/xnai/node-drive ${NODE0_IP}(rw,sync,no_subtree_check,all_squash,anonuid=1000,anongid=1000,fsid=0)
EOF

# Step 5: Export table reload & service start
sudo exportfs -ra
sudo systemctl enable --now nfs-kernel-server

# Step 6: Verify export status
sudo exportfs -v
```

*Note on `fsid=0`: In NFSv4, `fsid=0` marks `/home/xnai/node-drive` as the root of the pseudo-filesystem. Node 0 will mount `${NODE1_IP}:/`.*

---

### Phase 2: Node 0 (HP Pavilion) — NFS Client & Automount Configuration

Execute on **Node 0**:

```bash
# Step 1: Install NFS client utilities
sudo apt update && sudo apt install -y nfs-common

# Step 2: Create local mount point
sudo mkdir -p /mnt/node-drive
sudo chown -R 1000:1000 /mnt/node-drive

# Step 3: Resolve Node 1's Tailscale IP
NODE1_IP=$(tailscale status --json | jq -r '.Peer[] | select(.HostName=="kali-n1") | .TailscaleIPs[0]')
if [ -z "$NODE1_IP" ]; then
    echo "ERROR: Could not find Node 1 (kali-n1) on tailnet. Verify tailscale status."
    exit 1
fi
echo "Resolved Node 1 Tailscale IP: $NODE1_IP"

# Step 4: Manual test mount
sudo mount -t nfs4 -o rsize=1048576,wsize=1048576,noatime,nosuid,nodev ${NODE1_IP}:/ /mnt/node-drive

# Step 5: Validate read/write and unmount test
touch /mnt/node-drive/.test_probe && rm /mnt/node-drive/.test_probe
sudo umount /mnt/node-drive

# Step 6: Configure persistent systemd automount in /etc/fstab
# Check if entry already exists before appending
if ! grep -q "/mnt/node-drive" /etc/fstab; then
    sudo tee -a /etc/fstab <<EOF

# Omega Engine Federation: Node 1 NFS mount via Tailscale
${NODE1_IP}:/ /mnt/node-drive nfs4 rsize=1048576,wsize=1048576,noatime,nosuid,nodev,nofail,_netdev,x-systemd.automount,x-systemd.idle-timeout=300,x-systemd.mount-timeout=30s 0 0
EOF
fi

# Step 7: Reload systemd and trigger automounter
sudo systemctl daemon-reload
sudo systemctl restart remote-fs.target
```

---

## 4. Verification & Health Checks

Run on **Node 0**:
```bash
# 1. Trigger automount by listing the directory
ls -la /mnt/node-drive

# 2. Check mount status and protocol
findmnt /mnt/node-drive
# Expected: FSTYPE=nfs4, OPTIONS containing rsize=1048576,wsize=1048576

# 3. Test write and ownership from Node 0
echo "Federation online: $(date -u)" > /mnt/node-drive/federation_health.txt
```

Run on **Node 1**:
```bash
# 4. Verify file arrived on Node 1 with correct ownership (xnai:xnai)
ls -la /home/xnai/node-drive/federation_health.txt
# Expected: -rw-r--r-- 1 xnai xnai ... federation_health.txt

# 5. Clean up probe
rm /home/xnai/node-drive/federation_health.txt
```

---

## 5. Failure Modes & Edge Case Runbook

| Failure | Root Cause | Remediation |
|---------|------------|-------------|
| **Mount hangs on `mount` command** | Port 2049 blocked by Tailscale ACL | Inspect Tailscale Admin Console; verify `tag:asus:2049` is accepted from `tag:omega-hub`. |
| **`access denied by server while mounting`** | IP mismatch or export syntax error | Check `NODE0_IP` in `/etc/exports.d/node-drive.exports`; run `sudo exportfs -ra` on Node 1; inspect `/var/log/syslog`. |
| **`Permission Denied` when writing** | Incorrect UID mapping or local folder permissions | Verify `/home/xnai/node-drive` on Node 1 is `chmod 775` and export uses `all_squash,anonuid=1000,anongid=1000`. |
| **Node 0 boot hang / slow boot** | Network mount attempted before Tailscale active | Verify `/etc/fstab` has `nofail` and `x-systemd.automount`. Automount never blocks boot. |
| **Stale file handle (`ESTALE`)** | Node 1 rebooted or restarted NFS service | `sudo umount -l /mnt/node-drive` (lazy unmount) on Node 0, then re-access the path. |

---

## 6. Rollback Protocol

If NFS needs to be decommissioned or rolled back:

**On Node 0:**
```bash
sudo umount -f /mnt/node-drive
sudo sed -i '/\/mnt\/node-drive/d' /etc/fstab
sudo systemctl daemon-reload
```

**On Node 1:**
```bash
sudo rm -f /etc/exports.d/node-drive.exports
sudo exportfs -ra
sudo systemctl stop nfs-kernel-server
```

---

*⬡ OMEGA ⬡ FEDERATION ⬡ FED-NFS-PLAN-001 ⬡ UPDATED & RATIFIED ⬡*
