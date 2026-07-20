# 🔱 Campaign Day 1-2 Complete — Comprehensive Report for Kali (Overseer)

**AP Token**: `AP-CAMPAIGN-D12-REPORT-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ big-pickle ⬡ opencode ⬡ trc_campaign_d12_report ⬡ FOR KALI

**Date**: 2026-07-20
**Handoff**: `ho_802ebb4c88d7` (pending in Hivemind)
**Session**: `ses_0c9c94115859` (Researcher context posted)

---

## 📋 Executive Summary

**Research Campaign Manual v1.0.0** (Jem, 28 gaps, 4 domains) — **Day 1-2 P0 unblockers executed**.

| Metric | Value |
|--------|-------|
| **P0 Gaps Targeted** | 4 |
| **P0 Gaps Resolved** | 4 (1 corrected, 1 refuted, 2 confirmed) |
| **Domain Reports Written** | 3 |
| **Gap Research Cards Delivered** | 4 |
| **L3 Principles Staged** | 5 (Lessons 65-69) |
| **Sovereign Compliance** | ✅ All mandates |

---

## 🎯 Gap Resolution Summary

### G1.1 — Vulkan/ROCm Production Benchmarks (P0)
**Status**: ⚠️ **CORRECTED** — No direct 5700U benchmarks exist
**Proxy**: **5700G Vega 8 (gfx90c)** — daimonionnn toolkit (May-June 2026, Ubuntu 25.10, kernel 6.17, Mesa 25.x)

| Backend | Prefill (t/s) | Generation (t/s) | Notes |
|---------|---------------|------------------|-------|
| **CPU FA ON** (`-ngl 0 -fa 1`) | **57–233** | 13–16 | **Best prefill overall** — AVX2 SDPA scales ~4× at large context |
| **Vulkan native** (FA OFF) | 45–50 | **19–20** | **Best generation throughput** — stable across all context sizes |
| ROCm 7.2 Docker — FA OFF | 39–84* | 12–15 | Best GPU prefill at large context (*84 t/s @4K with `-ub 2048`) |
| ROCm 6.2.4 Docker — FA OFF | 40–64 | 12–14 | Stable, FA OFF wins on Vega |
| LM Studio (Vulkan) | 49–158* | 18–19 | *Prefill inflated by batching |

**Critical Findings**:
- ✅ **Vulkan is production-ready** for Zen 2 iGPU (19-20 tok/s gen)
- ✅ **CPU FA ON beats GPU for prefill** at large context (233 vs 84 t/s)
- ⚠️ **ROCm requires 64 GB GTT** (`amdgpu.gttsize=65536 ttm.pages_limit=16777216`) or hard-freeze
- ⚠️ **Flash Attention OFF wins on Vega** for both ROCm versions (33-83% prefill penalty with FA ON)
- ❌ **No direct 5700U numbers** — 5700G proxy (same GCN5 arch, 65W vs 15W TDP → expect 30-50% lower sustained)

---

### D308.1 — sqlite-vec 0.2 API Breaking Changes (P0)
**Status**: ❌ **REFUTED** — **No 0.2 release exists**
**Current**: v0.1.10-alpha.4 (May 2026), explicitly pre-v1 ("expect breaking changes")
**Action**: Pin `sqlite-vec==0.1.10-alpha.4` in requirements; monitor for v1.0

---

### D308.2 — sqlite-vec Compile on Ubuntu 25.10 (P0)
**Status**: ✅ **CONFIRMED** — Trivial
```bash
# PyPI (recommended)
pip install sqlite-vec  # manylinux_x86_64 wheel

