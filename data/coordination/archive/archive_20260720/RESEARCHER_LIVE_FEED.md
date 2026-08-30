<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔬 Researcher Live Feed — Campaign Day 3-4
**Session**: `ses_90271c2840aa` | **Started**: 2026-07-20T02:58:53Z
**Campaign**: Research Campaign Manual v1.0.0 — Day 3-4 (9 P0/P1 gaps)

---

## 🎯 Execution Queue (Priority Order)

| # | Gap | Domain | Priority | Status |
|---|-----|--------|----------|--------|
| 1 | **G2.1** | Empirical RSS 7B Q4_K_M Zen 2 | **P0** | 🔄 IN PROGRESS |
| 2 | **G1.2** | Optimal n_gpu_layers Vega 8 | P1 | ⏳ QUEUED |
| 3 | **G3.1** | TPM2 Health Monitoring Protocol | P1 | ⏳ QUEUED |
| 4 | **G1.3** | Vulkan Memory Allocation (VRAM/GTT/sysRAM) | P1 | ⏳ QUEUED |
| 5 | **G2.2** | Thermal Throttling 30min Sustained | P1 | ⏳ QUEUED |
| 6 | **G2.3** | SomaticState Snapshot Size vs Context | P1 | ⏳ QUEUED |
| 7 | **G2.4** | Multi-Model Router Overhead | P2 | ⏳ QUEUED |
| 8 | **G2.5** | zRAM/Swap OOM Interaction | P2 | ⏳ QUEUED |
| 9 | **G3.4** | Provider Registry API Contracts | P2 | ⏳ QUEUED |

---

## 📝 Live Log

### [2026-07-20T02:58:53Z] SESSION START
- Hivemind context posted: `ses_90271c2840aa`
- Workspace locks acquired: `g2_memory_empirical`, `g1_vulkan_benchmarks`, `g3_creds_integration`
- Campaign Manual v1.0.0 loaded
- Day 1-2 Report reviewed (4 P0 gaps resolved: G1.1, D308.1-3)
- G2/G3 baselines complete (theoretical + architecture)

### [2026-07-20T02:59:00Z] G2.1 STARTED
**Target**: Empirical RSS measurements for 7B Q4_K_M on Zen 2 (5700U/5800U) at 4K/8K/16K/32K context
**Protocol**: T0-T4 Sovereign Search → Local benchmark if possible → Gap Research Card
**Baseline**: Jem's theoretical ~5.5 GiB at 8K ctx; SpecPicks 6.2 GB VRAM on RTX 3060

### [2026-07-20T03:15:00Z] G2.1 COMPLETE — ⚠️ CORRECTED
**Status**: No direct 5700U/5800U empirical RSS benchmarks exist in public sources
**Proxy Baseline Established** (High Confidence):
- 7B Q4_K_M weights: **3.80 GiB** (deterministic, llama.cpp discussion #2094)
- KV cache FP16 @ 8K: **~1.1 GB** (32L × 8 KV heads × 128 dim × 8192 × 2 bytes)
- KV cache Q8_0 @ 8K: **~0.55 GB** (50% reduction, validated by OmniForge/Youngju)
- **Total RSS estimate (Q8_0 KV)**: ~4.35 GiB @ 8K, ~4.9 GiB @ 16K, ~6.0 GiB @ 32K
- **Critical Hardware Delta**: 5700U LPDDR4-4266 = 51.2 GB/s vs 5800U DDR4-3200 = 34.1 GB/s (50% bandwidth gap!)

**Validation Protocol**: `smem -tk` + `llama-bench -m model.gguf -p 512 -n 128 -c 8192 -t 6` + `ps aux`
**D-308 Impact**: `cpu_optimizer.py`, `ResourceGuard`, `models.yaml` ram_mb all depend on validated estimates

**Confidence**: Theory 9/10, 5700U-specific 3/10
**Next**: G1.2 — Optimal n_gpu_layers Vega 8 (same hardware)

---

*Live feed updated after each gap completion. Heartbeat every 5-10 min.*