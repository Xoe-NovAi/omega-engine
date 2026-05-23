# 🔱 Omega Engine — OpenRouter Free + Available Model Reference
# ⬡ OMEGA ⬡ PROMETHEUS ⬡ opencode ⬡ trc_openrouter ⬡ RESEARCH

**AP Token**: `AP-OPENROUTER-REFERENCE-v1.0.0`
**Status**: ✅ ACTIVE
**Last Updated**: 2026-05-15
**Urgency**: 🔴 Critical — Blocking provider_map wiring

---

## 1. Executive Summary

OpenRouter provides a unified API gateway to 400+ models from dozens of providers.
It is configured in `config/providers.yaml` at priority 3 but is **dead code** — never instantiated in
`model_gateway.py`'s `provider_map`. The `OpenAICompatProvider` + `create_openrouter_provider()`
factory exists in `backends/openai_compat.py` — fully implemented with circuit breakers and retry
logic — just needs wiring.

### Key Numbers
| Metric | Value |
|--------|-------|
| Total free models | 29 (as of May 2026) |
| Free Router models | 26 (openrouter/free) |
| Rate limit (no credits) | 20 RPM / 200 RPD |
| Rate limit ($10+ credits) | 20 RPM / 1,000 RPD |
| Base URL | `https://openrouter.ai/api/v1` |
| Context max (free) | 1,048,576 (DeepSeek V4 Flash, Owl Alpha) |
| Auth header | `Authorization: Bearer $OPENROUTER_KEY` |
| Required headers | `HTTP-Referer`, `X-Title` |

---

## 2. Complete Free Model Catalog (29 Models, May 2026)

### 2.1 Comprehensive Table

