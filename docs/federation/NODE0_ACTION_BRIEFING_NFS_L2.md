# 🔱 Node 0 Action Briefing — NFS over Tailscale L2 Federation
**Doc ID**: `FED-BRIEF-NODE0-NFS-001` | **Date**: 2026-09-16 (rev. 2026-09-21)  
**From**: Node 1 (ASUS ExpertBook / `xnai-n1-asus` / `100.89.40.17`)  
**To**: Node 0 (HP Pavilion Archival Bastion / `100.123.51.67`, Ubuntu 25.10, user `arcana-novai`)  
**Status**: ✅ COMPLETE — NFS mounted + automount live (2026-09-21)

> ## ✅ 2026-09-21 COMPLETED STATE (verified end-to-end from Node 1)
> - **NFS server**: fixed + live (`nfs-server.service` active, bound strictly
>   `100.89.40.17:2049`; `/etc/nfs.conf [nfsd] host` restored after errno 99).
> - **NFS client (Node 0)**: `mount.nfs4` present; **manual mount OK**
>   (vers=4.2, all_squash → `1000:1000` verified by probe file ownership);
>   **fstab automount added** (`100.89.40.17:/ /mnt/node-drive nfs4 ...`
>   + `findmnt --verify` 0 errors) and **triggered live** (autofs → nfs4,
>   AUTOMOUNT_OK).
> - **Round-trip proven**: Node 0 wrote
>   `exchange/final_probe_<ts>` → appeared on Node 1 server side
>   (`/home/xnai/node-drive/exchange/`) as `1000:1000`.
> - **MCP bidirectional**: `Omega Core Hub v1.30.0` (93 tools) on Node 0 and
>   `kali-n1-mcp` on Node 1 both answer over the Tailscale IPs.
> - **SSH**: `tailscale ssh arcana-novai@n0` works from Node 1.
> - **Canonical tags** (FED-ACL-001 v1.2): Node 0 = `tag:node0`, Node 1 =
>   `tag:node1` — live on both.
> - **▶ REMAINING (ACL migration only)**: paste **Phase A** (canonical tags)
>   from `docs/federation/ACL_POLICY.md` into the Tailscale Admin Console →
>   re-verify (NFS mount, MCP, SSH, ICMP) → then paste **Phase B**. NFS
>   operational work is finished.

---

## 1. Executive Summary

Node 1 (`xnai-n1-asus`) and Node 0 (`100.123.51.67`) are **actively peered directly over Tailscale WireGuard** (`192.168.10.168:41641` direct transport, zero DERP relay overhead, ~35-100ms local latency).

Node 1 has fully deployed, hardened, and verified the **NFSv4.2 server** (re-verified 2026-09-21 after binding fix). The shared scratch and model-exchange workspace (`/home/xnai/node-drive`) is live, bound strictly to the mesh IP (`100.89.40.17:2049`), and exported exclusively to Node 0 (`100.123.51.67`). Bidirectional MCP over the mesh is confirmed working; the only outstanding Node 0 step is the client mount (requires `sudo`, password-protected on Node 0).

This briefing provides:
1. The **new best practices & architectural standards** established during implementation.
2. The **exact, copy-paste execution sequence** for Node 0 to mount and automate the drive.
3. The **operational rules** (including the critical SQLite WAL hazard).

---

## 2. New Best Practices & Architectural Invariants

### A. Tri-Axial Hostname Schema (`<user>-<node>-<hardware>`)
To eliminate namespace collisions across multi-user environments and the broader Omegaverse:
- **Node 1 is now named**: `xnai-n1-asus` (`xnai-n1-asus.tail51f14a.ts.net`).
- **Node 0 recommendation**: Rename to `xnai-n0-hp` (`sudo tailscale set --hostname=xnai-n0-hp`).
- **Why**: `<user>` prevents collision with other operators/realms; `<node>` indicates topological rank (Node 0 Bastion vs Node 1 Vanguard); `<hardware>` informs orchestrator agents of physical silicon profile (CPU-only Raptor Lake vs GPU Bastion).

### B. Pure NFSv4.2 with Interface Isolation
- Legacy NFSv2 and NFSv3 are completely disabled. Legacy port sprawl (`rpcbind` port 111, `mountd` port 20048, `statd`, `lockd`) is eliminated. Only TCP port 2049 is active.
- `nfsd` is bound **strictly to `100.89.40.17`**. The daemon does not listen on `0.0.0.0` or physical Wi-Fi/LAN interfaces.
- NFSv4.2 enables `copy_file_range` (server-side copy) and sparse file allocation, optimizing multi-gigabyte GGUF model transfers.

### C. Permission Symmetry (`all_squash`)
- The export enforces `all_squash,anonuid=1000,anongid=1000`.
- Every file written by Node 0 (whether by root, systemd, or an automated agent) is mapped locally to UID `1000` / GID `1000` (`xnai:xnai`) on Node 1.
- Prevents root-owned un-deletable file collisions and permission deadlocks.

### D. Boot Resilience (`nofail` + `systemd.automount`)
- Node 0 mounts via `x-systemd.automount` with `nofail` and a 5-minute idle timeout.
- Node 0 will **never stall at boot** or drop into emergency recovery mode if Node 1 is offline, rebooting, or if the network is delayed.
- The tunnel and mount only activate on first directory access (`ls /mnt/node-drive`).

