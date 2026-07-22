# 🔬 OMEGA ENGINE RESEARCH CAMPAIGN MANUAL
## Comprehensive Strategic Research Program — All Active Knowledge Gaps

**AP Token**: `AP-RESEARCH-CAMPAIGN-MANUAL-v1.0.0`
⬡ OMEGA ⬡ JEM ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_research_campaign ⬡ 2026-07-20

**Purpose**: Single authoritative reference for Researcher executing parallel research across 4 domains, 27 gaps, coordinating with Jem (synthesis) and Kali (oversight) via Hivemind.

---

## 📋 CAMPAIGN OVERVIEW

### Research Domains & Gap Counts

| Domain | Code | Gaps | Priority | Status |
|--------|------|------|----------|--------|
| **Zen 2 Vulkan/ROCm GPU Inference** | `G1` | 8 | P0-P3 | Archaeology complete, benchmarks needed |
| **llama-cpp-python Memory Footprint** | `G2` | 5 | P0-P2 | Theoretical complete, empirical needed |
| **systemd-creds TPM2 + Rootless** | `G3` | 5 | P1-P2 | Foundational complete, integration needed |
| **Ubuntu 25.10 Toolchain (D-308)** | `D308` | 10 | P0-P2 | Phase 0+1 done, Phase 2/3 blocked |

**Total**: 28 gaps across 4 domains

### Campaign Timeline

```
WEEK 1 (This Sprint)
├── Day 1-2: G1 Benchmarks + D308.1-3 (P0 unblockers)
├── Day 3-4: G2 Empirical + D308.4-7 (P1 integration)
├── Day 5:   G3 Integration + D308.8-10 (P2 validation)
└── Day 6-7: Synthesis → Jem → Kali review

WEEK 2 (If needed)
├── Remaining P1/P2 gaps
├── Cross-domain synthesis
└── Campaign closure report
```

---

## 🔍 SOVEREIGN SEARCH PROTOCOL (MANDATORY)

### Tier Escalation (Never Skip)

| Tier | Tool | Scope | When |
|------|------|-------|------|
| **T0** | Local cache (`.firecrawl/`) | Free | ALWAYS FIRST |
| **T1** | `websearch` | Free, built-in | Primary search |
| **T2** | `webfetch` | Free, built-in | Deep extraction |
| **T3** | `searxng_searxng_search` | Free, sovereign | Semantic refinement |
| **T4** | `omega-hub_sovereign_search` | API (Exa) | High-precision seeds |
| **T5** | `firecrawl_firecrawl_scrape` | Credits | Full-page scrape |
| **T6** | `sieve research` | Local-first | Full pipeline |

**Fallback Chain**: T0 → T1 → T2 → T3 → T4 → T5 → T6

### Temporal Mandate
**All queries MUST include "2026" or "latest"**. No 2024/2025 searches.

### Evidence Logging (Per Claim)
```markdown
- **Claim**: [exact text]
- **Source**: [URL + access date]
- **Status**: ✅ CONFIRMED / ⚠️ CORRECTED / ❌ REFUTED / ❓ UNVERIFIABLE
- **Confidence**: High / Medium / Low
- **Impact**: [what changes in critical path]
```

---

## 🤝 HIVEMIND COORDINATION PROTOCOL

### Researcher Responsibilities

1. **Session Start**: `omega-hub_hivemind_post_context` with intent=`research`
2. **Every Gap**: Post progress update (intent=`observation`) when claim verified
3. **Blockers**: Post intent=`blocker` with specific question for Jem/Kali
4. **Session End**: Post intent=`handoff` with summary + next steps
5. **Heartbeat**: Every 30 min via `omega-hub_hivemind_heartbeat`

### Channel & Entity
```json
{
  "channel": "opencode",
  "entity": "researcher",
  "model": "nemotron-3-ultra-free"
}
```

### Coordination Signals

| Signal | From | To | Meaning |
|--------|------|-----|---------|
| `research:gap_complete` | Researcher | Jem | Gap verified, ready for synthesis |
| `research:blocker` | Researcher | Kali | Hard blocker needing architectural decision |
| `synthesis:gap_integrated` | Jem | Researcher | Gap integrated into strategy |
| `campaign:priority_change` | Kali | Researcher | Reprioritize based on new intel |

