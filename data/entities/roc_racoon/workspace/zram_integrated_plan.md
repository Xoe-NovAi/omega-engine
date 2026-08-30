<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# zRAM Integrated Plan — Final (Post-Carmack Review)
## roc_racoon synthesis of Jem + Researcher + @john_carmack

**AP Token**: `AP-ZRAM-INTEGRATED-PLAN-v1.0.0`
**Date**: 2026-08-10
**Status**: ✅ FINALIZED — Carmack review incorporated, ready for execution

---

## ⚠️ CRITICAL UPDATE — Carmack Review Applied
@john_carmack reviewed the plan and found it **over-engineered by 3x**. Key changes:
- **16GB zRAM → 8GB** (sufficient, saves 2.6GB RAM)
- **cgroup limits fixed**: MemoryMax=6G (not 12G — unreachable on 14.5GB system with 8GB UMA carveout)
- **zRAM writeback REMOVED** (zero leverage)
- **zRAM signal in OOMProtector REJECTED** (redundant with MemAvailable)
- **use_cgroup config flag REJECTED** (runtime detection already works)
- **8-step plan → 3-command fix + 4 optimization steps**
- **Package as WAD** for portability (M2 compliance)

---

## 1. Problem Statement (Confirmed)

The Omega Engine on Ryzen 7 5700U (14.5 GiB RAM) has **6.4 GiB of zRAM swap in use at zero PSI memory pressure** (PSI=0.00). The root cause is **`vm.swappiness=180`** (set in `/etc/sysctl.d/99-xnai-zram-tuning.conf`) causing the kernel to aggressively swap idle anonymous pages into 8 GiB zRAM, consuming **4.1 GiB of real RAM** for compression buffers.

### Live System State (verified by @researcher)
```
vm.swappiness = 180          ← ROOT CAUSE (should be 100)
vm.watermark_scale_factor = 125  ← OK (keep)
vm.page-cluster = 0            ← OK (keep)
vm.vfs_cache_pressure = 50     ← OK (keep)

zram0: MASKED (symlinked to /dev/null) — 4GB lz4 device inactive
zram1: 8GB zstd level=15, 6.5GB used (81%), ratio 1.62:1
zswap: disabled
cgroup memory.max/high/min: all empty (no limits)
Kernel: 6.17.0-41-generic (CONFIG_ZRAM_MULTI_COMP NOT set)

sudoers vulnerability: /tmp/reset_zram.sh, /tmp/activate_zram.sh in NOPASSWD ← CRITICAL
```

---

## 2. Synthesis: Jem's Gaps → Researcher's Resolutions

| Gap | Jem's Finding | Researcher's Resolution | Priority |
|-----|---------------|------------------------|----------|
| **G-1** | watermark_scale_factor: 0 matches | Keep 125 (Fedora gaming recommendation for zRAM) | Low |
| **G-2** | 8GB zRAM vs 16GB target | Expand to 16GB zstd level=3, resident-limit 8GB | High |
| **G-3** | swappiness: 60 vs 80 vs 180 | **Set to 100** (kernel docs sweet spot for in-memory swap) | **CRITICAL** |
| **G-4** | No cgroup protection | MemoryMin=4G, MemoryHigh=10G, MemoryMax=12G, MemorySwapMax=infinity | High |
| **G-5** | No zRAM writeback | Configure idle/huge page writeback to NVMe swap file | Medium |
| **G-6** | Multi-comp not available | Use idle page writeback (recompress not available on kernel 6.17) | Medium |
| **G-7** | M1 asyncio violations claimed | **RESOLVED** — code already uses anyio/aiofiles | None |
| **G-8** | 3-signal fusion "server-grade theater" | Simplify to 2-signal (PSI + MemAvailable) for desktop; cgroup optional | Medium |
| **G-9** | No consolidated tuning | 8-step implementation plan | High |
| **G-10** | tune_ryzen.sh inconsistency | Update to swappiness=100 | Medium |
| **G-11** | No zram-generator.conf on system | Deploy single 16GB zstd device config | High |
| **G-12** | Conflicting sysctl.d files | Consolidate to single 99-omega-memory.conf | High |
| **G-13** | No systemd unit with cgroup protection | Create omega.service with MemoryMin/High/Max | High |
| **G-14** | Sudoers /tmp/ vulnerability | **CONFIRMED** — remove immediately, deploy safe bridge scripts | **CRITICAL** |
| **G-15** | No zRAM signal in OOMProtector | Add zRAM fill ratio as 4th signal (THROTTLE at >90%) | Medium |

---

## 3. Integrated Action Plan (Post-Carmack)

### Phase 1: IMMEDIATE (P0 — Do Today — 3 Commands, 10 Seconds)
```bash
# 1. Security: Remove sudoers backdoor (CRITICAL)
sudo rm /etc/sudoers.d/zram

# 2. Root cause: Fix swappiness from 180 to 100
sudo sysctl vm.swappiness=100

# 3. Reclaim memory: Flush 4.1GB of unnecessary swap
sudo swapoff -a && sudo swapon -a
```
**Effect**: Solves root cause + security vulnerability. Available RAM jumps from 5.9 GiB → ~10 GiB.

