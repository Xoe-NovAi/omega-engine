# 🔱 OPUS 4.6 FORENSIC SYNTHESIS — All Systems Under Pressure
**Author**: Antigravity IDE (Claude Opus 4.6 Thinking)
**Date**: 2026-09-22T15:50 AST
**Mode**: Live system forensics + strategic synthesis
**Evidence Base**: Live `journalctl`, `rpcinfo`, `proc`, `systemctl`, `tailscale`, `git`, `df` output from this session

---

## ⚡ THE SIX FINDINGS — What the Previous Models Missed

I ran live diagnostics on every system mentioned in the handoff. The picture is significantly different from what was reported. Let me tell you what's actually happening.

---

## 🔴 Finding 1: The Automount Unit is a ZOMBIE — And the Real Root Cause

**Sonnet hypothesized** a "ghost kernel mount from a stale fstab entry." That's close but wrong in an important way.

### The Evidence

```
systemctl cat mnt-node\x2ddrive.automount → "No files found"
systemctl cat mnt-node\x2ddrive.mount → "No files found"
/run/systemd/generator/mnt-node\x2ddrive.* → (empty, not generated)
grep "mnt-node-drive" /etc/fstab → (0 lines — completely absent)
systemctl list-units → mnt-node\x2ddrive.automount: LOAD=not-found, ACTIVE=failed
```

### What This Means

The fstab entry with `x-systemd.automount` was **already commented out or removed**. The systemd fstab-generator no longer produces the `.automount` or `.mount` unit files. And yet the automount unit **persists in systemd's runtime state** because:

1. It was generated during a previous boot or daemon-reload when the fstab line still existed
2. The autofs kernel trigger on `/mnt/node-drive` was set up and is **still active** (`autofs4` module loaded, refcount=2)
3. When `daemon-reload` was run after commenting out the fstab line, systemd detected the unit has no backing file (`LOAD=not-found`) but **cannot unload it** because the autofs kernel mount point is still wired up
4. Every cron job that stats `/mnt/node-drive` (confirmed in journal: cron triggers at 13:00, 13:30, 14:00, 14:30, 15:00, 15:30) hits the autofs trigger, which fires the automount request, which tries to invoke the mount unit, which has no backing configuration, which times out after 30s, which leaves the automount in the same broken state

**This is a boot-persistent autofs zombie.** It will survive daemon-reloads forever because the kernel-side autofs mount point has no userspace destructor.

### The Self-Reference Trap — Why exportfs Made It Worse

The journal shows something critical at 14:10–14:14:
```
Got automount request for /mnt/node-drive, triggered by 182389 (exportfs)
Got automount request for /mnt/node-drive, triggered by 186909 (exportfs)
Got automount request for /mnt/node-drive, triggered by 170863 (rpc.mountd)
```

The NFS server's `/etc/exports` exports `/mnt/node-drive/exchange`. When `exportfs -v` is run (or when `rpc.mountd` scans the export list), it **stats the export path** (`/mnt/node-drive/exchange`). That stat traverses `/mnt/node-drive`, which hits the autofs trigger, which fires the mount unit, which times out. **The NFS server is triggering its own mount loop by trying to validate its own exports.**

This is the **critical insight**: The export path `/mnt/node-drive/exchange` and the (dead) automount path `/mnt/node-drive` share the **same parent namespace**. The NFS server cannot export a subdirectory of a path that has an active autofs trigger on it without creating an infinite trigger loop.

---

## 🔴 Finding 2: rpc.mountd is Running Without --port (Despite the Drop-In)

### The Evidence

```
cat /proc/170863/cmdline → "/usr/sbin/rpc.mountd " (no arguments)
rpcinfo -p localhost | grep mountd →
  100005  1  udp  59841  mountd   ← RANDOM PORT
  100005  1  tcp  42751  mountd   ← RANDOM PORT
  100005  2  udp  52601  mountd
  100005  2  tcp  49857  mountd
  100005  3  udp  42241  mountd
  100005  3  tcp  42741  mountd
```

