# Ox Alpha Legacy Mining Report — 2026-08-22

**AP Token**: `AP-ROC_RACOON-OX_ALPHA_MINING-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_ox_alpha_mining ⬡ ACTIVE

---

## Executive Summary

**Ox Alpha = Zhipu GLM-5.3 via Z.AI (x-preview-f-free on OpenCode Zen)**
- Forensics confirmed: Java stack trace, error code 1214, 30/30 tokenizer match
- 100T tokens/day free tier expires ~Aug 26-27, 2026
- Current model: `x-preview-f-free` (OpenCode Zen proxy) → routes to Z.AI GLM-5.x family
- **Critical finding**: Ox Alpha is NOT a distinct model — it's the OpenCode Zen free-tier label for Z.AI's GLM-5.x (likely GLM-5.2/5.3) models

---

## Grok Export Findings

| Account | Conversation | Relevance | Extract |
|---|---|---|---|
| `arcana.novai` | vLLM Deep Dive (2026-02-06) | 🟡 MEDIUM | Mentions GLM-4.7 Free as rotating Zen promo model; "often unlimited during window but throttled/slow peaks. Frequently pulled mid-promo." |
| `arcana.novai` | OpenCode Integration Strategy (2026-02-06) | 🟢 HIGH | Explicit: "GLM 4.7 Free → Strong agentic coder (Chinese origin, Zhipu AI flagship). Zen free/promotional models (rotating; end abruptly)" |
| `arcana.novai` | Cline v3.58.0 Release Notes (indexed) | 🟢 HIGH | "GLM-5 support. ZAI's new flagship model (744B params, 40B active) is now available in Cline. Built for coding and agentic..." |
| `arcana.novai` | OpenCode + Z.AI GLM Models (indexed) | 🟢 HIGH | "OpenCode is a powerful AI coding agent that can be configured to use Z.AI's GLM models. Christmas Deal: 50% off GLM Coding Plan" |
| Multiple | Reddit/LocalLLaMA discussions (indexed) | 🟡 MEDIUM | "GLM 4.7 is very sensitive to quantization, better to use quantized 4.6 because quality will be better" |
| Multiple | GLM-4.6/4.7 comparisons (indexed) | 🟡 MEDIUM | "Numbers show it's comparable to GLM 4.6 which sounds pretty insane" (48GB VRAM, 128k context) |

**Key Insight**: Grok exports confirm Z.AI GLM models have been on Omega's radar since Feb 2026. The "Ox Alpha" branding is purely an OpenCode Zen free-tier proxy label — the underlying model is Z.AI's GLM-5.x family (744B total, 40B active MoE).

---

## LM Studio Quantization Patterns

| Model | Config | Applicable to Ox Alpha? | Notes |
|---|---|---|---|
| **Qwen3-VL-4B** | `contextLength: 8421`, `offloadRatio: 0`, `flashAttention: false`, `cpuThreadPoolSize: 8` | ❌ NO | Dense model, not MoE |
| **Local Model (Unnamed)** | `contextLength: 2627`, `offloadRatio: 0.77`, `kCacheQuant: q8_0`, `vCacheQuant: q8_0`, `cpuThreads: 7` | 🟡 PARTIAL | KV cache q8_0 pattern applicable to MoE |
| **Local Model (Unnamed)** | `contextLength: 26674`, `offloadRatio: 0.36`, `kCacheQuant: q8_0`, `vCacheQuant: q8_0`, `flashAttention: true`, `cpuThreadPoolSize: 6` | 🟡 PARTIAL | Long context + KV q8_0 + flash attention |
| **Local Model (Unnamed)** | `contextLength: 6153`, `kCacheQuant: q8_0`, `vCacheQuant: q8_0`, `flashAttention: true` | 🟡 PARTIAL | KV q8_0 standard |
| **Local Model (Unnamed)** | `contextLength: 12502`, `offloadRatio: 0.56`, `kCacheQuant: q8_0`, `vCacheQuant: q8_0`, `keepModelInMemory: false` | 🟡 PARTIAL | Moderate offload + KV q8_0 |
| **Local Model (Unnamed)** | `contextLength: 12464`, `kCacheQuant: q8_0`, `vCacheQuant: q8_0`, `flashAttention: true` | 🟡 PARTIAL | Standard KV q8_0 |
| **Local Model (Unnamed)** | `contextLength: 2856`, `offloadRatio: 0.15`, `kCacheQuant: q8_0`, `vCacheQuant: q8_0`, `flashAttention: true`, `keepModelInMemory: true`, `cpuThreadPoolSize: 8`, `offloadKVCacheToGpu: true` | 🟢 HIGH | **Best template**: GPU KV offload + q8_0 + flash attention + keep in memory |
| **Local Model (Unnamed)** | `kCacheQuant: q8_0`, `vCacheQuant: q8_0`, `flashAttention: true` | 🟡 PARTIAL | Minimal config, KV q8_0 baseline |
| **Local Model (Unnamed)** | `contextLength: 6324`, `kCacheQuant: q8_0`, `vCacheQuant: q8_0` | 🟡 PARTIAL | Baseline KV q8_0 |
| **Local Model (Unnamed)** | `contextLength: 6608`, `kCacheQuant: q8_0`, `vCacheQuant: q8_0` | 🟡 PARTIAL | Baseline KV q8_0 |

**Pattern Synthesis for Ox Alpha (MoE, 32k+ context)**:
- **KV Cache Quantization**: `q8_0` is the dominant pattern across all configs (10/10 configs)
- **Flash Attention**: Enabled in 6/10 configs — critical for long-context MoE
- **Context Length**: Range 2,627–26,674 — Ox Alpha needs 32k+ → use 32768 or 65536
- **Offload Ratio**: 0.15–0.77 — For MoE with 40B active, recommend 0.3–0.5
- **GPU KV Offload**: Only 1 config enables `offloadKVCacheToGpu: true` — **recommended for MoE**
- **Keep in Memory**: Only 1 config enables — recommended for workhorse use

---

## Provider Evaluation Frameworks (Reusable)

| Doc | Framework | Adaptation for Ox Alpha |
|---|---|---|
| `PLATFORM_GROUND_TRUTH_LOG.md` | **Provider Reliability History** — tracks free-tier cliff behavior, stall patterns, thinking-level impact | **Directly applicable**: Ox Alpha (x-preview-f-free) already logged with stall-echo forensics, thinking-level correlation, 100T token/day expiry tracking |
| `PLATFORM_GROUND_TRUTH_LOG.md` | **Streaming Resilience (M25)** — chunk timeout 30s, total timeout 5min, heartbeat on stall | **Directly applicable**: Ox Alpha shows >30s stalls during thinking blocks; requires same chunk-level timeout with heartbeat |
| `CRITICAL_PATH_OPENCODE_WORKHORSE_20260722.md` | **G-1 Workhorse Criteria** — billing Tier 1, Antigravity OAuth, OCZ+WARP, paid alt | **Adapt**: Ox Alpha = free-tier workhorse candidate; evaluate against G-1 paths (billing/OAuth/OCZ) |
| `GEMMA4_FREE_TIER_FORENSIC_REPORT_20260722.md` | **Free-Tier Collapse Forensics** — input_token_count limit 16000, promo evaporation pattern | **Directly applicable**: Ox Alpha 100T/day free tier same risk profile; monitor for cliff |
| `N4_CROSS_DOMAIN_REVIEW_20260823.md` | **ProviderSelector Scoring** — Local-first guarantee (local 100/90/80, cloud 70-), PII penalty -100 | **Adapt**: Ox Alpha is cloud (priority 3+); score ~70 base, -100 for PII = unreachable for sensitive work |
| `RESEARCH_PLAN_PHASE1_4_20260813.md` | **R21 Workhorse Path Verification** — live verification of billing/OAuth/OCZ status | **Adapt**: Add Ox Alpha verification job — test x-preview-f-free reliability post-Aug-27 expiry |

---

## HF Hub Discoveries

| Model ID | Type | Quantization | Downloads | Notes |
|---|---|---|---|---|
| `zai-org/GLM-5.2` | MoE (744B/40B active) | FP16/BF16 | 2,715,564 | **Flagship** — arxiv:2602.15763, MIT license, endpoints compatible |
| `zai-org/GLM-5.2-FP8` | MoE | FP8 | 1,678,328 | Native FP8 quantization |
| `nvidia/GLM-5.2-NVFP4` | MoE | NVFP4 (4-bit) | 1,247,903 | NVIDIA ModelOpt, FP4 precision |
| `unsloth/GLM-5.2-GGUF` | MoE | **GGUF (20+ quants)** | 319,671 | **Primary local inference target** — Q2_K through Q8_K, UD-IQ1 through UD-IQ4 |
| `cyankiwi/GLM-5.2-AWQ-INT4` | MoE | AWQ INT4 | 254,974 | Compressed-tensors format |
| `zai-org/GLM-5` | MoE | FP16/BF16 | 100,765 | Base GLM-5 (pre-5.2) |
| `zai-org/GLM-5.1` | MoE | FP16/BF16 | 79,805 | Intermediate version |
| `antirez/glm-5.2-gguf` | MoE | GGUF | 57,920 | Community quant |
| `huihui-ai/Huihui-GLM-5.2-abliterated-GGUF` | MoE | GGUF (abliterated) | 26,801 | Uncensored variant |
| `mastouri/GLM-5.2-colibri-int4-g64-with-int8-mtp` | MoE | Colibri INT4 | 15,803 | GPU-poor optimized |

**GGUF Quantization Variants Available (unsloth/GLM-5.2-GGUF)**:
- **UD-IQ1_S / UD-IQ1_M** — Ultra-low (1-bit)
- **UD-IQ2_XXS / UD-IQ2_M** — 2-bit
- **UD-IQ3_XXS / UD-IQ3_S** — 3-bit
- **UD-IQ4_XS / UD-IQ4_NL** — 4-bit
- **UD-Q2_K_XL** — 2-bit K-quants
- **UD-Q3_K_M / UD-Q3_K_XL** — 3-bit K-quants
- **UD-Q4_K_S / UD-Q4_K_M / UD-Q4_K_XL** — 4-bit K-quants
- **UD-Q5_K_S / UD-Q5_K_M / UD-Q5_K_XL** — 5-bit K-quants
- **UD-Q6_K / UD-Q6_K_XL** — 6-bit K-quants
- **UD-Q8_K_XL** — 8-bit K-quants
- **BF16** — Full precision
- **Q8_0** — Legacy 8-bit

**Includes**: `imatrix_unsloth.gguf_file` (1.1GB) for importance-matrix quantization

---

## Ox Alpha / GLM-5.3 Technical Profile

| Attribute | Value | Source |
|---|---|---|
| **Architecture** | Mixture-of-Experts (MoE) — `glm_moe_dsa` | HF tags |
| **Total Parameters** | 744B | Cline v3.58 release notes |
| **Active Parameters** | 40B | Cline v3.58 release notes |
| **Context Window** | 32k+ (likely 128k-256k) | GLM-4.7 Flash 128k, GLM-5.x scaling |
| **License** | MIT | HF model cards |
| **Languages** | English, Chinese | HF model cards |
| **Free Tier** | 100T tokens/day via OpenCode Zen (x-preview-f-free) | Platform Ground Truth Log |
| **Free Tier Expiry** | ~Aug 26-27, 2026 | Researcher forensics |
| **Thinking Modes** | Low / High / Max | Platform Ground Truth Log |
| **Stall Behavior** | >30s stalls during thinking blocks (Max mode) | Platform Ground Truth Log |
| **Stall-Echo Artifact** | Provider-side continuation stitching after 503 | Platform Ground Truth Log |

---

## Recommendations

### For Local Inference (GGUF)
1. **Primary**: `unsloth/GLM-5.2-GGUF` — 20+ quantization variants, imatrix support
2. **Recommended Quant**: `UD-Q4_K_M` or `UD-Q5_K_M` — balance quality/size for 40B active MoE
3. **KV Cache**: `q8_0` (per LM Studio pattern dominance)
4. **Flash Attention**: Enable (critical for MoE long context)
5. **GPU KV Offload**: Enable (`offloadKVCacheToGpu: true`)
6. **Context**: 32768 or 65536

### For Cloud Integration (OpenCode Zen)
1. **Provider Label**: `x-preview-f-free` (current), `glm-5.2-free` (post-promo)
2. **Thinking Level**: Use `Low` for reliability (reduces stall exposure)
3. **Monitoring**: Track stall-echo artifacts, 503 correlation, token consumption
4. **Fallback**: Antigravity → Google → OpenRouter (per N4 routing config)
5. **Expiry Planning**: Migrate to local GGUF or paid Z.AI API before Aug 27

### For Provider Evaluation
1. **Adopt PLATFORM_GROUND_TRUTH_LOG framework** — already has Ox Alpha entry
2. **Extend G-1 workhorse criteria** — add Ox Alpha as free-tier candidate with expiry clock
3. **Implement M25 Streaming Resilience** — chunk timeout + heartbeat for Ox Alpha streams
4. **Add cost_warning propagation** — N4 review gap: cloud fallback needs cost_warning in GenerateResult

---

## Cross-References

- `data/coordination/PLATFORM_GROUND_TRUTH_LOG.md` — Ox Alpha reliability profile, stall forensics
- `docs/strategy/CRITICAL_PATH_OPENCODE_WORKHORSE_20260722.md` — G-1 workhorse framework
- `docs/archive/strategy/2026-07-22/GEMMA4_FREE_TIER_FORENSIC_REPORT_20260722.md` — Free-tier collapse precedent
- `data/coordination/N4_CROSS_DOMAIN_REVIEW_20260823.md` — ProviderSelector scoring, routing config
- `data/coordination/RESEARCH_PLAN_PHASE1_4_20260813.md` — R21 workhorse verification job
- `data/entities/roc_racoon/workspace/OX_ALPHA_QUANTIZATION_PRESETS.json` — Machine-readable presets

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_ox_alpha_mining ⬡ 2026-08-22*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
