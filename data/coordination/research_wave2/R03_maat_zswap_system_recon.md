---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: system_reconnaissance
task_id: R03-maat-zswap-recon
session_purpose: "Physical system reconnaissance for ZSWAP subsystem build (D-526/D-527)"
date: 2026-08-26
author: maat (Zswap Specialist)
status: COMPLETE
---

# R03 — Zswap System Reconnaissance

**Gap**: R3 — Physical system recon for ZSWAP subsystem build
**Ratified**: D-526 (zswap > zRAM), D-527 (zswap configuration spec)
**Session**: Persistent — wave 2 pages for swap/subsystem expertise

---

## §1 — Current System State

### 1.1 Hardware & OS

| Property | Value |
|---|---|
| Kernel | 6.17.0-41-generic (PREEMPT_DYNAMIC) |
| OS | Ubuntu 25.10 (Questing Quokka) |
| Systemd | 257 (257.9-0ubuntu2.5) |
| Architecture | x86_64 |
| Total RAM | 15,148 MB (~14.8 GB) |
| NVMe | 238.5 GB total (Samsung/unknown — SMART requires sudo) |

### 1.2 NVMe Partition Layout

| Partition | Size | FS | Mount | Used | Free | Use% |
|---|---|---|---|---|---|---|
| nvme0n1p1 | 260 MB | vfat | /boot/efi | — | — | — |
| nvme0n1p2 | 110.5 GB | ext4 | / (root) | 97 GB | 6 GB | 95% |
| nvme0n1p3 | 112.1 GB | ext4 | /media/arcana-novai/omega_library | 95 GB | 11 GB | 91% |
| nvme0n1p4 | 15.6 GB | ext4 | /media/arcana-novai/omega_vault | 9 GB | 7 GB | 57% |

### 1.3 Current Swap State

| Device | Type | Size | Used | Priority | Compression | Status |
|---|---|---|---|---|---|---|
| /dev/zram1 | zram | 8 GB | 169 MB | 50 | zstd (level=15) | **ACTIVE** |
| /dev/zram0 | zram | 4 GB | 0 | 100 | zstd (level=3) | Configured, not active |
| /swapfile | file | — | — | — | — | **DOES NOT EXIST** |

**Total swap**: 8 GB (all zram). **Zram usage**: 169 MB (2.1%).

### 1.4 Zswap Parameters (Current)

| Parameter | Current Value | Notes |
|---|---|---|
| enabled | **N** | DISABLED — must enable |
| compressor | lzo | Target is lzo_rle |
| zpool | zsmalloc | Matches target |
| max_pool_percent | 20 | Target is 25 |
| accept_threshold_percent | 90 | Default |
| shrinker_enabled | Y | Default |

### 1.5 ZRAM Module State

| Property | Value |
|---|---|
| Module loaded | Yes (`zram` 57344 bytes, 1 ref) |
| Active compressors | 842_compress, 842_decompress, lz4_compress, lz4hc_compress |
| systemd-zram-generator | Not active as systemd service |
| Config file | `/etc/systemd/zram-generator.conf` exists |
| SWAP devices | dev-zram0.swap (generated), dev-zram1.swap (generated) |

### 1.6 Cgroup & Memory Limits

| Property | Value |
|---|---|
| Cgroup version | v2 (cgroup2fs) |
| Mount | `/sys/fs/cgroup` (rw, nsdelegate, memory_recursiveprot) |
| omega-engine service | **DOES NOT EXIST** |
| omega-hub service | **DOES NOT EXIST** |
| omega-restic-backup.service | loaded, **failed** |
| Memory limits set | None (all services use system default) |

### 1.7 Kernel Memory Parameters

| Parameter | Current | Target (D-527) | Delta |
|---|---|---|---|
| vm.swappiness | **180** | 100 | Reduce by 80 |

> **Note**: swappiness=180 is unusually high (standard default is 60). This suggests prior tuning. D-527 target of 100 is still aggressive but less swap-happy than current.

### 1.8 Systemd Swap Units

| Unit | Status |
|---|---|
| systemd-zram-setup@zram1.service | loaded, active, exited |
| dev-zram1.swap | loaded, active, active |
| swap.target | loaded, active, active |
| systemd-swapfile.service | **masked**, enabled |
| dev-zram0.swap | generated (not active) |

### 1.9 Container Workload (Memory)