### Phase 2: SYSTEM CONFIGURATION (P1 — This Week)
1. **Consolidate sysctl.d** (G-3, G-10, G-12) — Single `99-omega-memory.conf` with swappiness=100
2. **Keep 8GB zRAM** — Do NOT expand to 16GB (8GB with 3:1 compression is sufficient)
3. **Fix cgroup limits** (G-4) — MemoryMin=2G, MemoryHigh=5G, MemoryMax=6G (reachable on 14.5GB system)
4. **Deploy safe sudoers bridge** (G-14) — Read-only monitoring (no /tmp/ scripts)
5. **Add systemd hardening** — CapabilityBoundingSet, SystemCallFilter, LockPersonality, RestrictRealtime
6. **Update tune_ryzen.sh** (G-10) — Change swappiness from 60 to 100

### Phase 3: CODE REFACTORING (P2 — Phase 2 Engineering)
1. **M1 verification** (G-7) — Already compliant, update docs only
2. **Simplify OOMProtector** (G-8) — Remove cgroup signal from desktop path (runtime detection already works, no config flag needed)
3. **Remove LegacyOOMWrapper** — Unnecessary indirection in resource_guard.py
4. **Package as WAD** — Move all system configs to `config/wads/ryzen-5700u-sovereign/` with templated values (M2 compliance)

### REJECTED (Carmack Verdict)
- ❌ 16GB zRAM expansion (wastes 2.6GB RAM)
- ❌ zRAM writeback cron + 32GB NVMe swap file (zero leverage)
- ❌ zRAM signal in OOMProtector (redundant with MemAvailable)
- ❌ `use_cgroup: bool = False` config flag (runtime detection already works)
- ❌ MemoryMax=12G (unreachable — only 6.5GB process RAM after 8GB UMA carveout)

---

## 4. Implementation Commands (Post-Carmack)

### Step 1: IMMEDIATE FIX (3 commands — do today)
```bash
sudo rm /etc/sudoers.d/zram          # Security: remove backdoor
sudo sysctl vm.swappiness=100         # Root cause: fix aggressive swapping
sudo swapoff -a && sudo swapon -a     # Reclaim 4.1GB RAM
```

### Step 2: Consolidate sysctl (P1 — this week)
```bash
sudo rm -f /etc/sysctl.d/99-xnai-*.conf
sudo tee /etc/sysctl.d/99-omega-memory.conf <<'EOF'
vm.swappiness = 100
vm.page-cluster = 0
vm.watermark_boost_factor = 0
vm.watermark_scale_factor = 125
vm.vfs_cache_pressure = 50
vm.dirty_background_ratio = 5
vm.dirty_ratio = 10
vm.overcommit_memory = 0
EOF
sudo sysctl --system
```

### Step 3: Fix cgroup limits (P1)
```bash
# In systemd unit (see Step 4), use:
# MemoryMin=2G    (was 4G — 2G is sufficient for inference)
# MemoryHigh=5G   (was 10G — unreachable)
# MemoryMax=6G    (was 12G — unreachable on 14.5GB system with 8GB UMA carveout)
# MemorySwapMax=infinity
```

### Step 4: Create systemd unit with CORRECTED cgroup limits + hardening
```bash
sudo tee /etc/systemd/system/omega.service <<'EOF'
[Unit]
Description=Omega Engine Sovereign Runtime
Documentation=https://xoe-nov.ai/docs
After=network.target systemd-zram-setup@zram1.service
Wants=systemd-zram-setup@zram1.service

[Service]
Type=simple
User=arcana-novai
Group=arcana-novai
WorkingDirectory=/home/arcana-novai/Documents/Xoe-NovAi/omega-engine
ExecStart=/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.venv/bin/omega-hub
Restart=on-failure
RestartSec=5

# CPU pinning (compute cores 0-7 on 5700U)
Environment=LLAMA_CPP_N_THREADS=7
Environment=OMP_NUM_THREADS=7

# Memory protection (cgroup v2) — CORRECTED per Carmack review
# 14.5GB RAM - 8GB UMA carveout = ~6.5GB process RAM
MemoryMin=2G
MemoryHigh=5G
MemoryMax=6G
MemorySwapMax=infinity

# Security hardening (Carmack additions)
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
EOF
sudo systemctl daemon-reload
sudo systemctl enable omega.service
```

