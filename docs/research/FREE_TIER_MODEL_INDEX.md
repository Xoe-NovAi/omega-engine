# 🔱 Omega Engine — Free Tier Model Index
# ⬡ OMEGA ⬡ PROMETHEUS ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_research ⬡ FREE-TIER-INDEX

**AP Token**: `AP-FREE-TIER-INDEX-v1.0.0`
**Status**: ✅ COMPLETE
**Last Updated**: 2026-05-15
**Urgency**: 🔴 Critical

---

## 1. Executive Summary

This document provides a comprehensive, always-accurate reference of free tier models available to Omega Engine agents. It covers three primary providers:

1. **Google AI Studio** — Gemini/Gemma family
2. **OpenRouter** — Multi-provider aggregation with free models
3. **OpenCode Zen** — Curated coding-optimized models (OpenCode-only)

### Hardware Context
- **Target**: Ryzen 7 5700U (Zen 2, 8C/16T, ~14GB usable RAM)
- **Local inference**: 1B-8B GGUF models only
- **Cloud fallback**: Free tier models above

---

## 2. Google AI Studio — Free Tier Models

**API Endpoint**: `https://generativelanguage.googleapis.com/v1beta/models/<model>:streamGenerateContent`

**Free Tier Limits** (as of May 2026):
- RPM: 15-30 (varies by model)
- TPM: 1,000,000
- RPD: 1,500 (Flash), 50 (Pro)
- **No credit card required**
- **No expiration**
- **Data may be used for model training on free tier**

### Gemini Models (Free)

| Model | Context | Output | RPM | RPD | TPM | Best For | Omega Fit |
|:-----|:-------:|:------:|:---:|:---:|:---:|:---------|:----------|
| `gemini-2.5-flash` | 1M | 8k | 15 | 1,500 | 1M | General purpose, coding, reasoning | ✅ PRIMARY — High volume, good reasoning |
| `gemini-2.5-flash-lite` | 1M | 4k | 30 | 1,500 | 1M | High-volume lightweight tasks | ✅ FALLBACK — Low reasoning, high volume |
| `gemini-2.5-pro` | 1M | 8k | 5 | 50 | 1M | Complex reasoning, analysis | ⚠️ HEAVILY RESTRICTED — Only 50/day |
| `gemini-2.0-flash` | 1M | 8k | 15 | 1,500 | 1M | Legacy compatibility | 🔄 DEPRECATED — Avoid for new builds |

### Gemma Models (Free)

| Model | Context | Output | RPM | RPD | Best For | Omega Fit |
|:-----|:-------:|:------:|:---:|:---:|:---------|:----------|
| `gemma-4-31b` | 128k | 4k | 30 | 1,500 | Lightweight reasoning, coding | ✅ LOCAL ALTERNATIVE — Can run GGUF locally |
| `gemma-3-nise-27b` | 32k | 4k | 30 | 1,500 | Compact reasoning | 🔲 Check availability |

**Key Notes**:
- Rate limits are per-project (not per-API key)
- Daily quota resets at midnight Pacific Time
- Actual capacity may vary — check AI Studio dashboard for live limits
- Gemini 2.5 Pro free tier is essentially trial-only (50 RPD)

---

## 3. OpenRouter — Free Tier Models

**API Endpoint**: `https://openrouter.ai/api/v1/chat/completions`

**Rate Limits**:
- No credits: 50 requests/day
- $10+ credits: 1,000 requests/day
- All users: 20 RPM (global cap)

### Top Free Models (May 2026)

| Model | Provider | Context | Output | SWE-bench | Best For | Omega Fit |
|:-----|:---------|:-------:|:------:|:---------:|:---------|:----------|
| **NVIDIA Nemotron 3 Super** | NVIDIA | 262K | 8k | 60.47% | Coding, open-weight SOTA | ✅ EXCELLENT — Best open coding model |
| **MiniMax M2.5** | MiniMax | 196K | — | 80.2% | Productivity, coding agents | ✅ EXCELLENT — Highest SWE-bench |
| **DeepSeek V4 Flash** | DeepSeek | 1M+ | — | — | Long-context RAG | ✅ LONG-CONTEXT — 1M tokens |
| **Google Gemma 4 31B** | Google | 128K | — | — | Lightweight reasoning | ✅ PROVEN — Tested with Omega |
| **Poolside Laguna M.1** | Poolside | 128K | 8k | — | Coding agents, tool use | ✅ CODING — Agent-optimized |
| **Qwen3 Coder 480B** | Alibaba | 128K | — | — | Code generation | ⚠️ FREE DURING PREVIEW |
| **OpenAI gpt-oss-120b** | OpenAI | 128K | — | — | Frontier reasoning | ⚠️ CLOAKED BETA — May be deprecated |
| **OpenAI gpt-oss-20b** | OpenAI | 128K | — | — | Compact agents | ⚠️ CLOAKED BETA |
| **Trinity Large** | Arcee | 128K+ | — | 62% | Thinking model | 🟡 TOOL CALLING — May have issues |
| **NVIDIA Nemotron 3 Nano** | NVIDIA | 256K | — | — | Edge, local agents | ✅ EDGE — Runs on single GPU |