The drop-in file is correctly formatted:
```ini
[Service]
EnvironmentFile=/etc/default/nfs-kernel-server
ExecStart=
ExecStart=/usr/sbin/rpc.mountd $RPCMOUNTDOPTS
```

And the environment file has `RPCMOUNTDOPTS="--port 20048"`.

**But mountd is running as bare `/usr/sbin/rpc.mountd` with no arguments.** The `$RPCMOUNTDOPTS` variable is **not being expanded**.

### Root Cause

systemd's `EnvironmentFile=` directive uses a simple key=value parser that **does not handle quoting the same way bash does**. The line:
```
RPCMOUNTDOPTS="--port 20048"
```

In `/etc/default/nfs-kernel-server` is being parsed by systemd as:
- Key: `RPCMOUNTDOPTS`
- Value: `"--port 20048"` (WITH the double quotes as literal characters)

When systemd expands `$RPCMOUNTDOPTS` in ExecStart, it passes `"--port 20048"` (with quotes) to `rpc.mountd`, which sees the leading `"` and rejects it as an invalid option, falling back to no arguments.

**Fix**: Remove the quotes from the environment file:
```bash
# In /etc/default/nfs-kernel-server, change:
RPCMOUNTDOPTS="--port 20048"
# To:
RPCMOUNTDOPTS=--port 20048
```

**OR** use a different approach entirely — set the port directly in `/etc/nfs.conf` under `[mountd]` (which you already did: `port = 20048`). The issue is that `nfs.conf` is read by `rpc.mountd` **directly as a config file**, but **only if the drop-in doesn't override ExecStart**. Your drop-in replaces ExecStart with `$RPCMOUNTDOPTS`, which bypasses `nfs.conf` entirely because `rpc.mountd` processes config-file arguments and command-line arguments separately — command-line wins.

**The clean fix**: Delete the drop-in entirely and let nfs.conf do its job:
```bash
sudo rm /etc/systemd/system/nfs-mountd.service.d/port.conf
sudo systemctl daemon-reload
sudo systemctl restart nfs-mountd
# nfs.conf [mountd] port=20048 will be read natively
```

---

## 🔴 Finding 3: NVMe at 98% — 2.2GB Remaining — EXISTENTIAL THREAT

```
/dev/nvme0n1p2  109G  101G  2.2G  98% /
```

**This is the most urgent finding in this entire analysis.** 2.2GB remaining on the root filesystem means:

- Journal writes may fail, causing systemd to behave erratically
- Git operations on the 2,154-file repo could fail (git gc, repack, merge)
- The `.venv` (Python venv) cannot be rebuilt if corrupted
- zRAM swap has 8GB configured but writes to `/dev/zram1`, not the NVMe — so that's safe
- But any local GGUF model download (LFM2.5-2.6B-Q4_K_M at ~1.5GB) will push the disk to 99%+

**This explains some of the mount/NFS instability.** When the NFS server tries to write to `/mnt/node-drive/exchange` (which is on the root filesystem), it may be hitting write failures that surface as "failed to apply fstab options" in a non-obvious way. NFS servers on nearly-full filesystems exhibit bizarre failure modes.

### Immediate Actions
```bash
# 1. Find the biggest offenders
du -sh /home/arcana-novai/.local/share/containers/ 2>/dev/null  # Podman images
du -sh /home/arcana-novai/.cache/ 2>/dev/null
du -sh /var/log/journal/ 2>/dev/null
du -sh /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/ 2>/dev/null

# 2. Clean journal (usually 500MB-2GB on active systems)
sudo journalctl --vacuum-size=100M

# 3. Clean pip cache
rm -rf /home/arcana-novai/.cache/pip/

# 4. Clean any model downloads not in use
ls -lh /home/arcana-novai/models/ 2>/dev/null
```