| Container | Memory Used | Limit |
|---|---|---|
| omega-infra-infra | 53 KB | 15.51 GB |
| omega-redis | 3.1 MB | 15.51 GB |
| omega-qdrant | 74.4 MB | 15.51 GB |
| omega-iris | 89.9 MB | 15.51 GB |
| **Total containers** | **~167 MB** | — |

> All containers run without memory limits (uncapped, using host RAM directly).

### 1.10 Memory Pressure

| Metric | Value |
|---|---|
| PSI memory some avg10/60/300 | 0.00 / 0.00 / 0.00 |
| PSI memory full avg10/60/300 | 0.00 / 0.00 / 0.00 |
| Zswap pool size | 0 kB (disabled) |
| Zswap pages stored | 0 kB |
| Shmem | 418 MB |

> System is NOT under memory pressure. PSI shows zero stall. Swap usage is minimal (169 MB of 8 GB).

---

## §2 — Delta Table (Current → Target per D-526/D-527)

### 2.1 Swap Subsystem Changes

| Component | Current State | Target State | Delta Action |
|---|---|---|---|
| **Swap backing store** | zram1 (8GB, zstd) | 16GB NVMe swap file | CREATE swap file on NVMe; DISABLE zram1 |
| **zswap** | enabled=N | enabled=Y | `echo 1 > /sys/module/zswap/parameters/enabled` |
| **zswap compressor** | lzo | lzo_rle | `echo lzo_rle > /sys/module/zswap/parameters/compressor` |
| **zswap zpool** | zsmalloc | zsmalloc | **No change** (already correct) |
| **zswap max_pool_percent** | 20 | 25 | `echo 25 > /sys/module/zswap/parameters/max_pool_percent` |
| **vm.swappiness** | 180 | 100 | Reduce sysctl value |
| **zram devices** | zram1 active (8GB) | All zram DISABLED | Disable zram-generator, remove swap |
| **systemd-swapfile.service** | masked | masked | **No change** (already masked) |

### 2.2 Cgroup Memory Limits

| Service | Current Limit | Target Limit | Delta Action |
|---|---|---|---|
| omega-engine | None (uncapped) | MemoryMax=6G | Create systemd unit with `MemoryMax=6G` |
| omega-hub | None (uncapped) | MemoryMax=6G | Create systemd unit with `MemoryMax=6G` |
| omega-infra containers | None (uncapped) | MemoryMax=6G | Add memory limits to Podman quadlets |

### 2.3 Disk Space Impact

| Partition | Current Free | After 16GB Swap File | New Free |
|---|---|---|---|
| / (root) | 6 GB | — | 6 GB (swap file goes elsewhere) |
| omega_library | 11 GB | -5 GB (if swap here) | ~6 GB |
| omega_vault | 7 GB | — | 7 GB |

### 2.4 CRITICAL BLOCKER: NVMe Space

**Finding**: No single partition has 16GB free.

| Partition | Free Space | Fits 16GB? |
|---|---|---|
| / (nvme0n1p2) | 6 GB | **NO** |
| omega_library (nvme0n1p3) | 11 GB | **NO** |
| omega_vault (nvme0n1p4) | 7 GB | **NO** |

**Options to resolve** (ordered by risk):

1. **Free space on omega_library** (~5GB needed): Move/archive data from omega_library to create room. Lowest risk.
2. **Shrink omega_vault** (~9GB): Reduce nvme0n1p4 from 15.6GB to ~7GB, expand omega_library by ~9GB to reach 20GB free. Moderate risk (requires unmount + partition resize).
3. **Shrink root** (~10GB): Reduce nvme0n1p2 from 110GB to ~100GB, expand omega_library by ~10GB. Moderate risk.
4. **Create swap on omega_library at 10GB** (reduced from 16GB): Pragmatic compromise. Still provides significant swap with zswap compression. Lowest implementation risk.
5. **Re-partition entire NVMe**: High risk on live system, requires full backup.

**Recommendation for implementer**: Option 1 (free space on omega_library) or Option 4 (reduced swap size) are safest. Option 2-3 require `gparted` or `parted` on unmounted partitions.

### 2.5 ZRAM → Zswap Transition Risk

Current zram usage: 169 MB of 8 GB (2.1% used). This is trivial — no data loss risk from disabling zram. However:

- Must disable zram BEFORE enabling zswap to avoid double-compression overhead
- Must ensure no process is pinned to zram swap (check with `fuser /dev/zram1`)
- zram-generator config must be neutralized (not just masked)

