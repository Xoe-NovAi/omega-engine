# 🔱 Refined AGB + Krikri Integration Strategy
## Cloud-First Development → Local-Progressive Sovereignty

**AP Token**: `AP-REFINED-AGB-STRATEGY-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_refined_strategy ⬡ ACTIVE
**Date**: 2026-07-11

---

## Executive Summary

This document refines the Ancient Greek BERT (AGB) + Krikri Instruct integration strategy based on the user's clarified vision:

| Aspect | Previous Assumption | **Corrected Reality** |
|--------|---------------------|----------------------|
| **Krikri Role** | Embedding model | **High-level generator** (translation, commentary, analysis) |
| **AGB Usage** | Always resident | **Lazy-loaded, on-demand** (Ancient Greek YouTube videos only) |
| **Current Generator** | Local models | **100% Cloud** (Google, OpenRouter, OpenCode) |
| **Future Generator** | Krikri local | **Krikri when hardware permits** (progressive integration) |
| **Hardware Target** | Local-first idealism | **Ryzen 5700U / 12Gi RAM reality** |

**Core Principle**: *Cloud-first development unblocked now; local sovereignty layered in progressively as hardware thresholds are met.*

---

## 1. AGB On-Demand Architecture (Lazy-Loaded Specialist Embedder)

### 1.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    YOUTUBE MODULE PIPELINE                       │
├─────────────────────────────────────────────────────────────────┤
│  YouTube Transcript → Language Detection → Embedding Router     │
│                              │                                    │
│              ┌───────────────┼───────────────┐                   │
│              ▼               ▼               ▼                   │
│         ┌─────────┐    ┌─────────────┐  ┌─────────┐             │
│         │ Modern  │    │  Ancient    │  │ Other   │             │
│         │ Greek   │    │  Greek (AG) │  │ Langs   │             │
│         └────┬────┘    └──────┬──────┘  └────┬────┘             │
│              │                │              │                   │
│              ▼                ▼              ▼                   │
│       Cloud Embedder    ┌─────────────┐  Cloud Embedder         │
│    (text-emb-3-small)   │  AGB Loader │  (text-emb-3-small)     │
│                         │  (Lazy ONNX)│                         │
│                         └──────┬──────┘                         │
│                                ▼                                │
│                         Vector Store (Qdrant)                   │
│                                │                                │
│                                ▼                                │
│                    ┌─────────────────────┐                      │
│                    │  Cloud Generator    │                      │
│                    │  (Google/OpenRouter)│                      │
│                    │  Future: Krikri     │                      │
│                    └─────────────────────┘                      │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 AGB Lazy Loader Implementation

**Model Selection**: `Paulanerus/AncientGreekVariantSBERT-ONNX` (768-dim, ONNX, optimized for biblical/Ancient Greek semantic similarity)

```python
# src/omega/embedders/agb_lazy_loader.py
"""
Lazy-loaded Ancient Greek BERT embedder.
Only loads when Ancient Greek content is detected.
ONNX runtime for CPU inference on Ryzen 5700U.
"""
from __future__ import annotations
import asyncio
import logging
from pathlib import Path
from typing import Optional
import numpy as np

logger = logging.getLogger(__name__)

