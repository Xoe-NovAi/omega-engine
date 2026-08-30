# 🔱 Omega Engine — High Performance Memory Management KB
## Definitive Best Practices & Technical Data

**AP Token**: `AP-MEMORY-KB-v1.0.0`
**Date**: 2026-08-10
**Status**: ✅ DEFINITIVE — Supersedes all previous memory docs
**Model**: opencode/longcat-2.0-free
**Supersedes**: SYSTEMD_DEPLOYMENT_GUIDE.md, hardware_profile.yaml (memory sections), tune_ryzen.sh

---

## §1 Executive Summary

### Current System State (Ryzen 7 5700U, 14.5GB RAM)
- **Problem**: 6.4GB zRAM swap used at zero PSI pressure (swappiness=180)
- **Root cause**: Aggressive proactive swapping consuming 4.1GB real RAM
- **Immediate fix**: 3 commands (swappiness=100, remove sudoers vuln, swapoff/swapon)
- **Long-term architecture**: zswap + NVMe swap file (NOT zRAM)

### Key Decisions (Post-Carmack Review)
| Decision | Value | Rationale |
|----------|-------|-----------|
| Swap architecture | **zswap + NVMe** | Dynamic, graceful degradation, kernel-integrated |
| zswap compressor | **lzo_rle** | Lowest CPU overhead for swap workloads |
| zswap pool | **25% of RAM** | Dynamic 0-3.6GB, grows on demand |
| NVMe swap file | **16GB** | Fast fallback, lower priority |
| swappiness | **100** | Kernel-documented sweet spot for in-memory swap |
| watermark_scale_factor | **125** | Fedora gaming recommendation for compressed swap |
| cgroup MemoryMin | **2GB** | Guarantee for inference |
| cgroup MemoryHigh | **5GB** | Soft ceiling (~77% of available) |
| cgroup MemoryMax | **6GB** | Hard ceiling (leaves 0.5GB for OS) |

---

## §2 Memory Architecture

### 2.1 Physical Memory Layout
```
Total RAM:        14,793 MB (14.5 GB)
UMA Carveout:      8,192 MB (8.0 GB) — Vega 8 iGPU
Available:         ~6,601 MB (6.5 GB) — for OS + processes
```

### 2.2 Swap Architecture (Target)
```
┌─────────────────────────────────────────────────────────────┐
│                  Omega Engine Memory Stack                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Physical RAM: 14.5 GiB                                     │
│  ├─ UMA Carveout: 8 GiB (Vega 8 iGPU)                       │
│  └─ Available: ~6.5 GiB                                     │
│                                                             │
│  zSwap Pool: 0-25% of RAM (0-3.6 GiB dynamic)              │
│  ├─ Hot anonymous pages compressed in RAM (lzo_rle)          │
│  └─ Cold pages evicted to NVMe swap file                   │
│                                                             │
│  NVMe Swap File: 16 GiB (fast fallback)                    │
│  ├─ Priority lower than zswap (implicit)                    │
│  └─ Cold page eviction target                               │
│                                                             │
│  vm.swappiness: 100                                         │
│  vm.watermark_scale_factor: 125                             │
│  vm.page-cluster: 0                                         │
│                                                             │
│  cgroup v2: MemoryMin=2G, MemoryHigh=5G, MemoryMax=6G       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 Why zswap > zRAM for This System

| Factor | zRAM (Legacy) | zswap (Current) | Source |
|--------|---------------|-----------------|--------|
| Architecture | Fixed 8GB block device | Dynamic 0-3.6GB cache + 16GB NVMe | Kernel docs |
| Failure mode | Hard cliff when full | Graceful eviction to NVMe | Chris Down 2026 |
| CPU overhead | Higher (zstd lvl=15) | Lower (lzo_rle) | LinuxBlog 2025 |
| SSD wear | All-or-nothing | Write-reduction filter | Chris Down 2026 |
| Kernel integration | None | Full reclaim + LRU | Chris Down 2026 |
| Suspend/resume | Can cause hangs | No issues | LinuxBlog 2025 |
| Incompressible data | Wastes CPU storing | Rejects, sends to disk | Chris Down 2026 |

**Primary sources**:
- Chris Down (Meta kernel team): https://chrisdown.name/2026/03/24/zswap-vs-zram-when-to-use-what.html
- LinuxBlog.io: https://linuxblog.io/zswap-better-than-zram
- ArchWiki: https://wiki.archlinux.org/title/Zswap
- Kernel docs: https://www.kernel.org/doc/html/latest/admin-guide/mm/zswap.html

---

## §3 Implementation

### 3.1 Immediate Fix (P0 — Do Today)
```bash
# 1. Security: Remove sudoers backdoor
sudo rm /etc/sudoers.d/zram