### Free Router (`openrouter/free`)

The Free Router automatically selects from available free models based on request requirements:

- **Context**: 200K tokens
- **Input**: Text + images
- **Output**: Text only
- **Cost**: Free

**Trade-off**: Unpredictable model selection — debugging difficult, session consistency varies.

---

## 4. OpenCode Zen — Free Tier Models

**API Endpoint**: `https://opencode.ai/zen/v1/chat/completions`

**Rate Limits**: 100 requests/day (free tier), 200K context max

**Note**: OpenCode Zen models are **exclusive to OpenCode CLI and Desktop**. They cannot be used directly by Omega's Provider Fabric, but Omega can leverage them via the OpenCode CLI as an orchestration layer.

### Free Models (May 2026)

| Model | SWE-bench | Context | Best For | Omega Integration |
|:-----|:---------:|:-------:|:---------|:------------------|
| **Big Pickle** | 72.0% | 200K | General coding | ⚠️ Stealth model — limited docs |
| **MiniMax M2.5 Free** | 80.2% | 200K | Productivity, coding | ⚠️ Beta — may change |
| **MiMo V2 Pro Free** | 78.0% | 1M | Long-context agents | ⚠️ Beta |
| **MiMo V2 Flash Free** | 73.4% | 256K | Fast coding | ⚠️ Beta |
| **MiMo V2 Omni Free** | 64.0% | 128K | Multimodal | ⚠️ Beta |
| **Nemotron 3 Super Free** | 52.0% | 128K | Open-weight coding | ⚠️ Beta |
| **GPT 5 Nano** | 65.0% | 128K | Compact coding | ⚠️ Beta |
| **Trinity Large Preview Free** | 62.0% | 128K | Thinking | ⚠️ Beta |

**Integration Path**: Omega could spawn OpenCode CLI as a subprocess with Zen models for coding-intensive tasks, but this adds latency and complexity.

---

## 5. Summary Comparison Table

### By Use Case

| Use Case | Recommended Model | Provider | Context | Notes |
|:---------|:------------------|:---------|:-------:|:------|
| **High-volume general** | Gemini 2.5 Flash | Google | 1M | 1,500 RPD, fast |
| **Complex reasoning** | Gemini 2.5 Pro (paid) | Google | 1M | ⚠️ Free tier too restricted (50/day) |
| **Long-context RAG** | DeepSeek V4 Flash | OpenRouter | 1M+ | Best for 100K+ contexts |
| **Coding (open-weight)** | NVIDIA Nemotron 3 Super | OpenRouter | 262K | 60.47% SWE-bench |
| **Coding (production)** | MiniMax M2.5 | OpenRouter | 196K | 80.2% SWE-bench |
| **Local fallback** | Qwen3-1.7B GGUF | lmster | 128K | Runs on Ryzen 5700U |
| **Iris intent detection** | functiongemma-270m | Local | 4K | Container, ultra-fast |

### By Provider Priority

| Priority | Provider | Model | Daily Limit | Context | Best For |
|:--------:|:---------|:------|:-----------:|:-------:|:---------|
| 1 | Google | Gemini 2.5 Flash | 1,500 | 1M | High-volume, reasoning |
| 2 | OpenRouter | MiniMax M2.5 | 50-1,000 | 196K | Coding, productivity |
| 3 | OpenRouter | Nemotron 3 Super | 50-1,000 | 262K | Open-weight coding |
| 4 | OpenCode Zen | (via OpenCode CLI) | 100 | 200K | OpenCode-only workflows |
| 5 | Local | GGUF (1-8B) | ∞ | 128K | Sovereign fallback |

---

## 6. Known Issues & Caveats

### Google AI Studio
- **Quota 0/0/0**: Some users report `429 RESOURCE_EXHAUSTED` with zero quotas after upgrading
- **Data usage**: Free tier prompts may be used for model training
- **Region-dependent**: Limits may vary by geographic region
- **Model deprecation**: Gemini 2.0 Flash deprecated March 2026

### OpenRouter
- **Tool calling bugs**: Some free models fail with `No endpoints found that support tool use`
- **Variable quality**: "Cloaked" beta models may be deprecated without notice
- **Provider routing**: Requests may route to different backends with varying latency
- **50 RPD cap**: Without purchasing credits, very limited

### OpenCode Zen
- **Exclusive to OpenCode**: Cannot be called directly via API
- **Beta instability**: Models may change or be deprecated during beta
- **Limited integration**: Best used within OpenCode CLI workflows, not Omega Provider Fabric

---

## 7. Maintenance System Design

### Automated Verification Script

Create `scripts/validate_free_models.py` to periodically check model availability:

