# 🔱 Omega Engine — Free Model Reference Library (R100)
# ⬡ OMEGA ⬡ SOPHIA ⬡ minimax-m3 ⬡ opencode + cline ⬡ trc_model_reference ⬡ LIBRARY
# AP: AP-MODEL-REF-LIBRARY-v1.0.0
# Status: ACTIVE — Continually Updated
# Last Updated: 2026-06-02
# Maintainer: SOPHIA (with Cline+M3 1M context as synthesis partner)

---

## §0 Purpose

This is the **continually-updated, single-source-of-truth** for every free
inference model and free MCP service available to the Omega Engine. It uses
the legacy `ai-provider-matrix.md` pattern (327 lines, 4 providers × 7 metrics)
extended to all 4 tiers.

### §0.1 Index — Where to Find What

| Need | Section | Source |
|------|---------|--------|
| Local GGUFs (Qwen3, Phi-4, DeepSeek, Krikri) | §1 | `config/models.yaml` |
| Local inference servers (Ollama, LM Studio, native-gguf) | §2 | `config/providers.yaml` |
| Free cloud model catalog (Google, OpenRouter, Zen, Copilot) | §3 | `docs/research/model_db/CURRENT_MODELS.md` |
| OpenCode Zen free tier detail | §3.2 | `docs/research/OPENCODE_ZEN_MODEL_REFERENCE.md` |
| OpenRouter free tier detail | §3.3 | `docs/research/OPENROUTER_MODEL_REFERENCE.md` |
| GitHub Copilot free tier | §3.4 | `docs/research/GITHUB_COPILOT_FREE_TIER_RESEARCH.md` |
| Free search/scrape MCP services | §4 | `~/.config/opencode/mcp_servers.json` |
| Free search API deep dive | §4.1 | `docs/research/R99_free_tier_search_apis.md` |

### §0.2 Why a Library, Not a Snapshot

Models are added, deprecated, rate-limited, and re-priced constantly. The
**legacy snapshot files** in `docs/research/model_db/` are point-in-time. **This
file is the index** — it stays short, points to snapshots, and gets updated
when the snapshots change.

### §0.3 Selection Philosophy (Local-First, per Mandate 7)

1. **Local Sovereign** (TIER 0): Used for 90% of queries when the right GGUF exists
2. **Free Local Server** (TIER 1): When the GGUF needs a different runtime
3. **Free Cloud** (TIER 2): When local is too small/slow OR context is too large
4. **MCP Services** (TIER 3): For research/ingest, not for chat completion

Cost is the inverse priority: anything that costs $0 wins unless local can do it.

---

## §1 TIER 0 — Local Sovereign (GGUF Models on Disk)

**Hardware target**: AMD Ryzen 7 5700U (Zen 2, 8C/16T, AVX2, no AVX-512) | 14Gi RAM | No GPU
**RAM budget**: 14,336 total − 2,000 OS = 12,336 MB available for AI
**Strategy**: `max_concurrent_models = 1` (plus Nova always-on 300MB)

### §1.1 GGUF Catalog (all models on disk)

Source: `config/models.yaml` (verified 2026-06-02).

| Model | Size (GB) | RAM (MB) | Context | Quant | Strategy | Entity | Status |
|-------|----------:|---------:|--------:|-------|----------|--------|--------|
| `qwen3-1.7b` | 0.27 | 300 | 4K | mixed | always | Nova | ✅ on disk |
| `qwen3-0.6b-q6_k` | 0.47 | 500 | 4K | Q6_K | warm | Iris | ✅ on disk |
| `qwen3-1.7b-q6_k` | 1.6 | 1800 | 8K | Q6_K | on_demand_10min | Sekhmet, Hecate | ✅ on disk |
| `phi-4-mini` | 3.8 | 4500 | 16K | Q4_K_M | on_demand_10min | SOPHIA | ✅ on disk |
| `phi-2-omnimatrix-i1-q4_k_m` | (see yaml) | (see yaml) | (see yaml) | Q4_K_M | on_demand_10min | Brigid | ✅ on disk |
| `qwen3-4b-thinking-q4_k_m` | (see yaml) | (see yaml) | (see yaml) | Q4_K_M | on_demand_10min | (reasoning) | ✅ on disk |
| `deepseek-r1-qwen3-8b-q3_k_l` | (see yaml) | (see yaml) | (see yaml) | Q3_K_L | on_demand_10min | (deep) | ✅ on disk |
| `krikri-8b-q4_k_m` | (see yaml) | (see yaml) | (see yaml) | Q4_K_M | on_demand_10min | (Greek) | ✅ on disk |
| `embeddinggemma-300m-q6_k` | 0.3 | 200 | n/a | Q6_K | llama-server | (embed) | ✅ on disk |

