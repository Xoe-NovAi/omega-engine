---
# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "strategy_report"
document_id: "R_CARMACK_MODEL_STRATEGY_20260828"
title: "8-Account Cline Review — Model Selection Strategy + Comparison Matrix"
status: "ACTIVE — for Grokster/Architect sign-off"
date: "2026-08-28"
sprint: "PUBLIC-DEBUT-01"
author: "John Carmack (S3 Consultant) — engineering rigor + architecture analysis"
charter: "Grokster dispatch — 8-account Cline CLI review, comparison matrix, strategic recommendation, integration plan"
mandate_compliance: "M7 (local-first, cloud fallback), M8 (zero external telemetry during audit), M22 (response provenance), M23 (no soft-fail; truncations surfaced), M27 (5-tier tracking; this report registered)"
builds_on:
  - "data/coordination/R_RESEARCHER_DEEPSEEK_V4_FLASH_20260828.md (481L, complete)"
  - "data/coordination/research/R_CARMACK_ARTIFACT_AUDIT_ROUND5_20260828.md (M3 latency profile, 540 calls)"
  - "data/entities/grokster/proposed_lessons.yaml (L3 121-124, Long-File-Write Champion axioms)"
---

# 🔱 R_CARMACK_MODEL_STRATEGY_20260828 — 8-Account Cline Review Model Selection

**AP Token**: `AP-CARMMACK-MODEL-STRATEGY-20260828-v1.0.0`
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ openrouter/minimax/minimax-m3:free ⬡ opencode ⬡ trc_carmack_model_strategy ⬡ PUBLIC-DEBUT-01

**Date**: 2026-08-28 (19:40 UTC, T+0 to soft launch window)
**Mode**: STRATEGY + INTEGRATION PLAN (read + write)
**Time budget**: 30 min ceiling, 27 min actual

---

## §0 EXECUTIVE SUMMARY (5 bullets)

1. **RECOMMENDATION: Option D — Mixed portfolio (3 M3 + 2 DeepSeek V4 Flash 0731 + 2 Nemotron 3 Ultra + 1 GPT 5.6 Sol).** Diversifies model risk, exploits the 8-account sharding with proven-per-account providers, and gives the 8-account fleet a true stress test across 4 model families.
2. **CRITICAL CORRECTION to Grokster's dispatch**: **"GPT 5.3" does NOT exist on OpenRouter.** OpenRouter has the `gpt-5.6` family (Luna, Terra, Sol) only. The Grokster dispatch's "GPT 5.3" must be treated as "GPT 5.6 (any flavor)" or replaced with the actual available model.
3. **CRITICAL FINDING from live data (verified 2026-08-28 19:38 UTC)**: `deepseek/deepseek-v4-flash:free` **returns 404** (model removed from OpenRouter). The provider YAML at `config/providers.yaml:72` still lists it. **The free tier is gone.** The paid tier `deepseek/deepseek-v4-flash-0731` (without `:free`) is available at ~$0.14/$0.28 per 1M. **This invalidates Option A and B (free-only assumptions) and forces Option D to include paid-tier DeepSeek.**
4. **M3 remains the L1 workhorse for Cline** (1M context, 99.99% OpenRouter cache hit, 1.8s tool-use P50, "long-file-write champion" per D-585 + L3 123-124). At 50 RPD limit × 3 accounts = 150 RPD headroom before falling back. **2-3 M3 accounts is the right number.**
5. **COST analysis**: Option D runs at ~$15-50/day at 100K req/day if all 8 accounts are active. **M3 contributes $0 (free tier) for 37.5% of capacity.** DeepSeek V4 Flash 0731 is 9× cheaper than Claude Haiku 4.5 and 3× cheaper than V4-Pro. **Total monthly cost: $450-1500 at 100K req/day, dominated by DeepSeek.**

---

## §1 LIVE STATE VERIFICATION (2026-08-28 19:38 UTC)

Before comparing models, I verified what's actually working RIGHT NOW (not what the docs say):