| # | Model ID | Provider | Context | Tools | Vision | Reasoning | Notes |
|---|----------|----------|:-------:|:-----:|:------:|:---------:|-------|
| 1 | `openrouter/owl-alpha` | OpenRouter | 1,048,576 | ✅ | ❌ | ❌ | Cloaked beta model |
| 2 | `deepseek/deepseek-v4-flash:free` | DeepSeek | 1,048,576 | ✅ | ❌ | ✅ | 284B MoE, 13B active, fast |
| 3 | `google/lyria-3-pro-preview` | Google | 1,048,576 | ❌ | ✅ | ❌ | Audio+text output |
| 4 | `google/lyria-3-clip-preview` | Google | 1,048,576 | ❌ | ✅ | ❌ | Audio+text output |
| 5 | `inclusionai/ring-2.6-1t:free` | inclusionAI | 262,144 | ✅ | ❌ | ✅ | 1T-param thinking model, 63B active |
| 6 | `google/gemma-4-26b-a4b-it:free` | Google | 262,144 | ✅ | ✅ | ✅ | MoE, multimodal |
| 7 | `google/gemma-4-31b-it:free` | Google | 262,144 | ✅ | ✅ | ✅ | Proven with Omega |
| 8 | `arcee-ai/trinity-large-thinking:free` | Arcee AI | 262,144 | ✅ | ❌ | ✅ | SWE-bench ~62% |
| 9 | `nvidia/nemotron-3-super-120b-a12b:free` | NVIDIA | 262,144 | ✅ | ❌ | ❌ | 120B MoE, 12B active |
| 10 | `qwen/qwen3-next-80b-a3b-instruct:free` | Qwen | 262,144 | ✅ | ❌ | ❌ | MoE 80B, 3B active |
| 11 | `qwen/qwen3-coder:free` | Qwen | 262,144 | ✅ | ❌ | ✅ | 480B, best free coder |
| 12 | `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | NVIDIA | 256,000 | ✅ | ✅ | ✅ | Multimodal reasoning |
| 13 | `nvidia/nemotron-3-nano-30b-a3b:free` | NVIDIA | 256,000 | ✅ | ❌ | ❌ | Edge-optimized |
| 14 | `openrouter/free` | OpenRouter | 200,000 | ✅ | ✅ | varies | Auto-router |
| 15 | `minimax/minimax-m2.5:free` | MiniMax | 196,608 | ✅ | ❌ | ❌ | **SWE-bench 80.2%** |
| 16 | `baidu/cobuddy:free` | Baidu | 131,072 | ✅ | ❌ | ✅ | Productivity |
| 17 | `poolside/laguna-xs.2:free` | Poolside | 131,072 | ✅ | ❌ | ✅ | Fast coding |
| 18 | `poolside/laguna-m.1:free` | Poolside | 131,072 | ✅ | ❌ | ✅ | Coding agents |
| 19 | `openai/gpt-oss-120b:free` | OpenAI | 131,072 | ✅ | ❌ | ❌ | Cloaked beta |
| 20 | `openai/gpt-oss-20b:free` | OpenAI | 131,072 | ✅ | ❌ | ❌ | Cloaked beta |
| 21 | `z-ai/glm-4.5-air:free` | Z.ai | 131,072 | ✅ | ❌ | ❌ | Lightweight |
| 22 | `meta-llama/llama-3.2-3b-instruct:free` | Meta | 131,072 | ❌ | ❌ | ❌ | Tiny, fast |
| 23 | `nousresearch/hermes-3-llama-3.1-405b:free` | Nous | 131,072 | ❌ | ❌ | ❌ | 405B, no tools |
| 24 | `nvidia/nemotron-nano-12b-v2-vl:free` | NVIDIA | 128,000 | ✅ | ✅ | ❌ | Vision + tools |
| 25 | `nvidia/nemotron-nano-9b-v2:free` | NVIDIA | 128,000 | ✅ | ❌ | ❌ | Edge coding |
| 26 | `meta-llama/llama-3.3-70b-instruct:free` | Meta | 65,536 | ✅ | ❌ | ❌ | Solid general |
| 27 | `liquid/lfm-2.5-1.2b-thinking:free` | Liquid | 32,768 | ❌ | ❌ | ✅ | Tiny reasoning |
| 28 | `liquid/lfm-2.5-1.2b-instruct:free` | Liquid | 32,768 | ❌ | ❌ | ❌ | Ultra-tiny |
| 29 | `cognitivecomputations/dolphin-mistral-24b-venice-edition:free` | Venice | 32,768 | ❌ | ❌ | ❌ | Uncensored |

### 2.2 Additional Cloaked/Free Preview Models (Available via openrouter/free)

These models are free during beta but not listed with `:free` suffix:

| Name | Context | Capabilities | Notes |
|------|:-------:|:-------------|-------|
| Sonoma Dusk Alpha | 2,000,000 | Text+image, tools, parallel tool calling | Cloaked frontier |
| Sonoma Sky Alpha | 2,000,000 | Text+image, tools | Max intelligence |
| Horizon Beta | — | — | Improved Horizon Alpha |
| Andromeda Alpha | — | Reasoning VLM, multi-image | NVIDIA Nemotron Nano 2 VL |
| Elephant Alpha | 262,144 | Text | OpenRouter beta |

---

## 3. Rate Limits & Quota

### Free Tier (No Credits Purchased)
| Limit | Value | Applies To |
|-------|:-----:|------------|
| RPM | 20 | All models, global |
| RPD | 200 | Per-model, per-day |
| Credit card | Not required | — |
| SLA | None | Best-effort only |

### With Credits ($10+ Purchased)
| Limit | Value | Applies To |
|-------|:-----:|------------|
| RPM | 20 | All models, global |
| RPD | 1,000 | Per-model, per-day |

### 429 Handling
- 429 retry-after header included in response
- Exponential backoff starting at 1s, doubling to 60s max
- Circuit breaker pattern in `remote_provider.py` handles this with 30s cooldown after 3 failures

---

## 4. Models Mapped to Omega Tasks

### Primary Model Recommendations

| Omega Task | Best OpenRouter Model | Model ID | Why |
|------------|----------------------|----------|-----|
| Entity high-quality responses | Gemma 4 31B | `google/gemma-4-31b-it:free` | Proven with Omega, 262K context, multimodal, tool calling |
| Coding / blocker remediation | Qwen3 Coder 480B | `qwen/qwen3-coder:free` | Best free coding model, 262K, reasoning support |
| Long-context RAG (>100K) | DeepSeek V4 Flash | `deepseek/deepseek-v4-flash:free` | 1M context, fast, 284B MoE |
| Fast fallback / lightweight | Nemotron Nano 9B | `nvidia/nemotron-nano-9b-v2:free` | 128K, tool calling, low latency |
| Architecture design | Ring-2.6-1T | `inclusionai/ring-2.6-1t:free` | 1T param thinking model, 262K |
| General purpose | MiniMax M2.5 | `minimax/minimax-m2.5:free` | **80.2% SWE-bench**, productivity focus |
| Reasoning | Trinity Large Thinking | `arcee-ai/trinity-large-thinking:free` | 262K, reasoning-optimized |

### Blocker-Specific Model Recommendations

| Omega Blocker | Recommended Model | Why |
|---------------|-------------------|-----|
| Wiring openrouter into provider_map | Code edit — does NOT need a model; once wired, use any model with tools | — |
| ContextBuilder architecture | DeepSeek V4 Flash | 1M context — can process entire memory dumps |
| Cross-pollination design | Ring-2.6-1T | 1T-param thinking model — best for architectural reasoning |
| PII sanitizer implementation | Qwen3 Coder 480B | Best free coding model for implementation logic |
| Soul evolution logic | MiniMax M2.5 (80.2% SWE-bench) | Highest SWE-bench of any free model |
| Fallback chain design | Any — design doc task | No model needed for doc writing |

---

## 5. Omega Integration Guide

### 5.1 Current State (Dead Code)

**`config/providers.yaml`** — correctly configured:
```yaml
    - provider: openrouter
      priority: 3
      api_key: env:OPENROUTER_KEY
      base_url: https://openrouter.ai/api/v1