### Workspace Locks
- Domain `g1_vulkan_benchmarks` — G1 benchmarks
- Domain `g2_memory_empirical` — G2 benchmarks
- Domain `g3_creds_integration` — G3 integration tests
- Domain `d308_phase23` — D-308 Phase 2/3

**Acquire before writing files**: `omega-hub_hivemind_workspace_lock_acquire`

---

## 📁 DELIVERABLE STRUCTURE

### Per-Gap Output
Each gap produces a **Gap Research Card** appended to domain report:

```markdown
## Gap G1.1 — Production Benchmarks on Mesa 25.3+ / llama.cpp b4000+
**Status**: ✅ CONFIRMED / ⚠️ CORRECTED / ❌ REFUTED / ❓ UNVERIFIABLE
**Sources**: [URLs with dates]
**Finding**: [2-3 sentence summary with numbers]
**Impact**: [Critical path change]
**Confidence**: High/Medium/Low
**Next Action**: [if any]
```

### Domain Reports (Updated Incrementally)
| Domain | File | Owner |
|--------|------|-------|
| G1 | `docs/research/R_G1_VULKAN_BENCHMARKS_20260720.md` | Researcher |
| G2 | `docs/research/R_G2_MEMORY_EMPIRICAL_20260720.md` | Researcher |
| G3 | `docs/research/R_G3_CREDS_INTEGRATION_20260720.md` | Researcher |
| D308 | `docs/research/R_D308_PHASE23_20260720.md` | Researcher |

### Campaign Synthesis (Jem)
- `docs/research/R_CAMPAIGN_SYNTHESIS_20260720.md` — Cross-domain integration
- `data/entities/jem/proposed_lessons.yaml` — L3 principles (blind staging)

---

## 🎯 DOMAIN G1: ZEN 2 VULKAN/ROCM GPU INFERENCE

### Context from Archaeology (Roc's Report)
- **Vulkan iGPU Implementation Log** (Jan 2026): 25-55% token gen improvement target, Vega 8, Mesa 25.3+
- **Vulkan Integration Roadmap**: 22% → 90% integration, >20% perf target
- **Native Inference Research**: RADV driver, `-DGGML_VULKAN=ON`, 1.5-2x speedup on Vega 7/8
- **Gap**: All data is 6+ months old. Need current Mesa 25.3+, llama.cpp b4000+ numbers.

### Gaps & Research Queries

| Gap | Priority | Research Queries (T1-T4) | Success Criteria |
|-----|----------|--------------------------|------------------|
| **G1.1** Production benchmarks | **P0** | `llama.cpp Vulkan benchmark 5700U 2026 Mesa 25.3` `llama.cpp b4000 Vulkan tok/s 7B Q4_K_M Vega 8` `GGML_VULKAN performance 2026` | ≥3 independent benchmarks with tok/s, VRAM, thermal |
| **G1.2** Optimal `n_gpu_layers` | **P1** | `llama.cpp n_gpu_layers Vega 8 optimal 2026` `GGML_VULKAN layer offload memory VRAM GTT` `llama.cpp partial GPU offload 5700U` | Specific layer count with memory/perf tradeoff |
| **G1.3** Vulkan memory allocation | **P1** | `RADV Vulkan memory allocation VRAM GTT system RAM shared 2026` `llama.cpp Vulkan memory mapping 5700U` `VK_AMD_memory_overallocation_behavior` | VRAM vs GTT vs sysRAM breakdown for 7B model |
| **G1.4** Thermal throttling sustained | **P1** | `5700U sustained LLM inference thermal 15W TDP 2026` `Vulkan iGPU thermal throttling llama.cpp 30min` `amd_pstate active Vulkan compute thermal` | Tok/s at 0min, 10min, 30min; temp curve |
| **G1.5** llama-cpp-python Vulkan wheel | **P2** | `llama-cpp-python Vulkan wheel abetlen 2026` `pip install llama-cpp-python GGML_VULKAN=ON 2026` `abetlen llama-cpp-python Vulkan availability` | Working install command + version pin |
| **G1.6** Podman Vulkan passthrough | **P2** | `podman rootless Vulkan /dev/dri renderD128 2026` `quadlet DeviceAllow=/dev/dri Vulkan 2026` `podman GPU passthrough iGPU rootless` | Working quadlet snippet with device access |
| **G1.7** Gemma 4 MTP on Vulkan | **P3** | `Gemma 4 MTP speculative decode Vulkan llama.cpp 2026` `llama.cpp MTP drafter Vulkan support 2026` | Feasibility assessment when model available |
| **G1.8** Qwen3/MiMo Vulkan benchmarks | **P3** | `Qwen3 Vulkan llama.cpp benchmark 2026` `MiMo Vulkan inference 2026` | Model zoo coverage assessment |