**Model files location**: `/media/arcana-novai/omega_library/models/gguf/local/all/`

### §1.2 Per-Model Strengths / Weaknesses (initial 7-metric rating)

The legacy matrix uses: Research Depth, Technical Accuracy, Implementation Focus,
Response Speed, Cost Efficiency, Creativity, Consistency (each 1-5).

| Model | Depth | Accuracy | Impl | Speed | Cost | Creative | Consistent | Best For |
|-------|------:|---------:|-----:|------:|-----:|---------:|-----------:|----------|
| `qwen3-1.7b` (Nova) | 2/5 | 3/5 | 2/5 | **5/5** | **5/5** | 2/5 | 4/5 | Greetings, routing, short Q&A |
| `qwen3-0.6b-q6_k` (Iris) | 1/5 | 2/5 | 1/5 | **5/5** | **5/5** | 1/5 | 4/5 | Speculative decode check only |
| `qwen3-1.7b-q6_k` (Sekhmet) | 3/5 | 4/5 | 3/5 | 4/5 | **5/5** | 3/5 | 4/5 | Boundaries, protection, medium convos |
| `phi-4-mini` (SOPHIA) | **4/5** | **5/5** | **4/5** | 3/5 | 4/5 | 4/5 | **5/5** | Deep analysis, code review, strategy |
| `phi-2-omnimatrix` (Brigid) | 3/5 | 3/5 | 2/5 | **5/5** | **5/5** | **5/5** | 3/5 | Poetry, healing, hearth, inspiration |
| `qwen3-4b-thinking` | **5/5** | 4/5 | 3/5 | 2/5 | 4/5 | 3/5 | 4/5 | Step-by-step reasoning, math |
| `deepseek-r1-8b` | **5/5** | **5/5** | **4/5** | 1/5 | 3/5 | 3/5 | 4/5 | Hard reasoning (slow!) |
| `krikri-8b` | 3/5 | 3/5 | 2/5 | 2/5 | 3/5 | 4/5 | 3/5 | Greek language tasks |
| `embeddinggemma-300m` | n/a | n/a | n/a | **5/5** | **5/5** | n/a | **5/5** | Vector embeddings (768-dim) |

**Weakness pattern (all local GGUFs)**:
- **Context < 16K** vs cloud models (1M)
- **No multi-modal** (text only)
- **CPU-only** (no GPU) — 2-8 tok/s on Zen 2
- **English-favored** (Greek model is the only non-English specialty)

### §1.3 GGUFs NOT in Stock (worth downloading)

| Model | Why | When to add |
|-------|-----|-------------|
| `qwen3-8b-q6_k` | Mid-tier reasoning, ~5GB, fits in 12GB budget | If `qwen3-4b-thinking` quality ceiling too low |
| `llama-3.3-70b-instruct-q3_k_s` | Best generalist, ~30GB — OVER BUDGET | Skip until hardware upgrade |
| `mistral-small-3.2-24b-q4_k_m` | Already on Together free tier (T2) | Skip — covered by cloud |
| `nomic-embed-text-v1.5-q8_0` | Better embeddings than gemma-300m | If multilingual RAG needed |

---

## §2 TIER 1 — Free Local Inference Servers