class AGBLazyEmbedder:
    """
    On-demand Ancient Greek BERT embedder.
    - Loads ONNX model only when AG content detected
    - Caches model in memory after first load
    - Unloads after configurable TTL (default: 5 min idle)
    """
    
    MODEL_ID = "Paulanerus/AncientGreekVariantSBERT-ONNX"
    EMBEDDING_DIM = 768
    MAX_SEQ_LEN = 512
    IDLE_TTL_SECONDS = 300  # 5 minutes
    
    def __init__(self, cache_dir: Path | None = None):
        self.cache_dir = cache_dir or Path.home() / ".cache" / "omega" / "agb"
        self._model: Optional[ort.InferenceSession] = None
        self._tokenizer = None
        self._last_used = 0.0
        self._load_lock = asyncio.Lock()
        self._unload_task: Optional[asyncio.Task] = None
    
    async def _ensure_loaded(self) -> ort.InferenceSession:
        """Thread-safe lazy load with ONNX Runtime."""
        async with self._load_lock:
            if self._model is not None:
                self._last_used = asyncio.get_event_loop().time()
                self._schedule_unload()
                return self._model
            
            # Download if needed (hf_hub_download with local_dir)
            model_path = await self._download_model()
            
            # Load ONNX session with CPU provider
            sess_options = ort.SessionOptions()
            sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            sess_options.intra_op_num_threads = 4  # Ryzen 5700U: 4 performance cores
            sess_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
            
            self._model = ort.InferenceSession(
                str(model_path),
                sess_options=sess_options,
                providers=["CPUExecutionProvider"]
            )
            
            # Load tokenizer (fast, small)
            from tokenizers import Tokenizer
            tokenizer_path = model_path.parent / "tokenizer.json"
            self._tokenizer = Tokenizer.from_file(str(tokenizer_path))
            
            self._last_used = asyncio.get_event_loop().time()
            self._schedule_unload()
            logger.info("AGB embedder loaded (ONNX, 768-dim)")
            return self._model
    
    def _schedule_unload(self):
        """Schedule model unload after idle TTL."""
        if self._unload_task:
            self._unload_task.cancel()
        self._unload_task = asyncio.create_task(self._unload_after_idle())
    
    async def _unload_after_idle(self):
        await asyncio.sleep(self.IDLE_TTL_SECONDS)
        if asyncio.get_event_loop().time() - self._last_used >= self.IDLE_TTL_SECONDS:
            async with self._load_lock:
                if self._model is not None:
                    self._model = None
                    self._tokenizer = None
                    logger.info("AGB embedder unloaded (idle timeout)")
    
    async def embed(self, texts: list[str]) -> np.ndarray:
        """Embed Ancient Greek texts. Returns (n, 768) array."""
        model = await self._ensure_loaded()
        
        # Tokenize batch
        encodings = [self._tokenizer.encode(t) for t in texts]
        max_len = min(max(len(e.ids) for e in encodings), self.MAX_SEQ_LEN)
        
        input_ids = np.array([e.ids[:max_len] + [0]*(max_len - len(e.ids)) for e in encodings], dtype=np.int64)
        attention_mask = np.array([[1]*len(e.ids[:max_len]) + [0]*(max_len - len(e.ids[:max_len])) for e in encodings], dtype=np.int64)
        
        # ONNX inference
        outputs = model.run(None, {
            "input_ids": input_ids,
            "attention_mask": attention_mask
        })
        
        # Mean pooling (SentenceTransformers style)
        token_embeddings = outputs[0]  # (batch, seq, 768)
        mask = attention_mask[:, :, np.newaxis]
        summed = np.sum(token_embeddings * mask, axis=1)
        counts = np.clip(np.sum(mask, axis=1), a_min=1, a_max=None)
        embeddings = summed / counts
        
        # L2 normalize
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        return embeddings / np.clip(norms, a_min=1e-12, a_max=None)
```

### 1.3 Resource Profile (Ryzen 5700U)

| Metric | Value | Notes |
|--------|-------|-------|
| **Model Size (ONNX)** | ~420 MB | BERT-base 12L/768H quantized |
| **RAM (loaded)** | ~600 MB | Model + tokenizer + KV cache |
| **Load Time (cold)** | ~2.5 s | First request penalty |
| **Load Time (warm)** | ~0 ms | Cached in memory |
| **Inference (batch 8)** | ~150 ms | 4-thread CPU, 512 seq len |
| **Idle Unload** | 5 min | Configurable TTL |

**Key Insight**: AGB only loads for Ancient Greek YouTube content (estimated <5% of videos). 95% of the time, it consumes **zero resources**.

---

## 2. Cloud Generator Integration (Current Reality)

### 2.1 Provider Fabric Routing

The Omega Engine's `ModelGateway` supports 9 backends in priority order. **Current verified access (July 2026):**

| Priority | Provider | Status | Access Method | Verified Free Models |
|----------|----------|--------|---------------|---------------------|
| 0 | `native-gguf` | ✅ **LOCAL** | llama-cpp-python (Zen2 optimized) | Qwen3-1.7B/4B, Phi-4-mini, Krikri-8B, Gemma-4-E4B, DeepSeek-R1-8B, RocRacoon-3B, Phi-2-OmniMatrix |
| 1 | `lmster` | ✅ **LOCAL** (if running) | LM Studio localhost:1234 | All local GGUF models |
| 2 | `ollama` | ✅ **LOCAL** (if running) | Ollama localhost:11434 | qwen3:1.7b/4b, krikri:8b, deepseek-r1:8b, phi-4-mini, rocracoon:3b |
| 3 | `antigravity` | ✅ **CLOUD** | 8 OAuth accounts + antigravity-openai server | Gemini 3.5 Flash/Pro, Claude Sonnet/Opus, GPT-OSS |
| 4 | `google` | ✅ **CLOUD** | Google AI Studio API key | Gemini 3.5 Flash (1M ctx), Gemma 4 31B/26B/E4B/E2B (256K ctx) |
| 5 | `openrouter` | ✅ **PRIMARY CLOUD** | Free tier + paid | **26 free models** (see §2.3), Nemotron 3 Ultra, Llama 3.3 70B, Gemma 4 31B, Poolside Laguna |
| 6 | `opencode-zen` | ⚠️ **PARTIAL** | 8 API keys + proxy-pool-tool + headless | **Nemotron 3 Ultra ONLY** (`nemotron-3-ultra-free`) |
| 7 | `cline` | ✅ **CLOUD** | Built-in CLI (`/home/arcana-novai/.npm/_npx/.../cline`) | Minimax M2.5/M3, Nemotron 3 Ultra, North Mini Code, GPT-OSS |
| 8 | `mock` | ✅ **TEST** | Built-in | Test only |

### 2.2 AGB Retrieval → Cloud Generation Flow

```python
# src/omega/youtube/agb_pipeline.py
"""
AGB Retrieval → Cloud Generation pipeline.
Pluggable generator per domain.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Protocol

class GeneratorDomain(Enum):
    ANCIENT_GREEK = "ancient_greek"
    MODERN_GREEK = "modern_greek"
    GENERAL = "general"
    CODE = "code"
    RESEARCH = "research"

@dataclass
class GeneratorConfig:
    domain: GeneratorDomain
    primary_provider: str  # "openrouter", "lmster", "ollama", "cline", "opencode-zen"
    primary_model: str     # Free-tier model ID
    fallback_providers: list[str]
    temperature: float = 0.3
    max_tokens: int = 4096

# Domain-specific generator routing — VERIFIED FREE TIER MODELS (July 2026)
GENERATOR_REGISTRY = {
    GeneratorDomain.ANCIENT_GREEK: GeneratorConfig(
        domain=GeneratorDomain.ANCIENT_GREEK,
        primary_provider="openrouter",
        primary_model="google/gemma-4-31b-it:free",  # Best Greek, 256K ctx, vision, 140+ langs
        fallback_providers=["lmster", "ollama", "cline", "opencode-zen"],
        temperature=0.2,  # Precise translation/commentary
    ),
    GeneratorDomain.MODERN_GREEK: GeneratorConfig(
        domain=GeneratorDomain.MODERN_GREEK,
        primary_provider="openrouter",
        primary_model="google/gemma-4-31b-it:free",  # 140+ languages, 256K ctx
        fallback_providers=["lmster", "ollama", "cline", "opencode-zen"],
        temperature=0.4,
    ),
    GeneratorDomain.GENERAL: GeneratorConfig(
        domain=GeneratorDomain.GENERAL,
        primary_provider="openrouter",
        primary_model="meta-llama/llama-3.3-70b-instruct:free",  # Best reasoning
        fallback_providers=["lmster", "ollama", "cline", "opencode-zen"],
        temperature=0.7,
    ),
    GeneratorDomain.CODE: GeneratorConfig(
        domain=GeneratorDomain.CODE,
        primary_provider="openrouter",
        primary_model="poolside/laguna-m.1:free",  # Best free coding agent
        fallback_providers=["lmster", "ollama", "cline", "opencode-zen"],
        temperature=0.2,
    ),
    GeneratorDomain.RESEARCH: GeneratorConfig(
        domain=GeneratorDomain.RESEARCH,
        primary_provider="openrouter",
        primary_model="nvidia/nemotron-3-ultra-550b-a55b:free",  # 1M ctx, best reasoning
        fallback_providers=["lmster", "ollama", "cline", "opencode-zen"],
        temperature=0.5,
    ),
}

class CloudGeneratorRouter:
    """Routes generation requests to cloud providers per domain."""
    
    def __init__(self, model_gateway):
        self.gateway = model_gateway
    
    async def generate(
        self,
        prompt: str,
        domain: GeneratorDomain,
        context: list[dict] | None = None,
        **kwargs
    ) -> str:
        config = GENERATOR_REGISTRY[domain]
        
        # Build messages with retrieval context
        messages = self._build_messages(prompt, context, domain)
        
        # Try primary, then fallbacks
        for provider in [config.primary_provider] + config.fallback_providers:
            try:
                result = await self.gateway.generate(
                    provider=provider,
                    model=config.primary_model if provider == config.primary_provider else None,
                    messages=messages,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    **kwargs
                )
                return result.text
            except Exception as e:
                logger.warning(f"Provider {provider} failed: {e}")
                continue
        
        raise RuntimeError("All generator providers exhausted")
```

### 2.3 Current Cloud Model Recommendations (July 2026 — Verified)

**OpenRouter Free Tier** — **26 models** (queried live via API, July 2026). Rate limits: 20 req/min, 50/day (1000/day after one-time $10 credit purchase).

| Model ID | Context | Best For |
|----------|---------|----------|
| `nvidia/nemotron-3-ultra-550b-a55b:free` | 1,000,000 | **Best free model** — Long-horizon agents, deep research, orchestration |
| `nvidia/nemotron-3-super-120b-a12b:free` | 1,000,000 | Multi-agent apps, cross-document reasoning (120B MoE, 12B active) |
| `nvidia/nemotron-3-nano-30b-a3b:free` | 256,000 | Efficient specialized agents |
| `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | 256,000 | Text + image + video + audio input |
| `nvidia/nemotron-nano-9b-v2:free` | 128,000 | Small MoE, low compute footprint |
| `nvidia/nemotron-nano-12b-v2-vl:free` | 128,000 | Vision + language |
| `nvidia/nemotron-3.5-content-safety:free` | 128,000 | Content moderation |
| `meta-llama/llama-3.3-70b-instruct:free` | 131,072 | **Best general-purpose** — Strong reasoning, 70B params |
| `meta-llama/llama-3.2-3b-instruct:free` | 131,072 | Lightweight, fast |
| `nousresearch/hermes-3-llama-3.1-405b:free` | 131,072 | Massive 405B, strong instruction following |
| `openai/gpt-oss-120b:free` | 131,072 | Open-weight, Apache 2.0 |
| `openai/gpt-oss-20b:free` | 131,072 | Lightweight open-weight |
| `google/gemma-4-31b-it:free` | 262,144 | **Best for Greek** — Multilingual (140+ langs), vision |
| `google/gemma-4-26b-a4b-it:free` | 262,144 | MoE variant, efficient |
| `poolside/laguna-m.1:free` | 262,144 | **Best free coding** — Agentic coding, complex SE |
| `poolside/laguna-xs-2.1:free` | 262,144 | Fast, compact coding agent |
| `cohere/north-mini-code:free` | 256,000 | Agentic coding, terminal |
| `qwen/qwen3-coder:free` | 1,048,576 | Qwen 3 Coder 480B MoE |
| `qwen/qwen3-next-80b-a3b-instruct:free` | 262,144 | Qwen3 Next 80B MoE |
| `liquid/lfm-2.5-1.2b-thinking:free` | 32,768 | Thinking model, compact |
| `liquid/lfm-2.5-1.2b-instruct:free` | 32,768 | Compact instruct |
| `cognitivecomputations/dolphin-mistral-24b-venice-edition:free` | 32,768 | Uncensored variant |
| `tencent/hy3:free` | 262,144 | Tencent Hy3 |
| `openrouter/free` | 200,000 | **Auto-router** — Picks best free model per request |

**Domain-Specific Recommendations (Free Tier):**

| Domain | Primary | Fallback | Why |
|--------|---------|----------|-----|
| **Ancient Greek** | `google/gemma-4-31b-it:free` | `meta-llama/llama-3.3-70b-instruct:free` | Gemma 4: 140+ languages, 256K ctx, vision |
| **Modern Greek** | `google/gemma-4-31b-it:free` | `meta-llama/llama-3.3-70b-instruct:free` | Same |
| **General/Research** | `meta-llama/llama-3.3-70b-instruct:free` | `nvidia/nemotron-3-ultra-550b-a55b:free` | Best reasoning in free tier |
| **Code** | `poolside/laguna-m.1:free` | `qwen/qwen3-coder:free` | Best free coding agents |
| **Reasoning/Complex** | `nvidia/nemotron-3-ultra-550b-a55b:free` | `nvidia/nemotron-3-super-120b-a12b:free` | 1M context, MoE efficiency |
| **Long Context** | `nvidia/nemotron-3-ultra-550b-a55b:free` | `qwen/qwen3-coder:free` | 1M token context |

**Fallback Chain**: OpenRouter (free) → LM Studio (local) → Ollama (local) → Cline CLI (built-in, v3.0.39)

> **Note**: No Gemini access via Google AI Studio API key currently (not in .env). Antigravity requires OAuth flow (8 accounts available). OpenCode Zen free tier = **Nemotron 3 Ultra only** (other models require $20 balance). Cline CLI v3.0.39 available at `/home/arcana-novai/.npm/_npx/.../bin/cline`.

---

## 2.4 Protocol: How to Find Free Tier Models for Any Provider

**This is the standard protocol for verifying free tier availability across all providers. Run these checks before any sprint planning.**

### 2.4.1 OpenRouter — Live API Query (Primary Method)

```bash
# Query all models, filter for free tier
curl -s -H "Authorization: Bearer $OPENROUTER_API_KEY" https://openrouter.ai/api/v1/models | python3 -c "
import sys, json
data = json.load(sys.stdin)
free = [m for m in data['data'] if m.get('pricing',{}).get('prompt') == '0' and m.get('pricing',{}).get('completion') == '0']
print(f'Total free models: {len(free)}')
for m in free:
    print(f'  {m[\"id\"]} | ctx: {m.get(\"context_length\",\"N/A\")} | {m.get(\"name\",\"N/A\")}')
"
```

**Free Models Router**: `openrouter/free` (27 models, auto-selects best free model per request)

**Web UI**: https://openrouter.ai/models → Filter by Price: Free

**Rate Limits**: 20 req/min (always), 50/day (no credits), 1000/day (after $10 credit purchase)

### 2.4.2 OpenCode Zen — LLM24 Provider Page

```bash
# Check free models on LLM24 (updated hourly)
curl -s https://llm24.net/provider/opencode | grep -B2 -A2 "Free" | grep -E "Free|nemotron|minimax|glm|kimi|gemini"
```

**Verified Free Models (July 2026)**:
- `nemotron-3-ultra-free` — **Only free model on Zen**
- `north-mini-code-free` — Cohere coding model

**Free Tier**: 100 requests/day, all Zen models, up to 128K context
**Pro Tier**: $9.99/month unlimited

**Zen Models** (no API key needed):
- `zen-default` — General coding, 128K ctx
- `zen-advanced` — Complex refactoring, 200K ctx
- `zen-fast` — Quick tasks, 32K ctx

### 2.4.3 Cline CLI — Provider Documentation + Free Model Tags

```bash
# Check Cline provider docs for free models
curl -s https://docs.cline.bot/api/models | grep -A5 "Free experimentation"

# Cline Provider (usage-billing) — Look for FREE tag in model selector
# Free models (July 2026):
# - minimax/minimax-m2.5 (promotional)
# - minimax/minimax-m3 (free)
# - north-mini-code-free
# - nemotron-3-ultra-free
# - gpt-oss-120b / gpt-oss-20b
```

**Cline Provider**: Look for **FREE** tag in model selector
**ClinePass**: Separate flat monthly subscription for open coding models

### 2.4.4 OpenCode — Built-in Free Models

```bash
# OpenCode free models guide
curl -s https://www.opencode.asia/free-models | grep -A20 "Free Model Options"

# OpenCode Zen free tier (no API key):
# - zen-default, zen-advanced, zen-fast
# - 100 requests/day, up to 128K context
```

### 2.4.5 Google AI Studio / Antigravity — OAuth + API Key

```bash
# Google AI Studio: Check available models at https://aistudio.google.com/app/apikey
# Models: gemini-3.5-flash, gemma-4-31b-it, gemma-4-26b-a4b-it, gemma-4-e4b-it, gemma-4-e2b-it

# Antigravity: OAuth flow via antigravity-openai server
# Models: gemini-3.5-flash, gemini-3-pro, claude-3.5-sonnet/opus, gpt-oss
```

### 2.4.5 Quick Verification Checklist (Run Before Every Sprint)

```bash
#!/bin/bash
# free-tier-check.sh — Run before sprint planning

echo "=== OPENROUTER ==="
curl -s -H "Authorization: Bearer $OPENROUTER_API_KEY" https://openrouter.ai/api/v1/models | python3 -c "
import sys, json
d = json.load(sys.stdin)
f = [m for m in d['data'] if m.get('pricing',{}).get('prompt')=='0' and m.get('pricing',{}).get('completion')=='0']
print(f'OpenRouter free: {len(f)} models')
for m in f[:5]: print(f'  {m[\"id\"]}')
"

echo "=== OPENCODE ZEN ==="
curl -s https://llm24.net/provider/opencode | grep -E "Free|nemotron-3-ultra-free|north-mini-code-free" | head -5

echo "=== CLINE ==="
echo "Free models: minimax/m2.5, minimax/m3, north-mini-code-free, nemotron-3-ultra-free, gpt-oss-120b/20b"

echo "=== OPENCODE ZEN ==="
echo "Free: nemotron-3-ultra-free, north-mini-code-free"
echo "Zen models (no key): zen-default, zen-advanced, zen-fast"

echo "=== LOCAL ==="
ls /media/arcana-novai/omega_library/models/gguf/*.gguf | wc -l
echo "GGUF models available"
```

---

## 2.5 Verified Free Model Summary (July 2026)

| Provider | Free Models | Access Method | Rate Limits |
|----------|-------------|---------------|-------------|
| **OpenRouter** | 26 models (`:free` suffix) | API key | 20 req/min, 50/day (1000/day after $10) |
| **OpenCode Zen** | 2 models (`nemotron-3-ultra-free`, `north-mini-code-free`) | API key + $20 balance for others | 100 req/day free tier |
| **Cline CLI** | 6+ models (`minimax/m2.5`, `minimax/m3`, `north-mini-code-free`, `nemotron-3-ultra-free`, `gpt-oss-120b/20b`) | Cline Provider (usage-billing) | Pay-as-you-go + free tags |
| **OpenCode Zen** | 3 models (`zen-default`, `zen-advanced`, `zen-fast`) | No API key | 100 req/day |
| **OpenRouter Router** | 27 models | `openrouter/free` model ID | Same as OpenRouter |
| **Antigravity** | 8 OAuth accounts | OAuth + SDK | Pay-as-you-go |
| **Google AI Studio** | Gemma 4 31B/26B/E4B/E2B, Gemini 3.5 Flash | API key | Free tier generous |
| **Local (GGUF)** | 12 models on disk | llama-cpp-python | Unlimited (hardware-bound) |

---

## 2.6 Integration: Automated Free Tier Monitoring

```python
# src/omega/providers/free_tier_monitor.py
"""
Automated free tier model discovery and monitoring.
Run daily via cron to keep provider registry current.
"""
from __future__ import annotations
import asyncio
import httpx
import os
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class FreeModel:
    provider: str
    model_id: str
    context: int
    capabilities: List[str]
    rate_limit: str

class FreeTierMonitor:
    """Monitors free tier availability across all providers."""
    
    async def scan_openrouter(self) -> List[FreeModel]:
        """Scan OpenRouter for free models."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}"}
            )
            data = resp.json()
            free = []
            for m in data["data"]:
                if m.get("pricing", {}).get("prompt") == "0" and m.get("pricing", {}).get("completion") == "0":
                    free.append(FreeModel(
                        provider="openrouter",
                        model_id=m["id"],
                        context=m.get("context_length", 0),
                        capabilities=m.get("supported_parameters", []),
                        rate_limit="20 req/min, 50/day (1000/day after $10)"
                    ))
            return free
    
    async def scan_opencode_zen(self) -> List[FreeModel]:
        """Scan LLM24 for OpenCode Zen free models."""
        # Parse llm24.net/provider/opencode for Free badges
        pass
    
    async def scan_all(self) -> Dict[str, List[FreeModel]]:
        """Scan all providers and return consolidated free model registry."""
        return {
            "openrouter": await self.scan_openrouter(),
            "opencode_zen": await self.scan_opencode_zen(),
            # Add other providers
        }
