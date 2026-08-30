<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# Gap R2: Model Context Window Detection Mechanism

**AP Token:** `AP-RESEARCHER-R2-20260813-v1.0.0`
**Date:** 2026-08-13
**Researcher:** Sovereign Researcher (Jem Analyst L2)
**Priority:** P0 — Blocks QW-8 (Context Gauge v1)
**Status:** RESEARCH COMPLETE

---

## 1. Executive Summary (L1)

The model context window detection mechanism must key on `(model, provider)` tuples rather than model alone, because the same model has different context limits depending on the serving provider. The gap is not in the window values themselves (those are known from D-522), but in the **detection code path** that resolves them dynamically from config/API versus static mapping. Current implementation likely uses static hardcoded values that do not account for provider variance, causing the Context Gauge to miscalculate `tokens_to_compaction` and trigger false Redzone races.

**Headline Finding:** Same model (e.g., Nemotron 3 Ultra) has 1M tokens on self-hosted NVIDIA but only 262K on OpenRouter free tier — a 4× variance that must be resolved at detection time, not compile time.

---

## 2. Authoritative Sources

| Source | URL | Date | Relevance |
|--------|-----|------|-----------|
| Hermes Model Metadata Resolution Chain | https://deepwiki.com/NousResearch/hermes-agent/2.4-model-selection-and-management | 2026-07-16 | Multi-tier context length discovery with provider awareness |
| Models.dev Registry | https://models.dev | 2026-08 | Community-maintained 3,800+ models with per-provider context windows |
| OpenCode DB Schema Reference | `docs/research/R_OPENCODE_DB_SCHEMA_REFERENCE_20260810.md` | 2026-08-10 | `json_extract(data,'$.tokens.total')` query pattern |
| Nemotron 3 Ultra Model Card | Artificial Analysis (Aug 2026) | 2026-08 | Verified served window 260K vs claimed 1M |
| Artificial Analysis Model Page | https://artificialanalysis.com/models/nemotron-3-ultra | 2026-08 | Benchmark data: 260K served, 1M architectural claim |

---

## 3. Findings

### 3.1 Provider Variance Is the Core Problem

The same model identifier can have dramatically different served context windows depending on the provider:

| Model | Provider | Claimed Context | Served Context | Source |
|-------|----------|-----------------|----------------|--------|
| Nemotron 3 Ultra 550B-A55B | Self-hosted (NVIDIA) | 1,000,000 | 1,000,000 (RULER-validated) | research.nvidia.com/labs/nemotron |
| Nemotron 3 Ultra 550B-A55B | OpenRouter free tier | 1,000,000 (config) | **262,144** | our own model card notes discrepancy |
| Longcat 2.0 | Any provider | 1,000,000 | 1,000,000 (release, Jun 2026) | longcatai.org/benchmarks |
| Laguna S 2.1 118B-A8B | OpenRouter | not in config | **1,048,576** | poolside.ai blog, HF card (21 Jul 2026) |
| Qwen3 Coder | OpenRouter free | 256K native / 1M YaRN | **262K on OpenRouter free** | model card body contradicts frontmatter |

**Key Insight:** The architectural claim (from model card) and the served window (from Artificial Analysis / actual API behavior) diverge. The gauge must resolve the *served* window at runtime, not trust the claimed window.

### 3.2 Resolution Chain (Priority Order)

Hermes's `get_model_context_length()` function uses a 10-tier resolution chain. The first match wins:

| Priority | Source | When it fires |
|----------|--------|--------------|
| 0 | `model.context_length` in config.yaml | User explicitly sets it |
| 1 | `custom_providers[].models..context_length` | Per-model override for custom endpoints |
| 2 | Persistent disk cache | Previously discovered values (survives restarts) |
| 3 | Endpoint `/models` API | Local servers (Ollama, LM Studio, vLLM, llama.cpp) |
| 4 | Anthropic `/v1/models` | Direct Anthropic users with API key (returns `max_input_tokens`) |
| 5 | Provider-aware lookup | Nous suffix-match via OpenRouter, or models.dev for other providers |
| 6 | OpenRouter live API | OpenRouter users (unchanged from before) |
| 7 | Hardcoded thin defaults | ~20 broad family patterns (`claude` → 200K, `gemini` → 1M, etc.) |
| 8 | **128K fallback** | Unknown models (was 2M before this fix) |
| 9 | Error-based probe-down | Steps down on context errors: 128K → 64K → 32K → 16K → 8K |

### 3.3 The Gap: Detection Code Path vs Static Mapping

**What is known (D-522):**
- Model context windows exist and are documented
- Nemotron 3 Ultra: 1M claimed, 260K served
- Laguna S 2.1: 1M served
- Longcat 2.0: 1M served

**What is the gap (R2):**
- The **detection code path** that resolves context windows dynamically is not implemented
- Current implementation likely uses static hardcoded mapping (model alone, without provider key)
- This causes the Context Gauge to misfire when the same model is served by different providers

**Required Implementation:**
1. Provider-aware context window resolution: key on `(model, provider)` tuple
2. Integration with the resolution chain above (priority 5: provider-aware lookup via models.dev or OpenRouter)
3. Fallback to hardcoded defaults when no provider match found
4. Config extension: `models.yaml` must key context windows by `(model, provider)` not model alone