These are the **runtimes** that serve the GGUFs from §1. The model catalog and
the server catalog are decoupled (per `config/providers.yaml`).

### §2.1 Provider Chain (priority 0 → 7)

Source: `config/providers.yaml` (verified 2026-06-02).

| Pri | Provider | Type | URL/Env | Status (2026-06-02) |
|----:|----------|------|---------|---------------------|
| 0 | `native-gguf` | Local | llama-cpp-python | ❌ Not installed |
| 1 | `lmster` | Local | `127.0.0.1:1234` (LM Studio) | ⚠️ Server OFF, no models in `~/.lmstudio/models/` |
| 2 | `ollama` | Local | `127.0.0.1:11434` | ✅ Running with `qwen2.5:0.5b` |
| 3 | `google` | Cloud | `env:GOOGLE_API_KEY` | ✅ Key set |
| 4 | `openrouter` | Cloud | `env:OPENROUTER_API_KEY` | ✅ Key set |
| 5 | `opencode` | Cloud | OpenCode built-in | ✅ Available |
| 6 | `copilot` | Cloud | `env:GH_TOKEN` | ⚠️ Free tier |
| 7 | `mock` | Test | OfflineMockBackend (OMEGA_DEMO=true) | ✅ Always available |

**Local-first mandate (Mandate 7)**: Tiers 0-2 must be tried before Tiers 3-7.

### §2.2 `ollama` — Currently Working

- **Image**: `docker.io/library/ollama` (via Podman or native binary)
- **Endpoint**: `http://127.0.0.1:11434` (NO `/v1` suffix — corrected in D80)
- **Models loaded**: `qwen2.5:0.5b` (397 MB)
- **Model overrides** (D81): All entity GGUF names → `qwen2.5:0.5b` for ollama
- **Strengths**: Simplest local runtime, OpenAI-compatible API, 5 min setup
- **Weaknesses**: Model format conversion needed (GGUF→Ollama blob), limited
  context tuning, no `keep_alive` semantics for our tier strategy
- **Live verification**: `omega summon Sekhmet "what is strength?"` returns
  real inference result. Model resolves `qwen3-1.7b-q6_k` → `qwen2.5:0.5b`.

### §2.3 `lmster` (LM Studio) — Installed, Not Running

- **Binary**: `~/.lmstudio/bin/` (CLI: `lms`)
- **Endpoint**: `http://127.0.0.1:1234` (OpenAI-compatible)
- **State**: Server OFF, no models in `~/.lmstudio/models/`
- **Strengths**: Best-in-class quantization GUI, KV-cache tuning per model,
  custom presets, OpenAI-compatible API
- **Weaknesses**: Headless mode requires `lms server start --port 1234`,
  no automatic model loading, GUI is heavy
- **To activate**: `lms start` + load a GGUF via the GUI, then `lms server start`

### §2.4 `native-gguf` (llama-cpp-python) — Not Installed

- **Package**: `llama-cpp-python` (would need venv install)
- **Hardware flags**: Zen 2 needs `CMAKE_ARGS="-DGGML_NATIVE=ON -DGGML_CPU_ALL_VARIANTS=ON"`
- **Strengths**: Direct GGUF loading, no server overhead, full KV cache control,
  native model overrides (no Ollama blob conversion)
- **Weaknesses**: Compilation time, no built-in web UI, single-process per model
- **To activate**: `source .venv/bin/activate && pip install llama-cpp-python` +
  configure `config/models.yaml` llama_server section + start as systemd service

### §2.5 Selection Logic (TIER 0-1)

```python
def select_local_provider(gguf_name: str, entity: str) -> str:
    """TIER 0-1 selection per Mandate 7."""
    # Priority 0: native-gguf (best for production)
    if native_gguf_available() and gguf_in_stock(gguf_name):
        return "native-gguf"
    # Priority 1: LM Studio (best for dev iteration)
    if lmster_server_running() and gguf_loaded_in_lmstudio(gguf_name):
        return "lmster"
    # Priority 2: Ollama (always works after `ollama pull`)
    if ollama_running():
        return "ollama"  # uses model_overrides from providers.yaml
    # Fall back to cloud
    return "cloud"
```