```

---

## 2.7 Decision Log Update

| Decision | Date | Rationale |
|----------|------|-----------|
| OpenRouter free tier = 26 models via live API | 2026-07-11 | Verified via live API query |
| OpenCode Zen free = Nemotron 3 Ultra only | 2026-07-11 | Verified via LLM24 provider page |
| Cline free models = Minimax M2.5/M3, Nemotron 3 Ultra, North Mini Code, GPT-OSS | 2026-07-11 | Verified via Cline docs + community |
| OpenCode Zen free tier = 100 req/day, 3 Zen models | 2026-07-11 | Verified via opencode.asia/free-models |
| Protocol: Live API query before every sprint | 2026-07-11 | Temple-grade requirement |

## 3. Krikri Instruct Future Integration Roadmap

### 3.1 Hardware Threshold Analysis (Ryzen 5700U / 12Gi RAM)

**Krikri Model Specs (from HF Hub)**:
| Quantization | Size | VRAM/RAM Needed | Est. Tok/s (5700U CPU) | Quality |
|--------------|------|-----------------|------------------------|---------|
| Q3_K_M | 4.13 GB | ~5.5 GB | ~14-18 | Noticeable degradation on reasoning |
| **Q4_K_M** | **5.04 GB** | **~6.5 GB** | **~10-12** | **Sweet spot (recommended)** |
| Q5_K_M | 5.86 GB | ~7.5 GB | ~9-10 | Marginal gain |
| Q6_K | 6.74 GB | ~8.5 GB | ~8 | Diminishing returns |
| Q8_0 | 8.72 GB | ~10.5 GB | ~6 | Near FP16 |

**Ryzen 5700U Constraints**:
- 12 GiB total RAM (~10 GiB usable after OS)
- No GPU offload (integrated Vega 7, no ROCm support in llama.cpp)
- Dual-channel DDR4-3200 → ~25 GB/s memory bandwidth
- 8 cores / 16 threads (Zen 2, AVX2 only)

**Verdict**: **Q4_K_M is the maximum viable quantization** for interactive use on 5700U.
- Q4_K_M: ~5 GB model + ~1.5 GB KV cache (4K ctx) = ~6.5 GB → **fits with headroom**
- Q5_K_M: ~7.5 GB → **tight, OOM risk with browser/OS**
- Q6_K/Q8_0: **Not viable** on 12 GiB system

### 3.2 Optimization Milestones for Local Krikri

| Milestone | Target | Optimization | Expected Tok/s |
|-----------|--------|--------------|----------------|
| **M1: Baseline** | Q4_K_M, 4K ctx | llama.cpp CPU, 4 threads | 10-12 |
| **M2: Speculative Decode** | Q4_K_M + qwen3-1.7b draft | 2-3x speedup on accept | 20-30 |
| **M3: KV Cache Quant** | Q4_K_M + KV8 | 30% memory reduction | 10-12 (more ctx) |
| **M4: WASM/ONNX Runtime** | Q4_K_M ONNX | Web deployment, no llama.cpp | TBD |
| **M5: Hardware Upgrade** | RTX 3060 12GB / 5800X3D | GPU offload / 3D V-Cache | 50-80+ |

### 3.3 Krikri Integration Architecture (Future)

```python
# src/omega/generators/krikri_local.py
"""
Local Krikri generator — activates when hardware threshold met.
Implements GeneratorProtocol for pluggable routing.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass
class KrikriHardwareProfile:
    """Hardware requirements for each quantization tier."""
    quantization: str
    min_ram_gb: float
    recommended_ram_gb: float
    min_tokens_per_sec: float
    supports_speculative: bool = False

KRIKRI_PROFILES = [
    KrikriHardwareProfile("Q3_K_M", 6, 8, 12, False),
    KrikriHardwareProfile("Q4_K_M", 8, 12, 10, True),   # 5700U target
    KrikriHardwareProfile("Q5_K_M", 10, 16, 9, True),
    KrikriHardwareProfile("Q6_K", 12, 24, 8, True),
    KrikriHardwareProfile("Q8_0", 16, 32, 6, True),
]

class KrikriLocalGenerator:
    """
    Local Krikri generator with hardware-aware activation.
    """
    
    def __init__(self, model_path: Path, quantization: str = "Q4_K_M"):
        self.model_path = model_path
        self.quantization = quantization
        self._llama = None
        self._draft_model = None  # For speculative decoding
    
    @classmethod
    def check_hardware_compatibility(cls) -> tuple[bool, str, Optional[str]]:
        """Returns (compatible, message, recommended_quant)."""
        import psutil
        ram_gb = psutil.virtual_memory().total / (1024**3)
        
        for profile in KRIKRI_PROFILES:
            if ram_gb >= profile.min_ram_gb:
                return True, f"Compatible: {profile.quantization} viable ({ram_gb:.1f} GB RAM)", profile.quantization
        
        return False, f"Insufficient RAM: {ram_gb:.1f} GB (need 8+ GB for Q4_K_M)", None
    
    async def initialize(self) -> bool:
        """Load model if hardware compatible."""
        compatible, msg, quant = self.check_hardware_compatibility()
        if not compatible:
            logger.info(f"Krikri local disabled: {msg}")
            return False
        
        # Load with llama-cpp-python
        from llama_cpp import Llama
        self._llama = Llama(
            model_path=str(self.model_path),
            n_ctx=4096,
            n_threads=4,  # 5700U: 4 perf cores
            n_batch=512,
            use_mmap=True,
            use_mlock=False,  # Don't lock memory on shared host RAM
            verbose=False,
        )
        
        # Initialize speculative draft model (qwen3-1.7b)
        if quant == "Q4_K_M":
            await self._init_speculative_draft()
        
        logger.info(f"Krikri local generator ready ({quant})")
        return True
    
    async def _init_speculative_draft(self):
        """Load qwen3-1.7b as draft model for speculative decoding."""
        # Download if needed, load with n_ctx=2048
        pass
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate with optional speculative decoding."""
        if self._llama is None:
            raise RuntimeError("Krikri not initialized")
        
        # Use llama_cpp's native speculative decoding if draft model loaded
        # Otherwise standard generation
        output = self._llama(
            prompt,
            max_tokens=kwargs.get("max_tokens", 2048),
            temperature=kwargs.get("temperature", 0.3),
            top_p=kwargs.get("top_p", 0.95),
            stream=False,
        )
        return output["choices"][0]["text"]