# 2. Root cause: Fix swappiness from 180 to 100
sudo sysctl vm.swappiness=100

# 3. Reclaim memory: Flush 4.1GB of unnecessary swap
sudo swapoff -a && sudo swapon -a
```

### 3.2 System Configuration (P1 — This Week)

#### zswap Configuration
```bash
# Enable zswap at runtime
echo 1 | sudo tee /sys/module/zswap/parameters/enabled
echo lzo_rle | sudo tee /sys/module/zswap/parameters/compressor
echo 25 | sudo tee /sys/module/zswap/parameters/max_pool_percent
echo 1 | sudo tee /sys/module/zswap/parameters/shrinker_enabled

# Persist in GRUB
sudo sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="[^"]*/& zswap.enabled=1 zswap.compressor=lzo_rle zswap.max_pool_percent=25 zswap.shrinker_enabled=1/' /etc/default/grub
sudo update-grub
```

#### NVMe Swap File
```bash
# Create 16GB NVMe swap file
sudo fallocate -l 16G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon -p 5 /swapfile

# Persist in /etc/fstab
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

#### sysctl Configuration
```bash
# /etc/sysctl.d/99-omega-memory.conf
vm.swappiness = 100
vm.page-cluster = 0
vm.watermark_boost_factor = 0
vm.watermark_scale_factor = 125
vm.vfs_cache_pressure = 50
vm.dirty_background_ratio = 5
vm.dirty_ratio = 10
vm.overcommit_memory = 0
```

#### systemd Unit with cgroup Protection
```ini
# /etc/systemd/system/omega.service
[Unit]
Description=Omega Engine Sovereign Runtime
After=network.target
Wants=systemd-zram-setup@zram0.service

[Service]
Type=simple
User=arcana-novai
Group=arcana-novai
WorkingDirectory=/home/arcana-novai/Documents/Xoe-NovAi/omega-engine
ExecStart=/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.venv/bin/omega-hub
Restart=on-failure
RestartSec=5
Environment=LLAMA_CPP_N_THREADS=7
Environment=OMP_NUM_THREADS=7
MemoryMin=2G
MemoryHigh=5G
MemoryMax=6G
MemorySwapMax=infinity
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
RestrictSUIDSGID=true
CapabilityBoundingSet=
AmbientCapabilities=
SystemCallFilter=@system-service
LockPersonality=true
RestrictRealtime=true

[Install]
WantedBy=multi-user.target
```

### 3.3 Code Refactoring (P2 — Phase 2 Engineering)

#### OOMProtector Simplification
- Remove cgroup signal from desktop path (runtime detection already works)
- Remove `LegacyOOMWrapper` indirection in resource_guard.py
- Add zswap stats to monitoring module (NOT as admission signal)

#### WAD Packaging
- Move all system configs to `config/wads/ryzen-5700u-sovereign/`
- Template all values (user paths, RAM sizes, CPU counts)
- Add install/uninstall scripts

---

## §4 Validation & Monitoring

