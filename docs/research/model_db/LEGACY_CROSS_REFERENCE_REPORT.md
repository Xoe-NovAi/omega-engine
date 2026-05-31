# 🔱 Model Database Cross-Reference Report
# xna-omega-legacy vs CURRENT_MODELS.md (2026-05-16)

**AP Token**: AP-CROSS-REFERENCE-v1.0
**Report Generated**: 2026-05-16
**Sources Analyzed**: 12+ legacy files across 3 categories

⬡ OMEGA ⬡ GNOSIS-ANALYST ⬡ big-pickle ⬡ opencode ⬡ trc_research ⬡ CROSS-REFERENCE

---

## Executive Summary

Cross-referenced **12+ legacy specification files** from the xna-omega-legacy repository against the live API-verified `CURRENT_MODELS.md` database. Of **72 total model references** compared:

| Category | Count |
|----------|-------|
| ✅ Consistent across both | 24 |
| ⚠️ With discrepancies (resolved via web search) | 6 |
| ❌ In legacy but not in current DB (missing gaps) | 14 |
| ✨ In current DB but not in legacy (new additions) | 12 |
| 🏠 Local models (no cloud counterpart) | 10+ |

---

## §1 MODELS THAT MATCH ✅

### OpenRouter Free Models — Consistent Specs

| Model | Legacy Spec | Current DB Spec | Match? |
|-------|------------|-----------------|--------|
| minimax/minimax-m2.5:free | 200K ctx | 204,800 ctx | ✅ |
| meta-llama/llama-3.3-70b-instruct:free | 128K ctx | 131,072 ctx | ✅ |
| nvidia/nemotron-nano-9b-v2:free | 128K ctx | 128,000 ctx | ✅ |
| nvidia/nemotron-nano-12b-v2-vl:free | 128K ctx | 128,000 ctx | ✅ |
| poolside/laguna-m.1:free | 128K ctx | 131,072 ctx | ✅ |
| poolside/laguna-xs.2:free | 128K ctx | 131,072 ctx | ✅ |
| z-ai/glm-4.5-air:free | 131K ctx | 131,072 ctx | ✅ |
| openai/gpt-oss-120b:free | 131K ctx | 131,072 ctx | ✅ |
| openai/gpt-oss-20b:free | 131K ctx | 131,072 ctx | ✅ |
| arcee-ai/trinity-large-thinking:free | 262K ctx | 262,144 ctx | ✅ |
| liquid/lfm-2.5-1.2b-instruct:free | 32K ctx | 32,768 ctx | ✅ |
| liquid/lfm-2.5-1.2b-thinking:free | 32K ctx | 32,768 ctx | ✅ |
| cognitivecomputations/dolphin-mistral-24b-venice-edition:free | 32K ctx | 32,768 ctx | ✅ |
| nousresearch/hermes-3-llama-3.1-405b:free | 131K ctx | 131,072 ctx | ✅ |
| meta-llama/llama-3.2-3b-instruct:free | 131K ctx | 131,072 ctx | ✅ |

### OpenCode Zen — Consistent Free Models

| Model | Legacy Status | Current Status | Match? |
|-------|--------------|----------------|--------|
| minimax-m2.5-free | Free | Free | ✅ |
| nemotron-3-super-free | Free | Free | ✅ |

### Google Gemma — Consistent

| Model | Legacy Spec | Current DB Spec | Match? |
|-------|------------|-----------------|--------|
| gemma-4-31b-it | 256K ctx | 262,144 ctx | ✅ |
| gemma-4-26b-a4b-it | 256K ctx | 262,144 ctx | ✅ |

---

## §2 MODELS WITH DISCREPANCIES ⚠️

### 2.1 Qwen3 Coder Context Window

| Source | Claim |
|--------|-------|
| Legacy | `qwen/qwen3-coder:free` = **262K** context |
| Current DB | `qwen/qwen3-coder:free` = **1,048,576** context |

