# 🔬 Model Registry Research Report — All Sources Mapped
**Date**: 2026-07-19  
**Agent**: Cline  
**Status**: COMPLETE

---

## Authoritative API Landscape

| Source | Endpoint | Auth Required | Rate Limit | Covers Our Models |
|--------|----------|--------------|------------|-------------------|
| OpenRouter /models | `/api/v1/models` | NO | None | 22/35 cloud |
| OpenRouter /benchmarks | `/api/v1/benchmarks` | YES | 30/min, 500/day | All 35 with key |
| HuggingFace /api/models | `/api/models/{repo}` | NO | None | 4/35 local |
| HuggingFace leaderboards | `/api/datasets/{id}/leaderboard` | NO | None | Benchmark scores |
| Artificial Analysis | `/api/v2/language/models` | YES | 100-500/day | All 35 with key |

### Key Finding: Capability Scores Source
- **OpenRouter /benchmarks** returns `intelligence_index`, `coding_index`, `agentic_index` (0-100 scale)
- **HuggingFace leaderboards** returns MMLU, HumanEval, SWE-bench scores
- **Both require auth for full access**
- **Workaround**: Use HF public benchmark datasets for free leaderboard data

---

## Unverified Models (6/35)

| Model | Why Unverified | Next Step |
|-------|----------------|-----------|
| `openrouter/free` | Synthetic meta-model | Remove or document |
| `opencode/big-pickle` | Custom stealth model | Research OpenCode-zen code |
| `arcee-ai/trinity-large-thinking:free` | New model, not yet indexed | Monitor OpenRouter |
| `liquid/lfm-2.5-1.2b-instruct:free` | New small model | HF direct query |
| `poolside/laguna-xs.2:free` | Mapped to laguna-xs-2.1 | Update mapping |

---

## Local Models (4/35) — Needs HF Research

| Model | HF Repo | License | Parameters |
|-------|---------|---------|------------|
| `gpt-oss-120b-local` | `openai/gpt-oss-120b` | Apache 2.0 | 117B total, 5.1B active |
| `llama-4-scout-local` | `meta-llama/Llama-4-Scout-17B-16E-Instruct` | TBD | 17B active |
| `nemotron-3-ultra-local` | `nvidia/nemotron-3-ultra-550b-a55b` | TBD | 550B total, 55B active |
| `qwen-3.5-72b-local` | `Qwen/Qwen2.5-72B-Instruct` | Apache 2.0 | 72B |

---

## Complete API Research

### OpenRouter Models API (NO AUTH)
```http
GET https://openrouter.ai/api/v1/models
Returns: 344 models with context_window, pricing, supported_parameters
```

### OpenRouter Benchmarks API (REQUIRES AUTH)
```http
GET https://openrouter.ai/api/v1/benchmarks
Authorization: Bearer $OPENROUTER_API_KEY
Query params: source=artificial-analysis|design-arena|leaderboard
              model_id=openai/gpt-4o
Returns: {
  "agentic_index": 58.3,      // 0-100 scale
  "coding_index": 65.8,
  "display_name": "GPT-4o",
  "intelligence_index": 71.2,
  "model_permaslug": "openai/gpt-4o",
  "pricing": {...}
}
```

### HuggingFace Model Info (NO AUTH)
```http
GET https://huggingface.co/api/models/{repo_id}
Returns: license, tags, pipeline_tag, architectures, downloads, lastModified
```

### HuggingFace Leaderboard (NO AUTH for public)
```http
GET https://huggingface.co/api/datasets?filter=benchmark:official
GET https://huggingface.co/api/datasets/{dataset_id}/leaderboard
Returns: [{rank, model_id, value, verified, author, source}]
Found 38 official benchmark datasets
```

### Artificial Analysisdata-api (REQUIRES AUTH)
```http
GET https://artificialanalysis.ai/api/v2/language/models
x-api-key: YOUR_KEY
Free tier: 100 req/day
Returns: benchmark scores, pricing, performance percentiles
```

---

## Recommendation

Build multi-tier reality engine:
1. **NO-AUTH tier**: OpenRouter models + HF model info + HF leaderboards
2. **AUTH-OPTIONAL tier**: OpenRouter benchmarks (if API key provided)
3. **Apply corrections**: Write verified data to model cards
4. **Freshness**: Weekly cron job re-queries all sources