### E. Critical Hazard: SQLite WAL Databases on NFS
- **Never initialize or run SQLite databases in WAL mode (`PRAGMA journal_mode=WAL`) on `/mnt/node-drive`**.
- WAL mode requires POSIX shared-memory (`-shm`) locks across processes on the *same kernel*. Over NFS, WAL mode will cause file lockups and silent corruption.
- Rule: Databases placed on `node-drive` must use rollback journaling (`PRAGMA journal_mode=DELETE` or `TRUNCATE`), or stay on local disk with flat files/JSON exported to the share.

---

## 3. Node 0 Execution Sequence (Exact Commands)

Run the following commands on **Node 0** (`omega-hub`, Ubuntu 25.10):

### Step 0: Pre-flight — capture Node 0's local UID
```bash
id -u && id -g
```
*NFS identity is numeric and server-side `all_squash` maps every write to
UID/GID 1000 (`xnai:xnai`) on Node 1 — Node 0's **username is irrelevant**.
The local UID only matters for ownership of Node 0's own mountpoint, so
`arcana-novai` can read/write there without sudo. Ubuntu's first user is UID
1000; if `id -u` reports otherwise, substitute the real values below.*

### Step 1: (Optional but Recommended) Align Hostname
```bash
sudo tailscale set --hostname=xnai-n0-hp
```

### Step 2: Install NFS Client
```bash
sudo apt update && sudo apt install -y nfs-common
```

### Step 3: Create Mountpoint
```bash
sudo mkdir -p /mnt/node-drive
# chown (NOT recursive) the mountpoint so the local user can use it;
# do this BEFORE mounting — recursive -R on a mounted share is harmful
sudo chown $(id -u):$(id -g) /mnt/node-drive
```

### Step 4: Perform Manual Verification Mount
```bash
# Mount from Node 1's Tailscale IP
sudo mount -t nfs4 -o rsize=1048576,wsize=1048576,noatime,nosuid,nodev 100.89.40.17:/ /mnt/node-drive

# Test read/write
echo "Node 0 verification probe: $(date -u)" > /mnt/node-drive/node0_probe.txt
cat /mnt/node-drive/node0_probe.txt

# Remove probe and unmount test
rm /mnt/node-drive/node0_probe.txt
sudo umount /mnt/node-drive
```

### Step 5: Configure Persistent, Boot-Safe Automount
First inspect `/etc/fstab` to see what's there (it may already contain an NFS
entry from a prior attempt — the guard below is idempotent, but knowing the
current state is required):

```bash
cat /etc/fstab
# If an OLD /mnt/node-drive line exists (e.g. an earlier test), either remove
# it or ensure the NEW line below is identical — duplicates are the bug.
```

Then append the single NFS entry (command is idempotent — re-running will not
duplicate):

```bash
if ! grep -q "/mnt/node-drive" /etc/fstab; then
    echo "100.89.40.17:/ /mnt/node-drive nfs4 rsize=1048576,wsize=1048576,noatime,nosuid,nodev,nofail,_netdev,x-systemd.automount,x-systemd.idle-timeout=300,x-systemd.mount-timeout=30s 0 0" | sudo tee -a /etc/fstab
fi

# Validate fstab syntax BEFORE relying on it (temple-grade check):
sudo findmnt --verify --fstab || echo "FSTAB WARNING — inspect above output"

# Reload systemd and start automounter
sudo systemctl daemon-reload
sudo systemctl restart remote-fs.target
```

### Step 6: Verify Live Automount
```bash
# Trigger automount by listing the directory
ls -la /mnt/node-drive

# Inspect mount details
findmnt /mnt/node-drive
```
*Expected: `FSTYPE=nfs4`, options include `rsize=1048576,wsize=1048576,noatime`.*

---

## 4. Tailscale Admin Console Note (ACLs)

Both nodes are currently untagged user devices — the default Tailscale policy
(implicit `autogroup:member`) allows them to communicate, which is why NFS
works today. **Do NOT paste a tag-only policy now**: saving a custom policy
REPLACES the default, and a tag-only policy with no `autogroup:member` rule
will **silently kill all traffic between the untagged nodes** (NFS, MCP, ICMP).

When tag-based enforcement is wanted, follow the **two-phase migration** in
`docs/federation/ACL_POLICY.md`: Phase A keeps `autogroup:member` while
staging tag rules, both nodes re-join tagged, and only then does Phase B
remove the member rule. The NFS rule itself is always:

```hujson
{"action": "accept", "src": ["tag:node0"], "dst": ["tag:node1:2049"]}
```

---

## 5. Verification Checklist for Node 0

- [ ] `tailscale ping xnai-n1-asus` returns direct pong (< 1ms).
- [ ] `/mnt/node-drive` mounts cleanly via automount.
- [ ] Files written from Node 0 appear in Node 1's `/home/xnai/node-drive` owned by `xnai:xnai`.
- [ ] Node 0 reboots cleanly without hanging on network mounts.

*⬡ OMEGA ⬡ FEDERATION ⬡ DUAL-NODE MESH COMPLETE ⬡*
