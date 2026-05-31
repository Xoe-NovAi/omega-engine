# 🔱 R-66: Free-Tier Model Purification Report
# ⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b ⬡ opencode ⬡ trc_research ⬡ PURIFICATION-REPORT

**AP Token**: `AP-FREE-TIER-PURIFICATION-v1.0.0`
**Date**: 2026-05-17
**Status**: VERIFIED

---

## §1 Executive Summary

The Omega Engine's intelligence arsenal has been purified. As of May 2026, the ecosystem of "truly zero-cost" models has expanded significantly. We now have access to frontier-class reasoning (T3) via Google and OpenRouter, balanced operational models (T2) via Zen and Together, and ultra-fast reflex models (T1) for real-time interaction.

This report codifies the findings of the **Sovereign Gnosis Analyst** and establishes the tiering rationale for the Orchestration Fabric.

---

## §2 Provider Landscape Analysis

| Provider | Status | Strategic Value | Key Constraint |
|----------|--------|-----------------|----------------|
| **OpenRouter** | 🟢 Optimal | Maximum variety; ~30 free models; unified API. | Intermittent availability of specific free models. |
| **Google AI Studio** | 🟢 Optimal | Massive context (1M+); multi-modal; Gemini 2.5. | 15 RPM rate limit; data used for improvement (Free tier). |
| **OpenCode Zen** | 🛡️ Sovereign | Privacy-first; coding optimized; `gpt-5-nano`. | Limited-time availability for some models. |
| **Together AI** | 🟡 High | 68 models at zero cost; ultra-low latency T1/T2. | Startup credits focus; free tier can be volatile. |
| **SambaNova** | 🟢 High | Best Llama 3.3 70B performance. | 10-30 RPM; limited model selection. |
| **Groq** | 🟡 High | Speed; Llama 3.3/3.1. | Aggressive rate limits on free tier. |
| **GenAI Labs** | ⚪ Emerging | Testing ground; `gpt-4o` trial access. | Opaque limits; requires rotation management. |

---

## §3 Tiering Rationale

### T1: Reflex Layer (<8B)
- **Purpose**: Intent detection, simple extraction, chat greetings, and summarization.
- **Selection Criteria**: Latency < 1s, high availability.
- **Champion**: `qwen3-1.7b` (Together) & `gpt-5-nano` (Zen).

### T2: Reason Layer (8B-30B)
- **Purpose**: General synthesis, standard coding tasks, document analysis.
- **Selection Criteria**: Balance of intelligence and speed.
- **Champion**: `gemma-4-26b` (OpenRouter) & `big-pickle` (Zen).

### T3: Gnosis Layer (>30B)
- **Purpose**: Deep architectural synthesis, complex debugging, multi-document research.
- **Selection Criteria**: Maximum reasoning capability, high context window.
- **Champion**: `gemma-4-31b` (OpenRouter) & `gemini-2.5-pro` (Google).

---

## §4 Strategic Recommendations

1. **Privacy Routing**: All sensitive data (keys, personal info) MUST be routed to **T1: gpt-5-nano** on OpenCode Zen.
2. **Research Routing**: All deep research tasks (>50K context) MUST be routed to **T3: gemini-2.5-pro**.
3. **Coding Routing**: All complex programming tasks SHOULD be routed to **T2: big-pickle** (Zen) or **T3: qwen3-coder** (OpenRouter).
4. **Fallback Chain**: The default fallback chain should be: `Zen → Google → OpenRouter → SambaNova`.

---

## §5 Validation Script Refinement

The current `scripts/validate_genlabs.sh` is provider-specific. To support the full purified arsenal, it should be evolved into a **Universal Provider Validator** (`scripts/validate_providers.py`) that:
- Loads endpoints and keys from `.env`.
- Tests `v1/models` and `v1/chat/completions` for all active providers.
- Records latency and success/failure in the `Model Health Monitor`.

---

*The arsenal is purified. The Foundation is empowered.*