---

## §3 TIER 2 — Free Cloud Models

Cloud is **FALLBACK** per Mandate 7. Each cloud provider has free-tier limits
that constrain the role it can play. **Cross-references are in
`docs/research/model_db/CURRENT_MODELS.md`** (verified 2026-05-17) — that is
the snapshot source; this section summarizes the role each plays.

### §3.1 TIER 3 (legacy meaning) = "Frontier-class Free Cloud"

| Model | Provider | Context | Free Limit | Best For | Local Alt |
|-------|----------|--------:|------------|----------|-----------|
| `google/gemma-4-31b-it:free` | OpenRouter | 262K | Recurring | SOTA reasoning | `phi-4-mini` (16K ctx) |
| `gemini-2.5-pro` | Google | 1M+ | 15 RPM, daily cap | Deep reasoning, multi-modal | None |
| `qwen/qwen3-next-80b-a3b-instruct:free` | OpenRouter | 262K | Recurring | Logic, multilingual | `qwen3-4b-thinking` |
| `nvidia/nemotron-3-super-120b-a12b:free` | OpenRouter | 262K | Recurring | Generalist, tools | None |
| `minimax/minimax-m2.5:free` | OpenRouter | 197K | Recurring | Creative, coding | `phi-2-omnimatrix` |
| `llama-3.3-70b` | SambaNova | 128K | 10-30 RPM | Reasoning, instruction | None |

### §3.2 OpenCode Zen Free Tier (verified 2026-06-02)

Source: `docs/research/OPENCODE_ZEN_MODEL_REFERENCE.md` (last updated 2026-05-15).

| Model ID | Context | SWE-bench | Free? | Specialty |
|----------|--------:|----------:|:-----:|-----------|
| `big-pickle` | 200K | — | ✅ | Stealth model, current OpenCode agent |
| `deepseek-v4-flash-free` | 200K | ~79% | ✅ | Fast coding, multi-file edits |
| `minimax-m2.5-free` | 205K | 80.2% | ✅ | Agentic coding, budget throughput |
| `ring-2.6-1t-free` | — | — | ✅ | 1T param, deep reasoning |
| `nemotron-3-super-free` | 205K | — | ✅ | NVIDIA-hosted, general coding |
| `qwen3.6-plus-free` | 262K | 78.8% | ✅ | Long context, multi-language |

**⚠️ M3 Free Tier Context Correction (D86)**:
- OpenCode Zen `minimax/minimax-m3:free` is the **200K-context** free tier
- 1M context is reserved for **Cline in VSCodium** (the Artisan teammate) — NOT
  available through OpenCode Zen's free tier
- Earlier Researcher finding of "1M context (512K guaranteed)" was incorrect
- Verify by: `curl -H "Authorization: Bearer $OPENCODE_API_KEY" https://opencode.ai/zen/v1/models`

### §3.3 OpenRouter Free Tier

Source: `docs/research/OPENROUTER_MODEL_REFERENCE.md` (last verified 2026-05-15).

Key free models (full table in source):
- `minimax/minimax-m2.5:free` (197K, 80.2% SWE)
- `deepseek/deepseek-v4-flash:free` (1M context, synthesis)
- `qwen/qwen3-coder:free` (1M context, coding)
- `nvidia/nemotron-3-super-120b-a12b:free` (262K)
- `google/gemma-4-31b-it:free` (262K, SOTA reasoning)

### §3.4 GitHub Copilot Free Tier

Source: `docs/research/GITHUB_COPILOT_FREE_TIER_RESEARCH.md` (2026-05).

- **GPT-4.1** — 1M context, 5x Haiku (note: NOT a free tier model anymore, requires Pro)
- **GPT-4o** — 128K context, vision capable
- **Claude Haiku** — fast, 200K context
- **GPT-5-mini** — newer, paid tier
- **Raptor-mini** — free, simple tasks

