<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Roc Racoon — Hardware Inventory
**Entity**: roc_racoon | **Channel**: opencode | **Initiated**: 2026-09-06
**Purpose**: Centralized catalog of all equipment for the Omega Engine forge

---

## 📋 Inventory Index

| # | Device | Role | Status | Location | Added |
|---|--------|------|--------|----------|-------|
| 1 | ASUS ExpertBook P1 | Primary Workstation | Provisioning | Desk | 2026-09-06 |

---

## 💻 Entry 1: ASUS ExpertBook P1 (Primary Workstation)

### Specifications
| Component | Detail |
|-----------|--------|
| **Model** | ASUS ExpertBook P1 (P1503CVA) — 13th Gen Intel Core |
| **CPU Options** | i7-13620H / i7-13700H (14C/20T, up to 5.0 GHz) · i5-13500H (12C/16T) · i3-1315U (6C/8T) |
| **Your CPU** | Intel Core i7-13620H (10C/16T, 2.4 GHz base, up to 4.9 GHz) |
| **RAM** | 16 GB DDR5-5200 MT/s (SO-DIMM, **2 slots**, dual-channel) — **Upgrade planned: 32 GB (2×16 GB kit)** |
| **Max RAM** | 64 GB (2×32 GB DDR5-5200) — modules must be installed in pairs for dual-channel |
| **Storage** | 512 GB NVMe PCIe 4.0 (M.2 2280, Slot 1) |
| **Secondary Slot** | M.2 2230 PCIe 4.0 x4 (Slot 2, up to 512 GB) — **2230 form factor only** |
| **Display** | 15.6" FHD (1920×1080), anti-glare, IPS, 300 nits, 45% NTSC, 16:9 |
| **Graphics** | Intel Iris Xe (dual-channel) / Intel UHD (single-channel) |
| **Battery** | 50 Wh, 3-cell Li-ion, 65W USB-C PD charger |
| **Weight** | ~1.61–1.65 kg |
| **Durability** | MIL-STD-810H military-grade certified |
| **Ports** | 2× USB-C 3.2 Gen 2 (DP 1.4, PD 3.0), 2× USB-A 3.2 Gen 1, HDMI 1.4b, RJ45 GbE, 3.5mm combo, microSD |
| **Wireless** | Wi-Fi 6 (802.11ax) 2×2, Bluetooth 5.4 |
| **Security** | TPM 2.0 (discrete), fingerprint sensor (touchpad-integrated), Kensington nano lock slot, webcam privacy shutter, NIST SP 800-155 BIOS |
| **Audio** | 2× speakers (Dirac), 2× array mics, ASUS AI Noise-Canceling |
| **Camera** | 720p HD with privacy shutter |
| **Keyboard** | Chiclet, num-key, 1.35mm travel, spill-resistant |

### Operating System
| Item | Detail |
|------|--------|
| **Target OS** | Ubuntu 26.04.1 LTS "Resolute Raccoon" (kernel 7.0, GNOME 50) |
| **Install Method** | Clean install via bootable USB (created with `dd` — VALIDATED 2026-09-06, D-423) |
| **Partition Plan** | EFI (512 MB, FAT32) + LUKS2-encrypted root (ext4, remaining space) |
| **Boot Mode** | UEFI (Secure Boot: **ENABLED** — dual-signed shim handles it) |
| **Critical Fix** | Dual-signed shim (`shimx64.efi.dualsigned` → `bootx64.efi` on USB ESP) required for Secure Boot |
| **Boot Key** | **Esc** = one-time boot menu (NOT F2 — corrected 2026-09-06, D-425) |
| **Ventoy** | ⚠️ DISQUALIFIED for this machine (D-424) — firmware lacks Microsoft UEFI CA; Ventoy shim rejected pre-MOK |

