# 🔱 CANONICAL MODEL FLEET — Model Assignments, Capabilities, Costs
**AP Token**: `AP-CANONICAL-MODEL-FLEET-20260829-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ jem-2.0 ⬡ opencode ⬡ trc_canonical_model_fleet ⬡ ACTIVE

**Date**: 2026-08-29
**Status**: CANONICAL — Consolidated from `R_CARMACK_MODEL_STRATEGY_20260828.md` + `MODEL_WINDOW_ECONOMICS_20260823.md` + `COGNITIVE_ROUTING_PLAYBOOK.md` + `CLINE_STRATEGIC_STATE_SYNTHESIS_20260828.md` + `R_RESEARCHER_DEEPSEEK_V4_FLASH_20260828.md` + `R_ANTIGRAVITY_GPT53_20260828.md` + `R_RESEARCHER_GPT53_CLINE_20260828.md` + `ACTIVE_SPRINT.json` + `config/providers.yaml` + `config/model_registry/`

---

## 📋 EXECUTIVE SUMMARY

This document is the **single authoritative model fleet reference**. It defines:
- **Current 8-account Cline review fleet** (Carmack Option E — awaiting Architect sign-off)
- **Provider fabric model mappings** (config/providers.yaml + model_registry)
- **Cognitive Architecture role assignments** (D-569 / D-601)
- **Model window economics** (D-601 binding doctrine)
- **Local inference tier matrix** (LI-4 / D-559)

---

## 🎯 CURRENT 8-ACCOUNT CLINE REVIEW FLEET (Option E)

*Source: `R_CARMACK_MODEL_STRATEGY_20260828.md` §4 + `ACTIVE_SPRINT.json` + `CLINE_STRATEGIC_STATE_SYNTHESIS_20260828.md`*

**Status**: Awaiting Architect sign-off (as of 2026-08-28)

| Account | Model | OpenRouter ID | Role | Context | Cost/1M (in/out) | Status |
|---------|-------|---------------|------|---------|------------------|--------|
| 1-3 | **M3:free** | `minimax/minimax-m3:free` | Long-write workhorse (L3 121-124 champion) | 1M | $0 / $0 | ✅ LIVE |
| 4-7 | **DeepSeek V4 Flash 0731** | `deepseek/deepseek-v4-flash-0731` | Bulk coding (4 accounts = doubled throughput) | 1M | $0.14 / $0.28 | ✅ LIVE (paid) |
| 8 | **GPT 5.6 Sol** | `openai/gpt-5.6-sol` | Newer family probe (12.5% blast radius) | 1.05M | ~$4.00 / $20.00* | ✅ LIVE (paid) |

\* Post 2026-08-22 price cut (>20% for 3 months). Standard was $5/$30.

### Key Metrics (Verified 2026-08-28)

| Model | Context (verified) | SWE-bench Verified | TTFT | Cache Hit | Long-File Write |
|-------|-------------------|-------------------|------|-----------|-----------------|
| M3:free | ≥400K no degradation | Unknown | 1.13s | 99.99% | ✅ 8/8 success (D-585) |
| DeepSeek V4 Flash 0731 | 32% AUC@1M (degrades) | 79.0% (vendor) | ~1.5-3s | — | ⚠️ Partial |
| GPT 5.6 Sol | 1.05M (claimed) | 64.6% (lab) | n/a | — | ❓ Unknown |

### Cost Analysis (Option E)

| Metric | Value |
|--------|-------|
| **Cost per 1K requests** (weighted) | (3×$0 + 4×$0.069 + 1×$1.80) / 8 = **$0.26** |
| **Monthly @ 100K req/day** | $0.26 × 30 × 100 = **~$780/mo** |
| **Free tier sustainability** | ✅ 3 of 8 = $0; 4 of 8 = cheap |
| **Quality** | High for 7 of 8; UNKNOWN for 1 (12.5% probe) |
| **Risk** | 🟢 Lowest among realistic options |

### Why Option E (Carmack Rationale)

1. **M3 as L1 workhorse** (3 accounts): D-585 long-write champion axioms honored. 3×50 RPD = 150 RPD free headroom.
2. **DeepSeek V4 Flash 0731 as bulk tier** (4 accounts): 9× cheaper than Claude Haiku 4.5; SWE-bench 79% (vendor); 2,500 concurrent/account.
3. **GPT 5.6 Sol as controlled probe** (1 account): Newer family for risk-controlled testing; 1/8 blast radius = 12.5%.
4. **Cost**: ~$780/mo = 9× cheaper than all-GPT-5.6, 14× cheaper than all-Claude, 4× more than all-M3 but with 4× family diversification.
5. **Architectural soundness**: 4 model families = 4× blast-radius diversification. $0 for 37.5% of fleet.

---

## 🔌 PROVIDER FABRIC MODEL MAPPINGS (config/providers.yaml)

*Source: `config/providers.yaml` (fallback_chain) + `config/model_registry/providers/*.yaml`*

### Flat Chain Entries (What ModelGateway Actually Reads)

| Priority | Provider | Base URL | Supported Models (Key) |
|----------|----------|----------|------------------------|
| 0 | `native-gguf` | — | `qwen3-1.7b`, `qwen3-4b-thinking`, `phi-4-mini`, `krikri-8b`, `phi-2-omnimatrix-i1` |
| 1 | `lmster` | — | LM Studio models |
| 2 | `ollama` | — | Local Ollama models |
| 3 | `antigravity` | `https://api.antigravity.ai/v1` | `gemini-3.1-pro-preview-customtools`, `sonnet-4.6`, `opus-4.6` |
| 4 | `google` / `google-compat` | `https://generativelanguage.googleapis.com` | `gemini-2.5-pro`, `gemini-2.5-flash` |
| 5 | `openrouter` | `https://openrouter.ai/api` | **See full list below** |
| 6 | `opencode-zen` | `https://opencode.ai/zen/v1` | `x-preview-f-free`, `nemotron-3-super-free`, `deepseek-v4-flash-free`, `gpt-5-nano`, `gpt-5-codex`, `big-pickle`, `claude-opus-4.8`, `glm-5.1`, `kimi-k2.6` |
| 7 | `cline` | `https://api.cline.bot/api` | `deepseek-v4-flash`, `mimo-v2.5` (client-gated 403) |
| 8 | `anthropic` | `https://api.anthropic.com/v1` | `claude-sonnet-5-high-thinking`, `claude-haiku-4.5-extended`, `claude-opus-4.8` |
| 9 | `xai` | `https://api.x.ai/v1` | `grok-4.3-web`, `grok-4.1-fast-web` |

### OpenRouter Supported Models (Priority 5 — Primary Cloud Aggregator)

```yaml
# Tier 1: Free tier fallbacks
- "google/gemma-4-31b-it:free"
- "google/gemma-4-26b-a4b-it:free"
- "minimax/minimax-m2.5:free"
- "nvidia/nemotron-3-super-120b-a12b:free"
- "qwen/qwen3-next-80b-a3b-instruct:free"
- "openai/gpt-oss-120b:free"
- "openai/gpt-oss-20b:free"

# Tier 2: 8-Account Cline Review Fleet (Option E)
- "minimax/minimax-m3:free"           # 3 accounts — long-write workhorse
- "deepseek/deepseek-v4-flash-0731"   # 4 accounts — bulk coding
- "openai/gpt-5.6-sol"                # 1 account — newer family probe

# Tier 3: Cognitive Architecture Roles (D-569)
- "nvidia/nemotron-3-ultra-550b-a55b:free"  # Primer engine (1M window)
- "openai/gpt-5.3-codex"                    # Agentic validation probe (NEW)
- "anthropic/claude-opus-4.8"               # Break-glass adjudicator
- "google/gemini-3.1-pro-preview-customtools" # Final reviewer (1M window)
```

### Model Registry Overrides (OpenRouter `model_overrides`)

```yaml
model_overrides:
  # Local name → OpenRouter ID
  "cline-m3": "minimax/minimax-m3:free"
  "cline-v4-flash": "deepseek/deepseek-v4-flash-0731"
  "cline-gpt-5.6": "openai/gpt-5.6-sol"
  "primer": "nvidia/nemotron-3-ultra-550b-a55b:free"
  "agentic-probe": "openai/gpt-5.3-codex"
  "adjudicator": "anthropic/claude-opus-4.8"
  "final-reviewer": "google/gemini-3.1-pro-preview-customtools"
```

---

## 🧠 COGNITIVE ARCHITECTURE ROLE ASSIGNMENTS (D-569 / D-601)

*Source: `POST_DEBUT_ROADMAP.md` §🧠 + `MODEL_WINDOW_ECONOMICS_20260823.md` + `COGNITIVE_ROUTING_PLAYBOOK.md`*

### Model Window Economics Table (D-601 — Binding)

| Model | Window | Pool | Role | Priming Ceiling |
|-------|--------|------|------|-----------------|
| **Gemini 3.1 Pro (Antigravity)** | **1M** | Antigravity (separate from Google free) | Final reviewer · wide-corpus reader · cross-examiner | No practical ceiling |
| **Sonnet 4.6 (Antigravity)** | 200K | Antigravity ×8 accounts | Deep reviewer · coder | **≤150K** |
| **Opus 4.6 (Antigravity)** | 200K | Antigravity (smaller pool) | Break-glass adjudicator | **≤150K** |
| **Sonnet 5 (Claude.ai)** | Large | Claude.ai ×8 accounts | Tier-2 deep adjudication | N/A (fresh sessions) |
| **Haiku 4.5 (Claude.ai)** | Large | Claude.ai | Cheap drafting · digest-writing | N/A |
| **Nemotron 3 Ultra (OCZ)** | 1M | OpenCode Zen | Primer engine · digest-writer · staging | High |
| **qwen3-4b / 1.7b (local)** | Small | Local, free | Tool-call workhorse · classification | Local-first default |

### Cognitive Architecture Phases (P0–P10)

| Phase | Component | Model Assignment | Window | Owner |
|-------|-----------|------------------|--------|-------|
| **P0** | Context Window Registry | `config/model_context_windows.yaml` | — | Ma'at |
| **P1** | Dynamic Prompt Builder | Planner: mimo-7b-rl (32K) | 32K | Ma'at |
| **P2** | Role-Aware Model Router | Planner→mimo-7b-rl; Executor→qwen3-1.7b; Critic→qwen3-1.7b | 32K/8K/2K | Ma'at |
| **P3** | Domain Module Loader | `load_domain("engineering", 8K)` | 8K | Ma'at |
| **P4** | Planner/Executor Engine | Planner (mimo-7b 32K) → DAG; Executor (qwen3-1.7b 4K) | 32K/4K | Ma'at |
| **P5** | Context Packer | Builds executor context ≤4K | 4K | Ma'at |
| **P6** | Critic + Verifier | Critic: qwen3-1.7b 2K (rubric); Verifier: deterministic | 2K | Verity |
| **P7** | Local Pre-load + KV Cache | Planner: mimo-7b q8_0; Executor: qwen3-1.7b f16 | 32K/8K | Ma'at |
| **P8** | SomaticState Planner | State save/restore between sprints | — | Ma'at |
| **P9** | EvolveR Distillation | Nightly on Qwen3-1.7B → principle store | — | Researcher + Ma'at |
| **P10** | Freshness System | Scabera composite (age + embed_lag + owner weights) | — | Researcher + Ma'at |

### Standard Play: Dual Review (D-601)

```
1. PRIME    — cheap/local models gather corpus to ≤150K
2. REVIEW-1 — Sonnet 4.6 deep review (pure cognition, zero tool calls)
3. REVIEW-2 — switch → Gemini 3.1 Pro (no compaction; inherits Review-1)
              mandate: adversarial cross-examination of Review-1
4. RESOLVE  — agreement ⇒ verdict logged (T0 dual-provenance)
              disagreement ⇒ Tier-3 Opus break-glass or Architect escalation
```

---

## 🏠 LOCAL INFERENCE TIER MATRIX (LI-4 / D-559)

*Source: `ACTIVE_SPRINT.json` workstream `LOCAL-INFERENCE-OPT` + `HOLISTIC_ARCHITECTURE_PLAN_20260820.md` + `CARMACK_FULL_REPO_REVIEW_CHECKLIST_VALIDATED_20260828.md`*

### Tier 0 (Sequential Loading — One Model at a Time)

| Tier | Model | Quant | KV Cache | Threads | Role | Flags |
|------|-------|-------|----------|---------|------|-------|
| **0** | **Qwen3-4B** | Q6_K | q8_0 (max context) | 7 (throughput) | Planner / Heavy reasoning | `--no-mmap --mlock` |
| **0** | **Qwen3-4B-Thinking** | Q6_K | q8_0 | 7 | Planner (thinking mode) | `--no-mmap --mlock` |
| **0** | **Qwen3-1.7B** | Q6_K | f16 (speed) | 4 (latency) | Executor / Tool calls | `--no-mmap --mlock` |

### Adaptive Context Buffer (LI-1)

- **Startup**: `llama-fit-params` hardware probe → optimal n_ctx, n_batch, n_gpu_layers
- **Runtime**: Token-pressure gauge auto-reduces context before OOM
- **SomaticState**: Planner saves state between sprints; instant resume

### Hardware Profile (config/hardware_profile.yaml)

```yaml
cpu: "Ryzen 7 5700U"
ram_total_gb: 16
ram_engine_max_gb: 6
nvme_swap_gb: 16
zswap_enabled: true
zswap_pool_percent: 25
zswap_compressor: "lzo_rle"
zswap_allocator: "zsmalloc"
zram_enabled: false
swappiness: 100
cgroup_memory_max_gb: 6
gguf_models_dir: "/media/arcana-novai/omega_library/models"
hf_cache_dir: "/home/arcana-novai/OmegaLibrary/hf_cache"
```

---

## 🔬 SPECIALIZED MODELS (Research / Validation)

| Model | Purpose | Source | Status |
|-------|---------|--------|--------|
| **GPT-5.3-Codex** | Agentic validation probe (Terminal-Bench/OSWorld/Cyber CTF) | `R_RESEARCHER_GPT53_CLINE_20260828.md` | ✅ Available via OpenRouter (`openai/gpt-5.3-codex`) |
| **GPT-5.3-Codex-Spark** | ChatGPT Pro research preview only | OpenAI Codex docs | ❌ No API |
| **GPT-5.6 Terra** | Balanced tier (GPT-5.5 quality at ~60% cost) | OpenAI blog / Carmack | ✅ Available (`openai/gpt-5.6-terra`) |
| **GPT-5.6 Luna** | Efficient tier (fast, cheap) | OpenAI blog | ✅ Available (`openai/gpt-5.6-luna`) |
| **GPT-5.6 Luna Pro** | Cheapest 1M context, reasoning-enabled | OpenRouter | ✅ Available (`openai/gpt-5.6-luna-pro`) |
| **Nemotron 3 Ultra** | Primer engine (1M window, $0.00 true cost) | D-601 amendment | ✅ Available (OCZ + OpenRouter) |
| **Ornith-9B** | Qwen3.5 fine-tune (MIT, 69.4 SWE-Bench) | YouTube Research Session | ⚠️ Hardware-gated (16GB+ VRAM) |
| **Vulkan llama.cpp** | GPU-agnostic binary (14k/14k tests pass) | YouTube Research Session | ✅ Phase 1 ready |
| **llama-optimus** | Auto-tuning (15-35% CPU speedup) | YouTube Research Session | ✅ Phase 1 ready |

---

## 🚫 DEPRECATED / REMOVED MODELS

| Model | Reason | Replacement |
|-------|--------|-------------|
| `deepseek/deepseek-v4-flash:free` | **HTTP 404 — removed from OpenRouter 2026-08-28** | `deepseek/deepseek-v4-flash-0731` (paid) |
| `nemotron-3-ultra-550b:free` | RPD exhausted (HTTP 429) | Use OCZ Nemotron or OpenRouter overflow |
| `nemotron-3-super-120b:free` | RPD exhausted (HTTP 429) | Use OCZ Nemotron or OpenRouter overflow |
| `gpt-5.3` (bare) | **Does not exist** — was hallucination in Grokster dispatch | `gpt-5.3-codex` or `gpt-5.6` family |
| Gemma 4 31B free | Input token limit 16K since 2026-07-15 | M3:free (1M context, 50 RPD) |

---

## 📊 MODEL FLEET DECISION LOG

| Decision | Date | Summary |
|----------|------|---------|
| **D-522** | 2026-08-17 | Nemotron 3 Ultra = 1M, Laguna S 2.1 = 262K (ground truth for config) |
| **D-557** | 2026-08-20 | Cline DeepSeek V4 Flash = 1M context — primary surgical tool for DEL-1 Week 2 |
| **D-559** | 2026-08-20 | INST-1 model assignment: Nemotron 30B for logic/bash; DeepSeek 1M for cross-file |
| **D-563** | 2026-08-20 | 1 active Cline instance max; 8 accounts = rate-limit resilience |
| **D-569** | 2026-08-25 | Cognitive Architecture Blueprint ratified (DP-1..DP-8) |
| **D-570** | 2026-08-25 | Qdrant replaces sqlite-vec POST-DEBUT (Horizon 2) |
| **D-582/583** | 2026-08-25 | Gemini Notebook free-tier-only (3 accounts, 10 DR/mo corrected, 2-NB) |
| **D-601** | 2026-08-23 | Model Window Economics Doctrine (6 laws + challenge mechanism) |
| **CARMACK-REVIEW** | 2026-08-20 | Option E accepted with modifications; Hardware-honest Tier 0 viable |

---

## 🔍 OPEN QUESTIONS / VALIDATION NEEDED

| Question | Blocked On | Priority |
|----------|------------|----------|
| GPT 5.6 Sol actual benchmark vs. lab claims (64.6% SWE-bench) | Independent AA verification | HIGH |
| GPT-5.3-Codex Cline integration via `openai-codex` OAuth (Responses API routing) | 1-account smoke test | HIGH |
| OpenAI ORG rate-limit interpretation for 8 keys (shared vs. per-key) | Tier-1 $5 test + burst | MEDIUM |
| ChatGPT Plus Codex bucket sharing across 8 Cline OAuth instances | Empirical test | MEDIUM |
| DeepSeek V4 Flash 0731 independent SWE-bench verification (beyond vendor) | AA re-run | MEDIUM |
| Nemotron 3 Ultra true cost $0.00 — message-level audit for all fleet | roc_racoon mining | LOW |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ CANONICAL-MODEL-FLEET ⬡ 2026-08-29*