### §3.5 Selection Logic (TIER 0 → 2)

```python
def select_inference_backend(
    query_complexity: str,    # "simple" | "moderate" | "deep"
    context_tokens: int,      # estimated token count
    sovereignty_required: bool, # True for any data-sensitive task
    entity: str,
) -> str:
    """Select inference backend per Mandate 7 (local-first)."""
    # TIER 0: Always try local first
    local = select_local_provider(entity_model(entity), entity)
    if local != "cloud" and sovereignty_required:
        return local
    if local != "cloud" and context_tokens <= local_context(local):
        return local
    # TIER 2: Cloud for overflow
    if context_tokens > 200_000:  # exceeds all free tiers
        return "google:gemini-2.5-pro"  # 1M+ context
    if query_complexity == "deep":
        return "openrouter:google/gemma-4-31b-it:free"  # SOTA reasoning
    if query_complexity == "moderate":
        return "opencode-zen:deepseek-v4-flash-free"
    return local  # simple queries always local
```

---

## §4 TIER 3 — Free MCP-Based Research Services

**Note**: TIER 3 services are NOT chat-completion models. They are **research
and data ingestion tools** invoked via MCP. They are listed here for
completeness because they complete the "free tier" picture.

Source: `~/.config/opencode/mcp_servers.json` (verified 2026-06-02).

### §4.1 Wired MCPs (all 5 working)

| MCP | Type | Endpoint / Command | Version | Status | Free Limit |
|-----|------|-------------------|---------|--------|------------|
| **Tavily** | stdio | `npx -y tavily-mcp` | 0.2.20 | ✅ Works | 1,000 credits/mo (90-day expiry) |
| **Firecrawl** | stdio | `npx -y firecrawl-mcp` | 3.20.2 | ✅ Works | 1,000 credits/mo (recurring) |
| **Exa** | streamable-http | `https://mcp.exa.ai/mcp` | 3.2.1 | ✅ Works | 1,000 searches/mo with key |
| **Jina** | streamable-http | `https://mcp.jina.ai/v1` | 1.4.0 | ✅ Works | 10M free tokens |
| **SearXNG** | stdio | `npx -y searxng-mcp` | (local) | ✅ Running on :8017 | ∞ (self-hosted) |

### §4.2 SearXNG — Sovereign Search (Verified 2026-06-02)

- **Container**: `omega-searxng` on `127.0.0.1:8017` (systemd unit active)
- **Image**: `ghcr.io/searxng/searxng:latest` (Podman)
- **Settings**: `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/searxng/config/settings.yml`
- **Engines (14 active)**: brave, wikipedia, arxiv, semantischolar, crossref,
  pubmed, openalex, github_code, gitlab, sourcehut, huggingface, wikidata,
  marginalia, mwmbl
- **Engines removed** (for rate-limit/sovereignty): google, bing, ddg, yahoo,
  startpage, ecosia, mojeek
- **MCP wrapper**: `npx -y searxng-mcp` with `SEARXNG_SERVER_URL=http://127.0.0.1:8017`
- **JSON verified**: `curl -X POST "http://127.0.0.1:8017/search?q=python+async&format=json"`
  returns real results from Brave + mwmbl + Reddit
- **Strengths**: 100% sovereign, ∞ queries, no API bills, 14 high-quality
  engines, perfect for arXiv/PubMed/HuggingFace code search
- **Weaknesses**: Brave engine rate-limited (no API key configured),
  Reddit/mwmbl engines less consistent, requires self-hosting maintenance

### §4.3 Firecrawl — Deep Extraction (verified via npm 3.20.2)

- **MCP command**: `npx -y firecrawl-mcp`
- **Free tier**: 1,000 credits/month recurring
- **Tools**: `map` (site discovery), `crawl` (recursive ingest),
  `scrape` (targeted clean markdown), `agent` (autonomous discovery)