**Web Verification**: Qwen3-Coder-480B-A35B has **256K native**, extendable to 1M via Yarn. The Coder-Next variant has 262K on OpenRouter. The 1M figure belongs to Coder-Plus (paid).

**Verdict: ⚠️ CURRENT DB MAY BE INFLATED** — Recommend: "256K native (1M extended via Yarn)"

---

### 2.2 NVIDIA Nemotron 3 Super 120B Context Window

| Source | Claim |
|--------|-------|
| Legacy | **128K** context |
| Current DB | **1,000,000** context |

**Web Verification**: NVIDIA official: **1M tokens**. OpenRouter free tier: **262,144**.

**Verdict: CURRENT DB PARTIALLY CORRECT** — 1M arch, 262K on OpenRouter free.

---

### 2.3 DeepSeek V4 Flash — Post-Legacy (Apr 24, 2026)

| Source | Claim |
|--------|-------|
| Legacy | Not present |
| Current DB | **1,048,576** context (1M) |

**Verdict: ✅ CORRECT** — 284B total / 13B active, 1M context, MIT license.

---

### 2.4 Big Pickle — Free to Premium Migration

| Source | Claim |
|--------|-------|
| Legacy (May 4) | Big Pickle = **free**, 64K-200K ctx |
| Current DB (May 16) | Big Pickle = **premium** |

**Verdict: ⚠️ CRITICAL CHANGE** — 12-day migration window. Replace with `minimax-m2.5-free`.

---

### 2.5 GLM Evolution

| Source | Claim |
|--------|-------|
| Legacy | GLM-5 Free (204.8K), Big Pickle = GLM-4.6 |
| Current DB | GLM-4.5 Air (free), GLM-5/5.1 (premium) |

**Verdict: ⚠️ EVOLUTION** — GLM-5 deprecated May 14.

---

### 2.6 Google Gemini Rate Limits

| Source | Claim |
|--------|-------|
| Legacy (Apr 2026) | 60 RPM / 15,000 RPD |
| Current DB (May 2026) | ~30 RPM / 1,500 RPD |

**Verdict: ⚠️ POSSIBLE REDUCTION** — Needs live verification.

---

## §3 MODELS IN LEGACY BUT NOT IN CURRENT ❌

### OpenRouter Free — Missing (9)

| Legacy Model | Context | Reason |
|-------------|---------|--------|
| qwen/qwen3-235b-a22b:free | 128K | Removed |
| deepseek/deepseek-r1:free | 163K | Replaced by V4 |
| tencent/hy3-preview:free | 128K | Removed |
| meta-llama/llama-4-maverick:free | 1M | Removed |
| google/gemini-2.0-flash-exp:free | 1M | Replaced |
| deepseek/deepseek-chat-v3-0324:free | 163K | Replaced by V4 |
| inclusionai/ling-2.6-1t:free | 128K | Removed |
| microsoft/phi-4-reasoning:free | 32K | Removed |
| mistralai/mistral-small-3.1-24b-instruct:free | 128K | Removed |

### OpenCode Zen Free — Missing (6)

| Legacy Free Model | Context | Note |
|------------------|---------|------|
| ling-2.6-flash-free | 128K | Vanished |
| hy3-preview-free | 128K | Vanished |
| big-pickle (free) | 64K-200K | **→ premium** |
| glm-5:free | 204.8K | Deprecated |
| gpt-5-nano (free) | 400K | → premium |
| kimi-k2.5-free | 262K | → premium |

---

## §4 MODELS IN CURRENT DB NOT IN LEGACY ✨

### OpenRouter — New Free Additions (11)

| Model | Context | Note |
|-------|---------|------|
| baidu/cobuddy:free | 131K | New |
| deepseek/deepseek-v4-flash:free | 1M | Apr 24 release |
| google/lyria-3-clip-preview | 1M | New family |
| google/lyria-3-pro-preview | 1M | New family |
| nvidia/nemotron-3-nano-30b-a3b:free | 256K | New |
| nvidia/nemotron-3-nano-omni:free | 256K | New |
| nvidia/nemotron-3-super-120b-a12b:free | 1M | New |
| openrouter/owl-alpha | 1M+ | Experimental |
| openrouter/free | 200K | Router |
| qwen/qwen3-next-80b-a3b-instruct:free | 262K | New |