### 4.1 Post-Implementation Verification
```bash
# 1. Verify zswap is active
cat /sys/module/zswap/parameters/enabled  # Should be 1
cat /sys/kernel/debug/zswap/stats  # If debugfs mounted

# 2. Verify swap file is active
swapon --show

# 3. Verify cgroup protection
systemctl show omega.service | grep -E "MemoryMin|MemoryHigh|MemoryMax"
cat /sys/fs/cgroup/system.slice/omega.service/memory.max

# 4. Verify sudoers
sudo visudo -c
grep -r "/tmp/" /etc/sudoers.d/  # Should return nothing

# 5. Monitor PSI and swap usage
watch -n 5 'cat /proc/pressure/memory; echo "---"; free -h; echo "---"; swapon --show'
```

### 4.2 Expected Outcomes
| Metric | Before | After (P0) | After (P1) |
|--------|--------|-----------|-----------|
| Swap device | 8GB zRAM (fixed) | 8GB zRAM (fixed) | zSwap pool + 16GB NVMe |
| Swap used | 6.4 GiB | ~1.5 GiB | <500 MiB |
| Available RAM | 5.9 GiB | ~10 GiB | ~10 GiB |
| Compression ratio | 1.62:1 (zstd) | 1.62:1 | ~1.8:1 (lzo_rle) |
| CPU overhead | Higher | Higher | Lower |
| Failure mode | Hard cliff | Hard cliff | Graceful eviction |

---

## §5 Deprecated Documents

The following documents are **superseded** by this KB and should be archived:

| Document | Reason | Action |
|----------|--------|--------|
| `docs/architecture/SYSTEMD_DEPLOYMENT_GUIDE.md` | Recommends 16GB zRAM, MemoryMax=12G (rejected) | Archive to docs/archive/ |
| `config/hardware_profile.yaml` (memory section) | swap_zram_mb: 16384 (should be 8GB) | Update to zswap config |
| `scripts/tune_ryzen.sh` | vm.swappiness=60 (should be 100) | Update to swappiness=100 |
| `docs/archive/web-sessions/2026-08/Web-Grok_xyz_coordinates_and_zram.md` | zRAM-specific | Already archived |
| `docs/archive/web-sessions/2026-08/Web-Grok_zRAM_and_model_disk_swap.md` | zRAM-specific | Already archived |
| `docs/archive/web-sessions/2026-08/Web-Gemini-OMEGA-ENGINE-REFACTORING.md` | zRAM-specific configs | Already archived |
| `docs/archive/web-sessions/2026-08/Web-Gemini-MaKaLi-Hierarchy-Clarification.md` | zRAM-specific configs | Already archived |
| `docs/archive/web-sessions/2026-08/Web-Grok_OMEGA_ENGINE Unified Implementation.md` | zRAM-specific | Already archived |
| `docs/archive/web-sessions/2026-08/Web-Grok_entry_level_hardware_community.md` | zRAM-specific | Already archived |
| `docs/archive/web-sessions/2026-08/Qdrant for Omega Engine Memory_full.md` | zRAM-specific | Already archived |

---

## §6 References

### Primary Sources
- Chris Down (Meta kernel team): https://chrisdown.name/2026/03/24/zswap-vs-zram-when-to-use-what.html
- LinuxBlog.io: https://linuxblog.io/zswap-better-than-zram
- ArchWiki zswap: https://wiki.archlinux.org/title/Zswap
- Kernel zswap docs: https://www.kernel.org/doc/html/latest/admin-guide/mm/zswap.html
- Kernel zram docs: https://www.kernel.org/doc/html/latest/admin-guide/blockdev/zram.html

### Internal Documents
- Jem's Excavation Report: `data/entities/jem/workspace/zram_excavation_report.md`
- Researcher's Tuning Guide: `data/entities/researcher/workspace/zram_tuning_guide.md`
- Carmack's Design Review: `data/entities/john_carmack/workspace/zram_design_review.md`
- Integrated Plan: `data/entities/roc_racoon/workspace/zram_integrated_plan.md`
- zswap Deepened Analysis: `data/entities/roc_racoon/workspace/ZRAM_ZSWAP_DEEPENED_ANALYSIS.md`
- Multi-Write Subagent Method: `data/entities/roc_racoon/workspace/MULTI_WRITE_SUBAGENT_METHOD.md`

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ opencode/longcat-2.0-free ⬡ trc_kb ⬡ 2026-08-10*
