# 📁 NFS over Tailscale — Implementation Plan
**Doc ID**: `FED-NFS-PLAN-001` | **Status**: READY FOR IMPLEMENTATION  
**Scope**: Share `~/node-drive` from Node 1 to Node 0 via NFS over Tailscale mesh (encrypted, zero-config networking)  
**Research Source**: Deep web research on NFS vs Samba vs Taildrive, NFS performance tuning, systemd integration

---

## 1. Decision Rationale

| Factor | NFS over Tailscale | Samba | Taildrive |
|--------|-------------------|-------|-----------|
| **Linux→Linux speed** | **~110 MiB/s** (25-30% faster than SMB) | ~80 MiB/s baseline | WebDAV — slower for large files |
| **Setup complexity** | Simple (server + client) | More config | Simplest (`tailscale drive share`) |
| **Security** | Encrypted via WireGuard | Encrypted via WireGuard | Encrypted via WireGuard |
| **Stability** | **Proven, production-ready** | Proven | **Alpha** (known issues) |
| **Large file handling** | **Excellent** (sequential streaming) | Good | Limited (50MB default on Windows) |
| **Systemd integration** | **Excellent** (automount, dependencies) | Good | Manual mount |

**Verdict**: NFS over Tailscale until Taildrive matures.

---

## 2. Architecture

```
Node 1 (ASUS)                              Node 0 (HP)
┌─────────────────────┐                    ┌─────────────────────┐
│  ~/node-drive/      │   Tailscale mesh   │  /mnt/node-drive/   │
│  (NFS server)       │◄══════════════════►│  (NFS client mount) │
│  nfs-kernel-server  │   WireGuard加密     │  nfs-common         │
└─────────────────────┘                    └─────────────────────┘
```

**Network path**: Node 1 Tailscale IP ←→ WireGuard tunnel ←→ Node 0 Tailscale IP  
**Encryption**: All traffic encrypted in transit (WireGuard)  
**Access control**: NFS export restricted to Node 0's Tailscale IP only

---

## 3. Pre-Requirements

- [ ] Node 1: Tailscale logged in and active
- [ ] Node 0: Tailscale logged in and active  
- [ ] Both nodes on same tailnet
- [ ] Node 0's Tailscale IP known
- [ ] Node 1's Tailscale IP known

---

## 4. Implementation Steps

### Phase 1: Node 1 — NFS Server Setup

```bash
# 1. Install NFS server
sudo apt install nfs-kernel-server

# 2. Create shared directory (if not exists)
mkdir -p ~/node-drive

# 3. Get Node 0's Tailscale IP
NODE0_IP=$(tailscale status | grep "node0-hostname" | awk '{print $3}')
echo "Node 0 Tailscale IP: $NODE0_IP"

# 4. Export to Node 0 only (security by restriction)
echo "/home/xnai/node-drive ${NODE0_IP}(rw,sync,no_subtree_check,no_root_squash,fsid=0)" | sudo tee -a /etc/exports

# 5. Apply exports
sudo exportfs -ra

# 6. Enable and start NFS server
sudo systemctl enable --now nfs-kernel-server

# 7. Verify exports
showmount -e localhost
```

**Export options explained:**
| Option | Purpose |
|--------|---------|
| `rw` | Read-write access for shared workspace |
| `sync` | Write to disk before replying (safer than async) |
| `no_subtree_check` | Skip subdirectory verification (faster) |
| `no_root_squash` | Allow root access from trusted Tailscale peer |
| `fsid=0` | Root of NFSv4 hierarchy (required for NFSv4) |

### Phase 2: Node 0 — NFS Client Mount

```bash
# 1. Install NFS client
sudo apt install nfs-common

# 2. Get Node 1's Tailscale IP
NODE1_IP=$(tailscale status | grep "kali-n1" | awk '{print $3}')
echo "Node 1 Tailscale IP: $NODE1_IP"

# 3. Create mount point
sudo mkdir -p /mnt/node-drive

# 4. Test mount (manual)
sudo mount -t nfs4 -o rsize=1048576,wsize=1048576,noatime,nosuid,nodev ${NODE1_IP}:/ /mnt/node-drive

# 5. Verify
ls -la /mnt/node-drive/
df -h /mnt/node-drive

# 6. Unmount test
sudo umount /mnt/node-drive
```

