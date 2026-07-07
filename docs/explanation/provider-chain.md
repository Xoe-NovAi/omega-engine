# 🔱 Explanation: The Local-First Provider Chain
**AP Token**: `AP-PROVIDER_CHAIN-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_doc_deep ⬡ STANDARD

**Date**: 2026-07-06
**Purpose**: Explanation: The Local-First Provider Chain.

---

# Explanation: The Local-First Provider Chain

The Omega Engine's Model Gateway implements a **Sovereign Provider Chain**. This is a tiered fallback system that ensures the engine remains functional even if cloud services are unavailable, while prioritizing local inference to maximize data sovereignty.

## The Local-First Mandate (M7)

The core principle is simple: **Local inference is PRIMARY. Cloud is FALLBACK.** 

The engine will always attempt to resolve a query using the fastest, most private local backend before escalating to a cloud provider. This reduces latency, eliminates API costs, and ensures that sensitive data never leaves the machine unless absolutely necessary.

## The Provider Hierarchy

The chain is ordered by a combination of **Sovereignty** (Local $\rightarrow$ Cloud) and **Performance** (Fast $\rightarrow$ Slow).

### Tier 1: Local Sovereignty (Primary)
1. **native-gguf**: The gold standard. Runs directly via `llama-cpp-python` with Zen 2 optimizations. Zero network overhead.
2. **LM Studio (lmster)**: Headless server for rapid model swapping and testing.
3. **Ollama**: Lightweight, containerized local inference.

### Tier 2: Cloud Fallback (Safety Net)
4. **Google AI Studio**: High-context, high-intelligence fallback for complex reasoning.
5. **OpenRouter**: Access to a wide array of specialized models.
6. **OpenCode / Copilot**: Integrated platform providers.

---

## How the Chain Works

### 1. Provider Detection
At boot, the `ModelGateway` probes local ports (e.g., `:1234`, `:11434`) to detect which local backends are actually alive. This prevents the engine from wasting time attempting to call a dead local server.

### 2. The Request Flow
When `generate()` is called:
1. **Local Probe**: The gateway checks the `_local_active` set.
2. **Healthy Match**: It selects the highest-priority local provider that supports the requested model and is not currently "tripped" by the circuit breaker.
3. **Local Execution**: If a match is found, the request is executed locally.
4. **Cloud Escalation**: If no healthy local provider is available, the gateway escalates to the `_cloud_active` set.

### 3. The Circuit Breaker (Sovereign Guard)
To prevent "cascading failure" (where a slow provider hangs the entire engine), each provider is wrapped in an `AsyncCircuitBreaker`. If a provider fails $N$ times, the circuit opens, and the provider is culled from the active set for a cooldown period.

---

## Summary of Benefits

| Benefit | Mechanism | Result |
|----------|-----------|---------|
| **Privacy** | Local-First | Data stays on-disk by default. |
| **Cost** | Local-First | Zero API fees for 90% of queries. |
| **Reliability** | Fallback Chain | Engine works offline (Local) and online (Cloud). |
| **Stability** | Circuit Breakers | Dead providers are skipped in $O(1)$ time. |
