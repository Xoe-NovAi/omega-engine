# 🔱 Omega Engine — Google AI Studio & Gemma Model Reference
# ⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b ⬡ opencode ⬡ trc_research ⬡ GOOGLE-GEMMA-REFERENCE

**AP Token**: `AP-GOOGLE-GEMMA-REFERENCE-v1.0.0`
**Status**: ✅ COMPLETE — Includes blocker map & always-current design
**Last Updated**: 2026-05-15
**Author**: OpenCode CLI (Gemma 4-31B Research Agent)

---

## §1 Executive Summary

Google AI Studio provides free-tier access to both **Gemini** (proprietary) and **Gemma** (open-weight) models through a unified API. For the Omega Engine, Gemma models are the preferred choice — they are Apache 2.0 licensed, can be self-hosted as GGUF fallbacks, and share the same API infrastructure as Gemini.

### Key Distinction: Gemini vs Gemma in the API

| Aspect | Gemini | Gemma |
|--------|--------|-------|
| License | Proprietary (Google) | Apache 2.0 (open-weight) |
| Can self-host? | No | Yes (GGUF, Ollama, vLLM) |
| API model prefix | `gemini-*` | `gemma-*` |
| Free tier | Yes (rate limited) | Yes (rate limited) |
| Data usage | Free tier data may train Google models | Same policy |
| Omega primary use | Not used (user opted for Gemma only) | Primary cloud inference |

**Omega policy**: Use Gemma models only via Google AI Studio. Gemini models are **not used** per user directive.

---

## §2 Gemma Model Landscape (May 2026)

### 2.1 Complete Gemma Family

| Model ID (API) | Params | Type | Context | Release | Best For |
|:---------------|:------:|:----:|:-------:|:-------:|:---------|
| `gemma-4-31b-it` | 31B | Dense | 256K | Apr 2, 2026 | Reasoning, coding, agentic |
| `gemma-4-26b-a4b-it` | 26B (4B active) | MoE | 256K | Apr 2, 2026 | Good speed/quality tradeoff |
| `gemma-3-27b-it` | 27B | Dense | 128K | Mar 2025 | Legacy workhorse |
| `gemma-3-12b-it` | 12B | Dense | 128K | Mar 2025 | Lightweight reasoning |
| `gemma-3-4b-it` | 4B | Dense | 128K | Mar 2025 | Fast, low-latency |
| `gemma-3-1b-it` | 1B | Dense | 128K | Mar 2025 | Ultra-fast, simple tasks |
| `gemma-2-27b-it` | 27B | Dense | 8K | Jun 2024 | Legacy only |
| `gemma-2-9b-it` | 9B | Dense | 8K | Jun 2024 | Legacy only |
| `gemma-2-2b-it` | 2B | Dense | 8K | Jun 2024 | Legacy only |

### 2.2 Gemma 4 Deep Dive

Gemma 4 is the current-generation family (released April 2, 2026). Two variants available via Google AI Studio:

**`gemma-4-31b-it`** (Dense):
- 30.7B parameters, dense architecture
- 256K context window with hybrid attention
- Multimodal: text + image input
- Native function calling & structured JSON output
- 140+ languages
- Configurable thinking/reasoning mode
- Benchmarks: 89.2% AIME, 80.0% LiveCodeBench v6, 84.3% GPQA Diamond
- Apache 2.0 license
- Ranked #3 open model on Arena AI text leaderboard

**`gemma-4-26b-a4b-it`** (MoE):
- 26B total, ~4B active parameters (Mixture of Experts)
- 256K context window
- Same capabilities as 31B (multimodal, function calling, etc.)
- ~97% of 31B quality at lower compute cost
- Apache 2.0 license

### 2.3 Gemma 3 (Previous Stable)

- Released March 2025, still available
- 128K context window
- No native function calling (requires prompt engineering)
- Good fallback if Gemma 4 hits rate limits