---

## §3 — Prerequisites (Before Implementation)

### 3.1 Must Exist Before Systemd Unit

| Prerequisite | Why | Command to Verify |
|---|---|---|
| **16GB swap file created** | zswap needs backing store | `swapon --show` shows NVMe swap file |
| **zswap module loaded** | Kernel module must be present | `lsmod | grep zswap` |
| **lzo_rle compressor available** | Target compressor | `cat /sys/module/zswap/parameters/compressor` returns lzo_rle |
| **zsmalloc allocator loaded** | Target pool type | `cat /sys/module/zswap/parameters/zpool` returns zsmalloc |
| **omega-engine service file** | Unit to apply MemoryMax to | `systemctl cat omega-engine` succeeds |
| **omega-hub service file** | Unit to apply MemoryMax to | `systemctl cat omega-hub` succeeds |
| **NVMe free space ≥16GB** | Swap file must fit | `df -h` on target partition |

### 3.2 Must Be True Before `systemctl start`

| Condition | Current | Required Action |
|---|---|---|
| zram1 swap disabled | Active | `swapoff /dev/zram1` |
| zram module unloaded or generator disabled | Module loaded, generator configured | `rmmod zram` or disable generator |
| swap file activated | No swap file | `mkswap /path/to/swapfile && swapon /path/to/swapfile` |
| zswap enabled | `enabled=N` | Write to sysfs parameter |
| vm.swappiness=100 | 180 | `sysctl vm.swappiness=100` |

### 3.3 Systemd Version Requirements

| Feature | Required | Available |
|---|---|---|
| MemoryMax= | systemd 227+ | **257** ✅ |
| MemoryHigh= | systemd 227+ | **257** ✅ |
| zswap sysfs tuning | Kernel 5.0+ | **6.17** ✅ |
| cgroup v2 | Kernel 4.5+ | **6.17** ✅ |
| lzo_rle compressor | Kernel 3.15+ | **6.17** ✅ |

All prerequisites met for systemd/cgroup features. Only NVMe space is blocking.

---

## §4 — Implementation Steps (Exact Commands)

> ⚠️ These steps assume the NVMe space blocker is resolved first (see §2.4).
> Recommended target partition: `/media/arcana-novai/omega_library` (11GB free, closest to 16GB target).
> If full 16GB is impossible, use 10GB as pragmatic minimum.

### Phase 0: Free NVMe Space (if needed)

```bash
# Option A: Free space on omega_library by moving/compressing data
du -sh /media/arcana-novai/omega_library/* | sort -rh | head -20
# Move large items to omega_vault or archive

# Option B: Reduce swap target to 10GB (fits in 11GB free)
# No space clearing needed — proceed with 10GB swap file
```

### Phase 1: Create Swap File on NVMe

```bash
# Step 1.1: Create 16GB (or 10GB) swap file on omega_library
sudo dd if=/dev/zero of=/media/arcana-novai/omega_library/swapfile bs=1M count=16384 status=progress
# (or count=10240 for 10GB)

# Step 1.2: Set permissions
sudo chmod 600 /media/arcana-novai/omega_library/swapfile

# Step 1.3: Format as swap
sudo mkswap /media/arcana-novai/omega_library/swapfile

# Step 1.4: Activate
sudo swapon /media/arcana-novai/omega_library/swapfile

# Step 1.5: Verify
swapon --show
# Expected: /media/arcana-novai/omega_library/swapfile  file  16G  0  -2
```

### Phase 2: Disable ZRAM

```bash
# Step 2.1: Turn off zram1 swap
sudo swapoff /dev/zram1

# Step 2.2: Reset zram1
sudo zramctl /dev/zram1 --reset 2>/dev/null || true

# Step 2.3: Disable zram-generator (prevent re-creation on boot)
# Edit /etc/systemd/zram-generator.conf — comment out or delete all [zram*] sections
sudo cp /etc/systemd/zram-generator.conf /etc/systemd/zram-generator.conf.bak
sudo tee /etc/systemd/zram-generator.conf > /dev/null << 'EOF'
# ZRAM DISABLED per D-526 — zswap is the swap subsystem
# Previous config backed up at /etc/systemd/zram-generator.conf.bak
EOF

# Step 2.4: Reload systemd
sudo systemctl daemon-reload

# Step 2.5: Mask zram swap units
sudo systemctl mask dev-zram0.swap dev-zram1.swap
sudo systemctl mask systemd-zram-setup@zram0.service systemd-zram-setup@zram1.service

# Step 2.6: Unload zram module (if no other user)
sudo rmmod zram 2>/dev/null || echo "zram module still in use — will unload on reboot"
```