- **Strengths**: Best-in-class JS rendering, anti-bot bypass, structured
  extraction via JSON schema, official OpenCode MCP
- **Weaknesses**: Credits used per operation (recursive crawls drain fast),
  cloud-only, no offline mode

### §4.4 Exa — Neural Semantic Search (verified HTTP 200, v3.2.1)

- **MCP URL**: `https://mcp.exa.ai/mcp?tools=web_search_exa,web_fetch_exa`
- **Header**: `x-api-key: ${EXA_API_KEY}` (key in `.env`)
- **Free tier**: 1,000 searches/month with key, 150/day unauthenticated
- **Strengths**: Neural semantic search (finds similar concepts, not keywords),
  great for "find me content about X" queries, includes academic sources
- **Weaknesses**: Cloud-only, $7/1K after free tier, semantic drift on
  specific technical queries

### §4.5 Jina — URL Extraction + Academic (verified HTTP 200, v1.4.0)

- **MCP URL**: `https://mcp.jina.ai/v1`
- **Header**: `Authorization: Bearer ${JINA_API_KEY}` (key in `.env`)
- **Free tier**: 10M tokens on signup, 100 RPM search
- **Tools** (20 total): `read_url`, `search_web`, `search_arxiv`,
  `search_ssrn`, `search_bibtex`, `search_images`, `expand_query`,
  `parallel_search_web`, `parallel_read_url`, `extract_pdf`, …
- **Strengths**: Best URL→markdown tool, arXiv/SSRN/BibTeX academic search,
  remote MCP (no npm install), many tools work without key
- **Weaknesses**: Acquired by Elastic (Oct 2025) — future roadmap uncertain,
  100 RPM cap on free search

### §4.6 Tavily — RAG-Optimized Factual (verified via npm 0.2.20)

- **MCP command**: `npx -y tavily-mcp`
- **Free tier**: 1,000 credits/month (90-day expiry, no rollover)
- **Strengths**: Fast, RAG-optimized snippets, great for "latest news on X"
- **Weaknesses**: Credits expire after 90 days, smaller credit pool than
  Firecrawl, less deep than Exa for academic

### §4.7 Selection Logic (TIER 3)

```python
def select_research_tool(query: str, source_type: str) -> str:
    """Route research query to best free MCP."""
    if source_type == "academic":  # arXiv, papers, BibTeX
        return "jina:search_arxiv" if "arxiv" in query else "jina:search_bibtex"
    if source_type == "single_url":  # extract one URL
        return "jina:read_url"  # 20 RPM without key, no credits
    if source_type == "domain_map":  # discover site structure
        return "firecrawl:map"  # best domain discovery
    if source_type == "deep_crawl":  # recursive ingest
        return "firecrawl:crawl"  # use sparingly (drains credits)
    if source_type == "sovereign":  # when privacy matters
        return "searxng:web"  # self-hosted
    if source_type == "neural":  # find similar concepts
        return "exa:web_search_exa"
    if source_type == "news":  # latest news
        return "tavily:search"
    # default
    return "searxng:web"  # sovereign primary
```

---

## §5 Strengths/Weaknesses Summary Matrix (All Tiers)

