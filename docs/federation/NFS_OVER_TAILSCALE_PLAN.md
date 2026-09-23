# 📁 NFS over Tailscale — Sovereign Federation Implementation Plan — **IMPLEMENTED & VERIFIED 2026-09-21**
**Doc ID**: `FED-NFS-PLAN-001` | **Version**: 2.1 | **Status**: ✅ **IMPLEMENTED & FULLY VERIFIED**  
**Scope**: Share `~/node-drive` from Node 1 (ASUS) to Node 0 (HP Pavilion) over Tailscale WireGuard mesh — **LIVE**  
**Dependencies**: `docs/federation/ACL_POLICY.md` (port 2049 rule required), `docs/federation/NAMESPACE_COLLISION_STRATEGY.md`

---

## 1. Architectural Summary & Invariants

```
Node 1 (ASUS / xnai-n1-asus)                Node 0 (HP / xnai-n0-hp)
100.89.40.17                                100.123.51.67
┌─────────────────────────┐                 ┌─────────────────────────┐
│ /home/xnai/node-drive   │                 │ /mnt/node-drive         │
│ (Pure NFSv4.2 Server)   │ Tailscale Mesh  │ (NFSv4.2 Client)        │
│ Bound strictly to TS IP │◄═══════════════►│ nfs-common              │
│ port 2049 only          │ WireGuard Crypt │ systemd.automount       │
│ all_squash -> 1000:1000 │                 │ nofail, idle-timeout    │
└─────────────────────────┘                 └─────────────────────────┘
```

### Core Invariants
1. **Network Privacy & Interface Binding**: Zero raw NFS traffic across the physical LAN or internet. `nfsd` is configured in `/etc/nfs.conf` with `host = 100.89.40.17` to bind **strictly** to Tailscale. It does NOT listen on `0.0.0.0` or physical Wi-Fi/Ethernet (`192.168.10.x`).
2. **Protocol Hardening (Pure NFSv4.2)**: NFSv2 and NFSv3 are explicitly disabled in `/etc/nfs.conf`. No legacy port sprawl (`rpcbind` port 111, `mountd` port 20048, `statd`, `lockd`). TCP 2049 is the only port. Enables `copy_file_range` for fast server-side model copies and sparse file support.
3. **Access Control (Default Deny)**: Only Node 0's identity is permitted in `/etc/exports.d/node-drive.exports` and `docs/federation/ACL_POLICY.md`.
4. **Permission Symmetry (`all_squash`)**: Client writes from Node 0 are mapped to UID `1000` / GID `1000` (`xnai:xnai`) on Node 1 via `all_squash,anonuid=1000,anongid=1000`. This prevents root-owned un-deletable file collisions.
5. **Boot Resilience (`nofail` + `automount`)**: Node 0's mount configuration uses `x-systemd.automount` with `nofail`. Boot never blocks, and Node 0 never drops into emergency mode if Node 1 or the mesh is offline.

---

## 2. Hostname Architecture: Tri-Axial Schema (`<user>-<node>-<hardware>`)

To prevent namespace collisions in multi-user environments and the broader Omegaverse:

| Node | Hostname | Role / Silicon Profile |
|------|----------|------------------------|
| **Node 1** | `xnai-n1-asus` | Exploration Vanguard — Intel i7-13620H (10C/16T, CPU-only), 16GB DDR5 |
| **Node 0** | `xnai-n0-hp` (or `omega-hub`) | Archival Bastion — Core database, statekeeper, model repository |

**Why this schema is mandatory:**
- `<user>`: Isolates user realm (`xnai` vs `alice` vs consortiums).
- `<node>`: Designates topological hierarchy (`n0` Bastion vs `n1` Vanguard).
- `<hardware>`: Informs delegator agents of silicon capability (CPU-only vs GPU) for model routing.
- Complies strictly with RFC 1123 DNS requirements for MagicDNS (`xnai-n1-asus.tail51f14a.ts.net`).

---

## 3. Operational Caveats & Hazards

1. **SQLite WAL Database Hazard**:
   - **Never place SQLite databases using WAL mode (`PRAGMA journal_mode=WAL`) on `/mnt/node-drive`**.
   - WAL mode requires shared-memory POSIX locks (`-shm`) across processes on the *same kernel/host*. Over NFSv4, WAL will corrupt or lock up.
   - If SQLite must reside on `node-drive`, use rollback journaling (`PRAGMA journal_mode=DELETE` or `TRUNCATE`). Otherwise, keep DBs local and sync flat snapshots.
2. **Directory Traversal**:
   - `/home/xnai` must maintain at least `chmod 750` so UID 1000 (`xnai`) can traverse to `/home/xnai/node-drive`.

---

## 4. Implementation Steps

### Phase 1: Node 1 (ASUS) — NFSv4.2 Server Configuration

Execute on **Node 1 (`xnai-n1-asus`)**:

```bash
# Step 1: Update Tailscale Hostname to Tri-Axial Schema
pkexec tailscale set --hostname=xnai-n1-asus

# Step 2: Install kernel NFS server
sudo apt update && sudo apt install -y nfs-kernel-server

# Step 3: Enforce Pure NFSv4.2 and Bind to Tailscale Interface
# Edit or append to /etc/nfs.conf
sudo tee -a /etc/nfs.conf <<EOF

[nfsd]
vers2=n
vers3=n
vers4=y
vers4.0=y
vers4.1=y
vers4.2=y
host=100.89.40.17
EOF

# Step 4: Ensure shared directory exists and has correct ownership
mkdir -p /home/xnai/node-drive
chown -R 1000:1000 /home/xnai/node-drive
chmod 775 /home/xnai/node-drive

# Step 5: Resolve Node 0's Tailscale IP
# Live peer detected: 100.123.51.67 (omega-hub)
NODE0_IP=$(tailscale status --json | jq -r '.Peer[] | select(.HostName=="omega-hub" or .HostName=="xnai-n0-hp") | .TailscaleIPs[0]')
if [ -z "$NODE0_IP" ]; then
    NODE0_IP="100.123.51.67"
fi
echo "Resolved Node 0 Tailscale IP: $NODE0_IP"

# Step 6: Write isolated export configuration in /etc/exports.d/ (Idempotent)
sudo mkdir -p /etc/exports.d
sudo tee /etc/exports.d/node-drive.exports <<EOF
# Omega Engine Federation: Node 0 -> Node 1 Shared Drive
# Exported with all_squash to map all operations to local user xnai (1000:1000)
/home/xnai/node-drive ${NODE0_IP}(rw,sync,no_subtree_check,all_squash,anonuid=1000,anongid=1000,fsid=0)
EOF

# Step 7: Export table reload & service restart
sudo exportfs -ra
sudo systemctl restart nfs-kernel-server

# Step 8: Verify export status and network binding
sudo exportfs -v
ss -tulpn | grep 2049
```

*Note on `fsid=0`: In NFSv4, `fsid=0` marks `/home/xnai/node-drive` as the root of the pseudo-filesystem. Node 0 will mount `${NODE1_IP}:/`.*

---

### Phase 2: Node 0 (HP Pavilion) — NFS Client & Automount Configuration

Execute on **Node 0 (`omega-hub` / `xnai-n0-hp`, Ubuntu 25.10, user `arcana-novai`)**:

```bash
# Step 0: Pre-flight — capture Node 0's local UID/GID
# NFS identity is numeric and server-side `all_squash` maps all writes to
# UID/GID 1000 on Node 1 regardless of the client's UID. The local UID
# matters only for ownership of Node 0's own mountpoint (Step 2):
id -u && id -g
# If not 1000, substitute the real values into the chown below.

# Step 1: Install NFS client utilities
sudo apt update && sudo apt install -y nfs-common

# Step 2: Create local mount point
sudo mkdir -p /mnt/node-drive
sudo chown -R 1000:1000 /mnt/node-drive

# Step 3: Resolve Node 1's Tailscale IP (100.89.40.17)
NODE1_IP=$(tailscale status --json | jq -r '.Peer[] | select(.HostName=="xnai-n1-asus" or .HostName=="kali-n1") | .TailscaleIPs[0]')
if [ -z "$NODE1_IP" ]; then
    NODE1_IP="100.89.40.17"
fi
echo "Resolved Node 1 Tailscale IP: $NODE1_IP"

# Step 4: Manual test mount
sudo mount -t nfs4 -o rsize=1048576,wsize=1048576,noatime,nosuid,nodev ${NODE1_IP}:/ /mnt/node-drive

# Step 5: Validate read/write and unmount test
touch /mnt/node-drive/.test_probe && rm /mnt/node-drive/.test_probe
sudo umount /mnt/node-drive

# Step 6: Configure persistent systemd automount in /etc/fstab
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

## 5. Verification & Health Checks

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

## 6. Failure Modes & Edge Case Runbook

| Failure | Root Cause | Remediation |
|---------|------------|-------------|
| **Mount hangs on `mount` command** | Port 2049 blocked by Tailscale ACL | Inspect Tailscale Admin Console; verify `tag:node1:2049` is accepted from `tag:node0`. |
| **`access denied by server while mounting`** | IP mismatch or export syntax error | Check `NODE0_IP` in `/etc/exports.d/node-drive.exports`; run `sudo exportfs -ra` on Node 1; inspect `/var/log/syslog`. |
| **`Permission Denied` when writing** | Incorrect UID mapping or local folder permissions | Verify `/home/xnai/node-drive` on Node 1 is `chmod 775` and export uses `all_squash,anonuid=1000,anongid=1000`. |
| **Node 0 boot hang / slow boot** | Network mount attempted before Tailscale active | Verify `/etc/fstab` has `nofail` and `x-systemd.automount`. Automount never blocks boot. |
| **Stale file handle (`ESTALE`)** | Node 1 rebooted or restarted NFS service | `sudo umount -l /mnt/node-drive` (lazy unmount) on Node 0, then re-access the path. |
| **Database corruption / SQLite lock error** | SQLite database opened with WAL mode on NFS share | Switch SQLite db to rollback journal: `PRAGMA journal_mode=DELETE;` |

---

## 7. Rollback Protocol

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

*⬡ OMEGA ⬡ FEDERATION ⬡ FED-NFS-PLAN-001 ⬡ v2.1 ✅ IMPLEMENTED & VERIFIED 2026-09-21 ⬡*