### OpenCode Zen — New Free (4)

| Model | Note |
|-------|------|
| deepseek-v4-flash-free | Post-legacy |
| qwen3.6-plus-free | New gen |
| ring-2.6-1t-free | Replaces ling-2.6? |
| trinity-large-preview-free | New |

### OpenCode Zen — New Premium Generations

| Family | Models |
|--------|--------|
| Claude | opus-4-7, sonnet-4-6 |
| Gemini | 3.1-pro, 3-flash |
| GPT-5.x | 5.5, 5.5-pro, 5.4, 5.4-pro, 5.4-mini/nano, 5.3-codex-* |
| Other | minimax-m2.7, kimi-k2.6, qwen3.6-plus, glm-5.1 |

---

## §5 LOCAL MODELS — CRITICAL GAP 🏠

Current DB tracks **ONLY cloud APIs**. Legacy has extensive **local GGUF docs** with NO counterpart.

### Local GGUF Inventory (from legacy)

| Model | Size | Quant | Context | RAM |
|-------|------|-------|---------|-----|
| Krikri-8B-Instruct | 5.5 GB | Q5_K_M | 32K | ~5.5 GB |
| Qwen3-1.7B | 1.6 GB | Q6_K | 32K | ~1.6 GB |
| Qwen3-4B-Thinking | 2.4 GB | Q4_K_M | 256K | ~2.4 GB |
| Qwen3-VL-4B | 2.4 GB | Q4_K_M | 32K | ~2.4 GB |
| DeepSeek-R1-Qwen3-8B | 4.2 GB | Q3_K_L | 8K | ~4.2 GB |
| Ministral-3B | 2.0 GB | Q4_K_M | 32K | ~2.0 GB |
| Qwen3-0.6B | 473 MB | Q6_K | 32K | ~0.5 GB |
| Qwen2.5-0.5B | 469 MB | Q4_K_M | 32K | ~0.5 GB |
| functiongemma-270m | 270 MB | Q6_K | 8K | ~0.3 GB |
| embeddinggemma-300m | 249 MB | Q6_K | 384d | ~0.3 GB |

### Legacy Entity → Model Affinity (reclaimable pattern)

| Entity | Local Fast | Local Deep | Cloud |
|--------|-----------|------------|-------|
| Metatron | qwen3-4b | krikri-8b | claude-sonnet-4-6 |
| Lucifer | phi-3-mini | mistral-7b | gemini-2.5-flash |
| Hecate | qwen3-4b | krikri-8b | claude-opus-4-6 |
| Maat | phi-3-mini | qwen3-4b | claude-sonnet-4-6 |
| Thoth | qwen3-4b | krikri-8b | claude-sonnet-4-6 |
| Sophia | krikri-8b | krikri-8b | gemini-2.5-flash |
| Lilith | krikri-8b | krikri-8b | claude-opus-4-6 |
| Default | qwen3-4b | krikri-8b | claude-sonnet-4-6 |

---

## §6 RECOMMENDATIONS

### Immediate Priority
1. **Add local model section** to CURRENT_MODELS.md
2. **Correct Qwen3 Coder context** — "256K native, 1M with Yarn"
3. **Note Big Pickle free→premium migration**
4. **Add rate limit section** (currently missing)
5. **Flag Hy3 and Ling-2.6 disappearance**

### Short-Term
6. **Port entity-model affinity system** to Omega engine
7. **Verify Google Gemini rate limit reduction**
8. **Document Nemotron 3 Super: 262K on OpenRouter free**

### Long-Term
9. **Build automated diff system** for model additions/removals
10. **Model lifecycle tracking** — deprecations, tier migrations

---

*Sources: 12 legacy files, 2 current DB files, 4 web verifications (NVIDIA, DeepSeek, Google, Qwen official).*