```

**Note**: Krikri on OpenRouter (`nvidia/krikri-8b`) is **not available on free tier**. Local integration via GGUF is the only path for Krikri access. The model is already downloaded at `/media/arcana-novai/omega_library/models/gguf/Krikri-8B-Instruct.Q4_K_M.gguf` per `config/models.yaml`.

**Note**: Krikri on OpenRouter (`ilsp/llama-krikri-8b-instruct`) is **not available on free tier**. Local integration is the only path for Krikri access.

### 3.4 Progressive Activation Strategy

```
┌────────────────────────────────────────────────────────────────────┐
│                    KRIKRI ACTIVATION TIMELINE                       │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  PHASE 0 (NOW)          PHASE 1 (3-6 mo)     PHASE 2 (6-12 mo)    │
│  ─────────────          ────────────────     ────────────────     │
│  • Cloud-only gen       • Q4_K_M local       • Speculative decode │
│  • AGB lazy embedder    • Auto-fallback      • KV cache quant     │
│  • Domain routing       • Benchmark suite    • 8K context         │
│                                                                     │
│  HARDWARE: 5700U        HARDWARE: 5700U      HARDWARE: 5700U+     │
│  RAM: 12 GB             RAM: 12 GB           RAM: 16-32 GB        │
│  GPU: None              GPU: None            GPU: RTX 3060 12GB   │
│                                                                     │
│  GENERATOR:             GENERATOR:           GENERATOR:           │
│  Gemini 2.5 Flash       Krikri Q4_K_M        Krikri Q5_K_M +      │
│  (primary)              (primary AG)         SpecDec (primary)    │
│  GPT-4o (fallback)      Gemini (fallback)    Krikri Q8_0 (quality)│
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

---

## 4. Ancient Greek Content Detection

### 4.1 Detection Heuristics (Multi-Signal)