### Benchmark Protocol (If Running Locally)
```bash
# Standardized test matrix
MODELS=("Llama-3-8B-Q4_K_M" "Qwen2.5-7B-Q4_K_M" "Gemma-2-9B-Q4_K_M")
CTX_SIZES=(4096 8192 16384)
N_GPU_LAYERS=(0 20 28 35 99)  # 99 = all

# Metrics to capture per run:
# - tok/s (prompt processing + token generation)
# - VRAM usage (radeontop)
# - GTT usage
# - System RAM RSS
# - Package temp (sensors)
# - Time to first token
```

---

## 🎯 DOMAIN G2: LLAMA-CPP-PYTHON MEMORY FOOTPRINT (ZEN 2)

### Context from Jem's Research
- **Theoretical formula**: `state_size = n_ctx * n_layer * n_embd * 2` (FP16 KV cache)
- **14Gi RAM ceiling** — absolute hard constraint
- **No empirical Linux/Zen 2 data** — only Apple Silicon / theoretical

### Gaps & Research Queries

| Gap | Priority | Research Queries | Success Criteria |
|-----|----------|------------------|------------------|
| **G2.1** Empirical RSS 7B Q4_K_M | **P0** | `llama.cpp RSS 7B Q4_K_M 8K context Linux 2026` `llama-cpp-python memory usage 5700U 8K 16K 32K` `llama.cpp memory benchmark Zen 2 2026` | RSS measurements for 4K/8K/16K/32K ctx |
| **G2.2** Thermal throttling 30min | **P1** | `llama.cpp sustained inference thermal 5700U 30min 2026` `Zen 2 15W TDP llama.cpp thermal curve` | Tok/s degradation curve + temp over 30min |
| **G2.3** SomaticState snapshot size | **P1** | `llama_copy_state_data size context length 2026` `llama.cpp state serialization memory disk 2026` `M20 SomaticState llama.cpp checkpoint size` | Bytes per context length (4K/8K/16K/32K) |
| **G2.4** Multi-model router overhead | **P2** | `llama-server --models-max memory overhead 2026` `llama.cpp multi-model router RSS 2026` `llama-cpp-python concurrent models memory` | Router + N models vs standalone |
| **G2.5** zRAM/swap OOM interaction | **P2** | `zRAM llama.cpp OOM behavior 2026` `Podman memory limit llama.cpp swap 2026` `M6 Podman Sovereignty memory pressure llama.cpp` | OOM behavior under memory pressure |

### Measurement Protocol
```bash
# For each model + ctx + n_gpu_layers:
# 1. Warm start (model loaded)
# 2. Measure: RSS (ps), VRAM (radeontop), swap (free)
# 3. Run 100 token generation
# 4. Measure peak RSS during generation
# 5. SomaticState: llama_copy_state_data → measure file size
# 6. Thermal: sensors every 30s for 30min sustained
```

---

## 🎯 DOMAIN G3: SYSTEMD-CREDS TPM2 + ROOTLESS INTEGRATION

### Context from Researcher's Report
- **systemd 257 (Ubuntu 25.04/25.10)**: Rootless TPM2 **BROKEN** — "Permission denied"
- **systemd 258+ (Sep 2025)**: Per-user creds via Varlink — **WORKS**
- **AMD fTPM on Zen 2**: **UNSTABLE** — Linus: "plague"
- **Hybrid architecture mandated**: systemd-creds (system) + age/rage (rootless 257) → systemd-creds --user (258+)

### Gaps & Research Queries