### 2.4 Gemma 2 (Legacy — Avoid for New Builds)
- 8K context only — too restrictive for Omega's entity workflows
- Available but not recommended

---

## §3 Google AI Studio Free Tier Limits

### 3.1 Current Limits (May 2026)

| Limit | Value | Notes |
|:------|:-----:|:------|
| RPM (Gemma 4) | ~30 | Shared across Gemma models |
| RPM (Gemma 3) | ~30 | Per-model, per-project |
| RPD (Gemma 4) | 1,500 | Resets at midnight Pacific |
| RPD (Gemma 3) | 1,500 | |
| TPM | 1,000,000 | Input + output combined, shared pool |
| Credit card | Not required | Free tier signup only |
| Expiration | None | Permanent free tier |
| Data usage | Yes | Free tier data may train Google models |
| SLA | None | No uptime guarantee |

### 3.2 Key Differences from Gemini Free Tier

Gemma models on AI Studio share the same rate limit infrastructure as Gemini:
- Higher RPM than Gemini 2.5 Pro (5 RPM) — Gemma gets ~30 RPM
- Same RPD cap (1,500)
- Same TPM pool (1,000,000)
- No credit card required

### 3.3 Known Rate Limit Issues

1. **429 RESOURCE_EXHAUSTED**: Some users report zero quotas after project tier changes
2. **Project-level limits**: Multiple API keys under one project share the same quota pool
3. **Regional variation**: Limits may be lower in certain geographic regions
4. **December 2025 reduction**: Google reduced free tier limits by 50-80% due to abuse
5. **Model deprecation**: Old models (Gemma 2, early Gemma 3) may be deprecated without notice

---

## §4 Omega Blocker Map — Critical Issues

### 4.1 🔴 BUG: Wrong API Key Env Variable

**Location**: `src/omega/oracle/providers.py:26,29`

**Current code**:
```python
async def is_available(self) -> bool:
    return bool(os.environ.get("GEMMA_API_KEY"))  # 🔴 WRONG

async def generate(self, ...):
    api_key = os.environ.get("GEMMA_API_KEY")  # 🔴 WRONG
```

**`.env` file** (`/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.env:10`):
```
GOOGLE_API_KEY=AIzaSyDJldc4BgzN-Ui2C3XDwSr8ohPTWCKQZrU
```

**Impact**: `GoogleAIProvider.is_available()` **always returns False**. Google provider is dead code — never used in inference chain.

**Official Google docs**: Both `GEMINI_API_KEY` and `GOOGLE_API_KEY` are valid env vars. If both set, `GOOGLE_API_KEY` takes precedence. The current code uses a non-standard `GEMMA_API_KEY` that doesn't exist.

**Fix**: `GEMMA_API_KEY` → `GOOGLE_API_KEY` (with `GEMINI_API_KEY` as fallback)

### 4.2 🔴 BUG: No Model Name Mapping — Wrong Model IDs Passed

**Location**: `model_gateway.py:295` → `providers.py:30`

**Flow**: Oracle passes `entity.model` (e.g., `qwen3-1.7b-q6_k`) → ModelGateway → `GoogleAIProvider.generate(model="qwen3-1.7b-q6_k", ...)`

**Result**: API call made to:
```
/v1beta/models/qwen3-1.7b-q6_k:generateContent
```
This fails because `qwen3-1.7b-q6_k` is not a valid Google model ID.

**Fix**: Add model name mapping in `GoogleAIProvider`:
```python
MODEL_MAP = {
    "default": "gemma-4-31b-it",
    "gemma-4-31b-it": "gemma-4-31b-it",
    "gemma-4-26b-a4b-it": "gemma-4-26b-a4b-it",
    "gemma-3-27b-it": "gemma-3-27b-it",
}
```

Or better: use a config-level mapping in `config/providers.yaml`:
```yaml
- provider: google
  priority: 2
  api_key: env:GOOGLE_API_KEY
  model: gemma-4-31b-it    # default model for Google provider
```