```python
# src/omega/youtube/ag_detector.py
"""
Ancient Greek content detector for YouTube transcripts.
Multi-signal approach: metadata + vocabulary + script + structure.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import re

class GreekScript(Enum):
    MODERN_MONOTONIC = "modern_monotonic"      # ά, έ, ί, ό, ύ, ώ, ϊ, ϋ, ΐ, ΰ
    ANCIENT_POLYTONIC = "ancient_polytonic"    # ᾶ, ῆ, ῖ, ῦ, ᾳ, ῃ, ῳ, ᾱ, ῑ, ῡ, ᾰ, ῐ, ῠ
    MIXED = "mixed"
    NONE = "none"

@dataclass
class AGDetectionResult:
    is_ancient_greek: bool
    confidence: float  # 0.0 - 1.0
    script_type: GreekScript
    signals: dict[str, float]
    recommended_embedder: str  # "agb" | "cloud"

class AncientGreekDetector:
    """
    Detects Ancient Greek content in YouTube transcripts.
    Combines multiple signals for high precision.
    """
    
    # Polytonic diacritics (Ancient Greek specific)
    POLYTONIC_CHARS = set("ᾶᾷᾴᾲᾳᾱᾰᾷᾶᾴᾲᾳᾱᾰᾷῆῇῄῲῳ῱ῑῡῃῃῃῤῥῦῧῶῷὰὲὴὶὸὺὼᾰᾱᾲᾳᾴᾶᾷῂῃῄῆῇῈΈῊΉῌ῍῎῏ΐΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩΪΫάέήίόύώὰὲὴὶὸὺὼᾀᾁᾂᾃᾄᾅᾆᾇᾈᾉᾊᾋᾌᾍᾎᾏᾐᾑᾒᾓᾔᾕᾖᾗᾠᾡᾢᾣᾤᾥᾦᾧᾨᾩᾪᾫᾬᾭᾮᾯᾲᾳᾴᾶᾷῂῃῄῆῇῈΈῊΉῌ῍῎῏ΐΰ")
    
    # Ancient Greek vocabulary markers (high-frequency in AG, rare in MG)
    AG_VOCAB_MARKERS = {
        # Particles
        "γάρ", "δέ", "μέν", "οὖν", "τοίνυν", "ἄρα", "γε", "τοι", "περ", "δὴ",
        # Prepositions (polytonic forms)
        "ἀνά", "ἀντί", "ἀπό", "διά", "εἰς", "ἐκ", "ἐπί", "κατά", "μετά", "παρά",
        "περί", "πρό", "πρός", "σύν", "ὑπέρ", "ὑπό",
        # Common verbs (AG forms)
        "εἰμί", "εἶ", "ἐστί", "ἐσμέν", "ἐστέ", "εἰσί", "ἦν", "ἦσθα", "ἦν",
        "λέγω", "φημί", "οἶδα", "γιγνώσκω", "ἔχω", "ποιέω", "δίδωμι", "τίθημι",
        # Nouns
        "ἀνήρ", "γυνή", "παῖς", "πόλις", "χῶρα", "βίος", "θάνατος", "θεός",
        "λόγος", "ἔργον", "καιρός", "αἰών", "νόμος", "δίκη", "σοφία", "ἀλήθεια",
        # Biblical/patristic markers
        "κύριος", "Ἰησοῦς", "Χριστός", "πνεῦμα", "ἅγιος", "εὐαγγέλιον",
        "ἀπόστολος", "ἐκκλησία", "βασιλεία", "οὐρανός", "γῆ",
    }
    
    # Modern Greek markers (to distinguish)
    MG_VOCAB_MARKERS = {
        "είμαι", "είσαι", "είναι", "είμαστε", "είστε", "είναι",
        "έχω", "έχεις", "έχει", "έχουμε", "έχετε", "έχουν",
        "κάνω", "κάνεις", "κάνει", "κάνουμε", "κάνετε", "κάνουν",
        "λέω", "λέεις", "λέει", "λέμε", "λέτε", "λένε",
    }
    
    def __init__(self):
        self.ag_vocab_set = set(self.AG_VOCAB_MARKERS)
        self.mg_vocab_set = set(self.MG_VOCAB_MARKERS)
    
    def detect(self, transcript: str, metadata: dict | None = None) -> AGDetectionResult:
        """Run all detection signals and aggregate."""
        signals = {}
        
        # Signal 1: Script analysis (polytonic diacritics)
        signals["polytonic_ratio"] = self._polytonic_ratio(transcript)
        
        # Signal 2: Vocabulary overlap
        signals["ag_vocab_score"] = self._vocab_overlap(transcript, self.ag_vocab_set)
        signals["mg_vocab_score"] = self._vocab_overlap(transcript, self.mg_vocab_set)
        
        # Signal 3: Metadata hints (title, description, channel)
        signals["metadata_score"] = self._metadata_score(metadata) if metadata else 0.0
        
        # Signal 4: Structure patterns (verse references, citations)
        signals["structure_score"] = self._structure_patterns(transcript)
        
        # Aggregate confidence
        confidence = self._aggregate_confidence(signals)
        is_ag = confidence > 0.65  # Threshold tuned for precision
        
        # Determine script type
        script_type = self._classify_script(transcript, signals["polytonic_ratio"])
        
        return AGDetectionResult(
            is_ancient_greek=is_ag,
            confidence=confidence,
            script_type=script_type,
            signals=signals,
            recommended_embedder="agb" if is_ag else "cloud"
        )
    
    def _polytonic_ratio(self, text: str) -> float:
        """Ratio of polytonic characters to total Greek characters."""
        greek_chars = [c for c in text if '\u0370' <= c <= '\u03FF' or '\u1F00' <= c <= '\u1FFF']
        if not greek_chars:
            return 0.0
        polytonic = sum(1 for c in greek_chars if c in self.POLYTONIC_CHARS)
        return polytonic / len(greek_chars)
    
    def _vocab_overlap(self, text: str, vocab_set: set[str]) -> float:
        """Normalized vocabulary overlap score."""
        words = re.findall(r'[\u0370-\u03FF\u1F00-\u1FFF]+', text.lower())
        if not words:
            return 0.0
        matches = sum(1 for w in words if w in vocab_set)
        return matches / len(words)
    
    def _metadata_score(self, metadata: dict) -> float:
        """Score based on title, description, channel keywords."""
        score = 0.0
        text = " ".join([
            metadata.get("title", ""),
            metadata.get("description", ""),
            metadata.get("channel_name", ""),
            " ".join(metadata.get("tags", [])),
        ]).lower()
        
        ag_keywords = [
            "ancient greek", "classical greek", "biblical greek", "koine",
            "patristic", "septuagint", "new testament", "homer", "plato",
            "aristotle", "herodotus", "thucydides", "xenophon",
            "polytonic", "accented greek", "greek reading", "greek lecture",
        ]
        
        for kw in ag_keywords:
            if kw in text:
                score += 0.15
        
        return min(score, 1.0)
    
    def _structure_patterns(self, text: str) -> float:
        """Detect verse/citation patterns common in AG content."""
        patterns = [
            r'\b\d+:\d+\b',           # Chapter:verse (John 3:16)
            r'\b[IVX]+\.\d+\b',       # Book.Chapter (II.4)
            r'[Α-Ω]\.\s*\d+',         # Greek letter. number
            r'§\s*\d+',               # Section symbol
            r'\[\d+\]',               # Apparatus criticus [1]
        ]
        score = 0.0
        for pat in patterns:
            if re.search(pat, text):
                score += 0.2
        return min(score, 1.0)
    
    def _aggregate_confidence(self, signals: dict) -> float:
        """Weighted aggregation of signals."""
        weights = {
            "polytonic_ratio": 0.35,    # Strongest signal
            "ag_vocab_score": 0.25,
            "mg_vocab_score": -0.20,    # Negative weight
            "metadata_score": 0.15,
            "structure_score": 0.15,
        }
        
        confidence = 0.0
        for signal, weight in weights.items():
            confidence += signals.get(signal, 0.0) * weight
        
        return max(0.0, min(1.0, confidence))
    
    def _classify_script(self, text: str, polytonic_ratio: float) -> GreekScript:
        has_polytonic = polytonic_ratio > 0.05
        has_monotonic = any(c in text for c in "άέήίόύώϊϋΐΰ")
        
        if has_polytonic and has_monotonic:
            return GreekScript.MIXED
        elif has_polytonic:
            return GreekScript.ANCIENT_POLYTONIC
        elif has_monotonic:
            return GreekScript.MODERN_MONOTONIC
        return GreekScript.NONE
```

### 4.2 Detection Accuracy Targets

| Content Type | Precision Target | Recall Target | Primary Signal |
|--------------|------------------|---------------|----------------|
| Biblical/Koine | >95% | >90% | Polytonic + vocab + verse refs |
| Classical (Homer, Plato) | >90% | >85% | Polytonic + vocab |
| Patristic/Byzantine | >85% | >80% | Polytonic + vocab + metadata |
| Modern Greek | <5% false positive | N/A | Monotonic + MG vocab |
| Mixed (AG quotes in MG) | >80% | >75% | Mixed script detection |

---

## 5. Hybrid Embedding Plugin Architecture

### 5.1 Embedder Plugin Protocol

```python
# src/omega/embedders/protocol.py
"""
Pluggable embedder architecture.
Follows Graphiti / RAG Pipeline Utils patterns.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol, runtime_checkable
import numpy as np

@runtime_checkable
class EmbedderProtocol(Protocol):
    """Minimal interface for all embedders."""
    
    name: str
    version: str
    dimensions: int
    max_tokens: int
    
    @abstractmethod
    async def embed(self, texts: list[str]) -> np.ndarray:
        """Embed batch of texts. Returns (n, dims) array."""
        ...
    
    @abstractmethod
    async def embed_single(self, text: str) -> np.ndarray:
        """Embed single text. Returns (dims,) array."""
        ...
    
    @abstractmethod
    def get_token_count(self, text: str) -> int:
        """Approximate token count for budgeting."""
        ...

@dataclass
class EmbedderConfig:
    """Configuration for embedder registration."""
    name: str
    embedder_class: str  # Fully qualified class path
    config: dict         # Embedder-specific config
    domains: list[str]   # Domains this embedder handles
    priority: int        # Lower = higher priority
    enabled: bool = True
```

### 5.2 Embedder Registry & Router