| Gap | Priority | Research Queries | Success Criteria |
|-----|----------|------------------|------------------|
| **G3.1** TPM2 health monitoring | **P1** | `systemd-analyze has-tpm2 production monitoring 2026` `TPM2 health check before credential sealing 2026` `systemd-creds TPM2 failure detection journal` | Pre-seal health check protocol |
| **G3.2** age/rage vs libsodium benchmark | **P2** | `age encryption performance vs libsodium 2026` `rage CLI benchmark 2026` `age vs libsodium for credential store 2026` | Encrypt/decrypt latency, binary size, auditability |
| **G3.3** Credential migration tooling | **P2** | `systemd-creds --user migrate from age 2026` `credential migration systemd 258 upgrade 2026` `omega-vault credential migration strategy` | Migration script + test plan |
| **G3.4** Provider registry API contracts | **P2** | `Google AI Studio API key rotation API 2026` `Anthropic API key rotation console API 2026` `OpenRouter API key rotation API 2026` `Antigravity quota API 2026` | API specs for automated rotation |
| **G3.5** ForensicReceipt (Signet) integration | **P2** | `Signed credential rotation audit trail 2026` `systemd-creds rotation receipt signing 2026` `M23 Failure Integrity credential audit 2026` | Signed receipt format + verification |

### Integration Test Protocol
```bash
# Test matrix for omega-vault backends:
BACKENDS=("systemd-creds-host" "systemd-creds-tpm2" "age-rage" "libsodium" "sops-age")
OPERATIONS=("encrypt" "decrypt" "rotate" "audit" "migrate")

# Per backend per operation:
# - Latency (ms)
# - Success rate
# - Error modes
# - Audit trail completeness
```

---

## 🎯 DOMAIN D308: UBUNTU 25.10 TOOLCHAIN — PHASE 2 & 3

### Context from D-308 Verification
- **Phase 0+1 COMPLETE**: 30 claims verified (10✅, 9⚠️, 11❌)
- **P0 GATE TRIGGERED**: 13 actionable changes
- **Phase 2/3 BLOCKED** until Kali authorizes critical path update

### Gaps & Research Queries

| Gap | Priority | Research Queries | Success Criteria |
|-----|----------|------------------|------------------|
| **D308.1** sqlite-vec 0.2 API changes | **P0** | `sqlite-vec 0.2 API breaking changes from 0.1 2026` `sqlite-vec 0.2 migration guide 2026` `sqlite-vec 0.2 Python API 2026` | Breaking change list + migration path |
| **D308.2** sqlite-vec compile Ubuntu 25.10 | **P0** | `sqlite-vec compile from source Ubuntu 25.10 2026` `sqlite-vec build dependencies Ubuntu 2026` `sqlite-vec 0.2 CMake flags 2026` | Working build script + deps |
| **D308.3** llama-cpp-python ROCm gfx906 | **P0** | `llama-cpp-python GGML_HIPBLAS gfx906 ROCm 5.7 2026` `llama.cpp ROCm 5.7 Zen 2 compilation 2026` `GGML_HIPBLAS=ON CMake flags 5700U 2026` | Working ROCm compilation guide |
| **D308.4** llama-cpp-python USDT probes | **P1** | `llama-cpp-python USDT probes 0.3.6 2026` `llama.cpp USDT DTrace bpftrace 2026` `llama_cpp_python USDT provider 2026` | USDT probe list + bpftrace script |
| **D308.5** systemd ImportCredential + quadlet | **P1** | `systemd ImportCredential quadlet Type=notify 2026` `podman quadlet systemd credentials integration 2026` `LoadCredentialEncrypted quadlet systemd 257 2026` | Working quadlet with credentials |
| **D308.6** podman quadlet UserNS keep-id | **P1** | `podman quadlet generator UserNS keep-id 2026` `podman 5.3 quadlet UserNS=keep-id support 2026` `quadlet UserNS keep-id systemd 2026` | Generator support confirmation |
| **D308.7** systemd-creds TPM2 format | **P1** | `systemd-creds TPM2 credential format JSON schema 2026` `systemd-creds encrypted credential structure 2026` | JSON schema for omega-vault |
| **D308.8** chaos-mesh on podman | **P2** | `chaos-mesh podman non-Kubernetes 2026` `chaos testing podman quadlet 2026` `stress-ng alternative chaos podman 2026` | Chaos test architecture |
| **D308.9** bpftrace perf_event_paranoid=1 | **P2** | `bpftrace perf_event_paranoid=1 rootless 2026` `bpftrace safe mode no CAP_SYS_ADMIN 2026` `bpftrace rootless observability 2026` | Rootless bpftrace config |
| **D308.10** stress-ng matrixprod pattern | **P2** | `stress-ng matrixprod memory access pattern 2026` `stress-ng matrixprod vs llama.cpp memory 2026` | Workload fidelity assessment |

