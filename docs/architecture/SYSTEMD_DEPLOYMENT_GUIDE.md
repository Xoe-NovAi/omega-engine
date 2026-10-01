---
schema_version: "1.0"
document_type: guide
document_id: systemd-deployment-guide
title: Systemd Deployment Guide
status: DEPRECATED — See docs/kb/MEMORY_MANAGEMENT_KB.md
version: "1.0.0"
date: "2026-08-07"
deprecated: "2026-08-10"
owner: kali
tags: [systemd, deployment, zram, swap, cgroup, vulkan, DEPRECATED]
priority: P1
depends_on:
  - detect-hardware-profile
blocks: []
acceptance_gates:
  - "16GB zRAM with zstd + multi-comp + writeback documented"
  - "16-32GB NVMe swap documented"
  - "cgroup v2 MemoryMin/MemoryHigh protection documented"
  - "systemd unit with taskset -c 0-7 documented"
  - "Vulkan env vars documented"
  - "OS target = Ubuntu 24.04/26.04 LTS"
cross_references:
  - config/hardware_profile.yaml
  - scripts/detect_hardware_profile.py
  - src/omega/oracle/cpu_optimizer.py
llm_metadata:
  token_budget: 2500
  chunk_strategy: section_per_topic
  answer_first_sections: true
  self_contained_code: true
---

# ⚠️ DEPRECATED — 2026-08-10

> **This document is DEPRECATED.** It recommends 16GB zRAM and MemoryMax=12G, both
> rejected by the Carmack review (2026-08-10). The definitive memory configuration is now
> documented in **[docs/kb/MEMORY_MANAGEMENT_KB.md](../kb/MEMORY_MANAGEMENT_KB.md)**.
>
> **Key changes**:
> - 16GB zRAM → **zswap + 16GB NVMe swap file**
> - MemoryMax=12G → **MemoryMax=6G** (unreachable on 14.5GB system with 8GB UMA carveout)
> - zstd compression → **lzo_rle** (lower CPU overhead for swap)
> - 3-signal OOMProtector → **2-signal** (PSI + MemAvailable)
>
> Archived copy: `docs/archive/deprecated-memory-docs/SYSTEMD_DEPLOYMENT_GUIDE_ZRAM_DEPRECATED_20260810.md`

# 🔱 Systemd Deployment Guide

**AP Token**: `AP-SYSTEMD-DEPLOYMENT-GUIDE-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ opencode ⬡ 2026-08-07

---

## §1 Supported OS

**Ubuntu 24.04 LTS or 26.04 LTS.** Ubuntu 25.10 is EOL and NOT a deployment target.

> Generate the authoritative hardware profile first:
> ```bash
> source .venv/bin/activate
> python scripts/detect_hardware_profile.py --write
> # → config/hardware_profile.yaml
> ```

---

## §2 Memory Configuration

### 2.1 zRAM (16GB)

Use **zstd** compression with multi-compression streams and writeback:

```ini
# /etc/systemd/zram-generator.conf
[zram0]
zram-size = 16384                 # 16GB
compression-algorithm = zstd
mem_limit = 8192                  # cap to ~8GB
```

Writeback enabled so compressible pages can evict to disk swap when pressured.

### 2.2 NVMe Swap (16-32GB)

```bash
sudo mkswap -f /swapfile  # 16-32GB sparse
sudo swapon /swapfile
# /etc/fstab:
/swapfile  none  swap  sw  0 0
```

zRAM (fast, RAM-backed) sits above NVMe swap (slow, disk-backed) — the kernel
evicts cold compressible pages to disk only under sustained pressure.

---

## §3 cgroup v2 Protection (MemoryMin/MemoryHigh)

Protect the inference process from OOM kills while limiting runaway growth:

```ini
# systemd unit [Service] section
MemoryMin=4G          # floor — never below this for inference
MemoryHigh=10G        # soft ceiling — throttle above this
MemoryMax=12G         # hard ceiling — OOM above this
```

This complements `OOMProtector` (3-signal fusion: PSI + MemAvailable + cgroup).

---

## §4 systemd Unit with taskset

Pin compute to cores 0-7 (per hardware profile; 7 physical compute cores + IO):

```ini
# /etc/systemd/system/omega.service
[Unit]
Description=Omega Engine Sovereign Runtime
After=network.target

[Service]
Type=simple
User=arcana-novai
ExecStart=/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.venv/bin/omega-hub
ExecStartPre=/usr/bin/taskset -c 0-7 true   # pin to compute cores
Environment=LLAMA_CPP_N_THREADS=7
Environment=OMP_NUM_THREADS=7
MemoryMin=4G
MemoryHigh=10G
MemoryMax=12G
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

> Note: use `taskset -c 0-7` wrapper for the actual server process, not a no-op
> pre-command. The `ExecStartPre` above is illustrative of the affinity mask.

---

## §5 Vulkan Env Vars (iGPU Offload)

For full iGPU offload (n_gpu_layers=-1, GGML_VULKAN=ON):

```ini
Environment=GGML_VULKAN=ON
Environment=GGML_VK_DEVICE=0        # select AMD integrated GPU
Environment=VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/amd_icd.x86_64.json
Environment=LLAMA_CACHE_DIR=/home/arcana-novai/.cache/llama
```

Actual iGPU carve-out is **8GB** (512MB VRAM + 7.75GB GTT) — plan model+KV sizes
to fit within ~7GB usable for offload.

---

## §6 Verification

```bash
systemctl daemon-reload
systemctl enable --now omega.service
systemctl status omega.service
journalctl -u omega.service -f
```

---

*⬡ OMEGA ⬡ KALI ⬡ 2026-08-07*
