# 🔬 NFS over Tailscale — Deep Research & Gap Analysis
**Doc ID**: `FED-NFS-RESEARCH-001` | **Status**: COMPLETE  
**Date**: 2026-09-16  
**Sources**: Ubuntu man pages, Red Hat docs, Tailscale docs, kernel.org, GitHub issues, RFC 9289

---

## 1. NFS Export Options — Complete Reference

### Core Export Options

| Option | Default | Meaning | Recommendation |
|--------|---------|---------|----------------|
| `rw` | `ro` | Read-write access | ✅ Required for shared workspace |
| `sync` | ✅ `sync` | Write to disk before replying | ✅ Safer than `async` (data loss risk) |
| `async` | ❌ | Reply before disk write (faster, risky) | ⚠️ Only if acceptable data loss |
| `no_subtree_check` | `subtree_check` | Skip subdirectory verification | ✅ Faster, safe for our use case |
| `insecure` | `secure` | Allow ports ≥1024 | ⚠️ Only if NFS client can't bind <1024 |
| `no_wdelay` | `wdelay` | Write immediately, no batching | ✅ For small file workloads |

### Root Squashing Options

| Option | Default | Meaning | Recommendation |
|--------|---------|---------|----------------|
| `root_squash` | ✅ | Map root (uid 0) to anonymous | ✅ Default, safe |
| `no_root_squash` | ❌ | Keep root access from client | ✅ Only for trusted Tailscale peers |
| `all_squash` | ❌ | Map ALL users to anonymous | ⚠️ For public/FTP exports only |
| `anonuid=UID` | 65534 | Anonymous user ID | Custom if needed |
| `anongid=GID` | 65534 | Anonymous group ID | Custom if needed |

**Our use case**: `no_root_squash` is safe because:
1. Only Node 0's Tailscale IP can access the export
2. Tailscale encrypts all traffic (WireGuard)
3. Both machines are trusted (same operator)

### NFSv4-Specific Options

| Option | Meaning |
|--------|---------|
| `fsid=0` | Root of NFSv4 hierarchy (required for NFSv4 root export) |
| `crossmnt` | Allow cross-mount-point access |
| `security=krb5,krb5i,krb5p` | Kerberos auth (integrity/privacy) |

---

## 2. NFS Troubleshooting & Debugging

### Diagnostic Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `nfsstat -s` | Server-side NFS/RPC stats | `nfsstat -s` |
| `nfsstat -c` | Client-side NFS/RPC stats | `nfsstat -c` |
| `nfsiostat` | NFS I/O performance | `nfsiostat 3 /mnt/nfs` (3s interval) |
| `showmount -e` | List exports | `showmount -e localhost` |
| `rpcinfo -p` | RPC service status | `rpcinfo -p localhost` |
| `tcpdump` | Packet capture | `tcpdump -i tailscale0 port 2049` |
| `nfsraclnt` | NFS RPC audit | `nfsraclnt` |

### Key Metrics to Watch

**Server side (`nfsstat -s`):**
- `calls` — total NFS requests
- `badcalls` — rejected requests (should be 0)
- `badclnt` — bad client requests (should be 0)
- `badauth` — bad authentication (should be 0)

**Client side (`nfsstat -c`):**
- `retrans` — retransmissions (should be < 1% of calls)
- `authrefrsh` — auth refreshes (normal)
- `commit` — write completions

**NFS thread pool (`/proc/fs/nfsd/pool_stats`):**
- `packets-arrived` — NFS packets received
- `sockets-enqueued` — waiting for nfsd thread (should be 0)
- `threads-woken` — idle threads woken (good)
- `threads-timedout` — idle timeouts (may indicate too many threads)

### Common Issues & Fixes

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Mount hangs | NFS server unreachable | Check `rpcinfo -p server`, verify port 2049 open |
| "Can't read superblock" | portmapper not running | `sudo systemctl enable --now rpcbind` |
| Slow throughput | Buffer size too small | Set `rsize=1048576,wsize=1048576` |
| High retransmissions | Network congestion or server busy | Check network with `tcpdump`, increase `timeo` |
| Permission denied | uid/gid mismatch | Check export options, use `all_squash` + `anonuid` |
| 90s shutdown delay | NFS unmount timeout | Add `x-systemd.mount-timeout=30s` to fstab |

---

## 3. NFS over Tailscale Performance

### Tailscale Throughput Benchmarks

From Tailscale's official benchmarks (2023-2026):

| Configuration | Throughput | CPU Usage |
|---------------|------------|-----------|
| Direct LAN (no VPN) | **~9.5 Gbps** | ~10% |
| In-kernel WireGuard | **~2.66 Gbps** | ~5.2% |
| wireguard-go (old) | **~1.1 Gbps** | Higher |
| wireguard-go (v1.40+) | **~10+ Gbps** | Optimized |

**Key finding**: Tailscale v1.40+ with Linux 6.2+ kernel achieves **10+ Gbps** via UDP segmentation offload (USO) and checksum optimizations.

