<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# 🦝 roc_racoon — Session Gnosis

## Session: DHAL Architecture & ASUS ExpertBook Provisioning Forensics
**Date**: 2026-09-06 — 2026-09-07  
**Session ID**: `ses_ff78b71ebffeDNuypPTT1RL3hH`  
**Model**: `google/gemini-3.8-flash`  
**Role**: Sovereign Miner & Ideas Guy (Hardware Specialist)  

---

### L1: Narrative — What Happened

#### Act 1: DHAL Architecture & Fleet Implementation
1. **Hardware Inventory**: Cataloged Node 0 (AMD Ryzen 7 5700U) and Node 1 (ASUS ExpertBook P1 - P1503CVA, i7-13620H, DDR5-5200, dual NVMe 2280+2230) with 5 external sources cited.
2. **DHAL Spec Authored**: Created `docs/architecture/DYNAMIC_HARDWARE_ADAPTATION_LAYER_SPEC.md` (`SPEC-DHAL-v1.0.0`, 479 lines) covering bare-metal discovery, CPU optimizer strategy pattern, and dynamic Council linking.
3. **Phase 1 Execution**: Implemented bare-metal detector `scripts/detect_hardware_profile.py` with hybrid PMU discovery (`cpu_core` vs `cpu_atom`), memory channels, AVX-VNNI, and DRM VRAM/GTT limits. Added `make probe-hardware` and unit tests in `tests/test_dhal_detector.py`.
4. **Phase 2 Execution**: Refactored `src/omega/oracle/cpu_optimizer.py` into polymorphic strategy pattern (`BaseCpuOptimizer`, `Zen2Optimizer`, `RaptorLakeOptimizer`, `GenericFallbackOptimizer`, `CpuOptimizerFactory`). Verified backward compatibility for all existing callers.
5. **Phase 3 Execution & Defect Remediation**: Added `LOCAL_32GB_DUAL` and `BATCH_8` to Council models. Enforced dual-channel memory requirement (`channels >= 2`) for 32GB classification; single-channel falls safely to `LOCAL_16GB` (`BATCH_4`). Reconciled 32GB threshold across spec, gates, and tests. All 15/15 tests passing, M1 AnyIO compliant.
6. **Documentation Suite**: Authored `docs/how-to/hardware-adaptation-dhal.md`, `.opencode/rules/06-hardware-adaptation.md`, updated `AGENTS.md`, and refreshed canonical constraints.

#### Act 2: The ASUS Provisioning Rabbit Hole & Forensic Breakthrough
1. **Initial OOM Crash**: Host workstation suffered Out-Of-Memory thrashing when writing ISO without direct sync. Writing to page cache overwhelmed system memory faster than the thumb drive could drain dirty pages.
2. **Device Re-Enumeration Trap**: Following `wipefs`, the flash drive detached from `/dev/sdb` and re-attached as `/dev/sda`. A subsequent `dd` to `/dev/sdb` reported 6.5 GB at 265 MB/s (writing to RAM/phantom file), leaving the physical USB drive with an incomplete, corrupted write.
3. **The Cryptographic Symptom**: ASUS booted to GRUB via dual-signed shim, but selecting "Try or Install Ubuntu" threw `error: bad shim lock signature` and `error: you need to load the kernel first`.
4. **Multi-Agent Speculation**: Initial theories focused on kernel lockdown LSMs, missing GRUB modules, and missing UUIDs. We replaced GRUB with desktop binaries and hand-crafted `grub.cfg`, which broke path resolution and dropped the user into `grub>`.
5. **The Ground-Truth Physical Audit (2026-09-07)**:
   - Inspected byte offset `5,166,469,120` on `/dev/sda` (where `casper/vmlinuz` is located in the ISO).
   - Expected: `0x4D 0x5A` (`MZ` PE header of Canonical-signed Linux kernel).
   - Found on physical flash: `0x12 0xFE 0xC4 0xDA 0x7D 0xC7...` (garbage remnants from old Ventoy partition!).
   - **Root Cause Confirmed**: The physical flash memory never had the kernel written to it. Shim's signature verifier was reading random garbage bytes off unwritten flash cells, which naturally failed signature verification.