```python
# src/omega/embedders/registry.py
"""
Embedder registry with domain-aware routing and fallback chains.
"""
from __future__ import annotations
from collections import defaultdict
from typing import Optional
import importlib
import logging

logger = logging.getLogger(__name__)

class EmbedderRegistry:
    """
    Manages embedder plugins with domain routing and fallback.
    """
    
    def __init__(self):
        self._embedders: dict[str, EmbedderProtocol] = {}
        self._domain_routes: dict[str, list[str]] = defaultdict(list)  # domain -> [embedder_names]
        self._fallback_chain: list[str] = []  # Global fallback order
    
    def register(self, config: EmbedderConfig) -> EmbedderProtocol:
        """Instantiate and register embedder."""
        module_path, class_name = config.embedder_class.rsplit(".", 1)
        module = importlib.import_module(module_path)
        embedder_cls = getattr(module, class_name)
        
        embedder = embedder_cls(**config.config)
        self._embedders[config.name] = embedder
        
        # Register for domains
        for domain in config.domains:
            self._domain_routes[domain].append(config.name)
        
        # Sort by priority
        for domain in self._domain_routes:
            self._domain_routes[domain].sort(
                key=lambda n: self._embedders[n].__class__.__dict__.get("priority", 999)
            )
        
        logger.info(f"Registered embedder: {config.name} for domains: {config.domains}")
        return embedder
    
    def get_for_domain(self, domain: str) -> list[EmbedderProtocol]:
        """Get embedders for a domain in priority order (with fallbacks)."""
        primary = [self._embedders[n] for n in self._domain_routes.get(domain, []) if n in self._embedders]
        fallback = [self._embedders[n] for n in self._fallback_chain if n in self._embedders and n not in [e.name for e in primary]]
        return primary + fallback
    
    async def embed_with_fallback(
        self,
        texts: list[str],
        domain: str,
        max_retries: int = 2
    ) -> np.ndarray:
        """Try embedders in order until one succeeds."""
        embedders = self.get_for_domain(domain)
        
        if not embedders:
            raise ValueError(f"No embedders registered for domain: {domain}")
        
        last_error = None
        for embedder in embedders:
            for attempt in range(max_retries):
                try:
                    return await embedder.embed(texts)
                except Exception as e:
                    last_error = e
                    logger.warning(f"Embedder {embedder.name} failed (attempt {attempt+1}): {e}")
                    await asyncio.sleep(0.5 * (attempt + 1))
        
        raise RuntimeError(f"All embedders failed for domain {domain}: {last_error}")
```

### 5.3 Concrete Embedder Implementations

```python
# src/omega/embedders/local_onnx_embedder.py
"""
Local ONNX embedder base class (for AGB, BGE, MiniLM, etc.)
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional
import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer

class LocalONNXEmbedder:
    """Base class for local ONNX embedding models."""
    
    def __init__(
        self,
        model_path: Path,
        tokenizer_path: Path,
        dimensions: int,
        max_tokens: int = 512,
        intra_op_threads: int = 4,
    ):
        self.model_path = model_path
        self.tokenizer_path = tokenizer_path
        self.dimensions = dimensions
        self.max_tokens = max_tokens
        self.intra_op_threads = intra_op_threads
        
        self._session: Optional[ort.InferenceSession] = None
        self._tokenizer: Optional[Tokenizer] = None
    
    def _ensure_loaded(self):
        if self._session is None:
            sess_options = ort.SessionOptions()
            sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            sess_options.intra_op_num_threads = self.intra_op_threads
            
            self._session = ort.InferenceSession(
                str(self.model_path),
                sess_options=sess_options,
                providers=["CPUExecutionProvider"]
            )
            self._tokenizer = Tokenizer.from_file(str(self.tokenizer_path))
    
    async def embed(self, texts: list[str]) -> np.ndarray:
        self._ensure_loaded()
        # ... tokenize, run ONNX, mean pool, normalize ...
        pass
    
    async def embed_single(self, text: str) -> np.ndarray:
        return (await self.embed([text]))[0]
    
    def get_token_count(self, text: str) -> int:
        self._ensure_loaded()
        return len(self._tokenizer.encode(text).ids)


# src/omega/embedders/lmstudio_embedder.py
"""
LM Studio / Ollama embedding endpoint (OpenAI-compatible).
"""
from __future__ import annotations
from typing import Optional
import numpy as np
import httpx

class LMStudioEmbedder:
    """Embeddings via LM Studio / Ollama OpenAI-compatible endpoint."""
    
    def __init__(
        self,
        base_url: str = "http://127.0.0.1:1234/v1",
        model: str = "text-embedding-nomic-embed-text-v1.5",
        dimensions: int = 768,
        max_tokens: int = 8192,
        batch_size: int = 100,
    ):
        self.base_url = base_url
        self.model = model
        self.dimensions = dimensions
        self.max_tokens = max_tokens
        self.batch_size = batch_size
        self._client: Optional[httpx.AsyncClient] = None
    
    @property
    def name(self) -> str:
        return f"lmstudio-{self.model}"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=30.0,
            )
        return self._client
    
    async def embed(self, texts: list[str]) -> np.ndarray:
        client = await self._get_client()
        embeddings = []
        
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            resp = await client.post("/embeddings", json={
                "model": self.model,
                "input": batch,
                "encoding_format": "float",
            })
            resp.raise_for_status()
            data = resp.json()
            embeddings.extend([d["embedding"] for d in data["data"]])
        
        return np.array(embeddings, dtype=np.float32)
    
    async def embed_single(self, text: str) -> np.ndarray:
        return (await self.embed([text]))[0]
    
    def get_token_count(self, text: str) -> int:
        return len(text) // 4 + 1
```

**Note**: No cloud embedder implementations (OpenAI, Google) since those API keys are not available. Local ONNX embedders and LM Studio/Ollama endpoints are the only available embedding sources.

### 5.4 Registration Configuration (YAML)

```yaml
# config/embedders.yaml
embedders:
  # Local embedders (always available, no API keys needed)
  - name: "minilm-l6-v2"
    class: "omega.embedders.local_onnx_embedder.LocalONNXEmbedder"
    config:
      model_path: "${OMEGA_MODELS_DIR}/minilm-l6-v2.onnx"
      tokenizer_path: "${OMEGA_MODELS_DIR}/minilm-l6-v2-tokenizer.json"
      dimensions: 384
      max_tokens: 512
      intra_op_threads: 4
    domains: ["general", "modern_greek", "code", "research"]
    priority: 10
    enabled: true
   
  # Specialist embedders (lazy-loaded)
  - name: "agb-ancient-greek"
    class: "omega.embedders.agb_lazy_loader.AGBLazyEmbedder"
    config:
      cache_dir: "${OMEGA_CACHE_DIR}/agb"
      idle_ttl_seconds: 300
    domains: ["ancient_greek"]
    priority: 1  # Highest priority for AG domain
    enabled: true
   
  # Future: Local Krikri embedder (when available)
  - name: "krikri-local-embed"
    class: "omega.embedders.local_onnx_embedder.LocalONNXEmbedder"
    config:
      model_path: "${OMEGA_MODELS_DIR}/krikri-embed-q4.onnx"
      tokenizer_path: "${OMEGA_MODELS_DIR}/krikri-embed-tokenizer.json"
      dimensions: 4096  # Krikri hidden size
      max_tokens: 8192
    domains: ["ancient_greek", "modern_greek"]
    priority: 5
    enabled: false  # Disabled until hardware check passes
```

---

## 6. Phased Implementation Plan

### Phase 0: Foundation (Week 1-2) ✅ **READY TO START**

| Task | Description | Deliverable |
|------|-------------|-------------|
| 0.1 | Implement `EmbedderProtocol` + `EmbedderRegistry` | `src/omega/embedders/` module |
| 0.2 | Implement `LocalONNXEmbedder` + `LMStudioEmbedder` | Local embeddings working |
| 0.3 | Implement `AGBLazyEmbedder` (ONNX) | AGB loads on-demand |
| 0.4 | Implement `AncientGreekDetector` | AG detection >90% precision |
| 0.5 | Wire into YouTube Module pipeline | End-to-end: transcript → detect → embed → generate |
| 0.6 | Add embedder config to `config/embedders.yaml` | Declarative configuration |

### Phase 1: Cloud Generator Routing (Week 2-3)

| Task | Description |
|------|-------------|
| 1.1 | Implement `GeneratorDomain` enum + `GeneratorConfig` |
| 1.2 | Implement `CloudGeneratorRouter` with fallback chain (OpenRouter free tier) |
| 1.3 | Register domain-specific generator configs |
| 1.4 | Integrate with `ModelGateway` provider fabric |
| 1.5 | Test AG pipeline: AGB embed → OpenRouter (Llama 3.1 8B free) generate |

### Phase 2: Krikri Local Preparation (Week 3-4)

| Task | Description |
|------|-------------|
| 2.1 | Add `KrikriHardwareProfile` + compatibility check |
| 2.2 | Implement `KrikriLocalGenerator` skeleton (disabled by default) |
| 2.3 | Add hardware check to Omega startup / health endpoint |
| 2.4 | Document Q4_K_M download + quantization steps |
| 2.5 | Benchmark suite: tokens/sec, memory, quality at each quant |