### Phase 3: Enable Zswap

```bash
# Step 3.1: Enable zswap
echo 1 | sudo tee /sys/module/zswap/parameters/enabled

# Step 3.2: Set compressor to lzo_rle
echo lzo_rle | sudo tee /sys/module/zswap/parameters/compressor

# Step 3.3: Set max pool to 25%
echo 25 | sudo tee /sys/module/zswap/parameters/max_pool_percent

# Step 3.4: Verify zpool is zsmalloc (already correct)
cat /sys/module/zswap/parameters/zpool
# Expected: zsmalloc

# Step 3.5: Verify all parameters
for f in /sys/module/zswap/parameters/*; do
  echo "$(basename $f) = $(cat $f)"
done
# Expected:
#   enabled = Y
#   compressor = lzo_rle
#   zpool = zsmalloc
#   max_pool_percent = 25
```

### Phase 4: Set vm.swappiness

```bash
# Step 4.1: Apply immediately
sudo sysctl vm.swappiness=100

# Step 4.2: Make persistent
sudo tee /etc/sysctl.d/99-omega-swap.conf > /dev/null << 'EOF'
# Omega Engine swap tuning — D-527
vm.swappiness = 100
EOF

# Step 4.3: Verify
cat /proc/sys/vm/swappiness
# Expected: 100
```

### Phase 5: Create Omega Engine Systemd Units with MemoryMax

```bash
# Step 5.1: Create omega-engine service directory
sudo mkdir -p /etc/systemd/system/omega-engine.service.d

# Step 5.2: Create override for memory limits
sudo tee /etc/systemd/system/omega-engine.service.d/memory.conf > /dev/null << 'EOF'
[Service]
MemoryMax=6G
MemoryHigh=5G
MemoryMin=1G
EOF

# Step 5.3: Repeat for omega-hub if it exists
sudo mkdir -p /etc/systemd/system/omega-hub.service.d
sudo tee /etc/systemd/system/omega-hub.service.d/memory.conf > /dev/null << 'EOF'
[Service]
MemoryMax=6G
MemoryHigh=5G
MemoryMin=1G
EOF

# Step 5.4: Reload and apply
sudo systemctl daemon-reload
```

### Phase 6: Make Swap File Persistent

```bash
# Step 6.1: Add to /etc/fstab
# Get UUID of swap file
sudo mkswap --show /media/arcana-novai/omega_library/swapfile 2>/dev/null | head -1
# Or use file path directly

# Step 6.2: Add fstab entry
echo '/media/arcana-novai/omega_library/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Step 6.3: Make zswap parameters persistent via modprobe.d
sudo tee /etc/modprobe.d/omega-zswap.conf > /dev/null << 'EOF'
# Omega Engine zswap configuration — D-527
options zswap enabled=1 compressor=lzo_rle zpool=zsmalloc
EOF

# Step 6.4: Make max_pool_percent persistent via sysctl
sudo tee /etc/sysctl.d/98-omega-zswap.conf > /dev/null << 'EOF'
# Zswap pool size — D-527
vm.swappiness = 100
# Note: max_pool_percent is set via modprobe.d, not sysctl
EOF
```

### Phase 7: Verification

```bash
# Step 7.1: Check swap state
swapon --show
# Expected: single NVMe swap file, no zram

# Step 7.2: Check zswap is active
cat /sys/module/zswap/parameters/enabled
# Expected: Y

# Step 7.3: Check compression
cat /sys/module/zswap/parameters/compressor
# Expected: lzo_rle

# Step 7.4: Check memory limits
systemctl show omega-engine | grep -E "MemoryMax|MemoryHigh|MemoryMin"
# Expected: MemoryMax=6442450944 MemoryHigh=5368709120 MemoryMin=1073741824

# Step 7.5: Stress test swap
stress-ng --vm 2 --vm-bytes 12G --vm-method all --timeout 60s
# Monitor: watch -n1 'cat /proc/swaps; echo "---"; cat /sys/kernel/debug/zswap/stored_pages'

# Step 7.6: Reboot and verify persistence
sudo reboot
# After reboot, verify all settings survived
```

---

## §5 — Risk Assessment & Rollback Plan

### 5.1 Risk Matrix