### Phase 3: Persistent Mount via fstab

```bash
# 1. Add to /etc/fstab with systemd dependencies
echo "${NODE1_IP}:/ /mnt/node-drive nfs4 rsize=1048576,wsize=1048576,noatime,nosuid,nodev,_netdev,x-systemd.requires=tailscaled.service,x-systemd.mount-timeout=30s 0 0" | sudo tee -a /etc/fstab

# 2. Apply
sudo systemctl daemon-reload
sudo mount /mnt/node-drive

# 3. Verify persistent mount
mount | grep node-drive
```

**fstab options explained:**
| Option | Purpose |
|--------|---------|
| `nfs4` | NFSv4 protocol (modern, stateful) |
| `rsize=1048576` | Max read buffer (1MB) — fastest throughput |
| `wsize=1048576` | Max write buffer (1MB) — fastest throughput |
| `noatime` | Don't update access times — reduces metadata |
| `nosuid` | Ignore SUID bits — security hardening |
| `nodev` | Ignore device files — security hardening |
| `_netdev` | Mark as network device — prevents mount before network |
| `x-systemd.requires=tailscaled.service` | Wait for Tailscale before mounting |
| `x-systemd.mount-timeout=30s` | Fail fast if Tailscale is down |

---

## 5. Verification Checklist

- [ ] Node 1: `showmount -e localhost` shows export
- [ ] Node 0: `mount | grep node-drive` shows mount
- [ ] Node 0: `ls /mnt/node-drive/` shows files
- [ ] Node 0: `df -h /mnt/node-drive` shows correct size
- [ ] Node 0: `touch /mnt/node-drive/test-file` succeeds
- [ ] Node 1: `ls ~/node-drive/` shows test file
- [ ] Node 1: `rm ~/node-drive/test-file` succeeds
- [ ] Node 0: `umount /mnt/node-drive` succeeds
- [ ] Node 0: `sudo mount /mnt/node-drive` remounts

---

## 6. Known Issues & Fixes

### NFS Mount Cascade Pathology
**Problem**: NFS mount may hang if Tailscale isn't fully ready when systemd tries to mount.  
**Fix**: Use `x-systemd.requires=tailscaled.service` + `x-systemd.mount-timeout=30s`.  
**Alternative**: Use `x-systemd.automount` for on-demand mounting (mounts only when accessed).

### Performance Optimization
**Server side**: `sync` is safer than `async` (async risks data loss on crash).  
**Client side**: `rsize=1048576` and `wsize=1048576` for max throughput.  
**Network**: Tailscale WireGuard tunnel adds minimal overhead (~1-2% on GigE).

### Security Considerations
- `no_root_squash` is safe here because:
  1. Only Node 0's Tailscale IP can access the export
  2. Tailscale encrypts all traffic (WireGuard)
  3. Both machines are trusted (same operator)

---

## 7. Rollback Plan

If NFS over Tailscale doesn't work:

1. **Fallback to LAN**: Change export to LAN IP, mount via LAN
2. **Fallback to Samba**: Install samba, configure share
3. **Fallback to Taildrive**: Use `tailscale drive share` (alpha)
4. **Fallback to rsync**: Manual sync via `rsync -avz` over Tailscale SSH

---

## 8. Future Improvements

- [ ] Add `x-systemd.automount` for on-demand mounting
- [ ] Add NFS performance monitoring (`nfsstat`, `iostat`)
- [ ] Add backup automation (rsync over NFS mount)
- [ ] Evaluate Taildrive when stable (replace NFS)

---

*⬡ OMEGA ⬡ FEDERATION ⬡ NFS-PLAN-001 ⬡ READY-FOR-IMPLEMENTATION ⬡*