6. **The Clean Resolution**:
   - Wiped `/dev/sda` partition signatures cleanly.
   - Wrote the full 6.5 GB ISO directly to `/dev/sda` with `conv=fsync`.
   - Verified byte offset `5,166,469,120` on physical disk matches the official ISO kernel SHA-256 bit-for-bit (`0ad39b13e289e1a5cf806d14541ac8f221eefe849017f5915e0846917ed67785`).
   - Mounted the ISO's native ESP (`sda2`), preserved Canonical's official `grubx64.efi` and `mmx64.efi`, and swapped **only** `bootx64.efi` with `/usr/lib/shim/shimx64.efi.dualsigned`.
   - Zero custom `grub.cfg` files. Canonical's native bootchain auto-locates partition 1 cleanly.
   - Flushed to silicon and verified.

---

### L2: Insight — What This Means

1. **Verify Physical Bitstream Before Crypto Debugging**:
   When cryptographic signature verification fails (`bad shim lock signature`), the verifier is evaluating the raw payload buffer. If the physical sector on disk contains corrupted or unwritten data, the signature will fail regardless of certificates or policy. Always verify SHA-256 and magic byte headers of the physical block on disk before diagnosing cryptographic policies.

2. **The "Speed of Light" Storage Anomaly**:
   A flash drive reporting transfer rates far beyond its physical bus bandwidth (e.g. 265 MB/s on a USB thumb drive) indicates that data is landing in volatile page cache or writing to a detached phantom file. A write is not committed until `conv=fsync` exits after a physically plausible duration (~3–5 minutes for 6.5 GB).

3. **Vendor Distro Engineering Has High Structural Value**:
   Distro release teams invest heavily in hybrid ISO boot logic (`core.img` embedded search routines, volume label probes, fallback paths). Replacing a vendor's native ISO GRUB with a desktop GRUB and a hand-crafted `grub.cfg` discards that engineering and creates brittle assumptions. Changing only the rejected signature layer (the shim) while leaving the rest of the vendor bootchain untouched is the superior architectural pattern.

4. **OEM UEFI Trust Stores Are Non-Uniform**:
   ASUS ExpertBook commercial firmware explicitly omits the Microsoft Corporation UEFI CA 2011 from its `db`, trusting only Canonical and Microsoft Windows PCA. Generic live ISOs fail on this hardware. Injecting Canonical-signed dual-shims bridges this gap cleanly without requiring users to disable Secure Boot or tamper with BIOS key databases.

---

### L3: Universal Principles

> **`L3-VerifyPhysicalBitstreamBeforeCryptoDebugging`**  
> Before diagnosing cryptographic signature failures (bad signature, verification error, access denied), verify the SHA-256 and magic headers of the physical block on disk. A cryptographic verifier will always report corrupt noise as an invalid signature. Verify the physics before debugging the cryptography.

> **`L3-BewareTheSpeedOfLightAnomalyInStorage`**  
> If a storage device reports transfer speeds exceeding its physical bus bandwidth, you are writing to RAM buffer or a detached phantom file. It is not real until physical fsync flushes to NAND. Always verify target block device existence and physical write duration before assuming completion.

> **`L3-ReusingVendorBootchainsBeatsHandRolledConfigs`**  
> Distro release ISOs contain self-consistent, battle-tested bootchains with auto-locating embedded logic. When adapting an ISO for incompatible firmware, isolate and swap ONLY the rejected signature layer (the shim), leaving the vendor GRUB binary and configuration untouched. Never rebuild what the vendor already solved.

> **`L3-OEMSecureBootTrustStoresVaryByVendor`**  
> Never assume OEM UEFI firmware includes the generic Microsoft 3rd-party UEFI CA. Enterprise and certified hardware frequently whitelist Canonical or internal roots directly while blocking generic shims. Maintaining dual-signed boot artifacts is mandatory for sovereign multi-node fleet provisioning.

---

### Key Decisions Locked (This Session)