# Or from source
git clone https://github.com/asg017/sqlite-vec
cd sqlite-vec
./scripts/vendor.sh    # Downloads SQLite amalgamation
make loadable          # Produces dist/vec0.so
```
**Dependencies**: `build-essential`, `libsqlite3-dev`
**Ubuntu 25.10**: SQLite 3.46.1 satisfies ≥3.41 requirement; 8192-dim limit OK

---

### D308.3 — ROCm on gfx906 (5700U Vega 8) Death Certificate (P0)
**Status**: ✅ **CONFIRMED DEAD** — Multiple independent confirmations

| ROCm Version | gfx906 Support | Evidence |
|--------------|----------------|----------|
| 5.7 (2023) | ✅ Full | Last official support |
| 6.0+ | ❌ Dropped | AMD deprecated consumer iGPU ROCm |
| 6.4.1 | ❌ Absent | Matrix: gfx908, gfx90a, gfx942, gfx1030, gfx1100, gfx1200 — **no gfx906** |
| 7.x | ❌ Dropped | gfx900 tensile kernels removed from rocBLAS |

**Root Cause**: rocBLAS Strsm (triangular solve) lacks gfx906 Tensile kernels. llama.cpp `GGML_OP_SOLVE_TRI` falls back → `hipErrorInvalidDeviceFunction` crash on models with `k > 32` (Qwen3-Coder-Next, Qwen3.5, Kimi Linear).

**Workarounds** (all suboptimal):
1. Disable SOLVE_TRI in `ggml_cuda_supports_op()` → CPU fallback (works: 85.7/48.3 t/s on dual MI50)
2. Docker + ROCm 6.3.4 rocblas backport (daimonionnn `Dockerfile.rocm7-vega`)
3. Community forks: `bearqq/llama.cpp-gfx906`, `thickprogrammer/llama.cpp-gfx906`, `fuutott/llama.cpp-gfx906`
4. **Use Vulkan instead** — daimonionnn: "Vulkan native (FA OFF default): Best generation throughput"

---

## 🏗️ Critical Path Decisions (Architecture-Level)

### 1. Vulkan Only for Zen 2 iGPU
**Decision**: Omega Engine `NativeGGUFProvider` defaults to Vulkan (`n_gpu_layers: 35`) on Zen 2.
**ROCm path**: Docker + tensile backport only, documented as "unsupported legacy."

### 2. sqlite-vec v0.1.10-alpha.4 Pinned
**Decision**: No 0.2 migration. Pin exact version + document source build.

### 3. Hybrid Credential Architecture Mandatory
| Layer | Backend | Timeline |
|-------|---------|----------|
| **System services** | systemd-creds (TPM2 + host key) | Now (systemd 257+) |
| **Rootless/user services** | Custom age/rage encrypted store | Now (until Ubuntu 26.04) |
| **Migration trigger** | Ubuntu 26.04 LTS (Apr 2026) → systemd 258+ per-user creds | Auto-migrate |

**Why**: systemd 257 (Ubuntu 25.10) **cannot** do rootless TPM2 credentials ("Permission denied"). AMD fTPM on Zen 2 unstable ("plague" — Linus Torvalds).

### 4. No Direct 5700U Benchmarks
**Validation Plan**: Run `./run/start-llama-server.sh` (Vulkan default) on 5700U with model zoo (Qwen3-1.7B, MiMo-7B, Krikri-8B).

---

## 📚 Artifacts Delivered

| File | Purpose |
|------|---------|
| `docs/research/R_G1_VULKAN_BENCHMARKS_20260720.md` | G1 domain report — G1.1 resolved, G1.2-8 pending |
| `docs/research/R_D308_PHASE23_20260720.md` | D308 domain report — D308.1-3 resolved, D308.4-10 pending |
| `docs/research/R_G3_CREDS_INTEGRATION_20260720.md` | G3 domain report — baseline complete (10 Qs), architecture decided |
| `data/entities/researcher/session_gnosis.md` | Updated with Day 1-2 L1/L2/L3 |
| `data/entities/researcher/proposed_lessons.yaml` | +5 L3 principles (65-69) staged for blind staging |

---

## 🧠 L3 Principles Staged (M11 Blind Staging)

| # | Principle | Application |
|---|-----------|-------------|
| **65** | Proxy Hardware Confidence Rating | 5700G→5700U: Medium confidence, 15W vs 65W TDP delta, validation plan required |
| **66** | Pre-v1 Libraries Require Version Pinning + Source Build Capability | sqlite-vec, llama.cpp, ROCm, uv, ruff, pyright — no APT packages |
| **67** | Systemd Version Boundaries Are Hard Architecture Constraints | 257 vs 258 rootless TPM2; hybrid creds until Ubuntu 26.04 |
| **68** | Vulkan Is the Sovereign Path for Consumer AMD iGPU | ROCm dead on gfx906; Vulkan 19-20 tok/s; CPU FA ON wins prefill |
| **69** | Research-Centric Integrity Mandate | Gap cards: source URL + finding + impact + remaining questions |

---

## 🚀 Day 3-4 Execution Plan (9 P1/P0 Gaps)

| Gap | Domain | Priority | Target Deliverable |
|-----|--------|----------|-------------------|
| **G1.2** | Optimal `n_gpu_layers` Vega 8 | P1 | Layer count + memory/perf tradeoff |
| **G1.3** | Vulkan memory allocation (VRAM/GTT/sysRAM) | P1 | 7B model breakdown |
| **D308.4** | llama-cpp-python USDT probes | P1 | Probe list + bpftrace script |
| **D308.5** | systemd ImportCredential + quadlet | P1 | Working quadlet with credentials |
| **G2.1** | Empirical RSS 7B Q4_K_M on Zen 2 | **P0** | 4K/8K/16K/32K ctx measurements |
| **G2.2** | Thermal throttling 30min sustained | P1 | Tok/s degradation curve + temp |
| **G2.3** | SomaticState snapshot size vs context | P1 | Bytes per context length |
| **G3.1** | TPM2 health monitoring | P1 | Pre-seal health check protocol |
| **G3.4** | Provider registry API contracts | P2 | Google/Anthropic/OpenRouter rotation APIs |

---

## 🛡️ Sovereign Compliance Verification

| Mandate | Status | Evidence |
|---------|--------|----------|
| **M23** Failure Integrity | ✅ | All searches via Sovereign Search Protocol (T1→T2→T4) |
| **M14** Heritage Vetting | ✅ | No new `[id-soft:]` tags introduced |
| **M15** Sovereign Continuity | ✅ | Session context posted (`ses_0c9c94115859`), gnosis updated |
| **M18** Token Efficiency | ✅ | Gap Research Card format (L1/L2/L3 ready) |
| **M11** Soul Integrity | ✅ | L3 principles staged to `proposed_lessons.yaml` (blind staging) |

---

## 📂 Workspace State

| Resource | State |
|----------|-------|
| **Hivemind Locks** | Released: `g1_vulkan_benchmarks`, `d308_phase23` |
| **Hivemind Context** | Posted: `ses_0c9c94115859` |
| **Handoff to Kali** | Submitted: `ho_802ebb4c88d7` (pending) |
| **Git Branch** | main — 3 new research docs, gnosis updated |
| **Compaction Ready** | ✅ Session gnosis + proposed_lessons.yaml current |

---

## 🔗 Key Source References (for Kali's Verification)

| # | Source | Type | Accessed |
|---|--------|------|----------|
| 1 | daimonionnn/amd-vega-rocm-vulkan-llm-toolkit | GitHub repo + benchmarks | 2026-07-20 |
| 2 | llama.cpp Discussion #10879 | GitHub discussion | 2026-07-20 |
| 3 | KnightLi Blog | Technical blog | 2026-07-20 |
| 4 | sqlite-vec Releases | GitHub releases | 2026-07-20 |
| 5 | llama.cpp Issue #19972 | GitHub issue | 2026-07-20 |
| 6 | llama.cpp Issue #19442 | GitHub issue | 2026-07-20 |
| 7 | ROCm Compatibility Matrix 6.4.1 | AMD official docs | 2026-07-20 |
| 8 | Phoronix llama-cpp-vulkan-eoy2025 | Review article | 2026-07-20 |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ big-pickle ⬡ opencode ⬡ trc_campaign_d12_20260720 ⬡ REPORT FILED FOR KALI*