### Provisioning Project
| Phase | Task | Status |
|-------|------|--------|
| 0 | Deep research on remaining gaps (8 topics) — researcher report `hw-research-gaps-20260906-01` | ✅ Complete |
| 1 | Create bootable USB (Ubuntu 26.04.1 LTS via dd) | 🔄 Ready — awaiting burn |
| 2 | Apply dual-signed shim fix to USB (critical for Secure Boot) | ⬜ Pending |
| 3 | BIOS config (verify Secure Boot enabled, NVMe enabled, boot order) | ⬜ Pending |
| 4 | Partition & LUKS2 encrypt (EFI 512MB + ext4 root) | ⬜ Pending |
| 5 | Install Ubuntu 26.04.1 LTS (manual partitioning) | ⬜ Pending |
| 6 | Post-install: shim-signed fix, MOK enrollment, firmware updates | ⬜ Pending |
| 7 | Omega Engine repo clone & `./scripts/install.sh` | ⬜ Pending |
| 8 | RAM upgrade to 32 GB (2×16 GB DDR5-5200 SO-DIMM kit, when parts arrive) | ⬜ Planned |

### Software Downloads (2026-09-06)

| ISO | Version | Status | Purpose |
|-----|---------|--------|---------|
| Ubuntu 26.04.1 Desktop LTS | 26.04.1 LTS | 🟢 Downloading (~20 min) | **Primary install** for ASUS ExpertBook P1 |
| Ubuntu 24.04.4 Desktop LTS | 24.04.4 LTS | 🟢 Downloading | Omega Engine testing — current LTS baseline |
| Ubuntu 24.04.4 Server LTS | 24.04.4 LTS | 🟢 Downloading | Omega Engine testing — headless server environment |
| Ubuntu 26.04.1 Server LTS | 26.04.1 LTS | 🟢 Downloading | Omega Engine testing — latest LTS server environment |