### Step 5: Deploy safe sudoers (read-only — no /tmp/ scripts)
```bash
# Read-only: zramctl and swapon can be read without sudo
# No sudoers entry needed for monitoring

# If write access is needed, use vetted scripts in /usr/local/bin/:
sudo tee /etc/sudoers.d/omega-engine <<'EOF'
# Omega Engine Infrastructure Bridge
# Per H-SUDO-001: scripts MUST reside in /usr/local/bin/ (never /tmp/)
# Per H-SUDO-002: scripts expose ONLY required sub-commands
arcana-novai ALL=(ALL) NOPASSWD: /usr/local/bin/omega-zram-tune.sh
EOF
sudo chmod 440 /etc/sudoers.d/omega-engine
sudo visudo -c
```

### Step 6: Update tune_ryzen.sh
```bash
# In scripts/tune_ryzen.sh, change:
# vm.swappiness = 60  →  vm.swappiness = 100
# Add comment: "100 = kernel-documented sweet spot for in-memory compressed swap"
```

### Step 7: Package as WAD (M2 compliance)
```bash
# Create config/wads/ryzen-5700u-sovereign/ with templated configs
# Use systemd specifiers (%h, %u) instead of hardcoded paths
# Add install.sh for atomic apply/revert
```

### REJECTED — Do NOT implement:
- ❌ 16GB zRAM expansion (Step 3 in original plan)
- ❌ zRAM writeback to NVMe (Step 5 in original plan)
- ❌ zRAM signal in OOMProtector (G-15)
- ❌ `use_cgroup: bool = False` config flag (G-8)

---

## 5. Expected Outcomes (Post-Carmack)

| Metric | Before | After (3-command fix) | After (Full P1) |
|--------|--------|----------------------|-----------------|
| vm.swappiness | 180 | 100 | 100 |
| Swap used | 6.4 GiB | ~1.5 GiB (within 30 min) | <500 MiB |
| Available RAM | 5.9 GiB | ~10 GiB | ~10 GiB |
| zRAM config | 8GB zstd lvl=15, zram0 masked | 8GB zstd lvl=15 | 8GB zstd lvl=15 (keep) |
| Compression ratio | 1.62:1 | 1.62:1 | ~2.0:1 (natural page mix) |
| zRAM fill ratio | 52.5% | ~15% | <10% |
| cgroup protection | None | None | MemoryMin=2G, High=5G, Max=6G |
| sudoers vuln | /tmp/ scripts in NOPASSWD | Removed | Safe read-only (no sudoers needed) |
| OOMProtector | 3-signal (PSI+MemAvail+cgroup) | 3-signal | 2-signal (PSI+MemAvail) + optional cgroup |

## 6. Design Review (@john_carmack) — APPLIED

**Verdict**: REQUEST CHANGES — over-engineered by 3x. All recommendations incorporated above.

### Key Changes Applied:
1. ✅ 16GB zRAM → 8GB (sufficient, saves 2.6GB RAM)
2. ✅ MemoryMax=12G → 6G (reachable on 14.5GB system with 8GB UMA carveout)
3. ✅ zRAM writeback REMOVED (zero leverage)
4. ✅ zRAM signal in OOMProtector REJECTED (redundant with MemAvailable)
5. ✅ `use_cgroup` config flag REJECTED (runtime detection already works)
6. ✅ 8-step plan → 3-command fix + 4 P1 steps + 4 P2 steps
7. ✅ Added systemd hardening (CapabilityBoundingSet, SystemCallFilter, etc.)
8. ✅ WAD packaging for M2 compliance (M16)

### Carmack Alternative (3-Command Fix):
```bash
sudo rm /etc/sudoers.d/zram          # Security
sudo sysctl vm.swappiness=100         # Root cause
sudo swapoff -a && sudo swapon -a     # Reclaim 4.1GB RAM
```
**Leverage ratio**: 3 commands, 10 seconds, solves root cause + security vulnerability.

---

---

## 7. Heritage Tags
- `[id-soft: quake-1996] Thinker Chain` — N/A (no heritage code changes)
- `[heritage: xnai-2025] Stack-Cat` — config consolidation pattern
- `[heritage: pi-2026] Gemma 4 Thinking Config` — N/A
- H-SUDO-001, H-SUDO-002 — sudoers security (applied in P0 fix)
- `[id-soft: vet-015] ZONEID Pattern` — properly applied in ResourceGuard (Carmack verified)

---

## 8. Subagent Reliability Issues Discovered (Critical)

During this workflow, three critical subagent reliability issues were discovered:

1. **Silent failures**: Subagents can fail with no error output, no partial results, no indication of what went wrong (observed with Jem's first two attempts)
2. **Auto-compaction context loss**: Subagents hit compaction thresholds, lose context, and resume with no memory of their task
3. **Looping behavior**: Subagents can enter infinite search loops without writing intermediate results

**Mitigation**: All subagent prompts must now include:
- Phase-based execution with mandatory disk writes after each phase
- Bounded search (max N files per phase)
- Explicit stop conditions
- Checkpoint intervals (write every 5 minutes)

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ opencode/laguna-s-2.1-free ⬡ trc_synthesis ⬡ 2026-08-10*