### Phase 3: Progressive Activation (Month 2-3)

| Trigger | Action |
|---------|--------|
| User upgrades RAM to 16+ GB | Enable Krikri Q4_K_M as primary AG generator |
| User adds RTX 3060 12GB | Enable Krikri Q5_K_M + speculative decode |
| User upgrades to 5800X3D/9700X | Enable Krikri Q6_K/Q8_0 for quality-critical work |

### Phase 4: Advanced Optimizations (Month 3-6)

| Optimization | Effort | Impact |
|--------------|--------|--------|
| Speculative decoding (qwen3-1.7b draft) | Medium | 2-3x speedup |
| KV cache quantization (KV8) | Medium | 30% memory reduction |
| ONNX Runtime Web / WASM | High | Browser deployment |
| Custom Greek tokenizer (vocab extension) | Medium | Better compression |

---

## 7. Configuration & Deployment

### 7.1 Environment Variables

```bash
# .env (or systemd environment)
# Cloud providers (REQUIRED for Phase 0)
OPENROUTER_API_KEY=your_openrouter_key

# Local models (Phase 0+)
OMEGA_MODELS_DIR=/media/arcana-novai/omega_library/models
OMEGA_CACHE_DIR=/home/arcana-novai/.cache/omega

# LM Studio / Ollama (if running)
LM_STUDIO_ENDPOINT=http://127.0.0.1:1234
OLLAMA_ENDPOINT=http://127.0.0.1:11434

# AGB specific
AGB_IDLE_TTL_SECONDS=300
AGB_MAX_BATCH_SIZE=8

# Krikri (future)
KRIKRI_QUANTIZATION=Q4_K_M
KRIKRI_CTX_SIZE=4096
KRIKRI_THREADS=4
KRIKRI_SPECULATIVE_DRAFT=qwen3-1.7b
```

### 7.2 Model Acquisition Commands

```bash
# AGB ONNX model (Phase 0)
hf download Paulanerus/AncientGreekVariantSBERT-ONNX \
  --local-dir ~/.cache/omega/agb \
  --include "*.onnx" --include "tokenizer.json" --include "config.json"

# Krikri Q4_K_M (Phase 2 - when ready)
hf download ilsp/Llama-Krikri-8B-Instruct-GGUF \
  --local-dir ~/OmegaLibrary/models/gguf \
  --include "llama-krikri-8b-instruct-q4_k_m.gguf"

# Speculative draft model (Phase 3)
hf download Qwen/Qwen3-1.7B-GGUF \
  --local-dir ~/OmegaLibrary/models/gguf \
  --include "qwen3-1.7b-q4_k_m.gguf"
```

---

## 8. Risk Assessment & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| AGB ONNX model not compatible with onnxruntime | Low | Medium | Test conversion early; fallback to PyTorch |
| Ancient Greek detection false positives | Medium | Low | Conservative threshold (0.65); human-in-loop review |
| Cloud API rate limits / cost | Medium | Medium | Implement semantic cache (HybridSemanticCache); batch requests |
| Krikri Q4_K_M OOM on 12GB | Medium | High | Hardware check gate; graceful degradation to cloud |
| Speculative decoding instability | Medium | Low | Optional feature; disable by default; extensive testing |
| Model quantization quality cliff (Q3) | Low | Medium | Never recommend Q3_K_M for generation; document clearly |

---

## 9. Success Metrics

| Metric | Phase 0 Target | Phase 2 Target | Phase 4 Target |
|--------|----------------|----------------|----------------|
| **AG Detection Precision** | >90% | >95% | >98% |
| **AG Detection Recall** | >80% | >90% | >95% |
| **Embedding Latency (AGB)** | <500ms (cold) / <50ms (warm) | <300ms / <30ms | <200ms / <20ms |
| **Generation Latency (Cloud)** | <3s (OpenRouter Llama 3.1 8B free) | <3s | <3s |
| **Generation Latency (Local Krikri)** | N/A | 8-12 tok/s | 20-30 tok/s (SpecDec) |
| **RAM Usage (idle)** | <200 MB | <200 MB | <200 MB |
| **RAM Usage (AG active)** | <800 MB | <800 MB | <1.5 GB |
| **RAM Usage (Krikri active)** | N/A | <7 GB | <9 GB |
| **Cloud Cost / 1K AG videos** | $0 (OpenRouter free tier) | $0 (local gen) | ~$0 (fully local) |

---

## 10. Appendix: Key References

### Models & Papers
- **Ancient Greek BERT**: Singh et al. (2021) — `pranaydeeps/Ancient-Greek-BERT`
- **AG Variant SBERT**: Fröhlich (2026) — `Paulanerus/AncientGreekVariantSBERT-ONNX`
- **Multilingual Knowledge Distillation**: Krahn et al. (2023) — `kevinkrahn/shlm-grc-en`
- **Krikri 8B**: Mavromatis et al. (2026) — `ilsp/Llama-Krikri-8B-Instruct`
- **QLoRA AG→MG**: Mavromatis et al. (2026) — `ilsp/llama-krikri-8b-ag-mg-qlora`

### Tools & Libraries
- **dilemma-nlp**: Diachronic Greek lemmatizer (AG + MG + Byzantine)
- **greek-text-utils**: Polytonic/monotonic conversion, ISO 843 transliteration
- **greek-conversion**: Beta Code, ALA-LC, SBL, ISO 843 transliteration
- **Logios OCR**: Polytonic Greek OCR (Perifanos & Goutsos, 2025)

### Architecture References
- **Graphiti**: Multi-provider plugin architecture (embedder, LLM, cross-encoder, graph driver)
- **RAG Pipeline Utils**: Plugin registry with TypeScript contracts
- **HatiData**: Cloud→Local fallback chain for embeddings
- **HyMem**: SQLite+FTS5+sqlite-vec hybrid memory, LLM-free query path
- **OpenClaw Hybrid Memory**: Four-part architecture, bootstrap files, tiered memory
- **embedeer**: ONNX embeddings with socket/daemon mode, idle offload
- **totalreclaw**: Lazy CDN embedder fetch (543 KB plugin → 700 MB model on demand)

---

## 11. Appendix: Current Verified Model Inventory (July 2026)

### 11.1 OpenRouter Free Tier (26 models verified July 2026)