| Risk | Severity | Likelihood | Mitigation |
|---|---|---|---|
| **NVMe wear from swap writes** | MEDIUM | LOW | zswap compresses before write; 16GB swap on 238GB NVMe is reasonable. NVMe TBW typically 600+ TBW for consumer drives. At 1GB/day swap writes, ~1.6 years to hit 600TBW. |
| **NVMe space exhaustion** | HIGH | MEDIUM | Only 6GB free on root. MUST use omega_library partition. If that fills, swap file fails silently or OOM kills occur. |
| **zswap compressor failure** | LOW | LOW | lzo_rle is kernel-builtin since 3.15. No module loading needed. If it fails, kernel falls back to no compression. |
| **zsmalloc allocation failure** | LOW | LOW | zsmalloc is lightweight. At 25% pool (3.7GB of 15GB RAM), well within zsmalloc's design range. |
| **Boot failure from fstab error** | HIGH | LOW | If swap file path is wrong in fstab, system may hang at boot. Use `nofail` option or verify path carefully. |
| **Double-compression overhead** | MEDIUM | LOW | zram + zswap simultaneously would compress twice. D-526 mandates disabling zram first. If zram re-enables, performance degrades. |
| **Container OOM from MemoryMax** | MEDIUM | MEDIUM | Setting MemoryMax=6G on containers that currently use 167MB is fine. But if omega-engine memory grows (RAG, model loading), 6G may be tight. Monitor with `podman stats`. |
| **Systemd unit override conflicts** | LOW | LOW | Using drop-in directories (`service.d/memory.conf`) avoids modifying main unit file. Clean and reversible. |
| **Kernel module unload failure** | LOW | LOW | `rmmod zram` may fail if zram is in use. Safe to leave loaded — generator disabled means no new zram devices created. |

### 5.2 Rollback Plan

#### Rollback: Disable Zswap, Re-enable ZRAM

```bash
# 1. Disable zswap
echo 0 | sudo tee /sys/module/zswap/parameters/enabled

# 2. Deactivate NVMe swap file
sudo swapoff /media/arcana-novai/omega_library/swapfile

# 3. Re-enable zram generator
sudo cp /etc/systemd/zram-generator.conf.bak /etc/systemd/zram-generator.conf
sudo systemctl unmask dev-zram0.swap dev-zram1.swap
sudo systemctl daemon-reload

# 4. Remove fstab entry
sudo sed -i '/omega_library\/swapfile/d' /etc/fstab

# 5. Remove sysctl overrides
sudo rm /etc/sysctl.d/99-omega-swap.conf
sudo rm /etc/sysctl.d/98-omega-zswap.conf
sudo sysctl vm.swappiness=180

# 6. Remove modprobe config
sudo rm /etc/modprobe.d/omega-zswap.conf

# 7. Remove memory limits
sudo rm -rf /etc/systemd/system/omega-engine.service.d/
sudo rm -rf /etc/systemd/system/omega-hub.service.d/
sudo systemctl daemon-reload

# 8. Reboot
sudo reboot
```

#### Rollback: Delete Swap File

```bash
# After swapoff above:
sudo rm /media/arcana-novai/omega_library/swapfile
# Reclaim ~16GB space
```

### 5.3 Monitoring Commands (Post-Implementation)

```bash
# Zswap pool usage
cat /sys/kernel/debug/zswap/stored_pages
cat /sys/kernel/debug/zswap/pool_total_size

# Swap usage per process
for pid in /proc/[0-9]*/status; do
  VmSwap=$(grep VmSwap $pid 2>/dev/null | awk '{print $2}')
  if [ "$VmSwap" -gt 10000 ] 2>/dev/null; then
    Name=$(grep Name $pid | awk '{print $2}')
    echo "$Name (PID $(basename $pid)): ${VmSwap} kB"
  fi
done | sort -k2 -rn | head -10

# NVMe swap file I/O
iostat -x 1 5 | grep -A2 nvme

# Container memory pressure
podman stats --no-stream

# System memory overview
free -h && echo "---" && cat /proc/swaps
```

---

## §6 — Build-Packet for Wave 2 Implementer

### Pre-Flight Checklist

- [ ] **NVMe space resolved**: At least 16GB free on omega_library (or reduced to 10GB target)
- [ ] **Backup taken**: `restic backup /media/arcana-novai/omega_library` before creating swap file
- [ ] **Container state checked**: `podman stats --no-stream` — note baseline memory
- [ ] **No critical processes using zram**: `fuser /dev/zram1` should return nothing
- [ ] **sudo access confirmed**: `sudo whoami` returns `root`