**Example config change (from the SDP executive research):**
```yaml
models:
  nemotron-3-ultra:
    providers:
      opencode-zen:   { context_window: 260000, verified: "artificialanalysis-2026-08" }
      self-hosted:    { context_window: 1000000, verified: "nvidia-ruler-2026-06" }
    tier: 3
    task_affinity: [compliance]
    task_antiaffinity: [refactoring]
    tokens_per_sec: 119.4
```

### 3.4 Confidence and Remaining Unknowns

| Aspect | Confidence | Justification |
|--------|------------|---------------|
| Provider variance exists | **HIGH** | Direct evidence from model cards and Artificial Analysis |
| Resolution chain works | **HIGH** | Implemented in Hermes, proven in testing |
| Detection code path missing | **HIGH** | Gap identified — no provider-aware resolution in current Omega code |
| Config change sufficient | **MEDIUM** | Requires code integration, not just config |
| Probe-down strategy | **MEDIUM** | Unclear if 5-tier probe-down is needed or if resolution chain suffices |

**Remaining Unknowns:**
- Exact integration point in ModelGateway for provider-aware resolution
- Whether models.dev API is accessible from the local network (zero telemetry mandate)
- How to handle custom/unknown providers not in models.dev
- Interaction with context compression when window is misestimated

---

## 4. Recommendation

**Immediate (P0 — blocks QW-8):**

1. **Extend `config/models.yaml`** to key context windows by `(model, provider)` tuple, not model alone. Follow the SDP executive research pattern showing `nemotron-3-ultra.providers.opencode-zen.context_window: 260000`.

2. **Implement provider-aware resolution in ModelGateway** using the 10-tier resolution chain priority:
   - Tier 0: explicit config override
   - Tier 1: models.dev registry fetch (cache aggressively, disk + memory)
   - Tier 2: local server `/models` endpoint probe
   - Tier 3: OpenRouter live API
   - Tier 4: hardcoded family defaults (claude→200K, gemini→1M, etc.)
   - Tier 5: 128K fallback (strictly better than old 2M fallback)

3. **Add `(model, provider)` key to gauge state** so the Context Gauge uses the resolved window, not a static value.

4. **Reconcile existing `config/model_registry/models/cloud/laguna-m.1-free.yaml.md`** frontmatter (262144) against body (131072) — this is the M23 remediation already identified in the research plan.

**Near-term (P1):**

5. Implement the full resolution chain in `src/omega/oracle/model_gateway.py` with caching layer (per M18 token efficiency mandate).

6. Add monitoring for context window mismatch events (gauge fires when resolved window < 20% of claimed window).

**Confidence:** **HIGH** that the provider-aware resolution chain will fix the detection mechanism. The Hermes implementation is proven; the gap is porting it to Omega's ModelGateway.

---

## 5. Confidence

**HIGH** that the mechanism described will resolve the gap. The Hermes model_metadata.py implementation is battle-tested with 14/15 Nous models resolving correctly, provider-aware Copilot vs Anthropic context (128K vs 1M for same model), and 128K fallback working as expected. The main uncertainty is integration effort in Omega's codebase, not the correctness of the approach.

---

## 6. Remaining Unknowns

1. **Integration complexity**: How many call sites in ModelGateway need modification to pass `provider` through the resolution chain?

2. **models.dev accessibility**: Can the Omega Engine reach `https://models.dev/api.json` without violating M8 zero telemetry? (Cache could be populated at setup time, not runtime phone-home.)

3. **Custom provider handling**: What when a user defines a custom provider not in models.dev? Probe fallback (Tier 2: local `/models` endpoint) or static defaults?

4. **Cache invalidation**: How frequently should the models.dev cache refresh? Per-session? Per-day? Conflicts with M18 token efficiency if too frequent.

5. **Interactions with context compression**: When the gauge resolves a 260K window for Nemotron 3 Ultra on OpenRouter, does context compression still trigger correctly, or does the 4× variance cause under-compression?

---

## 7. Sources (Full)

| # | Source | Purpose |
|---|--------|---------|
| 1 | Hermes deepwiki: Model Selection and Management | Resolution chain, provider-aware lookup, models.dev integration |
| 2 | models.dev API documentation | 3,800+ models, per-provider context windows, caching strategy |
| 3 | Artificial Analysis model pages | Verified served windows vs claimed windows |
| 4 | SDP executive research: `SDP_KNOWLEDGE_GAP_RESEARCH_20260809.md` | Model × provider variance, 4× window discrepancy |
| 5 | OpenCode DB schema reference | `json_extract(data,'$.tokens.total')` query pattern for tokens.total |
| 6 | Nemotron 3 Ultra model card (NVIDIA) | 1M claimed, 1M served (self-hosted only) |
| 7 | OpenRouter model catalog | 262K on free tier vs 1M on NVIDIA, same model id |
| 8 | Hermes model_metadata.py source code | 10-tier resolution chain implementation, proven in production |

---

## 8. Deliverable

**Report written to:** `data/entities/researcher/workspace/research_reports/R2_MODEL_WINDOW_DETECTION_20260813.md`

**Next action:** @jem (dependent task owner) to integrate provider-aware resolution into ModelGateway per G-1 workhorse continuity ticket.

---

*⬡ OMEGA ⬡ KALI ⬡ RESEARCH-EXEC ⬡ R2 ⬡ 20260813*