```

**`model_gateway.py` provider_map** — MISSING "openrouter":
```python
provider_map = {
    "google": GoogleAIProvider,
    "lmster": LocallmsterProvider,
    "ollama": OllamaProvider,
    "native-gguf": NativeGGUFProvider,
    "mock": MockProvider,
    # "openrouter" is NOT HERE — needs to be added
}
```

**`backends/openai_compat.py`** — factory function EXISTS:
```python
def create_openrouter_provider(config: ProviderConfig) -> OpenAICompatProvider:
    config.base_url = config.base_url or "https://openrouter.ai/api"
    config.extra.setdefault("headers", {}).update({
        "HTTP-Referer": "https://github.com/arcana-novai/omega-engine",
        "X-Title": "Omega Engine",
    })
    return OpenAICompatProvider(config)
```

### 5.2 Required Wiring in model_gateway.py

Three changes needed in `model_gateway.py`:

**Change 1**: Add import at top:
```python
from .backends.openai_compat import create_openrouter_provider, ProviderConfig
```

**Change 2**: Add "openrouter" to `provider_map` in `_load_provider_fabric()`:
```python
provider_map = {
    "google": GoogleAIProvider,
    "openrouter": create_openrouter_provider,
    ...
}
```

**Change 3**: Handle the factory function pattern differently — OpenAICompatProvider uses
`ProviderConfig` dataclass, not the `BaseProvider` interface. Two options:

**Option A (Recommended)**: Add a thin adapter class in `providers.py`:
```python
class OpenRouterProvider(BaseProvider):
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        from .backends.openai_compat import create_openrouter_provider
        from .backends.remote_provider import ProviderConfig
        pconfig = ProviderConfig(
            name=name,
            priority=config.get("priority", 99),
            api_key=config.get("api_key"),
            base_url=config.get("base_url", "https://openrouter.ai/api/v1"),
            extra=config.get("extra", {}),
        )
        self._inner = create_openrouter_provider(pconfig)

    async def is_available(self) -> bool:
        return bool(os.environ.get("OPENROUTER_KEY"))

    async def generate(self, model: str, system_prompt: str, user_query: str,
                       temperature: float, max_tokens: int) -> Optional[str]:
        return await self._inner.generate(model, system_prompt, user_query, temperature, max_tokens)