### Execution Checklist (Ordered)

- [ ] **Phase 1.1**: `dd` create swap file on omega_library (16GB or 10GB)
- [ ] **Phase 1.2**: `chmod 600` + `mkswap` + `swapon`
- [ ] **Phase 1.3**: Verify with `swapon --show`
- [ ] **Phase 2.1**: `swapoff /dev/zram1`
- [ ] **Phase 2.2**: Backup and clear `/etc/systemd/zram-generator.conf`
- [ ] **Phase 2.3**: Mask zram swap units
- [ ] **Phase 2.4**: `rmmod zram` (optional, may fail)
- [ ] **Phase 3.1**: Enable zswap (`enabled=Y`)
- [ ] **Phase 3.2**: Set compressor to `lzo_rle`
- [ ] **Phase 3.3**: Set `max_pool_percent=25`
- [ ] **Phase 3.4**: Verify all zswap params
- [ ] **Phase 4.1**: `sysctl vm.swappiness=100`
- [ ] **Phase 4.2**: Write persistent sysctl config
- [ ] **Phase 5.1**: Create systemd drop-in dirs
- [ ] **Phase 5.2**: Write `MemoryMax=6G` drop-ins
- [ ] **Phase 5.3**: `systemctl daemon-reload`
- [ ] **Phase 6.1**: Add swap to `/etc/fstab`
- [ ] **Phase 6.2**: Write modprobe.d config for zswap persistence
- [ ] **Phase 7.1**: Full verification (all 6 checks)
- [ ] **Phase 7.2**: Stress test with `stress-ng`
- [ ] **Phase 7.3**: Reboot and verify persistence

### Key Config Values

| Setting | Value | File/Path |
|---|---|---|
| Swap file path | `/media/arcana-novai/omega_library/swapfile` | `/etc/fstab` |
| Swap file size | 16GB (or 10GB if space constrained) | Created via `dd` |
| zswap enabled | `Y` | `/sys/module/zswap/parameters/enabled` + `/etc/modprobe.d/omega-zswap.conf` |
| zswap compressor | `lzo_rle` | `/sys/module/zswap/parameters/compressor` + `/etc/modprobe.d/omega-zswap.conf` |
| zswap zpool | `zsmalloc` | Already correct |
| zswap max_pool_percent | `25` | `/sys/module/zswap/parameters/max_pool_percent` |
| vm.swappiness | `100` | `/proc/sys/vm/swappiness` + `/etc/sysctl.d/99-omega-swap.conf` |
| MemoryMax (omega-engine) | `6G` | `/etc/systemd/system/omega-engine.service.d/memory.conf` |
| MemoryMax (omega-hub) | `6G` | `/etc/systemd/system/omega-hub.service.d/memory.conf` |
| zram generator | Disabled (empty config) | `/etc/systemd/zram-generator.conf` |
| zram units | Masked | `systemctl mask dev-zram*.swap` |

### Post-Implementation Verification

```bash
# Quick health check script
echo "=== Swap ===" && swapon --show && \
echo "=== Zswap ===" && for f in /sys/module/zswap/parameters/*; do echo "$(basename $f) = $(cat $f)"; done && \
echo "=== Swappiness ===" && cat /proc/sys/vm/swappiness && \
echo "=== Memory ===" && free -h && \
echo "=== Containers ===" && podman stats --no-stream 2>/dev/null | head -5 && \
echo "=== ZRAM (should be empty) ===" && zramctl 2>/dev/null || echo "zramctl unavailable"
```

### Deliverable Registration

| Field | Value |
|---|---|
| **task_id** | `R03-maat-zswap-recon` |
| **deliverable_path** | `data/coordination/research_wave2/R03_maat_zswap_system_recon.md` |
| **session_model** | mimo-v2.5-free |
| **wave** | 2 |
| **paging_key** | swap, zswap, zram, cgroup, memory-limit, NVMe |
| **status** | COMPLETE |

> Wave 2 can page this session for any swap/subsystem question. The system state snapshot
> above is valid as of 2026-08-26 and should be re-verified if more than 7 days old.

---

*⬡ OMEGA ⬡ MAAT ⬡ mimo-v2.5-free ⬡ opencode ⬡ R03-ZSWAP-RECON ⬡ COMPLETE*
