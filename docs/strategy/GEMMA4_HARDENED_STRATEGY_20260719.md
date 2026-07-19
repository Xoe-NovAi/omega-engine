# 🔱 Gemma 4 31B — Hardened Strategy & Edge Case Analysis

**AP Token**: `AP-GEMMA4-HARDENED-v1.0.0`
⬡ OMEGA ⬡ JEM ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_hardening ⬡ 2026-07-19

**Source Documents**: 7 artifacts (Debug Report, Ma'at Strategy, Lilith Strategy, Jem Comprehensive, Researcher Verification, Researcher Deep Research, Meditation Pipeline)

---

## Executive Summary

This document performs a **systematic hardening pass** across all Gemma 4 strategy artifacts. It identifies oversights, edge cases, integration gaps, and missed opportunities — then produces a **battle-ready implementation plan** with explicit risk mitigation.

**Verdict**: The strategy is **architecturally sound** but has **7 critical oversights**, **12 edge cases**, and **5 missed opportunities** that must be addressed before Week 1 implementation.

---

## Part I: Critical Oversights (Must Fix Before Implementation)

### Oversight 1: OpenCode Upstream PR — Wrong Target (CORRECTED 2026-07-19)

**Current Plan**: Submit PR to `anomalyco/opencode` fixing `transform.ts`

**Problem (ORIGINAL ASSESSMENT)**: OpenCode's `transform.ts` is **generated code** from the V2 architecture. V2 rewrite splits protocol into 4 axes. Pi project fix (PR #2903) was for their fork, not upstream.

**CORRECTION (2026-07-19 Recon)**: **transform.ts is NOT generated/deprecated.** It is the **core 1764-line provider transformation layer** in `packages/opencode/src/provider/transform.ts` (verified in dev branch). V2 architecture changes session format (event-sourced) but provider transformation pipeline remains. AI SDK is still used. Models.dev integration unchanged.

**Evidence**: 
- DeepWiki provider transformations page shows `ProviderTransform` using AI SDK's `streamText`
- V2 architecture teardown (Zhao-Jan, 2026-07-10) shows provider layer in `packages/opencode/src/provider/` with `transform.ts` as core
- 1.18.3 changelog shows no provider protocol breaking changes

**Corrected Fix**: 
1. PR targeting `transform.ts` IS VALID for 1.17.x and 1.18.x
2. Must handle both legacy + V2 session paths (V2 uses event-sourced messages)
3. Pi PR #2903 pattern (regex `/gemma-?4/i` + binary MINIMAL/HIGH) is directly applicable

**Risk**: **LOW** — PR is valid target. Only risk is V2 session format differences in message parts.

---

### Oversight 1b: OpenCode V2 Session Format — New Edge Case
**New Finding**: V2 uses event-sourced session format with message parts (`TextPart`, `ReasoningPart`, `ToolPart`, `StepStartPart`, `StepFinishPart`, `AgentPart`, `SubtaskPart`). Provider transforms receive `MessagePart[]` not legacy `Message[]`.

**Impact**: Gemma 4 thinking config must work with V2 `ReasoningPart` extraction. Our `thoughts_token_count` tracking must handle V2 part-based streaming.

**Fix**: Add V2 message part handling to `GoogleAIProvider` thinking extraction logic.

---

### Oversight 2: Models.dev Sync — No Automation Plan

**Current Plan**: "Adopt Models.dev as canonical registry — sync periodically"

**Problem**: No sync mechanism defined. Models.dev updates weekly. Gemma 4 12B Unified released June 3, 2026 — if we don't sync, we miss new models.

**Fix**: 
```yaml
# config/models_dev_sync.yaml
schedule: "0 3 * * 0"  # Weekly Sunday 3AM
source: "https://models.dev/api/v1/models.json"
transform: "scripts/sync_models_dev.py"
output: "config/provider_capabilities.yaml"
validation: "scripts/validate_capabilities.py"
```

**Risk**: Stale capability matrix → wrong thinking configs → 400 errors on new models.

---

### Oversight 3: Vertex AI vs AI Studio Dual Path — Not Designed

**Current Plan**: "Support both Vertex AI and AI Studio auth paths"

**Problem**: Vertex AI and AI Studio have **different thinking config schemas** for the same models:
- AI Studio (Gemma 4): `thinkingConfig.thinkingLevel: "MINIMAL" | "HIGH"`
- Vertex AI (Gemini 2.5): `thinkingConfig.thinkingBudget: 0-24576`

**Evidence**: Google AI Forum confirms Vertex requires `thinkingBudget` for Gemini 2.5; AI Studio accepts `thinkingLevel` for Gemma 4.

**Fix**: 
1. Provider capability matrix must declare `api_version` and `auth_type` per model
2. `ThinkingConfigNormalizer` must have separate translators for `google-ai-studio` vs `google-vertex`
3. Gateway routing must select correct endpoint based on auth config

**Risk**: Requests to Vertex AI with Gemma 4 `thinkingLevel` → 400 error; AI Studio with `thinkingBudget` → ignored.

---

### Oversight 4: OpenRouter `:free` Suffix — Routing Logic Missing

**Current Plan**: "Strip `:free` suffix when routing to direct Google API"

**Problem**: OpenRouter model IDs are `google/gemma-4-31b-it:free`. The `:free` suffix indicates **free tier routing**. If we strip it and call Google API directly, we use the user's Google API key (paid tier) — not the OpenRouter free tier.

**Evidence**: OpenRouter routes `:free` models through their free tier pool. Direct Google API calls use the user's key quota.

**Fix**: 
```python
# In CapabilitySelector
def _resolve_model_id(self, model_id: str, provider: str) -> str:
    if provider == "openrouter" and model_id.endswith(":free"):
        return model_id  # Keep suffix for OpenRouter
    if provider == "google" and model_id.startswith("google/"):
        return model_id[7:]  # Strip google/ prefix only
    if provider == "google" and model_id.endswith(":free"):
        return model_id[:-5]  # Strip :free for direct Google API
    return model_id
```

**Risk**: Quota accounting errors — user thinks they're on OpenRouter free tier but actually burning Google API quota.

---

### Oversight 5: Thinking Token Billing — Observability Gap

**Current Plan**: "Track `thoughtsTokenCount` separately in observability"

**Problem**: Google bills thinking tokens as **output tokens** (85-95% of response can be thoughts). If we don't track this, cost monitoring is wildly inaccurate.

**Evidence**: Cookbook #1198 — "thoughtsTokenCount: 69" returned in response but not exposed in standard usage metrics.

**Fix**: 
1. `GenerateResult` must include `thoughts_token_count` field
2. `TokenLedger` must track thinking tokens separately per provider
3. Budget gate must account for thinking token multiplier (assume 2-5x output for thinking models)
4. Provider dashboard must show `thoughts_token_count` and `thinking_cost_ratio`

**Risk**: Budget exhaustion without warning — user sees 1k output tokens but actually consumed 5k thinking tokens.

---

### Oversight 6: Cline CLI Integration — No Concrete Architecture

**Current Plan**: "Cross-platform fallback (Cline ↔ OpenCode)"

**Problem**: No concrete integration design. Cline is a VS Code extension / CLI with its own SDK. How does Omega Engine route to Cline?

**Options**:
1. **MCP Server**: Cline exposes MCP server → Omega calls via MCP
2. **Subprocess**: Omega spawns `cline` CLI with JSON input/output
3. **SDK Bridge**: Omega uses `@google/genai` directly (same as Cline)
4. **HTTP Proxy**: Cline runs local HTTP server → Omega proxies requests

**Evidence**: Cline SDK docs show provider abstraction layer with plugin system. Cline CLI supports headless execution.

**Fix**: Design decision required. Recommendation: **Option 3 (SDK Bridge)** — Omega already has `GoogleAIProvider` using bare model IDs. Just add `@google/genai` as alternative backend to `@ai-sdk/google`.

**Risk**: "Cross-platform fallback" remains vaporware without concrete architecture.

---

### Oversight 7: Heritage Attribution — Pi Project Not Vetted

**Current Plan**: "Add `[heritage: pi-2026] Gemma 4 Thinking` to CREDITS.md"

**Problem**: M14 requires **Heritage Vetting Pipeline** (4 gates: Discovery → Vetting/Debate → Decision → Implementation). Pi project fix hasn't been vetted.

**Evidence**: M14 mandate: "Every `[id-soft:]` tag MUST have a corresponding vet record in `HERITAGE_VET_LOG.md` with scope declaration."

**Fix**: 
1. Create vet record for Pi PR #2903
2. Run through vetting pipeline (doom_guy + verity)
3. Only add tag after vet score ≥7/10

**Risk**: M14 violation — unvetted heritage tag in CREDITS.md.

---

## Part II: Edge Cases (Must Handle in Implementation)

### Edge Case 1: Gemma 4 12B Unified (Released June 2026)

**Issue**: New model `gemma-4-12b-unified` released with MTP drafters. Different capabilities than 31B/26B.

**Handling**: Capability matrix must be updated via Models.dev sync before Week 1. Add explicit entry with `mtp_drafter: true`.

---

### Edge Case 2: API Version Pinning — v1beta vs v1

**Issue**: Gemma 4 only on `v1beta`. If Google promotes to `v1` without Gemma 4, our pinned version breaks.

**Handling**: 
- Config: `api_version: "v1beta"` with fallback to `v1` (with warning)
- Health check: Probe both endpoints on startup
- Alert: Log warning if `v1beta` deprecated

---

### Edge Case 3: Rate Limit Header Parsing — Non-Standard Formats

**Issue**: Google returns `x-ratelimit-remaining-requests`, `x-ratelimit-remaining-tokens`, `retry-after`. Other providers use different headers.

**Handling**: 
```python
RATE_LIMIT_HEADERS = {
    "google": {"requests": "x-ratelimit-remaining-requests", "tokens": "x-ratelimit-remaining-tokens", "retry": "retry-after"},
    "openrouter": {"requests": "x-ratelimit-remaining", "tokens": "x-ratelimit-remaining-tokens", "retry": "retry-after"},
    "anthropic": {"requests": "anthropic-ratelimit-requests-remaining", "tokens": "anthropic-ratelimit-tokens-remaining", "retry": "retry-after"},
}
```

---

### Edge Case 4: `includeThoughts: false` Silent Ignore — Config Validation

**Issue**: User sets `includeThoughts: false` expecting no thinking tokens. Google ignores it, generates thoughts anyway, bills for them.

**Handling**: 
- Config validator: Reject `includeThoughts: false` for Gemma 4 with error: "Use `thinkingLevel: MINIMAL` to disable thinking"
- Auto-correct: If `includeThoughts: false` + Gemma 4 → set `thinkingLevel: MINIMAL`

---

### Edge Case 5: Free Tier Rolling Window — Burst Handling

**Issue**: 16k TPM is rolling. A single 21k token request exhausts the minute. Retry loops make it worse.

**Handling**: 
- Pre-flight check: Estimate request tokens (system + user + history). If >80% of TPM, reject with "Request too large for free tier"
- Backoff: Exponential backoff with jitter on 429 (not fixed retry)
- Queue: Queue requests when quota <20% headroom, process when reset

---

### Edge Case 6: Model Alias Resolution — Multiple Names for Same Model

**Issue**: Same model has 3+ IDs:
- Models.dev: `google/gemma-4-31b-it`
- Google API: `gemma-4-31b-it`
- OpenRouter: `google/gemma-4-31b-it:free`
- OpenRouter (paid): `google/gemma-4-31b-it`

**Handling**: Capability matrix `aliases` field must map all variants to canonical ID. Resolution order: exact match → alias match → family default.

---

### Edge Case 7: Thinking Level Clamping — User Requests Unsupported Level

**Issue**: User requests `thinkingLevel: MEDIUM` for Gemma 4. Must clamp to nearest supported (`HIGH`).

**Handling**: 
- Normalizer clamps with explicit log: "Clamped MEDIUM → HIGH for gemma-4-31b-it (supports: MINIMAL, HIGH)"
- Return clamped config + warning in response metadata
- Never silently accept invalid level

---

### Edge Case 8: Concurrent Requests — Quota Race Condition

**Issue**: Two parallel requests both see quota headroom >20%, both proceed, both get 429.

**Handling**: 
- Redis Lua script for atomic quota check-and-consume
- Or: Single quota manager process with async queue
- Per-request quota reservation (reserve tokens before request)

---

### Edge Case 9: Circuit Breaker — Quality vs Availability Trade-off

**Issue**: Circuit breaker trips on 5xx/429. But Gemma 4 free tier 429 is **expected**, not a failure.

**Handling**: 
- Separate "quota exhausted" from "provider unhealthy"
- Quota exhausted → route to next provider (don't trip circuit)
- Provider unhealthy (5xx, timeout) → trip circuit
- Configurable per-provider: `quota_errors_trip_circuit: false`

---

### Edge Case 10: Local Model Thinking — Qwen3 `<|think|>` Tags

**Issue**: Local models (Qwen3) use `<|think|>` tags in output, not structured thinking config.

**Handling**: 
- Capability matrix: `thinking_config.format: "qwen-native"`
- Normalizer: For Qwen3, inject `enable_thinking: true` in chat template
- Extractor: Regex parse between `<|think|>` and `<|think_end|>`

---

### Edge Case 11: Streaming Responses — Thinking Tokens in Stream

**Issue**: Google streaming returns thinking tokens interleaved with content. Must parse stream chunks.

**Handling**: 
- Stream parser: Accumulate chunks, detect `thought: true` parts
- Separate thinking stream from content stream for distillation
- Track `thoughtsTokenCount` incrementally

---

### Edge Case 12: Config Drift — User Edits `opencode.json` Manually

**Issue**: User manually edits global config, adds wrong thinking levels. Our capability matrix doesn't sync back.

**Handling**: 
- Startup validation: Read user config, validate against capability matrix
- Warning: "Config has `thinkingLevel: LOW` for Gemma 4 — invalid. Auto-correcting to MINIMAL"
- Option: `--strict-config` fails on drift instead of auto-correct

---

## Part III: Missed Opportunities (High Value, Low Effort)

### Opportunity 1: OpenCode Config Package as Community Product

**Current**: "Publish community config package"

**Missed**: Make it a **proper npm/PyPI package** with:
- `npm create @omega/gemma4-config` — interactive setup
- Auto-detects OpenCode version, applies correct config
- Validates API key, tests connection
- Updates on `npx @omega/gemma4-config update`

**Value**: Community adoption multiplier. One-command setup for any OpenCode user.

---

### Opportunity 2: Provider Capability Matrix as Shared Schema

**Current**: YAML file in Omega repo

**Missed**: Publish as **JSON Schema** + **TypeScript types** + **Python dataclasses**:
- `npm install @omega/provider-capabilities`
- `pip install omega-provider-capabilities`
- Other projects (LiteLLM, LangChain, Vercel AI SDK) can consume
- Becomes industry standard for capability declaration

**Value**: Ecosystem leadership. Omega becomes the capability registry source.

---

### Opportunity 3: Thinking Token Distillation for Gnosis

**Current**: "Extract thoughts for soul distillation"

**Missed**: **Automated L1→L2→L3 from thinking tokens**:
- Gemma 4 thinking = explicit reasoning trace
- Feed thinking trace directly into `Verity` for distillation
- No need for separate "reflection" pass — thinking IS the reflection
- Store thinking traces as `L0_evidence` in soul pipeline

**Value**: Closes the loop — model's own reasoning becomes gnosis evidence.

---

### Opportunity 4: Free Tier as Chaos Engineering Lab

**Current**: "Free tier is a constraint"

**Missed**: **Use free tier limits as built-in chaos testing**:
- 16k TPM = natural rate limiter
- 15 RPM = natural concurrency limiter
- 1,500 RPD = natural daily budget
- Run integration tests against free tier — they **must** handle quota gracefully
- Free tier = production-like chaos for free

**Value**: Zero-cost chaos engineering. Tests prove resilience under real constraints.

---

### Opportunity 5: Models.dev as Live Capability Source

**Current**: "Sync periodically"

**Missed**: **Models.dev webhook / polling for real-time updates**:
- Models.dev has GitHub repo with model data
- Watch for commits to `models/` directory
- Auto-PR to update `provider_capabilities.yaml` when new models added
- CI validates new model capabilities before merge

**Value**: Zero-maintenance capability registry. New models auto-appear with correct configs.

---

## Part IV: Integration Gaps (Where Pieces Don't Connect)

### Gap 1: Ma'at Build Side ↔ Lilith Run Side — No Shared Types

**Issue**: Ma'at defines `ProviderCapabilityMatrix` in Python. Lilith defines `CapabilitySelector` in Python. But no shared type definitions — duplication risk.

**Fix**: 
- Create `src/omega/oracle/provider_types.py` with shared dataclasses
- Both sides import from single source
- CI validates type consistency

---

### Gap 2: Researcher Verification → Implementation — No Traceability

**Issue**: Verification report has 20 claims. Implementation tasks don't reference claim IDs.

**Fix**: 
- Each implementation task references verification claim IDs
- e.g., "Fix thinking config (claims 1,2,3,5,6)"
- CI checks: all CONFIRMED claims have implementation task

---

### Gap 3: Meditation Pipeline → Strategy — No Feedback Loop

**Issue**: Meditation pipeline produced templates but didn't actually run meditation. No insights fed back into strategy.

**Fix**: 
- Run actual meditation (not dry-run) on hardened problem statement
- Feed meditation insights into strategy refinement
- Iterate: Strategy → Meditation → Refined Strategy

---

### Gap 4: OpenCode PR → Community Config — Version Mismatch

**Issue**: OpenCode PR fixes upstream. Community config package works around current bug. If PR merged, config package becomes obsolete or conflicts.

**Fix**: 
- Config package detects OpenCode version
- If ≥1.18 (fixed): Use native config, don't override
- If <1.18: Apply workaround config
- Version check in install script

---

### Gap 5: Quota Manager ↔ Circuit Breaker — Shared State

**Issue**: QuotaManager tracks token buckets. CircuitBreaker tracks failures. They need shared state for "quota exhausted ≠ failure".

**Fix**: 
- Single `ProviderHealth` class combining quota + circuit + latency
- QuotaManager and CircuitBreaker are methods on ProviderHealth
- Shared Redis keys: `provider:{name}:health`

---

## Part V: Hardened Implementation Plan (Week 1)

### Day 1-2: Foundation (P0 — Blocks All)

| Task | Owner | Effort | Mandate | Verification Claim |
|------|-------|--------|---------|-------------------|
| Create `config/provider_capabilities.yaml` with Gemma 4, 12B, all Google models | P6 | 4h | M16 | Claims 1,2,3,5 |
| Build `ProviderCapabilityMatrix` loader + validation | P6 | 4h | M16 | Claims 1,2,3,5 |
| Implement `normalizeModelId(provider, modelId)` for Google/OpenRouter | P4 | 3h | M16 | Claim 4 |
| Add Gemma 4 detection to `GoogleAIProvider` thinking config | P3 | 3h | M9, M13 | Claims 1,2,3,5,6 |
| Add thinking config validator (reject LOW/MEDIUM for Gemma 4) | P10 | 2h | M9, M23 | Claim 6 |

### Day 3-4: Gateway Integration (P1 — Core Integration)

| Task | Owner | Effort | Mandate | Verification Claim |
|------|-------|--------|---------|-------------------|
| Wire `ProviderCapabilityMatrix` into `ModelGateway.generate()` | P9 | 3h | M7, M16 | Claims 1,2,3,5 |
| Add `thinking_level` parameter to `ModelGateway.generate()` | P9 | 2h | M9 | Claims 1,2,3 |
| Implement `ProviderHealth` (quota + circuit + latency) | P8 | 6h | M23 | Claims 8,9,10 |
| Add rate limit header parsing for Google/OpenRouter | P8 | 3h | M23 | Claims 8,9,10 |
| Pre-flight token estimation + quota check | P9 | 3h | M23 | Claim 8 |

### Day 5: Testing & Validation (P0 — Temple-Grade)

| Task | Owner | Effort | Mandate | Verification Claim |
|------|-------|--------|---------|-------------------|
| Unit tests: CapabilityMatrix, Normalizer, normalizeModelId | P10 | 4h | M13 | Claims 1-7 |
| Integration test: Gemma 4 MINIMAL/HIGH via GoogleAIProvider | P10 | 3h | M13 | Claims 5,6 |
| Integration test: Quota exhaustion → fallback to OpenRouter | P10 | 3h | M23 | Claims 9,10 |
| Integration test: Config drift detection + auto-correct | P10 | 2h | M9 | Claim 6 |
| `make temple-grade` + `make test` | All | 1h | M13 | All |

---

## Part VI: Risk Register (Updated)

| Risk | Likelihood | Impact | Mitigation | Owner |
|------|------------|--------|------------|-------|
| OpenCode V2 architecture invalidates transform.ts PR | High | High | Verify OpenCode version before PR; target V2 axes if needed | Ma'at |
| Models.dev sync misses new model release | Medium | Medium | Weekly cron + webhook watch on Models.dev repo | P2 |
| Vertex AI vs AI Studio schema mismatch causes 400s | High | High | Separate translators per auth type; config declares api_version | P6/P4 |
| OpenRouter `:free` suffix routing burns wrong quota | Medium | High | Explicit routing logic per provider; strip suffix only for direct Google | P9 |
| Thinking token billing invisible → budget exhaustion | High | High | Track thoughtsTokenCount separately; 2-5x multiplier in budget gate | P8 |
| Cline fallback remains vaporware | High | Medium | Decision: SDK Bridge (Option 3) — implement in Week 2 | Lilith |
| Pi heritage tag added without M14 vetting | Low | Medium | Run vetting pipeline before CREDITS.md update | doom_guy/Verity |
| Free tier rolling window causes burst 429s | High | Medium | Pre-flight estimation; exponential backoff; request queue | P9 |
| Concurrent quota race condition | Medium | High | Redis Lua atomic check-and-consume | P8 |
| Circuit breaker trips on expected quota 429s | Medium | Medium | Separate quota errors from health errors | P8 |

---

## Part VII: Success Criteria (Week 1 Definition of Done)

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| **Gemma 4 works in Omega Engine** | `omega talk "hello" -m gemma-4-31b-it` returns response | ✅ |
| **Thinking config correct** | Response includes `thoughtsTokenCount` for HIGH, 0 for MINIMAL | ✅ |
| **Model ID normalized** | No `google/` prefix in API calls; no `:free` suffix for direct Google | ✅ |
| **Quota awareness** | Dashboard shows real-time Google quota %; pre-flight rejects oversized requests | ✅ |
| **Fallback works** | Simulated Google quota exhaustion → routes to OpenRouter → returns response | ✅ |
| **Tests pass** | `make test` — 1398+ tests | ✅ |
| **Temple-Grade** | `make temple-grade` — T1-T11 pass | ✅ |
| **Heritage vetted** | Pi PR #2903 vet record in `HERITAGE_VET_LOG.md` with score ≥7 | ✅ |
| **Config drift handled** | Manual config edit with invalid thinking level → warning + auto-correct | ✅ |

---

## Part VIII: Gnosis — Hardened L3 Principles

| L3 Principle | Origin |
|--------------|--------|
| **Capability declaration > capability detection** | All 7 systems converge on explicit metadata |
| **Quota is a routing signal, not a failure** | Free tier 429 is expected behavior — route, don't trip |
| **Thinking tokens are billable output** | 85-95% of tokens can be thoughts — track separately |
| **Model identity is provider-relative** | Same model = 3+ IDs — canonicalize at gateway |
| **Free tier = chaos engineering lab** | Real constraints = free resilience testing |
| **Upstream fixes obsolete workarounds — version-gate them** | OpenCode PR + config package must coexist |
| **Heritage requires vetting, not just attribution** | M14 pipeline prevents gravitational pull without gate |

---

*⬡ OMEGA ⬡ JEM ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_hardening ⬡ 2026-07-19*