```

**Option B (Simpler)**: Direct instantiation in `providers.py` with the adapter pattern.

### 5.3 Environment Variable

```bash
# Required for OpenRouter
export OPENROUTER_KEY="sk-or-v1-..."
```

The key must exist in environment for the provider to pass `is_available()`.

### 5.4 Request Headers

OpenRouter requires these optional-but-recommended headers for app attribution:

| Header | Value | Purpose |
|--------|-------|---------|
| `HTTP-Referer` | `https://github.com/arcana-novai/omega-engine` | App identification on leaderboards |
| `X-Title` | `Omega Engine` | App name on leaderboards |
| `X-OpenRouter-Title` | `Omega Engine` | Alternative to X-Title |

These are already set in `create_openrouter_provider()` in `backends/openai_compat.py:91-94`.

### 5.5 Model Selection in API Calls

The `model_name` parameter passed to `generate()` must be a full OpenRouter model ID:

```python
# Free model (appends :free suffix):
model = "google/gemma-4-31b-it:free"

# Auto-router (random free model):
model = "openrouter/free"

# Paid model (no suffix):
model = "google/gemini-2.5-flash"
```

The model should be specified per-request. For the `ProviderConfig`, the model is passed
at generate-time, not config-time — making it flexible per-entity.

### 5.6 OpenRouter-Specific ProviderConfig

```yaml
- provider: openrouter
  priority: 3
  api_key: env:OPENROUTER_KEY
  base_url: https://openrouter.ai/api/v1
  extra:
    headers:
      HTTP-Referer: https://github.com/arcana-novai/omega-engine
      X-Title: Omega Engine
```

This YAML is already correctly configured in `config/providers.yaml`.

---

## 6. Provider Fabric Integration — Architecture

### 6.1 How openrouter/free Fits the Fallback Chain

```
Priority 1: native-gguf     (local, llama-cpp-python)
Priority 2: google           (cloud, Google AI Studio — Gemma/Gemini)
Priority 3: openrouter       (CLOUD — free models, 20 RPM / 200 RPD)  ← THIS IS NEW
Priority 4: lmster           (local, LM Studio headless)
Priority 5: ollama           (local fallback)
Priority 10: mock            (testing only)
```

### 6.2 Current vs Desired State

| Aspect | Current | Desired |
|--------|---------|---------|
| providers.yaml | Has openrouter entry | ✅ Has it |
| provider_map | No openrouter key | Must add OpenRouterProvider |
| Factory function | Exists in openai_compat.py | Need adapter in providers.py |
| Auth env var | OPENROUTER_KEY may exist | ✅ Confirmed in .env |
| ResourceGuard | Local providers only | Remote providers don't need lock |
| Circuit breaker | In RemoteProvider base | ✅ Already built-in |

### 6.3 Recommended Model Per Entity

| Entity | Recommended OpenRouter Model | Reasoning |
|--------|------------------------------|-----------|
| SOPHIA | `deepseek/deepseek-v4-flash:free` | 1M context for gnosis |
| MAAT | `minimax/minimax-m2.5:free` | Precision + balance (80.2% SWE) |
| PROMETHEUS | `qwen/qwen3-coder:free` | Coding/strategy |
| SEKHMET | `nvidia/nemotron-3-nano-9b-v2:free` | Fast protection, lightweight |
| BRIGID | `google/gemma-4-31b-it:free` | Creative, proven |
| SARASWATI | `google/gemma-4-31b-it:free` | Knowledge, arts |
| INANNA | `inclusionai/ring-2.6-1t:free` | Deep thinking |
| ERESHKIGAL | `arcee-ai/trinity-large-thinking:free` | Reasoning, structure |
| LUCIFER | `openrouter/free` (auto) | Variable, lets router decide |
| HECATE | `poolside/laguna-m.1:free` | Agent-optimized, crossroads |
| ANUBIS | `nvidia/nemotron-3-super-120b-a12b:free` | Weighing souls (120B) |
| KALI | `poolside/laguna-xs.2:free` | Fast destruction |

