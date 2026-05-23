# 🔱 Omega Engine — R-04: Provider Fabric Fallback Chain Design

**AP Token**: `AP-RESEARCH-R04-v1.0.0`
**Status**: ✅ READY
**Last Updated**: 2026-05-14
**Target**: MVE (Minimum Viable Engine) Implementation

---

## 1. Executive Summary

The Omega Engine requires a resilient, high-capability inference pipeline that maximizes the use of free-tier frontier models while maintaining local sovereignty. This document defines the optimal ordered fallback chain, error handling policies, and configuration schema for the `ModelGateway` and `ProviderFabric`.

## 2. The Optimal Fallback Chain

To balance reasoning capability, latency, and rate-limit generosity, the following priority chain is recommended for the MVE.

### Ordered Priority

| Priority | Provider | Primary Role | Rationale |
| :--- | :--- | :--- | :--- |
| **1** | **Google AI Studio** | Primary Reasoning & Context | Best-in-class reasoning (Gemini Pro) and massive context windows. High reliability. |
| **2** | **Cerebras** | High-Speed Workhorse | Extreme throughput (~1000+ t/s) and very generous free-tier token limits. |
| **3** | **SambaNova** | Specialized Reasoning | High capability (DeepSeek), but restricted by very low Daily Request limits (20 RPD). |
| **4** | **lmster** | Local Sovereign | Absolute privacy and zero rate limits. Primary local fallback. |
| **5** | **Ollama** | Local Backup | Secondary local inference engine. |
| **6** | **OfflineMock** | Development/Test | Deterministic responses for CI/CD and offline dev. |

---

## 3. Operational Specifications

### 3.1 Timeouts & Error Handling

Each provider in the fabric must adhere to a specific timeout and error classification to prevent the chain from hanging.

| Provider | Timeout | Retryable Errors (Exponential Backoff) | Hard Failures (Immediate Failover) |
| :--- | :--- | :--- | :--- |
| **Google** | 30s | `HTTP 429` (Rate Limit), `HTTP 500/503` | `HTTP 400` (Safety/Bad Req), `HTTP 401` |
| **Cerebras** | 15s | `HTTP 429` (RPM/TPM), `HTTP 500/503` | `HTTP 400` (Context Limit), `HTTP 401` |
| **SambaNova** | 20s | `HTTP 429` (RPM/RPD), `HTTP 500/503` | `HTTP 400` (Bad Req), `HTTP 401` |
| **Local (LMS/Ollama)** | 60s | N/A (usually network timeout) | `HTTP 404` (Model Not Found) |

### 3.2 Google AI Studio Integration Strategy

**Recommendation**: **Use the OpenAI-compatible endpoint.**

- **Base URL**: `https://generativelanguage.googleapis.com/v1beta/openai/`
- **Pros**: 
    - **Uniformity**: Allows the `RemoteProvider` class to use a single request/response logic for Google, Cerebras, and SambaNova.
    - **Simplicity**: Eliminates the need for the `google-genai` SDK dependency, reducing the codebase footprint.
    - **Interchangeability**: Simplifies the implementation of a generic `ModelGateway` that can switch providers mid-stream based on confidence scores.

---

## 4. Proposed `providers.yaml` Schema

The following schema is proposed for the `config/providers.yaml` file to support the fallback chain.

```yaml
inference:
  strategy: cloud_priority # MVE prioritizes frontier reasoning
  fallback_chain:
    - provider: google
      priority: 1
      base_url: "https://generativelanguage.googleapis.com/v1beta/openai/"
      api_key: env:GEMINI_API_KEY
      timeout: 30
      models:
        primary: "gemini-2.5-flash"
        reasoning: "gemini-3.1-pro-preview"
        sovereign: "gemma-4"
    
    - provider: cerebras
      priority: 2
      base_url: "https://api.cerebras.ai/v1"
      api_key: env:CEREBRAS_API_KEY
      timeout: 15
      models:
        primary: "llama3.1-8b"
        reasoning: "gpt-oss-120b"
    
    - provider: sambanova
      priority: 3
      base_url: "https://api.sambanova.ai/v1"
      api_key: env:SAMBANOVA_API_KEY
      timeout: 20
      models:
        primary: "Meta-Llama-3.3-70B-Instruct"
        reasoning: "DeepSeek-V3.1"
    
    - provider: lmster
      priority: 4
      base_url: "http://127.0.0.1:1234/v1"
      timeout: 60
      models:
        primary: "qwen3-1.7b"
    
    - provider: ollama
      priority: 5
      base_url: "http://127.0.0.1:11434/v1"
      timeout: 60
      models:
        primary: "llama3"
    
    - provider: mock
      priority: 6
      timeout: 5
```

---

## 🛠 Implementation Note for Builder Agent

When implementing the `ProviderFabric` in `src/omega/oracle/model_gateway.py`:

1. **Abstract Provider Class**: Create a `BaseProvider` class that handles the OpenAI-compatible `chat/completions` request.
2. **Circuit Breaker**: Implement a `CircuitBreaker` that tracks `HTTP 429` errors per provider. If a provider hits its limit, mark it as "cooling down" and skip to the next priority in the chain.
3. **Context Window Safeguard**: Specifically for **Cerebras**, implement a hard cap of 8,192 tokens for prompt length to avoid `HTTP 400` errors on the free tier.
4. **Token Budgeting**: Ensure that the `ModelGateway` logs the `usage` field from the response to track consumption against free-tier limits.