**Planned testing matrix** (post-migration, when PR #1 settles):

| ISO | Omega Engine Use Case |
|-----|----------------------|
| 26.04.1 Desktop | Primary workstation, local inference, GUI development |
| 24.04.4 Desktop | Regression testing — verify Omega Engine on stable LTS |
| 24.04.4 Server | Headless server testing — benchmarks, API serving, CI runner |
| 26.04.1 Server | Latest LTS server — production-like testing, performance baselines |

**Note**: All ISOs saved locally on HP laptop for USB creation. Will need to transfer to ASUS ExpertBook P1 via USB or network.

### Reference Guide
**Guide File**: `../ASUS-ExpertBook-P1-boot-drive--and-NVMe-guide.md`
- Contains: BIOS settings, partition scheme, encryption commands, post-install checklist, Omega Engine specific setup

### Omega Engine Relevance
- **Local inference**: 16 GB RAM → 32 GB upgrade enables 7B-13B GGUF models comfortably
- **NVMe speed**: PCIe 4.0 supports fast model loading, sqlite-vec performance
- **Military grade**: Durability for mobile forge work
- **Ports**: Dual USB-C supports external GPU dock (future eGPU for 30B+ models)

### Handoff Context
- **Handoff Packet**: `ho_9b4f7f2405fb`
- **Hivemind Session**: `ses_1b9315fa9b17`
- **Initiated By**: User (Architect/Node 0)
- **Assigned To**: roc_racoon (Sovereign Miner)

---

## 📝 Maintenance Log

| Date | Entry | Notes |
|------|-------|-------|
| 2026-09-06 | Inventory created | Initial entry for ASUS ExpertBook P1 |
| 2026-09-06 | Ubuntu 26.04.1 LTS confirmed available | Corrected from "releases April 2026" — now downloading |
| 2026-09-06 | Software downloads catalog added | 4 ISOs: 26.04.1 Desktop, 24.04.4 Desktop, 24.04.4 Server, 26.04.1 Server |
| 2026-09-06 | **dd methodology VALIDATED (D-423)** | Ubuntu 26.04.1 ISO has separate 5MB embedded ESP (GPT) — writable after dd; shim patch valid. Runbook corrected. |
| 2026-09-06 | **Ventoy DISQUALIFIED (D-424)** | ASUS firmware lacks Microsoft UEFI CA; Ventoy shim rejected pre-MOK. dd+shim is the path. |
| 2026-09-06 | **Boot key corrected (D-425)** | Esc = one-time boot menu; F2 = BIOS setup (was wrong in runbook) |
| 2026-09-06 | **AVX-VNNI confirmed on all cores (D-426)** | Gracemont E-cores support AVX2 + AVX-VNNI 256-bit; no SIGILL risk; no AVX-512 (fused off) |
| 2026-09-06 | **Installer GRUB behavior (D-427)** | ubuntu-desktop-installer hardcodes GRUB + /boot/efi; no skip option |
| 2026-09-06 | **Wi-Fi SKU-dependent** | Intel AX201/AX211 (OOTB) OR Realtek RTL8852BE (rtw89, suspend issues) OR MediaTek MT7920 (mt76) — verify with lspci |
| 2026-09-06 | **DDR5 kit recommendation** | Kingston KVR56S46BS8-16 ×2 or Crucial CT2K16G56C46S5 (2×16GB); DDR5-5600 downclocks to 5200 |
| 2026-09-06 | **2230 NVMe recommendation** | WD SN770M or Corsair MP600 Mini (TLC, sustained writes); P310 for max speed (QLC caveat) |
| 2026-09-06 | **Post-install shim copy NOT needed (D-428)** | Installed GRUB/shim is Canonical-signed, trusted by ASUS firmware. Runbook Phase 3 corrected. |
| 2026-09-06 | **TPM2+LUKS2 auto-unlock via Clevis (D-429)** | systemd-cryptenroll path broken; use Clevis + tss-user hook. PCR 7 volatility warning. |
| 2026-09-06 | **RTL8852BE suspend fix (D-430)** | systemd sleep hook + modprobe.d disable_aspm + NetworkManager powersave=2 |
| 2026-09-06 | **Ventoy dead on ASUS (D-431)** | No reliable path; dd+dualsigned shim only reliable method. |
| 2026-09-06 | **2230 NVMe heatsink mandatory (D-432)** | Copper foil heatsink (3.9mm) required for Slot 2 sustained writes. |
| 2026-09-06 | **DHAL validation schema confirmed (D-433)** | detect_hardware_profile.py covers all required fields for i7-13620H. |

---

## 🔍 Research Sources (2026-09-06)

| Source | Key Data |
|--------|----------|
| [ASUS ExpertBook P1 P1503 Tech Specs](https://www.asus.com/us/laptops/for-work/expertbook/expertbook-p1-p1503/techspec) | DDR5-5200 SO-DIMM, 2 slots, max 64GB; M.2 2280 + 2230 PCIe 4.0; CVA models = DDR5-5200 |
| [ASUS ExpertBook P1 P1503CVA Datasheet](https://dlcdnwebimgs.asus.com/files/media/cfb17ac1-99e5-4b03-9f56-498b61e0abbb/asusexpertbookp1(p1503cva).pdf) | Up to 64GB DDR5; dual SSD (2280 + 2230); Intel Core i7-13700H/i5-13500H/i3-1315U |
| [Kingston Memory Configurator](https://www.kingston.com/en/memory/search/model/110292/asus-expertbook-p1-p1503) | DDR5-5200/5600 SO-DIMM; 2 slots; modules in pairs for dual-channel; M.2 2230 + 2280 |
| [NanoReview ExpertBook P1](https://nanoreview.net/en/laptop/asus-expertbook-b5-flip-oled-11th-gen-intel) | DDR5-5200, 2 slots, max 64GB; PCIe 4.0 x4 NVMe; 2 slots (2280 + 2230) |
| [Leo Gaggl — Ubuntu on ASUS ExpertBook](https://gaggl.com/blogs/2026-02-25-installing-ubuntu-on-asus-expertbook-uefi-issues/) | Dual-signed shim fix for Secure Boot; F2 boot menu accessible without BIOS password |

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ HARDWARE-INVENTORY ⬡ 2026-09-06*