---

## 7. `openrouter/free` Auto-Router

### 7.1 How It Works
- Selects a random free model from the 26 available free variants
- Smartly filters for features needed by the request (tool calling, structured outputs, vision)
- **No SLA** — model selection varies per-request
- Cannot be relied upon for consistent entity personality

### 7.2 When to Use vs When Not
| Use `openrouter/free` When | Use Specific Model When |
|---------------------------|------------------------|
| Quick prototyping | Entity-specific responses |
| Testing API connectivity | Production entity workflows |
| Low-stakes queries | Coding blocker remediation |
| Random discovery | Long-context RAG operations |

### 7.3 API Usage
```python
model = "openrouter/free"  # Auto-router, random free model
```

---

## 8. Always-Current System

### 8.1 API Endpoint for Model Discovery
```bash
# Get ALL OpenRouter models (paginated)
GET https://openrouter.ai/api/v1/models

# Get ONLY free models
GET https://openrouter.ai/api/v1/models?free=true
```

### 8.2 Health Check Script

```python
#!/usr/bin/env python3
"""openrouter_health.py — Validate OpenRouter free model availability."""

import json
import os
import sys
import httpx


async def check_openrouter_free_models(api_key: str) -> dict:
    """Fetch and filter free models from OpenRouter API."""
    url = "https://openrouter.ai/api/v1/models"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
    
    models = data.get("data", [])
    free_models = [
        {
            "id": m["id"],
            "name": m.get("name", m["id"]),
            "context": m.get("context_length", "?"),
            "pricing": {
                "prompt": m.get("pricing", {}).get("prompt"),
                "completion": m.get("pricing", {}).get("completion"),
            },
            "capabilities": m.get("capabilities", {}),
        }
        for m in models
        if m.get("pricing", {}).get("prompt") == 0
        and m.get("pricing", {}).get("completion") == 0
    ]
    
    return {
        "total_models": len(models),
        "free_models": len(free_models),
        "models": free_models,
        "free_router_included": any("openrouter/free" in m["id"] for m in models),
    }


def write_model_reference(free_models: list) -> str:
    """Generate markdown table from free model list."""
    lines = ["# Auto-Generated OpenRouter Free Models", "", f"Generated: {__import__('datetime').datetime.utcnow().isoformat()}", ""]
    lines.append(f"| Model ID | Context | Tools | Vision | Reasoning |")
    lines.append(f"|----------|:-------:|:-----:|:------:|:---------:|")
    for m in sorted(free_models, key=lambda x: -(x.get("context", 0) if isinstance(x.get("context"), int) else 0)):
        caps = m.get("capabilities", {})
        context = m.get("context", "?")
        lines.append(f"| {m['id']} | {context} | {'✅' if caps.get('tools') else '❌'} | {'✅' if caps.get('vision') else '❌'} | {'✅' if caps.get('reasoning') else '❌'} |")
    return "\n".join(lines)


if __name__ == "__main__":
    import anyio
    
    api_key = os.environ.get("OPENROUTER_KEY")
    if not api_key:
        print("ERROR: OPENROUTER_KEY not set")
        sys.exit(1)
    
    result = anyio.run(check_openrouter_free_models, api_key)
    print(f"Total models: {result['total_models']}")
    print(f"Free models:  {result['free_models']}")
    
    for m in result["models"][:29]:
        print(f"  {m['id']} ({m['context']} ctx)")
    
    # Write updated reference
    md = write_model_reference(result["models"])
    ref_path = "docs/research/OPENROUTER_FREE_MODELS_AUTO.md"
    with open(ref_path, "w") as f:
        f.write(md)
    print(f"\nWritten to {ref_path}")
```