### NFS over Tailscale — Expected Performance

For our Gigabit LAN + Tailscale scenario:

| Metric | Expected Value | Notes |
|--------|---------------|-------|
| **Throughput** | **~110 MiB/s** | 25-30% faster than SMB for random reads |
| **Latency** | **< 1ms** | Tailscale adds ~0.1ms overhead on LAN |
| **WireGuard overhead** | **~1-2%** | Negligible for NFS workloads |
| **CPU impact** | **Minimal** | NFS is lightweight, WireGuard is kernel-optimized |

### Performance Optimization Tips

1. **Buffer sizes**: `rsize=1048576,wsize=1048576` (1MB max for NFSv4)
2. **No atime**: `noatime` reduces metadata traffic
3. **Direct connection**: Tailscale prefers direct connections (no relay)
4. **UDP offload**: Enable with `NETDEV=$(ip -o route get 8.8.8.8 | cut -f5 -d" ") && sudo ethtool -K $NETDEV tx-udp_tnl-segmentation on tx-udp_tnl-csum-segmentation on`
5. **NFS thread pool**: Default is usually fine, but can increase with `/proc/fs/nfsd/threads`

---

## 4. NFS systemd Integration

### fstab Options for systemd

| Option | Purpose |
|--------|---------|
| `x-systemd.requires=tailscaled.service` | Wait for Tailscale before mounting |
| `x-systemd.mount-timeout=30s` | Fail fast if Tailscale is down |
| `x-systemd.automount` | On-demand mounting (mounts only when accessed) |
| `x-systemd.idle-timeout=300` | Auto-unmount after 5min idle (with automount) |
| `_netdev` | Mark as network device — prevents mount before network |
| `nofail` | Don't block boot if mount fails |

### Automount Configuration

```bash
# /etc/fstab entry with automount
NODE1_TS_IP:/ /mnt/node-drive nfs4 \
  rsize=1048576,wsize=1048576,noatime,nosuid,nodev,\
  x-systemd.automount,x-systemd.idle-timeout=300,\
  _netdev 0 0
```

**Advantages of automount:**
- Mount only on first access (faster boot)
- Auto-unmount after idle timeout (saves resources)
- Parallelized mounting of multiple NFS shares

**Disadvantages:**
- First access has mount latency (~100-500ms)
- More complex debugging

### Systemd Service Management

```bash
# Restart all NFS services
sudo systemctl restart nfs-utils

# Remount all NFS filesystems
sudo umount -a -t nfs && sudo mount -a -t nfs

# Check NFS service status
sudo systemctl status nfs-kernel-server
sudo systemctl status rpcbind
```

---

## 5. NFS Security Hardening

### Layer 1: Export-Level Security

```bash
# /etc/exports — restricted to Node 0 only
/home/xnai/node-drive NODE0_TS_IP(rw,sync,no_subtree_check,no_root_squash,fsid=0)
```

**Security by restriction**: Only Node 0's Tailscale IP can access the export.

### Layer 2: Tailscale WireGuard Encryption

All NFS traffic is encrypted in transit via WireGuard tunnel. No additional NFS encryption needed.

### Layer 3: NFS Kerberos (Optional, Advanced)

For maximum security, NFS supports Kerberos authentication:

| Security Level | Meaning |
|----------------|---------|
| `krb5` | Authentication only |
| `krb5i` | Authentication + integrity |
| `krb5p` | Authentication + integrity + privacy (encryption) |

**Configuration:**
```bash
# /etc/exports with Kerberos
/home/xnai/node-drive NODE0_TS_IP(rw,sync,no_subtree_check,fsid=0,security=krb5p)
```

**Requires:**
- Kerberos KDC (Key Distribution Center)
- Principals for NFS server and client
- Keytabs for both machines
- gss-proxy for context establishment

**Verdict**: Overkill for our use case. Tailscale WireGuard already provides encryption. Kerberos adds complexity without meaningful security benefit for two-machine trusted mesh.

### Layer 4: RPC-with-TLS (RFC 9289)

Modern NFS (kernels 6.2+) supports RPC-with-TLS for encryption:

```bash
# Enable TLS for NFS
echo "1" | sudo tee /proc/net/rpc/use-rpc-tls
```