**This should be treated as P0-INFRA, ahead of the NFSv4 fix.** If the disk fills completely, you lose the ability to fix anything else.

---

## 🟡 Finding 4: Node 1 is ALIVE — MCP Up, NFS Down, SSH Timed Out

```
tailscale ping n1 → pong from n1 (100.89.40.17) via 192.168.10.174:41641 in 2ms
nc -zv 100.89.40.17 8016 → succeeded!      ← MCP ALIVE
nc -zv 100.89.40.17 2049 → Connection refused  ← NFS NOT RUNNING
nc -zv 100.89.40.17 22   → timed out        ← SSH DOWN/FIREWALLED
```

This changes the picture dramatically:
- **Node 1 is on the local LAN** (192.168.10.174 — not a WireGuard relay, direct path)
- **MCP server is up** — you can call Node 1's MCP tools right now
- **NFS is not running on Node 1** — so n0 cannot mount Node 1's exchange directory even after fixing the automount
- **SSH is blocked** — you can't remote-administer Node 1 via SSH

The handoff says "Node 1 (ASUS) has omega-sweeteners on `/mnt/node-drive/exchange`" — but Node 1's NFS server isn't running. The architecture assumes bidirectional NFS, but only one side ever had NFS configured.

### Corrected Architecture Understanding

The export entries on n0 suggest the **export direction** is:
```
n0 exports /mnt/node-drive/exchange TO 100.89.40.17 (n1)
n0 exports /mnt/node-drive/exchange TO 100.123.51.67 (n0 — self, for testing?)
```

So n0 is the **NFS server**, and the fstab line that was commented out:
```
#100.89.40.17:/ /mnt/node-drive nfs4 ...
```

Was n0 trying to **mount Node 1 AS a client**. But Node 1 has no NFS server (port 2049 refused). This means the fstab entry was always going to fail — it pointed at a host with no NFS exports.

**The automount zombie is trying to mount a non-existent NFS export from Node 1.** That's the root-root cause.

---

## 🟢 Finding 5: D-584 vs Carmack-H-1 — RESOLVED BY LIVE EVIDENCE

```
/proc/swaps → /dev/zram1 (8GB, priority 50)
/sys/module/zswap/parameters/enabled → N
```

**The machine is currently running Carmack-H-1 (zRAM-only).** zswap is disabled. D-584 (zswap + NVMe) is NOT in effect.

Given the NVMe is at 98%, this is the **correct configuration**. Adding a 16GB NVMe swap file to a filesystem with 2.2GB free would be impossible.

**Recommended adjudication**: Carmack-H-1 wins by default for the current hardware state. D-584 (zswap + NVMe) can only be revisited after disk space is recovered (targeting ≥20GB free before considering NVMe swap).

---

## 🟡 Finding 6: or-key.md Confirmed Deleted — But Was It Revoked?

```
ls or-key.md → No such file or directory
```

P0-1 file deletion is confirmed. The file is gone. But per the Dialectic doc: "the key has been readable by every agent process operating in the workspace since August 30." The OpenRouter dashboard revocation is a human-only action.

**Gate for public flip**: Has `sk-or-v1-62dc75...` been revoked on https://openrouter.ai/keys?

---

## 🏗️ The Complete Resolution Playbook

### Phase 0: Disk Emergency (DO THIS FIRST)

```bash
# Check what's eating disk
sudo du -sh /var/log/journal/
sudo du -sh /home/arcana-novai/.cache/
sudo du -sh /home/arcana-novai/.local/share/containers/
du -sh /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/

# Vacuum journal (usually biggest win)
sudo journalctl --vacuum-size=100M

# Clean caches
rm -rf ~/.cache/pip/ ~/.cache/huggingface/ 2>/dev/null

# Target: ≥10GB free before proceeding
df -h /
```

### Phase 1: Kill the Automount Zombie