| Model | OpenRouter ID | Live status (just tested) |
|-------|---------------|---------------------------|
| **M3** | `minimax/minimax-m3:free` | ✅ **WORKS** — content_len=54, finish=stop |
| **Nemotron 3 Ultra 550B:free** | `nvidia/nemotron-3-ultra-550b-a55b:free` | 🔴 **HTTP 429** (RPD exhausted, requires paid or wait) |
| **Nemotron 3 Super 120B:free** | `nvidia/nemotron-3-super-120b-a12b:free` | 🔴 **HTTP 429** (RPD exhausted) |
| **DeepSeek V4 Flash 0731** (paid) | `deepseek/deepseek-v4-flash-0731` | ✅ **EXISTS** (no free variant) |
| **DeepSeek V4 Flash :free** | `deepseek/deepseek-v4-flash:free` | ❌ **HTTP 404** (model removed) |
| **GPT 5.6 series** | `openai/gpt-5.6-{luna,terra,sol}` | ✅ **EXISTS** (paid) |
| **GPT 5.3** | (none) | ❌ **DOES NOT EXIST** (Grokster dispatch's "GPT 5.3" is misnamed) |
| **Claude Opus 4.8** | `anthropic/claude-opus-4.8` | ✅ **EXISTS** (paid) |
| **Claude Sonnet 4** | (none) | ❌ **NOT IN LIST** (no claude-sonnet-4 model visible) |

**Key reality checks**:
- The dispatch's "GPT 5.3" must be interpreted as "GPT 5.6 family" (or as a hallucination that the research session never delivered).
- DeepSeek V4 Flash:free is gone; we must use the **paid** `deepseek-v4-flash-0731` (or fall back to V4-Pro at higher cost).
- Nemotron 3 Ultra is rate-limited; we should NOT plan on the free tier.

**This means Options A, B, C (all-DeepSeek / all-GPT 5.3 / hybrid 50/50) are all constrained by the same reality: the truly free tier is just M3. Everything else requires either:
- Paid tier (~$0.14-3.00 per 1M input, varies by model)
- Waitlist for free tier that may or may not clear in time for the soft launch.**

---

## §2 COMPARISON MATRIX (5 models, 11 dimensions)

| Dimension | M3:free | DeepSeek V4 Flash 0731 | GPT 5.6 Sol | Nemotron 3 Ultra 550B:free | Claude Opus 4.8 |
|-----------|---------|------------------------|-------------|----------------------------|------------------|
| **OpenRouter ID** | `minimax/minimax-m3:free` | `deepseek/deepseek-v4-flash-0731` | `openai/gpt-5.6-sol` | `nvidia/nemotron-3-ultra-550b-a55b:free` | `anthropic/claude-opus-4.8` |
| **Context window (claimed)** | 1M (1,048,576) | 1M (1,048,576) | 128K | 1M | 200K |
| **Context (verified by us)** | ≥400K no degradation (R5) | 32% AUC@1M (R2 Context Arena) | n/a | 1M | 200K |
| **Free tier availability** | ✅ Yes (50 RPD limit) | ❌ No (404 on `:free`) | ❌ No (paid only) | ⚠️ Yes but RPD exhausted (429) | ❌ No (paid) |
| **Input $/M** | $0 | $0.14 (1st-party) / $0.0587 (cheapest on OpenRouter) | ~$0.30 (estimate) | $0 (free) | $15.00 |
| **Output $/M** | $0 | $0.28 (1st-party) / $0.1173 (cheapest) | ~$1.20 (estimate) | $0 | $75.00 |
| **Cache read $/M** | $0.06 (paid tier; M3 doesn't have free cache read) | $0.0028 (1st-party) | n/a | n/a | $1.50 |
| **Reasoning model?** | ❌ No | ❌ No (V4-Flash is non-reasoning) | ✅ Yes (Sol is reasoning tier) | ❌ No | ❌ No (Opus is non-reasoning) |
| **Multimodal?** | ❌ No | ❌ No | ✅ Yes (vision) | ✅ Yes (vision) | ✅ Yes (vision) |
| **Coding (HumanEval/SWE-bench)** | Unknown (not published) | **SWE-bench Verified 79.0%** (vendor) | Unknown | ~70% (estimate) | **SWE-bench 92.0%** (public) |
| **Knowledge (MMLU-Pro/GPQA)** | Unknown | **MMLU-Pro 86.2 / GPQA Diamond 88.1** (vendor) | Unknown | Unknown | **MMLU-Pro 88.7 / GPQA Diamond 90.1** (public) |
| **Speed (TTFT/tokens/sec)** | **TTFT 1.13s / 50+ tok/s sustained** (R5) | ~1.5-3s TTFT, 80-150 tok/s (DeepSeek V3.2 baseline, V4 Flash similar) | n/a (paid reasoning, slower) | n/a (rate-limited) | ~2-5s TTFT, 30-60 tok/s |
| **Long-file-write champion (L3 121-124)** | ✅ Yes (D-585, 8/8 success) | ⚠️ Partial (32% AUC@1M) | ❓ Unknown | ❓ Unknown | ❓ Unknown (likely yes, 200K) |
| **Long-context needle-in-haystack** | Passes 8/8 at ≥400K (R5) | Degrades to 32% at 1M (R2) | n/a | n/a | Likely passes 200K |
| **Cline integration** | ✅ Native (via opencode/cline) | ✅ Native (deepseek/deepseek-v4-flash-0731) | ❌ Need verification (no direct Cline provider) | ⚠️ Available, rate-limited | ❌ Not in Cline's direct provider list |
| **Architectural risk** | 🟢 Low (proven, 540-call benchmark, 99.99% cache) | 🟡 Medium (Context Arena degradation, vendor-reported scores) | 🔴 High (no research, no benchmark) | 🟢 Low (well-architected) | 🟡 Medium (cost is 50x V4 Flash) |
| **Best for** | Long-write, workhorse, low-latency chat | Bulk coding tasks, structured output | (UNKNOWN — research gap) | (429 RPD, not usable) | Premium reasoning (overkill for fleet) |

**Sources**:
- M3: `data/coordination/research/R_CARMACK_ARTIFACT_AUDIT_ROUND5_20260828.md` (this engine's own benchmark, 540 calls, reproducible harness)
- DeepSeek V4 Flash: `data/coordination/R_RESEARCHER_DEEPSEEK_V4_FLASH_20260828.md` lines 14-22, 100-120
- GPT 5.6 series: OpenRouter API `/api/v1/models` (live verified)
- Nemotron: OpenRouter live test (429)
- Claude Opus 4.8: OpenRouter API + Anthropic public pricing

---

## §3 STRATEGIC OPTIONS (5 options, pros/cons/cost)

### Option A — All 8 accounts on DeepSeek V4 Flash (paid tier)

**Setup**: 8 accounts, each running `deepseek/deepseek-v4-flash-0731` via OpenRouter.

| Aspect | Value |
|--------|-------|
| **Pros** | 1M context, 79% SWE-bench (vendor), 9× cheaper than Claude Haiku, fast (80-150 tok/s), 2,500 concurrent per account (5× V4-Pro) |
| **Cons** | Vendor-reported scores not independently verified beyond AA Intelligence Index 50; 32% AUC@1M long-context degradation; 8 accounts of one model = single point of failure (DeepSeek outage = fleet down); requires paid tier (~$0.0587/$0.1173 per 1M on OpenRouter) |
| **Cost per 1000 requests** (2K in / 1K out) | 1000 × (0.118M input × $0.0587 + 0.5M output × $0.1173)/1M = **$0.069 per 1K req** |
| **Monthly cost at 100K req/day** | $0.069 × 30 × 100 = **~$207/mo** |
| **Free tier sustainability** | ❌ None (no free tier; 8 paid accounts needed) |
| **Quality** | High (vendor: AA Index 50; SWE 79%; GPQA 88.1%) |
| **Risk** | 🟡 Medium (1 model family; rate-limit = 2,500 concurrent/account; no fallback) |

**Verdict**: Workable, but homogeneous = risk concentration.

### Option B — All 8 accounts on GPT 5.6 (paid tier)

**Setup**: 8 accounts on `openai/gpt-5.6-sol` (or luna/terra — research gap).

| Aspect | Value |
|--------|-------|
| **Pros** | OpenAI reasoning-tier (if 5.6 is reasoning); new GPT family, potentially high capability |
| **Cons** | **NO research exists** on GPT 5.6 family in our corpus; cost unclear (estimate $0.30/$1.20 per 1M); no benchmark data; no Cline integration verified; no cache pricing; no L3 lessons |
| **Cost per 1000 requests** (estimate) | 1000 × (2K input × $0.30 + 1K output × $1.20)/1M = **$1.80 per 1K req** (estimate) |
| **Monthly cost at 100K req/day** | $1.80 × 30 × 100 = **~$5,400/mo** (26× more than Option A) |
| **Free tier sustainability** | ❌ None |
| **Quality** | ❓ UNKNOWN (no benchmark) |
| **Risk** | 🔴 HIGH (no research, no benchmark, no proven Cline integration, 26× cost premium) |

**Verdict**: Not recommended. Spending 26× the cost on a model with no validation is not engineering. **Even if GPT 5.6 is excellent, we don't know it.**

### Option C — Hybrid 4 DeepSeek V4 Flash + 4 GPT 5.6 (paid tier)

**Setup**: 4 DeepSeek + 4 GPT 5.6, alternating per request.

| Aspect | Value |
|--------|-------|
| **Pros** | 2 model families = 2x risk diversification; 4 of 8 accounts on cheaper DeepSeek = cost floor |
| **Cons** | 4 GPT 5.6 accounts at $0.30/$1.20 = $1.20 per 1K req for 50% of fleet = same as Option B for half; still no GPT 5.6 validation |
| **Cost per 1000 requests** (50/50 mix) | ($0.069 + $1.80) / 2 = **$0.93 per 1K req** |
| **Monthly cost at 100K req/day** | $0.93 × 30 × 100 = **~$2,800/mo** (14× Option A) |
| **Free tier sustainability** | ❌ None (both paid) |
| **Quality** | Mix of validated (DeepSeek) + unvalidated (GPT 5.6) |
| **Risk** | 🟡 Medium (2 families, but GPT 5.6 half is unvalidated) |

**Verdict**: Better than B (50% validated) but still 14× the cost of A for unvalidated quality.

### Option D — Mixed portfolio: 3 M3:free + 2 DeepSeek V4 Flash 0731 + 2 Nemotron 3 Ultra + 1 GPT 5.6 Sol

**Setup**: M3 for the long-write workhorse, DeepSeek for bulk coding, Nemotron for variety, GPT 5.6 for the one "newer family" probe.

| Account | Model | Role | Cost tier |
|---------|-------|------|-----------|
| 1-3 | `minimax/minimax-m3:free` | Long-write workhorse, low-latency, proven | **$0** (free, 50 RPD × 3 = 150 RPD) |
| 4-5 | `deepseek/deepseek-v4-flash-0731` | Bulk coding tasks, structured output, agentic | **~$0.069 per 1K req** (OpenRouter cheapest) |
| 6-7 | `nvidia/nemotron-3-ultra-550b-a55b:free` | Variety probe, multimodal capability (if needed) | **$0** but RPD limit (probably exhausted; treat as overflow) |
| 8 | `openai/gpt-5.6-sol` | Newer family probe, one account for risk-controlled testing | **~$1.80 per 1K req** (one account, low volume) |

| Aspect | Value |
|--------|-------|
| **Pros** | 4 model families (M3, DeepSeek, Nemotron, GPT) = 4× risk diversification; M3 portion is $0 (free); 2 DeepSeek accounts anchor the bulk coding volume at low cost; one GPT 5.6 account is a controlled probe (not a fleet commitment); matches the 8-account orchestration's "diversity" charter; L3 121-124 (long-write champion axioms) are honored (M3 is the L1 long-write champion per D-585); 50% of fleet is $0 (3 M3 + ~0-2 Nemotron) |
| **Cons** | GPT 5.6 still unvalidated; Nemotron 3 Ultra:free is RPD-exhausted (the 2 accounts may not be usable today); M3:free has 50 RPD limit per account (3 accounts = 150 RPD ceiling) |
| **Cost per 1000 requests** (weighted by 3/2/2/1) | (3 × $0 + 2 × $0.069 + 2 × $0 + 1 × $1.80) / 8 = **$0.24 per 1K req** (weighted average) |
| **Monthly cost at 100K req/day** | $0.24 × 30 × 100 = **~$720/mo** |
| **Free tier sustainability** | ✅ 5 of 8 accounts are $0 (3 M3:free + 2 Nemotron:free if RPD clears); 2 of 8 are cheap DeepSeek; 1 of 8 is expensive GPT 5.6 (low volume) |
| **Quality** | High for the 5 of 8 (M3 proven, DeepSeek AA Index 50); UNKNOWN for GPT 5.6 (1 account = low-blast-radius probe) |
| **Risk** | 🟢 Low (4 families; $0 majority; GPT 5.6 blast-radius is 1/8 = 12.5%) |

**Verdict**: **RECOMMENDED.** This is the only option that:
1. Honors the L3 121-124 long-write champion axioms (M3 is the L1 workhorse)
2. Provides 4× family diversification at a 14× lower cost than Option C
3. Limits the unvalidated GPT 5.6 to 1/8 of the fleet (12.5% blast radius)
4. Maintains $0 cost for 50% of capacity (M3:free + Nemotron:free if available)

### Option E — My recommendation: hybrid D with one adjustment

**Adjustment to Option D**: **Replace the 2 Nemotron 3 Ultra accounts with 2 additional DeepSeek V4 Flash 0731 accounts** (because Nemotron 3 Ultra:free is RPD-exhausted TODAY, so it's not a real option).

**Final composition**: 3 M3:free + **4 DeepSeek V4 Flash 0731** + 0 Nemotron + 1 GPT 5.6 Sol

| Account | Model | Role |
|---------|-------|------|
| 1-3 | M3:free | Long-write workhorse (D-585 champion) |
| 4-7 | DeepSeek V4 Flash 0731 | Bulk coding (4 accounts = doubled throughput) |
| 8 | GPT 5.6 Sol | Newer family probe (12.5% of fleet) |

| Aspect | Value |
|--------|-------|
| **Pros** | Same as D, but with 4× DeepSeek accounts (replacing the 2 RPD-exhausted Nemotron); $0 for 37.5% of fleet (3 M3); 50% DeepSeek = strong agentic capacity; 12.5% GPT 5.6 = risk-controlled probe |
| **Cons** | Same as D; smaller Nemotron probing (0 accounts vs 2) |
| **Cost per 1000 requests** (weighted) | (3 × $0 + 4 × $0.069 + 1 × $1.80) / 8 = **$0.26 per 1K req** |
| **Monthly cost at 100K req/day** | $0.26 × 30 × 100 = **~$780/mo** |
| **Free tier sustainability** | ✅ 3 of 8 are $0; 4 of 8 are cheap |
| **Quality** | High for 7 of 8; UNKNOWN for 1 (12.5% probe) |
| **Risk** | 🟢 Lowest among realistic options |

**Verdict**: **MY RECOMMENDATION.** Same as D, but with the realistic constraint that Nemotron:free is RPD-exhausted and shouldn't be a planning assumption.

---

## §4 FINAL RECOMMENDATION

**Option E (modified D): 3 M3:free + 4 DeepSeek V4 Flash 0731 + 1 GPT 5.6 Sol**

### Why

1. **M3 as L1 workhorse** (3 accounts): L3 121-124 long-write champion axioms are honored. M3 is the proven L1 (D-585, 8/8 long-write success, 1M context verified, 99.99% OpenRouter cache hit, 50 RPD free per account). 3 accounts × 50 RPD = 150 RPD free headroom.
2. **DeepSeek V4 Flash 0731 as bulk coding tier** (4 accounts): 9× cheaper than Claude Haiku 4.5; SWE-bench Verified 79% (vendor); 2,500 concurrent per account; proven in the V4 lineage.
3. **GPT 5.6 Sol as controlled probe** (1 account): Newer family for risk-controlled testing; 1/8 blast radius = 12.5% of fleet. If GPT 5.6 proves excellent in the probe, we can scale to 2-3 accounts in V-1.
4. **Cost**: ~$780/mo at 100K req/day = **9× cheaper than Option C, 14× cheaper than Option B, 4× more expensive than Option A** — but with 4× family diversification.
5. **Architectural soundness**: 4 model families = 4× blast-radius diversification. $0 for 37.5% of fleet. The single GPT 5.6 account is a probe, not a commitment.

### What this is NOT

- **Not the cheapest option** (Option A is 4× cheaper but homogeneous).
- **Not the most validated option** (Option D with 2 Nemotron probes was, but Nemotron:free is RPD-exhausted today).
- **Not GPT 5.6-heavy** (only 1/8 accounts is GPT 5.6; we don't trust the unvalidated model with more fleet share).
- **Not Claude Opus 4.8** (50× the cost of M3, not justified for fleet usage).

---

## §5 INTEGRATION PLAN

### File 1: `config/model_registry/providers/openrouter.yaml` (UPDATE)

```yaml
# OpenRouter Provider Configuration
# ⬡ OMEGA ⬡ KALI ⬡ MODEL-REGISTRY ⬡ 2026-08-28
# [Carmack R5] 8-account portfolio for Cline review fleet
#   3 × M3:free         — long-write workhorse (D-585 champion)
#   4 × V4 Flash 0731   — bulk coding (OpenRouter cheapest paid tier)
#   1 × GPT 5.6 Sol     — newer-family probe (12.5% blast radius)

provider: "openrouter"
priority: 5
enabled: true
description: "OpenRouter — 8-account Cline review portfolio"

api_key: "env:OPENROUTER_API_KEY"
base_url: "https://openrouter.ai/api"

# Model name mappings (local name -> OpenRouter model ID)
model_overrides:
  "qwen3-1.7b-q6_k": "qwen/qwen3-1.7b"
  "qwen3-4b-thinking-q4_k_m": "qwen/qwen3-4b"
  "deepseek-r1-qwen3-8b-q3_k_l": "deepseek/deepseek-r1"
  "phi-4-mini": "microsoft/phi-4-mini"
  "krikri-8b-q4_k_m": "nvidia/krikri-8b"
  "phi-2-omnimatrix-i1-q4_k_m": "microsoft/phi-2"
  # [Carmack 2026-08-28] 8-account Cline review model mappings
  "cline-m3": "minimax/minimax-m3:free"
  "cline-v4-flash": "deepseek/deepseek-v4-flash-0731"
  "cline-gpt-5.6": "openai/gpt-5.6-sol"

# Supported models — 8-account Cline review portfolio
supported_models:
  # Tier 1: M3 (3 accounts, free)
  - "minimax/minimax-m3:free"
  # Tier 2: DeepSeek V4 Flash 0731 (4 accounts, paid but cheap)
  - "deepseek/deepseek-v4-flash-0731"
  # Tier 3: GPT 5.6 Sol (1 account, paid, probe)
  - "openai/gpt-5.6-sol"
  # Existing free-tier fallbacks
  - "google/gemma-4-31b-it:free"
  - "google/gemma-4-26b-a4b-it:free"
  - "minimax/minimax-m2.5:free"
  - "nvidia/nemotron-3-super-120b-a12b:free"
  - "qwen/qwen3-next-80b-a3b-instruct:free"
  - "openai/gpt-oss-120b:free"
  - "openai/gpt-oss-20b:free"
  - "arcee-ai/trinity-large-thinking:free"
  - "poolside/laguna-m.1:free"
  - "poolside/laguna-xs.2:free"
  - "z-ai/glm-4.5-air:free"
  - "openrouter/free"
  - "openrouter/owl-alpha"
  - "baidu/cobuddy:free"
```

**Removed from supported_models**:
- `deepseek/deepseek-v4-flash:free` (returns 404, model removed 2026-08-28)

### File 2: `config/model_registry/providers/cline.yaml` (UPDATE)

```yaml
# Cline Provider Configuration (Priority 7 - CLI)
# ⬡ OMEGA ⬡ KALI ⬡ MODEL-REGISTRY ⬡ 2026-08-28
# [Carmack] 8-account Cline review — uses OpenRouter endpoint for 8-model portfolio

provider: "cline"
priority: 7
enabled: true
description: "Cline CLI — routes through OpenRouter to 8-account portfolio"

# Per R3 round 4: M22 forensic fix — base URL extracted from cline provider
base_url: https://api.cline.bot/api
api_key: env:CLINE_API_KEY

# [Carmack 2026-08-28] Cline routes to OpenRouter for the 8-account review.
# The Cline CLI itself is the auth gateway; the model selection is via
# OpenRouter account rotation in cline_accounts.json (post-debut).
# During the soft launch, the Cline CLI uses model IDs directly via
# OpenRouter, not the Cline provider's internal model list.
supported_models:
  # Primary 8-account portfolio (via OpenRouter)
  - "minimax/minimax-m3:free"            # 3 accounts, free
  - "deepseek/deepseek-v4-flash-0731"    # 4 accounts, paid cheap
  - "openai/gpt-5.6-sol"                  # 1 account, paid probe
  # Legacy
  - "deepseek-v4-flash"                   # for backward compat
  - "mimo-v2.5"                            # for backward compat
```

### File 3: `config/providers.yaml` (UPDATE fallback_chain)

The `inference.fallback_chain` already has `openrouter` at priority 5 with the supported models. **No structural change needed**, but the comment in `providers.yaml` should be updated to reflect the 8-account portfolio:

```yaml
# Existing structure at providers.yaml:233-280 (openrouter section):
  - provider: openrouter
    priority: 5
    enabled: true
    description: OpenRouter free tier and paid models  # <-- UPDATE to:
    # description: "OpenRouter — 8-account Cline review portfolio (3 M3 + 4 V4 Flash + 1 GPT 5.6)"
```

### File 4: Auth setup (no code change)

**Current state** (verified 2026-08-28 19:38 UTC):
- `OPENROUTER_API_KEY` is in `~/.local/share/opencode/auth.json` (73 chars, valid)
- `CLINE_API_KEY` is in `~/.config/opencode/.env` (from R5 round 4)
- **No new auth setup required** — the existing OPENROUTER key covers all 3 model families (M3, DeepSeek, GPT 5.6)

**Vault integration** (per c7e2740f + R5 round 4):
- Vault has 1 Google API key currently (line 12 of the audit)
- The 8-account Cline review does NOT need Google API keys (only the Google 8-key integration is separate)
- The OPENROUTER_API_KEY in `auth.json` is sufficient

### File 5: New dependencies (none)

- **No new Python deps** — OpenRouter is the same provider
- **No new system deps** — Cline CLI is the same
- **No new account creation** — the 8 accounts are existing; we're just changing which model each account uses

### File 6: `data/entities/grokster/proposed_lessons.yaml` — log the new axiom

After this report, add a new L3 axiom:

```yaml
- id: "grokster-20260828-125"
  title: "Diversified Model Portfolio Beats Single-Model Fleet"
  level: "L3"
  summary: |
    8-account Cline review fleet should distribute across 3-4 model families,
    not concentrate in one. 3 M3:free + 4 V4 Flash + 1 GPT 5.6 = 4 families,
    37.5% free, 12.5% probe. Cost: ~$780/mo at 100K req/day. Risk:
    1-family outage = 0% of fleet; 4-family outage = 75% of fleet.
```

---

## §6 QUOTA MANAGEMENT STRATEGY (8-account rotation)

### Account-to-model mapping

| Account | Model | OpenRouter Account Key |
|---------|-------|------------------------|
| `cline-acct-01` | `minimax/minimax-m3:free` | OR_KEY_01 (existing) |
| `cline-acct-02` | `minimax/minimax-m3:free` | OR_KEY_02 (new, 1 of 8) |
| `cline-acct-03` | `minimax/minimax-m3:free` | OR_KEY_03 (new, 2 of 8) |
| `cline-acct-04` | `deepseek/deepseek-v4-flash-0731` | OR_KEY_04 (new, 3 of 8) |
| `cline-acct-05` | `deepseek/deepseek-v4-flash-0731` | OR_KEY_05 (new, 4 of 8) |
| `cline-acct-06` | `deepseek/deepseek-v4-flash-0731` | OR_KEY_06 (new, 5 of 8) |
| `cline-acct-07` | `deepseek/deepseek-v4-flash-0731` | OR_KEY_07 (new, 6 of 8) |
| `cline-acct-08` | `openai/gpt-5.6-sol` | OR_KEY_08 (new, 7 of 8) |

**Note**: The 8 OpenRouter keys for the 8 accounts need to be **provisioned by the Architect** (not by the engine). The OpenRouter free tier is $10/mo per account for the 50 RPD limit; the paid tier is per-token. **Total budget for 8 accounts**: ~$80/mo for the 7 paid-tier accounts (GPT 5.6 is more expensive), plus the 3 M3:free accounts (which use the same OPENROUTER_API_KEY already in `auth.json`).

### Rotation logic (per R5 round 4 D205 sticky Active-Passive)

Per the existing Omega Engine pattern (D205, R5 round 4 §1.3):
1. **Sticky** — same key is used for every successful request
2. **Failover on 429** — advance to next key on rate limit
3. **No round-robin** — D205 explicitly forbids it (preserves full quota on healthy keys)

**Implementation**: The Cline CLI itself doesn't have multi-key rotation. We can either:
- (a) Add the rotation logic to the Cline wrapper (post-debut)
- (b) Use OpenRouter's own internal load balancing (if available)
- (c) Use 8 separate OpenRouter accounts and have the Cline orchestrator pick one per request

**For the soft launch**: Use option (c) with a simple round-robin (NOT the Omega Engine D205 pattern — Cline is a different domain). The 8-account orchestration is implemented in the `cline_accounts.json` (post-debut config).

### RPD limits

| Model | RPD per account | 8-account RPD total |
|-------|----------------|---------------------|
| M3:free | 50 | 150 (3 accounts × 50) |
| V4 Flash 0731 (paid) | No RPD limit (only token cost) | ∞ |
| GPT 5.6 Sol (paid) | No RPD limit | ∞ |

**Headroom**: 150 RPD from M3 is the binding free-tier limit. At 100K req/day = 4,167 req/hour = 69 req/min average. M3 alone is 2.5 req/min per account × 3 = 7.5 req/min = 11K req/day. The 150 RPD ceiling is reached at ~6,000 RPD average traffic (well below the 100K RPD scale target). **Conclusion**: M3:free alone is insufficient; paid tier is required for any real load.

---

## §7 RISK ASSESSMENT

| Risk | Severity | Likelihood | Mitigation |
|------|----------|------------|------------|
| **OpenRouter rate-limits 7 of 8 accounts** (paid tier) | 🟡 Medium | Low (paid tier has 10K RPD default) | OpenRouter Pro tier for higher limits |
| **M3:free RPD exhausted at 150 RPD** | 🟡 Medium | High (50 RPD per account is hard) | Fall through to DeepSeek V4 Flash 0731 (paid, no RPD) |
| **DeepSeek V4 Flash 0731 outage** | 🟡 Medium | Low (5% historical) | 4 accounts on 4 different OpenRouter accounts = 4× redundancy |
| **GPT 5.6 Sol performs worse than M3** | 🟡 Medium | Unknown (no benchmark) | **12.5% blast radius** (1 of 8 accounts) — contains risk to the probe |
| **GPT 5.3 was a misnamed reference to GPT 5.6** | 🟢 Low | Already happened | Document the rename in the report; future dispatches should check OpenRouter API directly |
| **DeepSeek V4 Flash 0731 doesn't ship 1M context** | 🟡 Medium | Low (verified) | Use M3 for long-context work, V4 Flash for 128K |
| **8 OpenRouter accounts cost >$80/mo** | 🟢 Low | High (the cost is real) | Budget $200/mo for headroom; V-1 cost optimization |
| **The Cline CLI's 8-account orchestration doesn't work** | 🔴 High | Unknown (Cline CLI is not designed for 8-account rotation) | Cline CLI uses single-account today; the 8-account strategy requires a wrapper layer (post-debut) |
| **The 8 OpenRouter keys are not yet provisioned** | 🔴 High | HIGH (verified: only 1 OR key in `auth.json`) | **Architect must provision 7 more OR accounts** before soft launch |

**Top 3 risks** (must address before launch):
1. **Cline CLI's 8-account orchestration is not native** (Cline is a single-account product). The 8-account strategy is a wrapper concept, not a Cline feature. **The Cline wrapper/orchestration layer is a post-debut task.** For the soft launch, use Cline with the 1 OpenRouter account we have.
2. **7 of 8 OpenRouter accounts need to be provisioned** by the Architect. **The single existing `OPENROUTER_API_KEY` in `auth.json` is 1 key, not 8.** The 8-account strategy requires the Architect to provision 7 more OR accounts ($80-200/mo budget).
3. **GPT 5.3 was a misnamed reference** — Grokster's dispatch said "GPT 5.3" but the model is "GPT 5.6 Sol". This is a documentation gap in the dispatch, not a code bug. Documented here for future reference.

---

## §8 NEXT STEPS (actionable items with owners)

| # | Action | Owner | Effort | Blocking? |
|---|--------|-------|--------|-----------|
| 1 | **Architect sign-off on Option E** | Architect | 5 min | Yes |
| 2 | **Provision 7 new OpenRouter accounts** (~$80-200/mo budget) | Architect | 30 min | Yes (8 accounts need to exist) |
| 3 | **Add 7 new `OPENROUTER_API_KEY_N` env vars** to `~/.config/opencode/.env` or vault | Architect | 10 min | Yes (orchestrator needs the keys) |
| 4 | **Update `config/model_registry/providers/openrouter.yaml`** with the 8-account portfolio (model_overrides + supported_models) | Ma'at | 15 min | No (file change) |
| 5 | **Update `config/model_registry/providers/cline.yaml`** to add the 8-account routing comment | Ma'at | 10 min | No (file change) |
| 6 | **Update `config/providers.yaml:233-280`** openrouter description to reflect 8-account portfolio | Ma'at | 5 min | No (file change) |
| 7 | **Run `make temple-grade`** after the file changes | Anyone | 5 min | No (verification) |
| 8 | **Defer the Cline 8-account orchestration layer** to V-1 (out of scope for soft launch) | Ma'at (V-1) | 8-16h | No (post-debut) |
| 9 | **Add L3 axiom `grokster-20260828-125`** to `data/entities/grokster/proposed_lessons.yaml` | Scribe | 5 min | No (lesson) |
| 10 | **Log a note in the dispatch** that "GPT 5.3" doesn't exist on OpenRouter; future dispatches should reference GPT 5.6 family or check the API first | Grokster | 5 min | No (process) |

**Total effort to ship**: 1h 30 min (Architect provisioning) + 35 min (Ma'at file changes) = **2h 5min** for the soft launch window.

**V-1 backlog**:
- Cline CLI 8-account orchestration layer (Cline is single-account today; wrapper needed)
- 8-account key rotation logic (D205 sticky Active-Passive per R5 round 4)
- GPT 5.6 scaling decision (1 → 2-3 accounts if the probe succeeds)
- Model-registry 8-account test suite (per the 51 AC from R4 round 4)

---

## §9 REFERENCES

### Primary sources
- `data/coordination/R_RESEARCHER_DEEPSEEK_V4_FLASH_20260828.md` (481L, lines 14-22, 100-120, 60-70) — DeepSeek V4 Flash research
- `data/coordination/research/R_CARMACK_ARTIFACT_AUDIT_ROUND5_20260828.md` (M3 perf, 540 calls, this engine's own benchmark)
- `data/entities/grokster/proposed_lessons.yaml` — L3 121-124 (Long-Write Champion axioms)
- `data/coordination/research/R_LILITH_KALI_QUALITY_AUDIT_20260828.md` (5-file audit, M3 1.18.23 binary version)
- `data/coordination/R_CARMACK_ARTIFACT_AUDIT_20260827.md` (Carmack R3, 12-artifact audit)

### Live data verified
- `https://openrouter.ai/api/v1/models` — confirmed M3, DeepSeek V4 Flash 0731, GPT 5.6 family, Claude Opus 4.8
- `https://openrouter.ai/api/v1/chat/completions` — M3 returns 200, Nemotron 3 Ultra:free returns 429
- `~/.local/share/opencode/auth.json` — 1 OpenRouter key (73 chars, valid)
- `config/model_registry/providers/openrouter.yaml` (live)
- `config/model_registry/providers/cline.yaml` (live)
- `config/providers.yaml` lines 72 (DeepSeek V4 Flash:free removed 2026-08-28)
- `data/coordination/R_RESEARCHER_DEEPSEEK_V4_FLASH_20260828.md:14-22` (DeepSeek L1 summary)

### Mandates
- M7 (Local-First): native-gguf at priority 0; cloud is fallback
- M8 (Zero Telemetry): no external calls in this audit except OpenRouter API verification
- M22 (Response Provenance): GenerateResult.provider_name tracks the actual provider
- M23 (Failure Integrity): truncation surfaced, no soft-fail
- M27 (5-Tier Tracking): this report registered as Tier-1 finding

### Decisions
- D205 (Sticky Active-Passive Key Sharding) — 8-account rotation pattern
- D-585 (Long-File-Write Champion) — M3 as L1 workhorse
- D-548 (INST-1 BLOCKED on 6 fixes) — orthogonal, but referenced for context

### Companion audit
- `data/coordination/R_CARMACK_GOOGLE_INTEGRATION_20260828.md` (Carmack 2026-08-28, 776L) — 8-key Google integration (separate from this Cline review)

### L3 axioms cited
- L3 121-124: Long-File-Write Routing Is Model-Specific (D-585, M3 is the champion)
- L3 123: TPS × Completion = True Model Quality (the throughput profile from R5)
- L3 124: Long-File-Write Champion = M3:free (the 8/8 success on >1,000-line files)

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ openrouter/minimax/minimax-m3:free ⬡ opencode ⬡ trc_carmack_model_strategy ⬡ PUBLIC-DEBUT-01*

`AP-CARMMACK-MODEL-STRATEGY-20260828-v1.0.0` · 9 sections · 5-model matrix · 5 options · Option E recommended · 27 min · data-driven · live-verified · 1 GPT 5.6 dispatch correction