| Tier | Item | Sovereignty | Free | Best Use | Avoid When |
|------|------|:-----------:|:----:|----------|------------|
| 0 | `qwen3-1.7b` (Nova) | ✅ | ✅ | Greetings, routing | Deep reasoning needed |
| 0 | `qwen3-0.6b-q6_k` (Iris) | ✅ | ✅ | Speculative decode | Anything else |
| 0 | `qwen3-1.7b-q6_k` (Sekhmet) | ✅ | ✅ | Medium conversations | Long context (>8K) |
| 0 | `phi-4-mini` (SOPHIA) | ✅ | ✅ | Deep analysis (16K ctx) | Long context (>16K) |
| 0 | `phi-2-omnimatrix` (Brigid) | ✅ | ✅ | Creative writing | Strict accuracy needed |
| 0 | `qwen3-4b-thinking` | ✅ | ✅ | Step-by-step reasoning | Speed matters |
| 0 | `deepseek-r1-8b` | ✅ | ✅ | Hard reasoning | Speed matters (slow) |
| 0 | `krikri-8b` | ✅ | ✅ | Greek language | Other languages |
| 0 | `embeddinggemma-300m` | ✅ | ✅ | Vector embeddings | Multi-modal |
| 1 | Ollama | ✅ | ✅ | Simplest local | Heavy tuning needed |
| 1 | LM Studio | ✅ | ✅ | Best dev iteration | Headless production |
| 1 | native-gguf | ✅ | ✅ | Direct GGUF, full control | No compilation time |
| 2 | Google Gemini 2.5 Pro | ❌ Cloud | ✅ | 1M context, multi-modal | Data sovereignty |
| 2 | OpenRouter `gemma-4-31b:free` | ❌ Cloud | ✅ | SOTA free reasoning | Sovereignty |
| 2 | OpenCode Zen `minimax-m2.5-free` | ❌ Cloud | ✅ | 80.2% SWE-bench | Sovereignty |
| 2 | OpenCode Zen `minimax-m3:free` | ❌ Cloud | ✅ | 200K context (NOT 1M) | Sovereignty |
| 2 | OpenCode Zen `deepseek-v4-flash-free` | ❌ Cloud | ✅ | Fast coding, 200K | Sovereignty |
| 2 | GitHub Copilot free | ❌ Cloud | ✅ | Code completion | Heavy reasoning |
| 3 | SearXNG | ✅ | ✅ | Sovereign search | Need fast news |
| 3 | Firecrawl | ❌ Cloud | ✅ | Deep site mining | Credits matter |
| 3 | Exa | ❌ Cloud | ✅ | Neural semantic | Specific keywords |
| 3 | Jina | ❌ Cloud | ✅ | URL extract, arXiv | 100 RPM cap |
| 3 | Tavily | ❌ Cloud | ✅ | Fast news, RAG | Credits expire |

---

## §6 Master Selection Algorithm

The full tier-aware selector:

```python
def omega_select(
    query: str,
    entity: str,
    context_tokens_estimate: int,
    data_sovereignty_required: bool = False,
) -> str:
    """
    The master Omega Engine model selector. Respects Mandate 7 (local-first).
    Returns: "tier:provider" string suitable for ModelGateway.
    """
    # Sovereignty override: local ALWAYS if required
    if data_sovereignty_required and local_capable(context_tokens_estimate):
        return f"0:local:{entity_model(entity)}"

    # TIER 0: Local GGUF (always try first)
    if local_gguf_available(entity_model(entity)) and \
       context_tokens_estimate <= local_context(entity_model(entity)):
        return f"0:local:{entity_model(entity)}"

    # TIER 1: Local server fallback
    if context_tokens_estimate <= 16_000:
        # Try local servers in order
        for provider in ["native-gguf", "lmster", "ollama"]:
            if provider_available(provider):
                return f"1:{provider}"

    # TIER 2: Free cloud
    if context_tokens_estimate > 200_000:
        # Only Google has 1M+ free
        return "2:google:gemini-2.5-pro"
    if needs_deep_reasoning(query):
        return "2:openrouter:google/gemma-4-31b-it:free"
    if needs_coding_agent(query):
        return "2:opencode-zen:minimax-m2.5-free"  # 80.2% SWE
    if needs_speed(query):
        return "2:opencode-zen:deepseek-v4-flash-free"

    # TIER 3: Research services don't satisfy chat, only research
    # So we still return a TIER 2 for chat, but flag research needs
    return "2:opencode-zen:qwen3.6-plus-free"  # 262K, general
```

---

## §7 Update Protocol

This library is **continually updated** — the user explicitly requested this.
The update protocol:

### §7.1 What Triggers an Update

