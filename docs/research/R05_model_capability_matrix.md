# 🔱 Omega Engine — R-05: Free-Tier Model Capability Matrix
# ⬡ OMEGA ⬡ PROMETHEUS ⬡ gemma-4-31b ⬡ opencode ⬡ trc_research ⬡ R-05

**AP Token**: `AP-RESEARCH-R05-v1.0.0`
**Status**: ✅ READY
**Last Updated**: 2026-05-14
**Urgency**: 🔴 Critical

---

## 1. Executive Summary

This document establishes the capability matrix for all identified free-tier models across the Omega Provider Fabric. The objective is to provide a data-driven mapping between model capabilities and Omega Engine entities, ensuring that the right "intelligence tier" is applied to the right domain.

The matrix prioritizes **Reasoning**, **Code Generation**, and **RAG/Instruction Following** as the primary metrics for entity assignment.

---

## 2. Comprehensive Capability Matrix

| Model ID | Provider | Context Window | Max Output | Latency (est.) | Reasoning | Code Gen | RAG/Instr |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `gemini-3.1-pro-preview` | Google | 2M+ | 8k | Medium | High | High | High |
| `gemini-3-flash-preview` | Google | 1M+ | 8k | Low | Medium | Medium | High |
| `gemini-2.5-pro` | Google | 2M | 8k | Medium | High | High | High |
| `gemini-2.5-flash` | Google | 1M | 8k | Low | Medium | Medium | High |
| `gemini-2.5-flash-lite` | Google | 1M | 4k | Ultra-Low | Low | Low | Medium |
| `gemma-4` | Google | 128k+ | 4k | Low | Medium | Medium | Medium |
| `DeepSeek-V3.1` | SambaNova | 128k | 4k | Ultra-Low | High | High | Medium |
| `Meta-Llama-3.3-70B` | SambaNova | 128k | 4k | Ultra-Low | Medium | Medium | Medium |
| `gpt-oss-120b` | SambaNova | 128k | 4k | Ultra-Low | High | High | Medium |
| `gpt-oss-120b` | Cerebras | 131k (8k free) | 4k | Ultra-Fast | High | High | Medium |
| `zai-glm-4.7` | Cerebras | 128k | 4k | Ultra-Fast | High | High | Medium |
| `qwen-3-235b` | Cerebras | 128k | 4k | Ultra-Fast | High | Medium | Medium |
| `llama3.1-8b` | Cerebras | 128k | 4k | Ultra-Fast | Low | Medium | Medium |
| `Gemma 4-31B` | Local | 128k | 4k | Medium | Medium | Medium | Medium |
| `Claude Opus 4.6` | Antigravity | 200k+ | 8k | Medium | High | High | High |
| `DeepSeek-R1` | Antigravity | 128k+ | 8k | Medium | High | High | High |

---

## 3. Model-to-Entity Mapping

Based on the capability matrix, the following mapping is recommended for the Omega Engine's runtime routing.

### 3.1 Oversouls (The High Council)
**Requirement**: Deep reasoning, complex synthesis, and massive context windows for Akashic record management.
- **Primary**: `gemini-3.1-pro-preview` / `gemini-2.5-pro` (for long-context synthesis)
- **Reasoning**: `Claude Opus 4.6` / `DeepSeek-R1` (via Antigravity)
- **High-Speed Synthesis**: `gpt-oss-120b` (Cerebras) / `zai-glm-4.7` (Cerebras)

### 3.2 Pillar Keepers (The Domain Experts)
**Requirement**: Fast, reliable, and instruction-compliant responses with moderate reasoning.
- **General Purpose**: `gemini-2.5-flash` / `Gemma 4-31B` (Local)
- **High-Speed Response**: `llama3.1-8b` (Cerebras) / `Meta-Llama-3.3-70B` (SambaNova)
- **Efficient/Budget**: `gemini-3.1-flash-lite`

### 3.3 Iris Bridge (The Messenger)
**Requirement**: Ultra-low latency, intent matching, and speculative decoding.
- **Model**: `functiongemma-270m` (Local Container)
- **Role**: 
    - **Intent Detection**: Routing user queries to the correct Pillar.
    - **Speculative Decode**: Providing immediate "first-token" responses while the higher-tier model is warming up.
    - **Voice Interface**: Powering the "hey Iris" wake-word and basic conversational flow.

---

## 🛠 Implementation Note for Builder Agent

When configuring the `ModelGateway` and `providers.yaml`:
1. **Tiered Routing**: Implement a logic where `Oversoul` requests are routed to the "High" reasoning models (Gemini Pro / Antigravity) and `Pillar` requests are routed to "Medium/Low" latency models (Gemini Flash / Cerebras Llama).
2. **Context-Aware Selection**: If the prompt exceeds 128k tokens, force routing to Google AI Studio (`gemini-2.5-pro/flash`) as other free tiers will fail.
3. **Sovereign Baseline**: Always attempt `Gemma 4-31B` (Local) first for Pillar-level tasks to minimize API dependency.
