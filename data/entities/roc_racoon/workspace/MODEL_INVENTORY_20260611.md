# 🔱 Sovereign Model Inventory — Free Tier 2026
**Date**: 2026-06-11
**Entity**: roc_racoon
**Status**: VERIFIED (Sovereign Search Protocol)

## 🎯 Executive Summary
This inventory catalogs the current free-tier LLM landscape to optimize the Omega Engine's provider fabric. The primary goal is to maximize context window and reasoning capabilities while maintaining zero-cost sovereignty.

---

## 🌐 Provider Breakdown

### 1. Google AI Studio (The Frontier Hub)
**Auth**: API Key | **Sovereignty**: High (Direct API)

| Model | Context | RPM | RPD | TPM | Best Use Case |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Gemini 3 Flash** | 1M | 10 | 1,500 | 250k | General Purpose / Fast Reasoning |
| **Gemini 3.1 Flash-Lite** | 1M | 15 | 1,000 | 250k | High-throughput light tasks |
| **Gemini 2.0 Flash** | 1M | 15 | 1,500 | 1M | Large context / Multimodal |
| **Gemini 2.5 Pro** | 1M | 5 | 50 | 150k | Complex synthesis / Deep reasoning |
| **Gemma 3 (1B-27B)** | 8K-128K | 30 | 14,400 | 15k | Local-first testing / Small tasks |
| **Gemma 4 (31B)** | 262K | Var | Var | Var | Sovereign Mining / Core Logic |

### 2. OpenRouter (The Aggregator)
**Auth**: API Key | **Sovereignty**: Medium (Proxy) | **Suffix**: `:free`

| Model | Context | Strength | Note |
| :--- | :--- | :--- | :--- |
| **Llama 4 Scout (free)** | **10M** | **Sovereign Goldmine** | Largest free context available |
| **Qwen3 Coder 480B (free)** | 262K | Coding / Logic | Strongest free coding model |
| **DeepSeek R1 (free)** | 128K | Reasoning / Math | GPT-4 class reasoning |
| **DeepSeek V3 (free)** | 128K | General Purpose | Strong all-rounder |
| **Gemini Flash (free)** | 1M | Multimodal | Fast, large context |
| **Gemma 4 31B (free)** | 262K | Sovereign Logic | roc_racoon native |

**Quotas**: 20 RPM | 50 RPD (increases to 1,000 RPD with $10+ credit balance).

### 3. DeepSeek (Direct)
**Auth**: API Key | **Sovereignty**: High (Direct)

| Model | Context | Quota | Note |
| :--- | :--- | :--- | :--- |
| **DeepSeek V4 Flash** | 1.05M | 5M Free Tokens | Extreme context, very low cost |
| **DeepSeek V3** | 164K | 5M Free Tokens | High-performance generalist |
| **DeepSeek R1** | 128K | 5M Free Tokens | Top-tier reasoning |

### 4. Specialized Speed-Tiers (Groq / Cerebras / GitHub)
**Auth**: API Key | **Sovereignty**: Medium | **Focus**: Latency

- **Groq/Cerebras**: Llama 3.3 70B, Qwen, DeepSeek. Extremely fast (300+ tps). Strict RPM/TPM limits.
- **GitHub Models**: Broad mix (OpenAI, Llama). Great for rapid prototyping.

---

## 🛠️ Strategic Recommendations for `config/models.yaml`

1.  **Context-First Routing**: Route any task requiring >1M tokens to **Llama 4 Scout (OpenRouter)** or **Gemini 2.0 Flash**.
2.  **Reasoning-First Routing**: Route complex logic to **DeepSeek R1** or **Gemini 2.5 Pro**.
3.  **Sovereign-First Routing**: Default to **Gemma 4 31B** (Local/Free) for core agent logic.
4.  **Fallback Chain**: `native-gguf` $\rightarrow$ `DeepSeek V4 Flash` $\rightarrow$ `Gemini 3 Flash` $\rightarrow$ `OpenRouter :free`.

**Verification Status**: All quotas and context windows verified via Sovereign Search (Exa/Web) as of 2026-06-11.