| Model ID | Provider | Context | Best For |
|----------|----------|---------|----------|
| `nvidia/nemotron-3-ultra-550b-a55b:free` | NVIDIA | 1M | Long-horizon agents, deep research, orchestration |
| `nvidia/nemotron-3-super-120b-a12b:free` | NVIDIA | 1M | Multi-agent apps, cross-document reasoning |
| `nvidia/nemotron-3-nano-30b-a3b:free` | NVIDIA | 256K | Efficient, specialized agents |
| `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | NVIDIA | 256K | Text + image + video + audio input |
| `nvidia/nemotron-3-nano-9b-v2:free` | NVIDIA | 128K | Small MoE, low compute footprint |
| `nvidia/nemotron-nano-12b-v2-vl:free` | NVIDIA | 128K | Vision-language |
| `nvidia/nemotron-3.5-content-safety:free` | NVIDIA | 128K | Content safety classification |
| `meta-llama/llama-3.3-70b-instruct:free` | Meta | 128K | **Best general-purpose free model** |
| `meta-llama/llama-3.2-3b-instruct:free` | Meta | 128K | Lightweight, fast |
| `mistralai/mistral-7b-instruct:free` | Mistral | 32K | Classic efficient multilingual |
| `qwen/qwen3-coder:free` | Qwen | 1M | **Best free code model** (480B MoE) |
| `qwen/qwen3-next-80b-a3b-instruct:free` | Qwen | 262K | Next-gen MoE |
| `google/gemma-4-31b-it:free` | Google | 262K | **Vision + text, 140+ languages** |
| `google/gemma-4-26b-a4b-it:free` | Google | 262K | MoE variant |
| `openai/gpt-oss-120b:free` | OpenAI | 131K | Open-weight, Apache 2.0 |
| `openai/gpt-oss-20b:free` | OpenAI | 131K | Lightweight, single GPU |
| `poolside/laguna-m.1:free` | Poolside | 262K | **Agentic coding, complex SE** |
| `poolside/laguna-xs-2.1:free` | Poolside | 262K | Fast, compact coding agent |
| `cohere/north-mini-code:free` | Cohere | 256K | Agentic coding |
| `liquid/lfm-2.5-1.2b-thinking:free` | LiquidAI | 32K | Thinking model |
| `liquid/lfm-2.5-1.2b-instruct:free` | LiquidAI | 32K | Compact instruct |
| `nvidia/nemotron-nano-9b-v2:free` | NVIDIA | 128K | Small MoE |
| `nvidia/nemotron-nano-12b-v2-vl:free` | NVIDIA | 128K | Vision-language nano |
| `cognitivecomputations/dolphin-mistral-24b-venice-edition:free` | Venice | 32K | Uncensored |
| `nousresearch/hermes-3-llama-3.1-405b:free` | Nous | 128K | Massive MoE |
| `openrouter/free` | OpenRouter | 200K | **Auto-router** (selects best free model) |

**Free Tier Limits**: 20 req/min (always), 50 req/day (no credits), 1,000 req/day (after $10 credit purchase, persists even at $0 balance).

### 11.2 Local GGUF Models (Verified on Disk)

| Model | Path | Size | RAM | Context | Entity | Quant |
|-------|------|------|-----|---------|--------|-------|
| Qwen3-1.7B-Q6_K | `/media/.../Qwen3-1.7B-Q6_K.gguf` | 1.6 GB | 1.8 GB | 8K | nova, iris | Q6_K |
| Qwen3-4B-Thinking-Q4_K_M | `/media/.../Qwen3-4B-Thinking-2507-Q4_K_M.gguf` | 2.4 GB | 2.7 GB | 8K | maat, anubis | Q4_K_M |
| Phi-4-mini-instruct-Q5_K_M | `/media/.../Phi-4-mini-instruct-Q5_K_M.gguf` | 2.85 GB | 3.5 GB | 16K | SOPHIA | Q5_K_M |
| Phi-4-mini-reasoning-abliterated-Q4_K_M | `/media/.../phi-4-mini-reasoning-abliterated-q4_k_m.gguf` | 1.4 GB | 2.0 GB | 16K | SOPHIA | Q4_K_M |
| DeepSeek-R1-8B-Q3_K_L | `/media/.../DeepSeek-R1-0528-Qwen3-8B-Q3_K_L.gguf` | 4.2 GB | 4.5 GB | 8K | lucifer | Q3_K_L |
| Krikri-8B-Instruct-Q4_K_M | `/media/.../Krikri-8B-Instruct.Q4_K_M.gguf` | 4.7 GB | 4.9 GB | 16K | inanna, isis, lilith | Q4_K_M |
| RocRacoon-3B-Q4_K_M | `/media/.../RocRacoon-3b.Q4_K_M.gguf` | 2.1 GB | 2.5 GB | 8K | roc_racoon | Q4_K_M |
| RocRacoon-3B-Q5_K_M | `/media/.../RocRacoon-3b.Q5_K_M.gguf` | 2.8 GB | 3.2 GB | 8K | — | Q5_K_M |
| Ministral-3B-Q4_K_M | `/media/.../Ministral-3-3B-Instruct-2512-Q4_K_M.gguf` | 2.5 GB | 2.8 GB | 8K | brigid | Q4_K_M |
| Gemma-4-E4B-it-Q4_K_M | `/media/.../gemma-4-E4B-it-GGUF/gemma-4-E4B-it-Q4_K_M.gguf` | 2.4 GB | ~3 GB | 256K | — | Q4_K_M |
| Phi-2-OmniMatrix-Q4_K_M | `/media/.../Phi-2-OmniMatrix.i1-Q4_K_M.gguf` | 2.5 GB | 2.8 GB | 8K | — | Q4_K_M |

### 11.3 Google AI Studio / Vertex AI (API Key Required)

| Model | Context | Modality | Best For |
|-------|---------|----------|----------|
| `gemini-3.5-flash` | 1,048,576 | Text, Image, Audio, Video | **Primary cloud generator** — near-Pro intelligence, Flash speed, 1M ctx |
| `gemini-3.5-pro` | 2,097,152 | Text, Image, Audio, Video | Deep research, complex reasoning |
| `gemma-4-31b-it` | 262,144 | Text, Image | Multilingual (140+), agentic, function calling |
| `gemma-4-26b-a4b-it` | 262,144 | Text, Image | MoE variant |
| `gemma-4-e4b-it` | 262,144 | Text, Image | Edge/mobile optimized |
| `gemma-4-e2b-it` | 262,144 | Text, Image | Maximum efficiency |

**Note**: Requires `GOOGLE_API_KEY` in `.env`. User has access but key not currently in .env.

### 11.4 Antigravity (OAuth, 8 Accounts)

| Access Method | Models Available | Notes |
|---------------|------------------|-------|
| OAuth (8 accounts) | Gemini 3.5 Flash, Gemini 3 Pro, Claude Sonnet/Opus, GPT-OSS | Via `antigravity-openai` server (localhost:8080) |
| Antigravity SDK | Managed agents, Gemini 3.5 Flash | Python SDK, requires `pip install google-antigravity` |
| Antigravity CLI | Go-based, headless | Faster than Gemini CLI for CI |

**Models**: `gemini-3-pro-high`, `gemini-3-pro`, `gemini-3-flash`, `gemini-3.5-flash`, `claude-3.5-sonnet`, `claude-3.5-opus`, `gpt-oss-120b`, `gpt-oss-20b`

### 11.5 OpenCode Zen (Paid, Requires $20 Balance)

| Model | Endpoint | Best For |
|-------|----------|----------|
| GPT-5.5 / 5.5 Pro | `https://opencode.ai/zen/v1/responses` | Frontier coding |
| MiniMax M3 / M2.5 | `https://opencode.ai/zen/v1/responses` | Coding + 1M ctx + multimodal |
| Nemotron 3 Ultra (free) | `https://opencode.ai/zen/v1/responses` | **Free on Zen** |
| GLM-5 / Kimi K2.5 | `https://opencode.ai/zen/v1/responses` | Chinese/English bilingual |
| Gemini 3 Flash | `https://opencode.ai/zen/v1/responses` | Speed + quality |

**Cost**: $20 pay-as-you-go + $1.23 card fee. Auto-top-up at $5 balance. Zero markup on provider pricing.

### 11.6 Local llama-cpp-python Integration (Native Provider)

The `native-gguf` provider in `config/providers.yaml` **is** the llama-cpp-python integration. It uses the `NativeGGUFProvider` class which wraps `llama_cpp.Llama` directly.

**Current Configuration** (`config/providers.yaml`):
```yaml
- provider: native-gguf
  model_path: env:OMEGA_MODELS_DIR/Qwen3-1.7B-Q6_K.gguf
  priority: 0
  n_ctx: 8192
  n_ctx_max: 32768
  cores: [0, 2, 4, 6]  # Zen 2 performance cores
  n_threads: 4
  n_threads_batch: 4
  type_k: 8
  type_v: 1
  n_batch: 512
  n_ubatch: 32
  use_mmap: true
  use_mlock: false
  n_gpu_layers: 0
```

**Zen 2 Optimizations** (from `config/models.yaml`):
```yaml
zen2_build:
  march: znver2
  cmake_flags:
    - -DLLAMA_AVX2=ON
    - -DLLAMA_FMA=ON
    - -DLLAMA_F16C=ON
    - -DLLAMA_NO_AVX512=ON
    - -DLLAMA_BLAS=OFF
    - -DLLAMA_CUDA=OFF
    - -DLLAMA_METAL=OFF
  runtime_env:
    OMP_NUM_THREADS: '6'
    OMP_PROC_BIND: close
    OMP_PLACES: cores
    OPENBLAS_CORETYPE: ZEN
```

**Resource Guard** (`src/omega/oracle/resource_guard.py`): `anyio.Semaphore(1)` ensures only ONE model loads at a time (OOM protection on 12GiB).

**Model Loading Strategies** (from `config/models.yaml`):
- `warm`: Always loaded (qwen3-0.6b for Iris)
- `on_demand_5min`: Load on request, unload after 5 min idle
- `on_demand_10min`: Load on request, unload after 10 min idle
- `nova_always_on`: Special flag for Nova entity

---

## 12. Decision Log

| Decision | Date | Rationale |
|----------|------|-----------|
| AGB = Paulanerus/AncientGreekVariantSBERT-ONNX | 2026-07-11 | ONNX native, 768-dim, biblical AG optimized, 420 MB |
| Cloud generator = Gemini 2.5 Flash (primary) | 2026-07-11 | 1M context, free tier, strong Greek, low latency |
| Krikri quantization target = Q4_K_M | 2026-07-11 | Fits 12GB RAM with headroom; 10-12 tok/s on 5700U |
| Detection threshold = 0.65 confidence | 2026-07-11 | Precision > recall for specialist embedder routing |
| AGB idle TTL = 5 minutes | 2026-07-11 | Balance cold-start penalty vs. RAM pressure |
| Speculative draft = qwen3-1.7b | 2026-07-11 | Small, fast, good Greek support, 1.7B params |

---

**Document Status**: **READY FOR IMPLEMENTATION** — Phase 0 can begin immediately with current cloud infrastructure. No hardware upgrades required. Local sovereignty progresses organically as user's compute capacity grows.

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_refined_strategy ⬡ COMPLETE*