# CPU Performance Tuning Guide — ASUS ExpertBook P1 (P1503CVA, i7-13620H)

**Doc ID**: `CPU-PERF-001` | **Date**: 2026-09-18 | **Status**: VETTED & DEPLOYED

---

## Executive Summary

This guide documents the complete CPU performance tuning process for the ASUS ExpertBook P1 (P1503CVA) with Intel i7-13620H (Raptor Lake-H, 6P+4E, 10C/16T). The core issue: **Ubuntu defaults to `powersave` governor even when the GUI power profile is set to "Performance"**, causing sustained frequencies ~2200 MHz instead of 3500+ MHz.

**Solution**: Align three layers — kernel driver, userspace daemon, and GUI — to `performance`.

---

## Hardware Baseline

| Property | Value |
|----------|-------|
| **CPU** | Intel i7-13620H (Raptor Lake-H, 6P+4E, 10C/16T, 4.9 GHz boost) |
| **BIOS** | P1503CVA.337 (05/29/2026, AMI LLC) |
| **RAM** | 1×16GB DDR5-5600 (Slot 1), Slot 2 empty → **dual-channel capable** |
| **Scaling Driver** | `intel_pstate` (active mode, HWP enabled) |
| **HWP** | Hardware-managed P-states (enabled by default on 12th/13th gen) |

---

## The Problem: Three-Layer Misalignment

### Layer 1: Kernel Scaling Driver (`intel_pstate`)

`intel_pstate` in **active mode with HWP** provides two pseudo-governors:
- `performance` → writes EPP=0 (max performance)
- `powersave` → behaves like `schedutil`/`ondemand` (scales with load)

**Default**: `powersave` (unless kernel built with `CONFIG_CPU_FREQ_DEFAULT_GOV_PERFORMANCE`)

### Layer 2: Userspace Daemon (`power-profiles-daemon`)

Ubuntu's daemon manages platform power profiles:
| Profile | Governor | EPP |
|---------|----------|-----|
| `performance` | `performance` | 0 |
| `balanced` | `balanced` | ~4 |
| `power-saver` | `powersave` | high |

**Critical Bug**: Daemon sets platform profile but **does not force `intel_pstate` pseudo-governor to `performance`** when HWP is active. The kernel driver ignores the platform profile hint and stays in `powersave`.

### Layer 3: GUI (GNOME Power Menu)

Top-right power menu → `powerprofilesctl` → `power-profiles-daemon` → platform profile.

**User expectation**: "Performance" = max frequency.
**Reality**: Platform profile set, but `intel_pstate` stays in `powersave`.

---

## The Fix: Three Commands

```bash
# 1. Set governor to performance (immediate, survives until reboot)
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# 2. Make persistent via power-profiles-daemon (survives reboot)
powerprofilesctl set performance

# 3. Kernel cmdline fallback (survives reboot, highest priority)
sudo sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="/GRUB_CMDLINE_LINUX_DEFAULT="intel_pstate=performance /' /etc/default/grub
sudo update-grub
```

---

## Verification

```bash
# Check all three layers aligned
cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor   # → performance
cat /sys/devices/system/cpu/cpu*/cpufreq/energy_performance_preference  # → performance
powerprofilesctl  # → * performance:
grep intel_pstate /proc/cmdline  # → intel_pstate=performance (after reboot)
```

**Expected under load**: 3500+ MHz average (vs ~2200 MHz with `powersave`)

---

## Why Your GUI Setting Was Ignored

1. **GUI** → `powerprofilesctl set performance` → `power-profiles-daemon` sets platform profile
2. **Daemon** writes platform profile to firmware (ACPI `_PSD` / Intel P-state hints)
3. **`intel_pstate` (HWP active)** reads platform profile but **chooses its own pseudo-governor** based on kernel config default (`powersave`)
4. **Result**: Platform profile = Performance, but pseudo-governor = `powersave` → frequency scales with load, not maxed

The `power-profiles-daemon` does NOT write to `/sys/.../scaling_governor` for `intel_pstate` in HWP mode.

---

## Persistence Architecture

