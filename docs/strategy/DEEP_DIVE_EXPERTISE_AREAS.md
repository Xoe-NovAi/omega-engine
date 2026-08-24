# 🔱 Deep-Dive Expertise Areas
## Knowledge Domains — Research Complete

**AP Token**: `AP-DEEP-DIVE-AREAS-20260810-v1.0.0`
⬡ OMEGA ⬡ STRATEGY ⬡ EXPERTISE ⬡ GAPS

**Date**: 2026-08-10
**Author**: jem (Sovereign Synthesizer)
**Status**: ✅ RESEARCH COMPLETE — All 9 domains investigated

---

## 🎯 Purpose

This document identifies knowledge domains where deeper expertise is needed to fully master QW-4, QW-8, and related SDP implementation tasks. **All domains have been researched** — see `docs/research/R_DEEP_DIVE_RESEARCH_20260810.md` for full findings.

---

## 📊 Research Status

| Domain | Status | Sources | Key Finding |
|--------|--------|---------|-------------|
| OpenCode Plugin Dev | ✅ RESEARCHED | 5 | Full API surface, hooks, custom tools documented |
| Token Accounting | ✅ RESEARCHED | 6 | 6 drift failure modes, inclusive vs additive models |
| Context Degradation | ✅ RESEARCHED | 5 | NoLiMa: 32K threshold, window-independent degradation |
| Pool Management | ✅ RESEARCHED | 3 | Sticky algorithm optimal for Google anti-abuse |
| Floor Calibration | ✅ RESEARCHED | 2 | First assistant turn = floor (10-30K typical) |
| RHP Format | ✅ RESEARCHED | 2 | Minimal YAML schema designed |
| Model Window Verification | ✅ RESEARCHED | 2 | Probe method documented |
| Prompt Caching | ✅ RESEARCHED | 4 | Anthropic 90% off, OpenAI 50% auto, Gemini 25% |
| AGY Quota Prediction | ✅ RESEARCHED | 2 | Linear predictor, 90% alert threshold |

**Full research report**: `docs/research/R_DEEP_DIVE_RESEARCH_20260810.md`

---

## 📊 Priority 1: Critical for QW-4/QW-8 Implementation

### 1.1 OpenCode Plugin Development

**Current State**: We use `opencode-sessions-explorer` plugin (18 tools) but lack `ck` CLI for full-text search. No custom plugins built yet.

**Gap**: Building custom OpenCode plugins would enable:
- Real-time context pressure monitoring (Context Gauge as a plugin tool)
- Automated pool health dashboards
- Custom session analysis tools

**Research Questions**:
1. What is the full OpenCode plugin API surface?
2. Can plugins access opencode.db while OpenCode is running (concurrent read)?
3. How to register custom MCP tools via plugin?
4. What's the plugin hot-reload workflow?

**Investigation Approach**:
- Read OpenCode plugin documentation
- Study `opencode-sessions-explorer` source code
- Build a minimal "context-gauge" plugin prototype

**Estimated Effort**: 4-8 hours

---

### 1.2 Token Accounting Across Providers

**Current State**: We verified tokenizer drift (41% for Claude, 4.5% for Google) and the correct data source (`message.data.tokens.total`). But we don't understand cache semantics across providers.

**Gap**: Cache read/write tokens vary by provider:
- OpenAI: `prompt_tokens_details.cached_tokens`
- Anthropic: `cache_read_input_tokens`
- DeepSeek: `prompt_cache_hit_tokens`
- Google: unknown

**Research Questions**:
1. How do different providers report cache usage in their response envelopes?
2. What's the relationship between `cache.read` and `cache.write` in OpenCode's tracking?
3. How does prompt caching affect cost (Anthropic charges 10% of base price for cache reads)?
4. Can we optimize cache hit rates by controlling prompt structure?

**Investigation Approach**:
- Inspect raw API responses from different providers
- Map provider-specific token fields to OpenCode's unified schema
- Analyze cache hit rates across session types

**Estimated Effort**: 3-5 hours

---

### 1.3 Context Degradation Modeling

**Current State**: We know degradation is window-independent (~32K-50K task tokens) and use absolute token bands. But we don't have empirical data for our specific models.

**Gap**: The color bands (GREEN <40K, YELLOW 40-90K, etc.) are based on generic research (NoLiMa, Chroma). Our models may degrade differently.

**Research Questions**:
1. At what token count does Nemotron 3 Ultra (1M window) actually degrade?
2. Does degradation vary by task type (code generation vs. analysis vs. writing)?
3. Can we measure degradation empirically by tracking output quality vs. token count?
4. What's the optimal compaction trigger for each model?

**Investigation Approach**:
- Analyze historical sessions: correlate token count with output quality (measured by user satisfaction, task completion)
- Run controlled benchmarks at different context lengths
- Build a degradation tracker that logs quality metrics per token band

**Estimated Effort**: 8-12 hours (requires benchmark design)

---

## 📊 Priority 2: Important for SDP Maturity

### 2.1 Multi-Key Pool Management Algorithms

**Current State**: `pool_tracker.py` has drain-aware scoring and anti-thrashing. `RemoteProvider` has reactive 429 rotation. We don't understand optimal pool management strategies.