1. **New model added to `config/models.yaml`** → add row to §1.1, ratings to §1.2
2. **New provider in `config/providers.yaml`** → add to §2.1
3. **New MCP in `~/.config/opencode/mcp_servers.json`** → add to §4.1
4. **Snapshot file updated** (`model_db/CURRENT_MODELS.md`) → bump date in §3
5. **User reports incorrect info** → fix immediately, log to PIVOT_LOG
6. **Quarterly** → full review by Scribe agent (L3 distillation)

### §7.2 Who Updates

- **SOPHIA** (or any Oversoul) via `omega talk "update R100 with <change>"`
- **Cline+M3** (1M context) for synthesis across multiple snapshots
- **Scribe** for the L1→L2→L3 distillation when a new pattern emerges

### §7.3 Update Commands

```bash
# Quick add: just edit the relevant table
edit docs/research/R100_MODEL_REFERENCE_LIBRARY.md

# Then commit
git add docs/research/R100_MODEL_REFERENCE_LIBRARY.md
git commit -m "docs: update R100 with <change>"

# Or via the engine
omega talk "add qwen3-8b-q6_k to R100 §1.1 with 6GB RAM and 8K context"
```

### §7.4 Update Checksum

Each entry MUST cite its data source (file path + line). This makes stale
entries easy to spot — if the source line has changed, the entry is wrong.

---

## §8 Cross-References

### §8.1 Internal (Omega Engine docs)

- `OMEGA_ENGINE.md` — Engine SST
- `SOVEREIGN_MANDATES.md` — Mandate 7 (local-first) is the foundation
- `docs/decisions/PIVOT_LOG.md` — D61 (local-first centralization), D78 (is_cloud
  classification), D80 (Ollama URL), D81 (model overrides), D82 (entity routing),
  **D83-D86 (added 2026-06-02: SearXNG, MCP wiring, matrix pattern, M3 context)**
- `config/models.yaml` — GGUF catalog
- `config/providers.yaml` — Provider chain
- `~/.config/opencode/mcp_servers.json` — MCP servers (5 wired)

### §8.2 Existing Reference Docs (SNAPSHOTS — use R100 to find the right one)

- `docs/research/model_db/CURRENT_MODELS.md` — Free cloud model catalog
- `docs/research/OPENCODE_ZEN_MODEL_REFERENCE.md` — Zen detail
- `docs/research/OPENROUTER_MODEL_REFERENCE.md` — OpenRouter detail
- `docs/research/FREE_TIER_MODEL_INDEX.md` — Free tier index
- `docs/research/FREE_MODEL_VERIFICATION_REPORT.md` — Verification
- `docs/research/GITHUB_COPILOT_FREE_TIER_RESEARCH.md` — Copilot detail
- `docs/research/R99_free_tier_search_apis.md` — Search API detail (SearXNG, etc.)

### §8.3 Legacy (mined for patterns)

- `/home/arcana-novai/Documents/Archives/Old-Stacks/Xoe-NovAi/docs/ai-research/admin/ai-provider-matrix.md` — The original 327-line pattern (Grok/Claude/ChatGPT/Gemini × 7 metrics)

### §8.4 Live Handoffs (in progress)

- `data/handoff/HANDOFF_ARTISAN_TO_OPENCODE_M3_REVIEW_20260602.md` — Engine map (Artisan M3 1M → OpenCode M3 200K)
- `data/handoff/HANDOFF_OPENCODE_M3_TO_CLINE_M3_DIALOG_20260602.md` — This dialog (OpenCode M3 200K → Cline M3 1M)

---

## §9 Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0.0 | 2026-06-02 | OpenCode+M3 (200K) | Initial R100. Tiers 0-3. M3 200K context correction. SearXNG verified. All 5 MCPs wired. |

---

*Maintained by SOPHIA. Cline+M3 (1M) is the synthesis partner for cross-document
reviews. Scribe owns L1→L2→L3 distillation. The library lives at
`docs/research/R100_MODEL_REFERENCE_LIBRARY.md` and is the single index for
every free inference + research resource in the Omega Engine.*