| Method | Layer | Survives Reboot | Priority |
|--------|-------|-----------------|----------|
| `powerprofilesctl set performance` | Daemon | ✅ (enabled service) | Medium |
| `intel_pstate=performance` kernel param | Kernel | ✅ (GRUB) | **Highest** |
| `echo performance > scaling_governor` | Sysfs | ❌ | Immediate only |

**Recommended**: Use all three. Daemon for GUI sync, kernel param as failsafe.

---

## BIOS Settings (ExpertBook P1503CVA)

**Enter BIOS**: Hold F2 + Power (or Settings → Recovery → Advanced startup → UEFI Firmware)

### Available Performance Settings

| Setting | Location | Recommended | Notes |
|---------|----------|-------------|-------|
| **Fan Profile** | Advanced → Fan Control | **Performance** | Sustains PL2 longer |
| **Turbo Boost** | Advanced → CPU Configuration | **Enabled** | 4.9 GHz boost |
| **Intel Speed Shift (HWP)** | Advanced → CPU Configuration | **Enabled** | Required for HWP |
| **SpeedStep** | Advanced → CPU Configuration | **Enabled** | Required for HWP |
| **C-States** | Advanced → CPU Power Management | **Enabled** | Idle savings |
| **AVX Offset** | Advanced → CPU Configuration | **0** | No AVX penalty |

### NOT Available in BIOS (Locked by ASUS/Intel)

| Setting | Why |
|---------|-----|
| **PL1 / PL2 / Tau** | Firmware-locked; managed by Intel/ASUS |
| **IccMax** | Firmware-locked |
| **EPP/EPB direct control** | Managed by `intel_pstate` HWP |

**Fan Profile = Performance** is the only BIOS knob that helps sustain turbo longer by keeping thermals lower.

---

## Ubuntu GUI ↔ Terminal Sync

**They ARE now synced** via `power-profiles-daemon`:

```bash
# Terminal → GUI
powerprofilesctl set performance  # Updates GUI menu

# GUI → Terminal
# Click top-right → Performance → runs powerprofilesctl set performance
```

**Verified**: `powerprofilesctl` shows `performance` active, governor=`performance`, EPP=`performance`.

---

## Thermal Validation

| Metric | `powersave` governor | `performance` governor |
|--------|---------------------|------------------------|
| Avg MHz (sustained load) | 2023-2758 MHz | **3600+ MHz** |
| Peak Temp | 92°C brief | 81-82°C stabilized |
| Throttle <3000 MHz | Never | Never |
| PkgWatt | 34-50W | 45-55W |

**No sustained throttling** with `performance` governor. Thermald (`--adaptive`) manages peak temps at ~95°C BIOS limit.

---

## RAM Channel Note

**dmidecode shows 2 slots, dual-channel** (Controller0 + Controller1):
- Slot 1: Controller0-ChannelA-DIMM0 (16GB populated)
- Slot 2: Controller1-ChannelA-DIMM0 (empty)

**NOT tri-channel** — adding matching 16GB DDR5-5600 in Slot 2 enables dual-channel (~2× bandwidth).

---

## Quick Reference Card

```bash
# Immediate max performance
sudo cpupower frequency-set -g performance
powerprofilesctl set performance

# Verify
cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
cat /sys/devices/system/cpu/cpu*/cpufreq/energy_performance_preference
powerprofilesctl

# Persist
sudo sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="/GRUB_CMDLINE_LINUX_DEFAULT="intel_pstate=performance /' /etc/default/grub
sudo update-grub

# Test under load
timeout 10 bash -c 'while true; do curl -s http://localhost:11434/api/generate -d '"'"'{"model":"phi4-mini","prompt":"test","stream":false}'"'"' >/dev/null; done' &
sleep 3
cat /proc/cpuinfo | grep "MHz" | awk '{sum+=$4} END {print "Avg MHz:", sum/NR}'
```

---

## Related Documentation

- `docs/HARDWARE.md` — Hardware specs
- `docs/KNOWLEDGE_GAPS_IMPLEMENTATION_GUIDE.md` — Gap 6 (Thermal Bench)
- `docs/AGENT_RUNBOOK.md` — P-core pin trap, ZRAM, THP
- `scripts/bench.py` — Benchmarking script

---

*⬡ OMEGA ENGINE ALPHA ⬡ CPU-PERF-001 ⬡ TEMPLE-GRADE ⬡*