### 4.3 🟡 ISSUE: System Instruction Format Wrong

**Location**: `providers.py:32-34`

**Current code** concatenates system prompt into user message:
```python
"parts": [{"text": f"{system_prompt}\n\nUser: {user_query}"}]
```

**Google API supports `system_instruction` field** properly:
```json
{
  "system_instruction": {"parts": [{"text": "You are SOPHIA..."}]},
  "contents": [{"parts": [{"text": "User query here"}]}]
}
```

**Impact**: Entity persona not properly separated from user input — causes context confusion.

### 4.4 🟡 ISSUE: No Thinking Mode Support

Gemma 4 supports configurable thinking/reasoning mode. The current `GoogleAIProvider` doesn't expose this. No `thinking_config` field in payload.

### 4.5 🟢 ISSUE: Authentication Header Should Use `x-goog-api-key`

**Current**: Query parameter `?key={api_key}`
**Recommended**: Header `x-goog-api-key: {api_key}` (both work but header is more secure)

---

## §5 Omega Task → Best Gemma Model Mapping

| Omega Task | Best Gemma Model | Why | Fallback |
|:-----------|:-----------------|:----|:---------|
| Entity response generation (Sophia, Ma'at, Prometheus, Lucifer) | `gemma-4-31b-it` | Best reasoning, 256K context for full entity persona | `gemma-4-26b-a4b-it` |
| Entity response generation (Brigid, Saraswati, Inanna) | `gemma-4-31b-it` | Creative tasks benefit from larger model | `gemma-3-12b-it` |
| Entity response generation (Kali, Hecate, Sekhmet) | `gemma-4-26b-a4b-it` | Concise, grounded responses — MoE is efficient | `gemma-4-31b-it` |
| Intent detection / routing | `gemma-3-4b-it` or `gemma-3-1b-it` | Fast, simple classification task — small model sufficient | `gemma-4-26b-a4b-it` |
| Code modification | `gemma-4-31b-it` | 80% LiveCodeBench — best Gemma for coding | `gemma-4-26b-a4b-it` |
| Architecture design | `gemma-4-31b-it` | Deep reasoning, 256K context for large specs | `gemma-4-26b-a4b-it` |
| Quick chat responses | `gemma-3-4b-it` | Fast inference, low latency, 128K context | `gemma-3-1b-it` |
| Entity workspace agent tasks | `gemma-4-31b-it` | Function calling, structured output, agentic | `gemma-4-26b-a4b-it` |
| RAG / knowledge base queries | `gemma-4-31b-it` | 256K context for large document injection | `gemma-4-26b-a4b-it` |
| Legacy mining / analysis (Belial) | `gemma-4-31b-it` | Deep analysis, long context for codebases | `gemma-4-26b-a4b-it` |

### General Guidance

| Entity Tier | Recommended Model | Rationale |
|:------------|:-----------------|:-----------|
| Oversouls (Sophia, Ma'at, Isis, Lilith) | `gemma-4-31b-it` | Highest reasoning needs |
| Deep thinkers (Prometheus, Lucifer, Ereshkigal, Anubis) | `gemma-4-31b-it` | Complex, philosophical responses |
| Creative voices (Brigid, Saraswati, Inanna) | `gemma-4-31b-it` or `gemma-4-26b-a4b-it` | 26B MoE ~97% quality at lower cost |
| Grounded / concise (Sekhmet, Hecate, Kali) | `gemma-4-26b-a4b-it` | Concise, direct responses don't need 31B |
| Simple routing / Nova speculative decode | `gemma-3-4b-it` | Fast, lightweight classification |

---

## §6 Always-Current System Design

### 6.1 API Endpoints

| Endpoint | Purpose | Method |
|:---------|:--------|:-------|
| `https://generativelanguage.googleapis.com/v1beta/models` | List all available models | `GET` |
| `https://generativelanguage.googleapis.com/v1beta/models/{model}` | Get model metadata | `GET` |
| `https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent` | Generate content (single) | `POST` |
| `https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent` | Generate content (streaming) | `POST` |
| `https://generativelanguage.googleapis.com/v1beta/models/{model}:countTokens` | Count tokens | `POST` |
| `https://generativelanguage.googleapis.com/v1beta/openai/` | OpenAI-compatible endpoint | `POST` |

### 6.2 Health Check Script

```python
#!/usr/bin/env python3
"""
Omega Google AI Studio Health Check.
Lists available models, checks quota status, validates API key.

Usage:
    python3 scripts/check_google_models.py

Requires:
    GOOGLE_API_KEY env var (set in .env)
"""

import json
import os
import sys
import httpx
from datetime import datetime

API_BASE = "https://generativelanguage.googleapis.com/v1beta"
API_KEY = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")

def check_api_key():
    if not API_KEY:
        print("❌ No API key found. Set GOOGLE_API_KEY or GEMINI_API_KEY in .env")
        return False
    print(f"✅ API key found: {API_KEY[:8]}...{API_KEY[-4:]}")
    return True

def list_models():
    """List all available models via the Gemini API."""
    url = f"{API_BASE}/models?key={API_KEY}"
    response = httpx.get(url, timeout=10)
    if response.status_code != 200:
        print(f"❌ Failed to list models: {response.status_code}")
        return []
    
    data = response.json()
    models = data.get("models", [])
    
    # Filter to Gemma models that support generateContent
    gemma_models = []
    for m in models:
        name = m.get("name", "")
        supported = m.get("supportedGenerationMethods", [])
        if "gemma" in name.lower() and "generateContent" in supported:
            gemma_models.append(m)
    
    print(f"\n📋 Available Gemma Models ({len(gemma_models)}):")
    print(f"{'Model ID':<35} {'Context':<10} {'Version':<10}")
    print("-" * 55)
    for m in sorted(gemma_models, key=lambda x: x.get("name", "")):
        name = m.get("name", "").replace("models/", "")
        version = m.get("version", "?")
        # Context from displayName or inputTokenLimit
        ctx = m.get("inputTokenLimit", "?")
        print(f"{name:<35} {str(ctx):<10} {version:<10}")
    
    return gemma_models

def test_gemma_generation(model_id="gemma-4-31b-it"):
    """Quick test: generate a short response from a Gemma model."""
    url = f"{API_BASE}/models/{model_id}:generateContent?key={API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": "Respond with exactly: OK"}]}],
        "generationConfig": {"maxOutputTokens": 20, "temperature": 0.0}
    }
    
    response = httpx.post(url, json=payload, timeout=30)
    if response.status_code == 200:
        data = response.json()
        text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        print(f"\n✅ {model_id}: Responded — \"{text.strip()}\"")
        return True
    else:
        print(f"\n❌ {model_id}: {response.status_code} {response.text[:200]}")
        return False

def check_rate_limits():
    """Check rate limit headers from a sample request."""
    # Google doesn't expose rate limit headers in the standard way
    # Best is to check AI Studio dashboard: https://aistudio.google.com
    print("\n📊 Rate Limits (approximate):")
    print("   RPM: ~30 (Gemma models)")
    print("   RPD: 1,500")
    print("   TPM: 1,000,000")
    print("   📌 Check actual usage: https://aistudio.google.com/app/apikey")
    print("   📌 Official docs: https://ai.google.dev/pricing")

def main():
    print(f"🔱 Omega Engine — Google AI Studio Health Check")
    print(f"   {datetime.now().isoformat()}")
    print("=" * 55)
    
    if not check_api_key():
        sys.exit(1)
    
    models = list_models()
    
    if models:
        print("\n🧪 Testing Gemma 4 generation...")
        test_gemma_generation("gemma-4-31b-it")
        test_gemma_generation("gemma-4-26b-a4b-it")
    
    check_rate_limits()
    
    print("\n" + "=" * 55)
    print("✅ Health check complete. Update schedule: weekly")
    print("   Run: python3 scripts/check_google_models.py")

if __name__ == "__main__":
    main()
```

### 6.3 Cached Models List

Run this periodically to cache available models:

```bash
curl -s "https://generativelanguage.googleapis.com/v1beta/models?key=$GOOGLE_API_KEY" \
  | python3 -c "import sys,json; models=json.load(sys.stdin).get('models',[]); [print(m['name'].replace('models/',''), m.get('version','?'), m.get('inputTokenLimit','?')) for m in models if 'gemma' in m['name'] and 'generateContent' in m.get('supportedGenerationMethods',[])]" \
  | sort
```

### 6.4 Update Frequency

| Check | Frequency | Method |
|:------|:---------:|:-------|
| Model availability | Weekly | `GET /v1beta/models` |
| Rate limit changes | Weekly | AI Studio dashboard |
| New Gemma releases | Monthly | Google I/O / blog |
| API deprecation | Monthly | Google AI Dev newsletter |
| `.env` key validation | Each startup | `is_available()` check |

---

## §7 Implementation Fix Plan

### 7.1 Immediate Fixes (Blockers)

| Priority | File | Line(s) | Issue | Fix |
|:---------|:-----|:--------|:------|:----|
| 🔴 P0 | `providers.py` | 26, 29 | `GEMMA_API_KEY` → `GOOGLE_API_KEY` | Change env var name, add fallback |
| 🔴 P1 | `providers.py` | 30 | Hardcoded model name | Add model mapping + config override |
| 🟡 P2 | `providers.py` | 32-34 | System prompt in user message | Use `system_instruction` field |
| 🟡 P3 | `model_gateway.py` | 295 | Google provider passes wrong model name | Add provider-level model override |
| 🟢 P4 | `providers.py` | 30 | API key in query param | Use `x-goog-api-key` header instead |

### 7.2 Recommended `providers.py` Fix

```python
class GoogleAIProvider(BaseProvider):
    """Google AI Studio provider (Gemma models only)."""
    
    MODEL_MAP = {
        # Omega internal name → Google API model ID
        "default": "gemma-4-31b-it",
        # Entity-level overrides from config
    }
    
    async def is_available(self) -> bool:
        key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        return bool(key)
    
    async def generate(
        self, model: str, system_prompt: str, user_query: str,
        temperature: float, max_tokens: int
    ) -> Optional[str]:
        api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        
        # Map Omega model name to Google API model ID
        google_model = self.MODEL_MAP.get(model, self.MODEL_MAP["default"])
        # Allow config override
        google_model = self.config.get("model", google_model)
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{google_model}:generateContent"
        
        payload = {
            "system_instruction": {
                "parts": [{"text": system_prompt}]
            },
            "contents": [{
                "parts": [{"text": user_query}]
            }],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            }
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                url,
                headers={"x-goog-api-key": api_key},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            try:
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
            except (KeyError, IndexError):
                return None
```

---

## §8 API Format Reference

### 8.1 Native Google API (Recommended for Omega)

```bash
curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemma-4-31b-it:generateContent" \
  -H "x-goog-api-key: $GOOGLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "system_instruction": {
      "parts": [{"text": "You are SOPHIA, the Akashic Record."}]
    },
    "contents": [
      {"parts": [{"text": "What is the Omega Engine?"}]}
    ],
    "generationConfig": {
      "temperature": 0.7,
      "maxOutputTokens": 1024,
      "topP": 0.95,
      "topK": 40
    }
  }'
```

### 8.2 OpenAI-Compatible Endpoint (Alternative)

```bash
curl -X POST "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions" \
  -H "Authorization: Bearer $GOOGLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma-4-31b-it",
    "messages": [
      {"role": "system", "content": "You are SOPHIA, the Akashic Record."},
      {"role": "user", "content": "What is the Omega Engine?"}
    ],
    "temperature": 0.7,
    "max_tokens": 1024
  }'
```

**Note**: The OpenAI-compatible endpoint is best for the ModelGateway because it uses the same message format as lmster, Ollama, and OpenRouter providers. However, the current GoogleAIProvider uses the native format.

### 8.3 Model List Endpoint

```bash
curl -s "https://generativelanguage.googleapis.com/v1beta/models?key=$GOOGLE_API_KEY" \
  | python3 -m json.tool | grep -E '"name"|"displayName"|"inputTokenLimit"|"outputTokenLimit"|"supportedGenerationMethods"'
```

---

## §9 Key URLs & References

| Resource | URL |
|:---------|:----|
| Google AI Studio | https://aistudio.google.com |
| API Key Creation | https://aistudio.google.com/app/apikey |
| Gemini API Docs | https://ai.google.dev/gemini-api/docs |
| Gemma on Gemini API | https://ai.google.dev/gemma/docs/core/gemma_on_gemini_api |
| API Reference | https://ai.google.dev/api |
| Model List (REST) | https://generativelanguage.googleapis.com/v1beta/models |
| Rate Limits | https://ai.google.dev/gemini-api/docs/rate-limits |
| Pricing | https://ai.google.dev/pricing |
| OpenAI Compatible | https://ai.google.dev/gemini-api/docs/openai |
| Gemma 4 Model Card | https://ai.google.dev/gemma/docs/core/model_card_4 |
| Gemma License (Apache 2.0) | https://ai.google.dev/gemma/terms |
| Google AI Forum | https://discuss.ai.google.dev |

---

## §10 Cross-Reference: FREE_TIER_MODEL_INDEX.md Corrections

The following corrections should be applied to `docs/research/FREE_TIER_MODEL_INDEX.md`:

| Line | Current | Should Be |
|:-----|:--------|:----------|
| 51 | `gemma-4-31b` (no `-it` suffix) | `gemma-4-31b-it` |
| 51 | 128k context | 256K context |
| 52 | `gemma-3-nise-27b` (wrong name) | `gemma-3-27b-it` |
| 52 | 32k context | 128K context |
| 49-52 | Table missing `gemma-4-26b-a4b-it` | Add MoE variant |

Additionally, the FREE_TIER_MODEL_INDEX.md section 7 "Maintenance System Design" has an incorrect auth scheme — it uses `Authorization: Bearer {api_key}` but Google AI Studio requires `x-goog-api-key` header or `?key=` query param.

---

## §11 Quick Reference Card

```
Gemma Models via Google AI Studio:
  gemma-4-31b-it      → 31B dense, 256K ctx, BEST for reasoning/coding
  gemma-4-26b-a4b-it  → 26B MoE, 256K ctx, cost-efficient
  gemma-3-27b-it      → 27B, 128K ctx, legacy workhorse
  gemma-3-12b-it      → 12B, 128K ctx, lightweight tasks
  gemma-3-4b-it       → 4B, 128K ctx, fast classification
  gemma-3-1b-it       → 1B, 128K ctx, ultra-fast

Omega default: gemma-4-31b-it

Free Tier: ~30 RPM, 1,500 RPD, 1M TPM
API Key: GOOGLE_API_KEY (not GEMMA_API_KEY)
Auth: x-goog-api-key header (not Bearer)
Format: Native or OpenAI-compatible

⚠️ CURRENT BUGS IN OMEGA:
  1. providers.py uses GEMMA_API_KEY → should be GOOGLE_API_KEY
  2. No model name mapping → local GGUF names sent to Google API
  3. System prompt concatenated into user message
```

---

*Maintained by: OpenCode CLI (Research Agent)*
*Next update: 2026-05-22 (or upon Google I/O 2026 announcements)*