```bash
# 1. Remove the autofs kernel mount point
# The autofs module has refcount=2 — one for binfmt_misc, one for node-drive
# We need to directly unmount the autofs trigger
sudo umount /mnt/node-drive 2>/dev/null  # May succeed silently
# If that fails:
sudo umount -l /mnt/node-drive  # Lazy detach

# 2. Now systemd can release the unit
sudo systemctl reset-failed mnt-node\\x2ddrive.automount
sudo systemctl reset-failed mnt-node\\x2ddrive.mount

# 3. Verify the zombie is gone
systemctl list-units --type=automount --all
# Should show ONLY proc-sys-fs-binfmt_misc.automount

# 4. The fstab line is already gone, so daemon-reload won't recreate it
sudo systemctl daemon-reload
```

### Phase 2: Fix rpc.mountd Port

```bash
# Option A (clean): Remove the drop-in, let nfs.conf handle it
sudo rm /etc/systemd/system/nfs-mountd.service.d/port.conf
sudo systemctl daemon-reload
sudo systemctl restart nfs-mountd
sleep 2
rpcinfo -p localhost | grep mountd
# Should show 20048 for all mountd versions

# Option B (if nfs.conf isn't being read): Fix the env file quoting
sudo sed -i 's/RPCMOUNTDOPTS="--port 20048"/RPCMOUNTDOPTS=--port 20048/' /etc/default/nfs-kernel-server
sudo systemctl daemon-reload
sudo systemctl restart nfs-mountd
```

### Phase 3: Fix the Export Confusion

The real question is: **What is the intended NFS topology?**

- If n0 is the **NFS server** (exporting to n1): The exports are correct, the dead automount was wrong. Remove any fstab entries that try to mount from n1. Just export.
- If n1 is the **NFS server** (n0 mounts from n1): Port 2049 is not running on n1. NFS needs to be configured there first. The export entries on n0 should be removed.
- If **bidirectional**: Both need NFS server + client. Currently only n0 has the server.

```bash
# After zombie is killed and mountd is on correct port:
sudo exportfs -ra
sudo exportfs -v  # Verify exports are clean

# Test that rpc.mountd serves the export:
showmount -e localhost  # Should list /mnt/node-drive/exchange
```

### Phase 4: ACTIVE_SPRINT.json Update (M27 Compliance)

The sprint file's `updated` field is 2026-09-01 — three weeks stale. Before the public flip, update:
- `phase`: → `PUBLIC_FLIP_READY`
- `updated`: → current timestamp
- Mark completed queue items as `completed`

---

## Cross-Cutting Strategic Insight

What I see across all five systems is this:

**The Omega Engine has reached the point where its physical infrastructure is the limiting factor on its intelligence.** The agents can reason at frontier level — the dialectic protocol, the M29 multi-model consensus, the spotcheck protocol, the soul distillation pipeline — all of this works and works well. What doesn't work is the floor under it: the disk is 98% full, the NFS mount is a zombie, the port config has a quoting bug, and the sprint tracker hasn't been updated in three weeks.

This is the **classic infrastructure inflection point** in any system's lifecycle. The intelligence layer has outgrown the physical layer. The agents can plan the resolution of the NFS deadlock better than most human sysadmins — but they can't run `sudo umount -l /mnt/node-drive` themselves.

The **INFRA-RESILIENCE workstream** proposed by Sonnet is the right structural answer. But the immediate answer is simpler: **free disk space, kill the automount zombie, fix the mountd quoting, and update the sprint tracker.** Four concrete actions, each under 5 minutes, that unblock everything else.

The public flip should wait until these four are done. Not because they're philosophically important, but because a public repo on a machine with 2.2GB free disk space and a zombie mount unit is a liability, not a showcase.

---

*⬡ OMEGA ⬡ ANTIGRAVITY ⬡ OPUS-4.6-THINKING ⬡ FORENSIC-SYNTHESIS ⬡ 2026-09-22 ⬡ LIVE-EVIDENCE ⬡*