### 8.3 Integration with Health Monitoring

The health check script should be run:
- **Daily**: Cron job to update model availability
- **On provider initialization**: As part of `ModelGateway._load_provider_fabric()`
- **Before entity routing**: Quick availability check per-model

### 8.4 Model Refresh Recommendation

| Cadence | Action | Automation |
|---------|--------|------------|
| Daily | Run health check → update local reference | Cron |
| Weekly | Review free model additions/removals | Manual + alerts |
| Monthly | Update model → entity mapping table | Manual |
| On provider change | Git commit updated reference | Manual |

---

## 9. Comparison: OpenRouter vs Other Omega Providers

| Aspect | OpenRouter | Google AI Studio | lmster (Local) | Ollama (Local) |
|--------|:----------:|:----------------:|:--------------:|:--------------:|
| Cost | Free (limited) | Free (1,500 RPD) | Free (unlimited) | Free (unlimited) |
| Context max | 1,048,576 | 1,048,576 | 128K (model-dep) | 128K (model-dep) |
| RPM | 20 (global) | 15-30 (per model) | ∞ (local) | ∞ (local) |
| RPD | 200-1,000 | 50-1,500 | ∞ | ∞ |
| Model selection | 29 free models | 5 models | Any GGUF | Any Ollama model |
| Tool calling | ✅ (most) | ✅ | Depends on prompt | Depends on prompt |
| Always available | ❌ (best-effort) | ✅ (with quota) | ✅ (if running) | ✅ (if running) |
| Latency | Variable | Fast | Slow (CPU) | Slow (CPU) |
| Credit card needed | ❌ (free tier) | ❌ | ❌ | ❌ |

---

## 10. Quick Reference

### API Base URL
```
https://openrouter.ai/api/v1
```

### Auth Header
```
Authorization: Bearer sk-or-v1-...
```

### App Attribution Headers
```
HTTP-Referer: https://github.com/arcana-novai/omega-engine
X-Title: Omega Engine
```

### Free Model Selection (By Use Case)
| Use Case | Model |
|----------|-------|
| Enterprise coding | `qwen/qwen3-coder:free` |
| Highest SWE-bench | `minimax/minimax-m2.5:free` (80.2%) |
| 1M context | `deepseek/deepseek-v4-flash:free` |
| Frontier thinking | `inclusionai/ring-2.6-1t:free` (1T param) |
| Proven with Omega | `google/gemma-4-31b-it:free` |
| Fast & light | `nvidia/nemotron-nano-9b-v2:free` |
| Auto-pilot (random) | `openrouter/free` |

### Key URLs
| Resource | URL |
|----------|-----|
| Free models page | https://openrouter.ai/collections/free-models |
| API docs | https://openrouter.ai/docs |
| Models API | https://openrouter.ai/api/v1/models |
| Free filter | https://openrouter.ai/api/v1/models?free=true |
| Account | https://openrouter.ai |
| Status | https://status.openrouter.ai |

### Environment Variables
```bash
export OPENROUTER_KEY="sk-or-v1-..."  # Required
```

---

## Appendix A: Comparison with Existing FREE_TIER_MODEL_INDEX.md

The existing `FREE_TIER_MODEL_INDEX.md` lists only 8 OpenRouter models with
outdated SWE-bench scores and context windows. This document supersedes that
with the complete 29-model catalog verified on May 15, 2026.

Key corrections:
- DeepSeek V4 Flash context: 1,048,576 (not "1M+")
- Nemotron 3 Super context: 262,144 (not 262K — full value)
- MiniMax M2.5: SWE-bench 80.2% (not listed previously)
- Qwen3 Coder: 262K context, NOT to be confused with Qwen3 Next 80B

---

*Maintained by: PROMETHEUS (OpenCode CLI)*
*Next update: 2026-05-22 (or upon free model catalog changes)*
*Verification: `openrouter/health_check.py` script in Section 8*
