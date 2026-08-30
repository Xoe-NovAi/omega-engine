<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 📊 Sovereign Model Catalog – June 2026 (Updated)
# ⬡ OMEGA ⬡ KALI ⬡ big-pickle ⬡ opencode ⬡ model_db ⬡ CURRENT-MODELS

**AP Token**: `AP-CURRENT-MODELS-v2.0.0`
**Last Verified**: 2026-06-10
**Status**: LIVE — Model Intelligence Layer active

| Tier | Model ID | Provider | Context | Capabilities | Notes |
|------|----------|----------|---------|--------------|-------|
| **T3** | `google/gemma-4-31b-it:free` | OpenRouter | 262K | Reasoning, Knowledge | State-of-the-art free reasoning. |
| **T3** | `gemini-2.5-pro` | Google | 1M+ | Deep Reasoning, Multi-modal | 15 RPM limit on free tier. |
| **T3** | `qwen/qwen3-next-80b-a3b-instruct:free` | OpenRouter | 262K | Logic, Multilingual | High-density intelligence. |
| **T3** | `nvidia/nemotron-3-super-120b-a12b:free` | OpenRouter | 262K | Generalist, Tools | Massive parameter count for free. |
| **T3** | `minimax/minimax-m2.5:free` | OpenRouter | 197K | Creative, Coding | Exceptional for long-form synthesis. |
| **T3** | `z-ai/glm-5.3-flash` | OpenRouter | 1M | Reasoning, Tools, Coding | Ox Alpha revealed. $0.075/$0.25 per M tokens. |
| **T3** | `minimax/minimax-m3:free` | OpenRouter | 1M | Reasoning, Coding | Free tier; rate-limited but recovers with retries. |
| **T3** | `llama-3.3-70b` | SambaNova | 128K | Reasoning, Instruction | 10-30 RPM. High reliability. |
| **T2** | `google/gemma-4-26b-a4b-it:free` | OpenRouter | 262K | Balanced, Vision | Optimized for efficiency. |
| **T2** | `opencode/big-pickle` | **Zen (stealth)** | **200K** | **Tool calling, Reasoning, Coding** | **⚠️ Identity tracking active. Currently DeepSeek V4 Flash alias. CLI-exclusive.** |
| **T2** | `qwen3.6-plus-free` | Zen | 128K | General, Fast | Zen-optimized for non-sensitive projects. |
| **T2** | `mistral-small-3.2-24b` | Together | 32K | Concise, Logic | Fast reasoning at scale. |
| **T1** | `qwen3-1.7b` | Together | 32K | Reflex, Fast | Near-instant response for simple tasks. |
| **T1** | `gemma-3-1b` | Together | 8K | Reflex, Mobile | Ultra-low latency. |
| **T1** | `opencode/gpt-5-nano` | Zen | 16K | Privacy, Fast | Permanently free, data not used for training. |
| **T1** | `llama-3.2-1b-instruct` | Together | 128K | Reflex, Tools | High context for a tiny model. |

---

## §1 Model Definitions (Schema v1.0)

```yaml
models:
  google/gemma-4-31b-it:free:
    provider: openrouter
    context_window: 262144
    free_tier: true
    capabilities:
      reasoning: 0.92
      code_generation: 0.88
      knowledge: 0.96
      creative: 0.85
    cost_per_1k_tokens_usd: 0.0
    latency_p99_ms: 4200
    uptime_percent: 98.5
    community_rating: "4.8/5.0"
    community_notes:
      - "State-of-the-art reasoning for zero cost."
      - "Watch daily quota resets (00:00 UTC)."
    last_updated: "2026-05-17"
    last_verified_free: "2026-05-17"

  gemini-2.5-pro:
    provider: google
    context_window: 1000000
    free_tier: true
    capabilities:
      reasoning: 0.95
      code_generation: 0.90
      knowledge: 0.98
      creative: 0.92
    cost_per_1k_tokens_usd: 0.0
    latency_p99_ms: 5500
    uptime_percent: 99.9
    community_rating: "4.9/5.0"
    community_notes:
      - "Massive context window is the primary advantage."
      - "15 RPM is tight but usable for deep research."
    last_updated: "2026-05-17"
    last_verified_free: "2026-05-17"

  opencode/big-pickle:
    provider: opencode-zen
    context_window: 200000
    free_tier: true
    capabilities:
      reasoning: 0.88
      code_generation: 0.94
      knowledge: 0.80
      creative: 0.70
      tool_use: true
      structured_output: true
    cost_per_1k_tokens_usd: 0.0
    latency_p99_ms: 3200
    uptime_percent: 99.0
    community_rating: "4.5/5.0"
    community_notes:
      - "STEALTH MODEL — identity may swap without notice. Current: DeepSeek V4 Flash. Originally: GLM-4.6. Tracked in R_BIG_PICKLE_IDENTITY_20260610.md"
      - "CLI-exclusive — NOT routable from Engine provider fabric. Use deepseek/deepseek-v4-flash for equivalent."
      - "Limited-time free; prioritize for dev work."
      - "Stability: known AI_APICallError regression (GitHub #28141, May 2026)"
    routing:
      engine_routable: false
      opencode_cli_only: true
      recommended_engine_alternative: "deepseek/deepseek-v4-flash"
    identity_history:
      original: "glm-4.6"
      current: "deepseek-v4-flash"
      swap_detected: true
      last_verified: "2026-06-10"
    last_updated: "2026-06-10"
    last_verified_free: "2026-06-10"

  qwen3-1.7b:
    provider: together
    context_window: 32768
    free_tier: true
    capabilities:
      reasoning: 0.65
      code_generation: 0.60
      knowledge: 0.75
      creative: 0.70
    cost_per_1k_tokens_usd: 0.0
    latency_p99_ms: 450
    uptime_percent: 99.5
    community_rating: "4.0/5.0"
    community_notes:
      - "The king of Reflex tasks."
      - "Near-zero latency on Together AI."
    last_updated: "2026-05-17"
    last_verified_free: "2026-05-17"
```

---

## §2 Community Intelligence

- **OpenRouter Free Collection**: The most diverse source. Use `openrouter/free` as a dynamic router for high availability.
- **Google AI Studio**: Best for multi-modal and massive context.
- **OpenCode Zen**: Sovereignty-first. Use `gpt-5-nano` for sensitive data as it guarantees no training on user data.
- **SambaNova**: Best reliability for Llama 3.3 70B.
- **Together AI**: Best for T1/T2 variety. 68 models available for free.