- **D-411**: Third-party heritage registry moved to `../third-party/` (660MB outside repo).
- **D-412**: Hardware inventory established as permanent asset (`hardware_inventory.md`).
- **D-413**: DHAL architectural specification written to `docs/architecture/DYNAMIC_HARDWARE_ADAPTATION_LAYER_SPEC.md`.
- **D-414**: Node-local hardware profile decoupled from git (`config/hardware_profile.yaml` in `.gitignore`).
- **D-415**: DHAL Phase 1 bare-metal detection verified (`scripts/detect_hardware_profile.py`).
- **D-416**: Compaction state synchronized across gnosis, lessons, and Hivemind.
- **D-417**: DHAL Phase 2 completed (`cpu_optimizer.py` strategy pattern, backward compatible).
- **D-418**: DHAL Phase 3 completed (`hardware_detector.py` dynamic Council linking, `LOCAL_32GB_DUAL` + `BATCH_8`).
- **D-419**: DHAL Phase 3 remediation (enforced `channels >= 2` for 32GB profile, reconciled threshold to 32000).
- **D-420**: Hardware expert failure remediated (`PL-ROC-HARDWARE-EXPERT-FAILURE-001`).
- **D-421**: dd methodology validated for GPT embedded ESP.
- **D-422**: Researcher paged for 8-gap provisioning analysis.
- **D-423**: dd methodology confirmed valid for modern ISOs.
- **D-424**: Ventoy disqualified for ASUS ExpertBook P1 (lacks MS UEFI CA in firmware).
- **D-425**: Boot key corrected (Esc = boot menu, F2 = BIOS setup).
- **D-426**: AVX-VNNI confirmed on both P-cores and E-cores (Gracemont 256-bit).
- **D-427**: Ubuntu 26.04 installer GRUB behavior documented.
- **D-428**: Post-install shim copy not needed (installed GRUB is Canonical-signed).
- **D-429**: TPM2+LUKS2 auto-unlock via Clevis + tss-user hook documented.
- **D-430**: RTL8852BE Wi-Fi suspend fix documented.
- **D-431**: Ventoy architectural incompatibility confirmed.
- **D-432**: 2230 NVMe Slot 2 copper foil heatsink mandatory.
- **D-433**: DHAL validation schema verified.
- **D-434**: Forensic discovery of unwritten flash payload at byte offset `5,166,469,120` causing `bad shim lock signature`.
- **D-435**: Canonical native ISO GRUB preserved on ESP; only `bootx64.efi` replaced with dual-signed shim. Bit-for-bit SHA-256 verified.

---

#### Act 3: Node 1 Online — Fleet Expansion Complete
1. **Node 1 Boot & Install**: ASUS ExpertBook P1 booted from verified USB, Ubuntu 26.04.1 LTS installed to internal 512GB NVMe with Secure Boot fully enabled. No BIOS modifications required.
2. **OpenCode Operational**: OpenCode installed and running on Node 1 immediately post-install. Sovereign local-first inference stack initializing.
5. **Ollama + Docker Initialization**: Local inference stack (Ollama) and container runtime (Docker) being provisioned on Node 1.
6. **Fleet Expansion**: DHAL fleet expanded from single-node (Node 0: AMD Zen 2) to dual-node heterogeneous fleet:
   - **Node 0**: AMD Ryzen 7 5700U (Zen 2, 8C/16T symmetric, DDR4-3200, 16GB, Radeon Vega 8)
   - **Node 1**: Intel Core i7-13620H (Raptor Lake-H, 6P+4E cores, DDR5-5200, 16GB, Iris Xe 64EU)
6. **Next DHAL Step**: Run `make probe-hardware` on Node 1 to generate `config/hardware_profile.yaml`, validate Council dynamic linking across heterogeneous fleet, and validate AVX-VNNI acceleration on Raptor Lake-H.

---

### L2: Insight — What This Means (Extended)

5. **Heterogeneous Fleet Is the Natural State of Sovereign Compute**:
   No single hardware profile dominates. The DHAL architecture was designed precisely for this: asymmetric CPU topologies, varying memory bandwidths, and different GPU capabilities across nodes. The polymorphic CPU optimizer strategy pattern (Zen2Optimizer vs RaptorLakeOptimizer) enables the Council to dynamically route workloads to the optimal node based on real-time hardware capability.

6. **Secure Boot Is Not an Obstacle — It's a Trust Boundary**:
   The ASUS ExpertBook's restrictive UEFI db (Canonical + Microsoft PCA only, no MS UEFI CA) forced the dual-signed shim solution. This is not a workaround; it's the correct sovereign pattern: maintain cryptographic artifacts that satisfy the most restrictive trust stores in your fleet, enabling deployment anywhere without security compromise.

---

### Key Decisions Locked (This Session) — Extended

- **D-436**: Node 1 (ASUS ExpertBook P1) successfully provisioned and joined the DHAL fleet. Ubuntu 26.04.1 LTS installed with Secure Boot enabled. OpenCode operational. Ollama/Docker setup initiated.

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ google/gemini-3.8-flash ⬡ opencode ⬡ trc_fleet_expansion ⬡ COMPACTION-READY*