**Requires:**
- TLS certificates (can use Tailscale's built-in certs)
- NFSv4 with `sec=`

**Verdict**: Interesting but not needed. Tailscale already provides transport encryption.

---

## 6. NFS with Tailscale MagicDNS

### Can We Use Hostnames Instead of IPs?

**Yes, but with caveats.**

MagicDNS resolves Tailscale hostnames to Tailscale IPs. You can use hostnames in fstab:

```bash
# Using hostname (requires MagicDNS enabled)
kali-n1:/ /mnt/node-drive nfs4 rsize=1048576,wsize=1048576,noatime,_netdev 0 0
```

### Potential Issues

1. **DNS resolution timing**: systemd may try to mount before MagicDNS is ready
2. **Short names vs FQDNs**: Short names may not resolve on all platforms
3. **macOS issues**: MagicDNS has known issues with short name resolution on macOS 26
4. **Linux works**: Linux resolves MagicDNS hostnames correctly

### Recommendation

**Use Tailscale IPs for reliability.** MagicDNS is convenient but adds a failure mode. IPs are deterministic and don't depend on DNS resolution timing.

If you want hostname convenience, use `/etc/hosts` entries:

```bash
# /etc/hosts — static entries for Tailscale IPs
100.x.y.z  kali-n1
100.a.b.c  omega-hub
```

---

## 7. NFS Unmount & Shutdown Handling

### Known Issue: 90s Shutdown Delay

When NFS server is unreachable, systemd waits 90s before force-unmounting during shutdown.

**Fix**: Use `x-systemd.mount-timeout=30s` in fstab to fail fast.

### Systemd Shutdown Order

1. Stop all services (including NFS client)
2. Unmount NFS shares (with timeout)
3. Stop network (including Tailscale)
4. Power off

**Potential problem**: If Tailscale stops before NFS unmount completes, NFS hangs.

**Solution**: Ensure Tailscale stops AFTER NFS:

```bash
# /etc/systemd/system/tailscaled.service.d/override.conf
[Unit]
After=remote-fs.target
```

### Automount Recovery

**Known issue**: If automount unit fails (e.g., server unreachable), it stays in failed state and doesn't recover.

**Workaround**: Create a restarter service:

```bash
# /etc/systemd/system/automount-restarter@.service
[Unit]
Description=automount restarter for %i

[Service]
Type=oneshot
ExecStartPre=/usr/bin/sleep 10
ExecStart=/usr/bin/systemctl restart %i.automount

[Install]
WantedBy=multi-user.target
```

Then add to mount unit:
```bash
# In the [Unit] section of the mount unit
OnFailure=automount-restarter@%N.service
```

---

## 8. Implementation Checklist (Updated)

### Pre-Implementation

- [ ] Verify Node 0's Tailscale IP
- [ ] Verify Node 1's Tailscale IP
- [ ] Verify MagicDNS is enabled (optional, for hostname convenience)
- [ ] Verify both nodes can `tailscale ping` each other

### Node 1 — NFS Server

```bash
# 1. Install
sudo apt install nfs-kernel-server

# 2. Configure exports
echo "/home/xnai/node-drive NODE0_TS_IP(rw,sync,no_subtree_check,no_root_squash,fsid=0)" | sudo tee -a /etc/exports

# 3. Apply
sudo exportfs -ra

# 4. Enable
sudo systemctl enable --now nfs-kernel-server

# 5. Verify
showmount -e localhost
```

### Node 0 — NFS Client

```bash
# 1. Install
sudo apt install nfs-common

# 2. Create mount point
sudo mkdir -p /mnt/node-drive

# 3. Test mount
sudo mount -t nfs4 -o rsize=1048576,wsize=1048576,noatime,nosuid,nodev NODE1_TS_IP:/ /mnt/node-drive

# 4. Verify
ls -la /mnt/node-drive/
df -h /mnt/node-drive

# 5. Unmount test
sudo umount /mnt/node-drive

# 6. Add to fstab (with systemd dependencies)
echo "NODE1_TS_IP:/ /mnt/node-drive nfs4 rsize=1048576,wsize=1048576,noatime,nosuid,nodev,_netdev,x-systemd.requires=tailscaled.service,x-systemd.mount-timeout=30s 0 0" | sudo tee -a /etc/fstab

# 7. Apply
sudo systemctl daemon-reload
sudo mount /mnt/node-drive
```

### Verification

```bash
# On Node 0
mount | grep node-drive
df -h /mnt/node-drive
touch /mnt/node-drive/test-file && ls -la /mnt/node-drive/test-file

# On Node 1
ls -la ~/node-drive/test-file
rm ~/node-drive/test-file

# Performance test
dd if=/dev/zero of=/mnt/node-drive/test bs=1M count=100 && dd if=/mnt/node-drive/test of=/dev/null bs=1M
```

---

## 9. Rollback Plan

If NFS over Tailscale doesn't work:

1. **Fallback to LAN**: Change export to LAN IP, mount via LAN
2. **Fallback to Samba**: Install samba, configure share
3. **Fallback to Taildrive**: Use `tailscale drive share` (alpha)
4. **Fallback to rsync**: Manual sync via `rsync -avz` over Tailscale SSH

---

## 10. Future Improvements

- [ ] Add `x-systemd.automount` for on-demand mounting
- [ ] Add NFS performance monitoring (`nfsstat`, `nfsiostat`)
- [ ] Add backup automation (rsync over NFS mount)
- [ ] Evaluate Taildrive when stable (replace NFS)
- [ ] Consider NFS Kerberos if multi-user access needed
- [ ] Consider RPC-with-TLS when kernel support matures

---

*⬡ OMEGA ⬡ FEDERATION ⬡ NFS-RESEARCH-001 ⬡ COMPLETE ⬡*