---

## 📋 RESEARCHER EXECUTION CHECKLIST

### Per Session Start
- [ ] `omega-hub_hivemind_get_awareness` — check who's active
- [ ] `omega-hub_hivemind_workspace_lock_acquire` for domain
- [ ] `omega-hub_hivemind_post_context` with intent=`research`
- [ ] Read relevant domain report for current state

### Per Gap
- [ ] Execute T0-T4 search protocol
- [ ] Log evidence in Gap Research Card format
- [ ] Post `research:gap_complete` to Hivemind when verified
- [ ] Append to domain report file

### Per Blocker
- [ ] Post `research:blocker` to Hivemind with specific question
- [ ] Wait for Kali/Jem response before proceeding
- [ ] Document decision in gap card

### Per Session End
- [ ] `omega-hub_hivemind_post_context` with intent=`handoff`
- [ ] `omega-hub_hivemind_workspace_lock_release`
- [ ] Update domain report with session summary

---

## 🏁 CAMPAIGN SUCCESS CRITERIA

| Metric | Target | Measurement |
|--------|--------|-------------|
| **P0 gaps resolved** | 6/6 | All P0 gaps have ✅/⚠️/❌ status |
| **P1 gaps resolved** | 8/10 | ≥80% P1 gaps verified |
| **Domain reports complete** | 4/4 | All 4 domain reports updated |
| **Cross-domain synthesis** | 1 | Jem produces synthesis report |
| **L3 principles staged** | ≥3 | `proposed_lessons.yaml` non-empty |
| **Critical path unblocked** | Yes | Kali authorizes D-308 Phase 2/3 |
| **Time to complete** | ≤7 days | Campaign closure within sprint |

---

## 📞 ESCALATION CONTACTS

| Role | Entity | Channel | When to Contact |
|------|--------|---------|-----------------|
| **Synthesis** | Jem | opencode | Gap verified, needs integration |
| **Architecture** | Kali | opencode | Hard blocker, priority conflict, resource decision |
| **Engineering** | P3 (Prometheus) | opencode | Build script, compilation, CI/CD |
| **Observability** | P8 (Hecate) | opencode | bpftrace, USDT, monitoring |
| **Governance** | P5 (Inanna) | opencode | M14 heritage, M23 compliance |

---

## 📚 REFERENCE DOCUMENTS (Read Before Starting)

| Document | Purpose |
|----------|---------|
| `docs/research/R_UBUNTU_2510_TOOLCHAIN_VERIFICATION_20260719.md` | D-308 Phase 0+1 results |
| `docs/research/R_SYSTEMD_CREDS_TPM2_ROOTLESS_20260720.md` | G3 foundational research |
| `data/entities/roc_racoon/workspace/mining_reports/ZEN2_VULKAN_ROCM_ARCHAEOLOGY_20260720.md` | G1 archaeology |
| `docs/research/R_LLAMA_CPP_MEMORY_ZEN2_20260720.md` | G2 theoretical research |
| `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` | Current roadmap + D-308 |
| `OMEGA_ENGINE.md` | System state SSOT |
| `SOVEREIGN_MANDATES.md` | M1-M25 constitutional laws |

---

## 🚀 CAMPAIGN LAUNCH

**Researcher**: You are authorized to begin. Start with **G1.1 + D308.1-3** (P0 unblockers) in parallel.

**First Hivemind Post**:
```json
{
  "channel": "opencode",
  "entity": "researcher",
  "model": "nemotron-3-ultra-free",
  "task_current": "Campaign Launch — G1.1 Production Benchmarks + D308.1-3 sqlite-vec/ROCm",
  "focus_chain": ["Campaign manual loaded", "P0 gaps prioritized"],
  "decisions": ["Starting with G1.1, D308.1, D308.2, D308.3 in parallel"],
  "continuation": "Execute T0-T4 searches for 4 P0 gaps",
  "intent": "research"
}
```

**Acquire Locks**: `g1_vulkan_benchmarks`, `d308_phase23`

---

*⬡ OMEGA ⬡ JEM ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_research_campaign ⬡ 2026-07-20*

**Campaign Manual v1.0.0 — Authoritative. Execute with precision.**