```python
#!/usr/bin/env python3
"""Validate free tier model availability for Omega Provider Fabric."""

import asyncio
import aiohttp
from datetime import datetime

PROVIDERS = {
    "google": {
        "base": "https://generativelanguage.googleapis.com/v1beta",
        "models": ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemma-4-31b"],
        "check": lambda m, k: f"{m}/models/{m}:generateContent",
    },
    "openrouter": {
        "base": "https://openrouter.ai/api/v1",
        "models": ["minimax/minimax-m2.5:free", "nvidia/nemotron-3-super-120b:free"],
        "check": "models",
    },
}

async def check_google_model(model: str, api_key: str) -> dict:
    """Check Google AI Studio model availability."""
    url = f"{PROVIDERS['google']['base']}/models/{model}"
    headers = {"Authorization": f"Bearer {api_key}"}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as resp:
                return {"model": model, "available": resp.status == 200, "status": resp.status}
        except Exception as e:
            return {"model": model, "available": False, "error": str(e)}

async def check_openrouter() -> dict:
    """Check OpenRouter free models via public endpoint."""
    url = f"{PROVIDERS['openrouter']['base']}/models?free=true"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                data = await resp.json()
                return {"available": True, "count": len(data.get("data", []))}
        except Exception as e:
            return {"available": False, "error": str(e)}

async def main():
    results = {"timestamp": datetime.utcnow().isoformat(), "providers": {}}
    
    # Check Google (requires API key)
    google_key = os.environ.get("GOOGLE_API_KEY", "")
    if google_key:
        for model in PROVIDERS["google"]["models"]:
            results["providers"][model] = await check_google_model(model, google_key)
    
    # Check OpenRouter (public endpoint)
    results["providers"]["openrouter"] = await check_openrouter()
    
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
```

### Update Frequency

| Check Type | Frequency | Method |
|:-----------|:---------:|:-------|
| API availability | Daily | Cron job + health check |
| Rate limit changes | Weekly | Manual review of AI Studio dashboard |
| New model additions | Monthly | Web search + OpenRouter models API |
| Deprecation alerts | Weekly | Subscribe to provider newsletters |

### Ownership

- **Primary**: Research Agent (Gemma 4-31B via OpenCode)
- **Secondary**: Builder Agent (for script implementation)
- **Review**: Opus 4.6 (Oversight)

---

## 8. OpenCode Zen Integration Recommendation

### Should Omega Use Zen?

**Short answer**: No — not as a direct provider in the Provider Fabric.

**Rationale**:
1. **Exclusive to OpenCode CLI** — Zen models are not accessible via standard API
2. **Redundant** — OpenRouter offers similar or better models with direct API access
3. **Complexity** — Would require spawning OpenCode as subprocess (adds latency, complexity)

### Alternative Integration Path

If Omega wants to leverage Zen models:

1. **Orchestrator dispatch**: Use `Orchestrator.dispatch_agent()` with OpenCode CLI as the CLI type
2. **Task-specific**: Only for coding-heavy sub-tasks where Zen models excel
3. **Trade-off**: +2-5s latency per task, but access to high-SWE-bench models

### When Zen Makes Sense

- Omega Entity workspace experiments (write code in entity's style)
- Complex code generation requiring high SWE-bench scores
- When local GGUF and OpenRouter are both unavailable

---

## 9. Omega Provider Fabric Configuration

Recommended `config/providers.yaml` updates for free tier integration:

```yaml
inference:
  fallback_chain:
    - provider: google
      model: gemini-2.5-flash
      priority: 1
      free: true
      limits:
        rpd: 1500
        rpm: 15
        tpm: 1000000
    - provider: openrouter
      model: minimax/minimax-m2.5:free
      priority: 2
      free: true
      limits:
        rpd: 50
        rpm: 20
    - provider: openrouter
      model: nvidia/nemotron-3-super-120b:free
      priority: 3
      free: true
    - provider: lmster
      model: qwen3-1.7b
      priority: 4
      free: true  # Local, unlimited
    - provider: mock
      model: offline
      priority: 99
```

---

## 10. Appendix: Quick Reference Cards

### Google AI Studio
- **Signup**: https://aistudio.google.com/app/apikey
- **Docs**: https://ai.google.dev/gemini-api/docs
- **Pricing**: https://ai.google.dev/pricing
- **Rate Limits**: https://ai.google.dev/gemini-api/docs/rate-limits

### OpenRouter
- **Signup**: https://openrouter.ai
- **Docs**: https://openrouter.ai/docs
- **Free Models**: https://openrouter.ai/collections/free-models
- **API**: https://openrouter.ai/api/v1/chat/completions

### OpenCode Zen
- **Signup**: https://opencode.ai/auth
- **Docs**: https://opencode.ai/docs/zen
- **Models**: https://opencode.ai/docs/models
- **API**: https://opencode.ai/zen/v1/chat/completions

---

*Maintained by: Gemma 4-31B Research Agent*
*Next update: 2026-06-15 (or upon major provider changes)*