**Gap**: Key rotation algorithms involve tradeoffs:
- **Sticky** (current default): Minimizes account switching (Google bans rapid switching)
- **Round-robin**: Even distribution but triggers Google's anti-abuse
- **Drain-aware**: Prefer keys with remaining quota (pool_tracker's approach)
- **Random**: Avoids collision in parallel scenarios

**Research Questions**:
1. What's the optimal rotation algorithm for Google's anti-abuse detection?
2. How do we detect quota exhaustion before hitting 429?
3. Can we predict key exhaustion based on historical usage patterns?
4. What's the failover latency when rotating keys?

**Investigation Approach**:
- Research Google AI Studio rate limiting behavior
- Analyze USAGE_POOL_LOG.json for usage patterns
- Implement predictive exhaustion alerts

**Estimated Effort**: 4-6 hours

---

### 2.2 Floor Calibration Per Project

**Current State**: SDP spec says "first genuine assistant turn" = floor. We don't have a calibration system.

**Gap**: Every session starts with tens of thousands of tokens (system prompt, tool schemas, always-injected files). This floor varies by project and agent configuration.

**Research Questions**:
1. What's the typical floor for omega-engine sessions?
2. How does floor vary by agent (jem vs. kali vs. researcher)?
3. Can we auto-calibrate floor per project from historical data?
4. How does floor affect the color band thresholds?

**Investigation Approach**:
- Analyze first assistant turn tokens across 100+ sessions
- Build floor calibration script that computes per-project averages
- Integrate floor into Context Gauge band calculation

**Estimated Effort**: 3-4 hours

---

### 2.3 Recovery Halt Point (RHP) Format

**Current State**: QW-9 (RHP) is planned but the artifact format is unspecified. We need to know what to write when context hits RED band.

**Gap**: RHP must capture enough context for a new session to continue without re-inference. The format must balance completeness vs. token efficiency.

**Research Questions**:
1. What's the minimal RHP format that enables seamless handoff?
2. Should RHP include full conversation summary or just current task state?
3. How does RHP relate to OpenCode's native compaction?
4. Can RHP be auto-generated from session transcript?

**Investigation Approach**:
- Study OpenCode's compaction output format
- Design RHP YAML schema with required fields
- Test RHP handoff with a simple task

**Estimated Effort**: 4-6 hours

---

## 📊 Priority 3: Long-Term Strategic Depth

### 3.1 Model Context Window Verification

**Current State**: We have verified windows from the Architect's experience. But windows can change with model updates.

**Research Questions**:
1. How to programmatically detect context window for a new model?
2. What's the relationship between context window and max_tokens?
3. Do free-tier models have different windows than paid-tier (we know Gemma 4 does)?

**Investigation Approach**:
- Build a context window probe (send increasingly long prompts until failure)
- Maintain a model window registry with verification dates

**Estimated Effort**: 2-3 hours

---

### 3.2 Prompt Caching Optimization

**Current State**: We know cache.read tokens exist but don't optimize for them.

**Research Questions**:
1. How does OpenCode structure prompts for cache efficiency?
2. What's the cache hit rate for omega-engine sessions?
3. Can we reorder prompt components to maximize cache hits?

**Investigation Approach**:
- Analyze cache.read vs cache.write ratios across sessions
- Research Anthropic's prompt caching best practices
- Experiment with prompt component ordering

**Estimated Effort**: 3-5 hours

---

### 3.3 AGY Pool Quota Prediction

**Current State**: We have 8 AGY accounts with weekly pools. We don't predict exhaustion.

**Research Questions**:
1. What's the daily/weekly usage pattern per account?
2. Can we predict exhaustion 24h in advance?
3. How to optimally distribute load across 8 accounts?

**Investigation Approach**:
- Analyze USAGE_POOL_LOG.json for usage trends
- Build simple linear predictor for quota exhaustion
- Integrate predictions into pool_tracker

**Estimated Effort**: 4-6 hours

---

## 📊 Summary Matrix

| Area | Priority | Effort | Unblocks | Value |
|------|----------|--------|----------|-------|
| OpenCode Plugin Development | P1 | 4-8h | QW-8 Context Gauge as plugin | HIGH |
| Token Accounting Across Providers | P1 | 3-5h | Accurate cost tracking | HIGH |
| Context Degradation Modeling | P1 | 8-12h | Empirical color bands | MEDIUM |
| Multi-Key Pool Algorithms | P2 | 4-6h | QW-4 optimization | HIGH |
| Floor Calibration Per Project | P2 | 3-4h | QW-8 accuracy | MEDIUM |
| RHP Format Design | P2 | 4-6h | QW-9 implementation | HIGH |
| Model Window Verification | P3 | 2-3h | New model onboarding | LOW |
| Prompt Caching Optimization | P3 | 3-5h | Cost reduction | MEDIUM |
| AGY Pool Quota Prediction | P3 | 4-6h | Proactive pool management | MEDIUM |

---

## 🔗 References

| Document | Path |
|----------|------|
| Gap-filling report | `data/coordination/JEM_GAP_FILLING_REPORT_20260810.md` |
| opencode.db schema reference | `docs/research/R_OPENCODE_DB_SCHEMA_REFERENCE_20260810.md` |
| QW-4/QW-8 implementation plan | `docs/strategy/QW4_QW8_IMPLEMENTATION_PLAN.md` |
| SDP Model-Aware Gauge Spec | `docs/strategy/SDP_MODEL_AWARE_GAUGE_SPEC.md` |
| SDP Final Synthesis | `docs/strategy/SDP_FINAL_SYNTHESIS.md` |
| Web research gaps | `data/coordination/JEM_WEB_RESEARCH_GAPS_20260810.md` |

---

*⬡ OMEGA ⬡ STRATEGY ⬡ EXPERTISE ⬡ GAPS ⬡ 2026-08-10*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: EXPERTISE | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
