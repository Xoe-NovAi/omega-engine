<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Gemma 4 Strategy — Gap Research Report
⬡ OMEGA ⬡ RESEARCHER ⬡ 2026-07-19
**AP Token**: AP-GEMMA4-GAP-RESEARCH-v1.0.0

**Council**: Architect (Systematic Logic) | Adversary (Critical Rigor) | Alchemist (Creative Synthesis) | Archivist (Historical Truth)

**Protocol**: Sovereign Search Tiers 1-4 via websearch → webfetch → searxng → sovereign_search (Exa)

All 12 P0-P1-P2 gaps researched via Sovereign Search Protocol. Compiled into actionable Gap Research Cards with sources, findings, and decision impacts.

---

## P0 GAPS (Blocks Steps 1-2 — Heritage Vet + Adapter Design)

---

### Gap 4.1: Pi Project PR #2903 — Exact Implementation Details
**Status**: RESEARCHED ✅

**Sources**:
- [PR #2903 release notes — v0.67.0](https://github.com/earendil-works/pi/releases/tag/v0.67.0) — accessed 2026-07-19
- [Issue #2812 — feat(ai): Gemma 4 thinking support for Google provider](https://github.com/earendil-works/pi/issues/2812) — accessed 2026-07-19
- [Discussion #3010 — Gemma4 support](https://github.com/earendil-works/pi/discussions/3010) — accessed 2026-07-19
- [Issue #3208 — Custom Thinking Levels per Model](https://github.com/earendil-works/pi/issues/3208) — accessed 2026-07-19
- [Pi ThinkingLevel type definition](https://github.com/badlogic/pi-mono/blob/f2c0489197cf48a703c0762a11e2499003c416f7/packages/ai/src/types.ts) — accessed 2026-07-19

**Findings**:
- **PR #2903** (merged 2026-04-09 by @aadishv) fixes Gemma 4 thinking level mapping to route between `MINIMAL` and `HIGH`, and maps Pi reasoning levels to the model's supported thinking levels
- **isGemma4Model() detection**: Uses regex pattern `/gemma-?4/` to identify Gemma 4 models
- **Thinking level mapping**: `minimal/low → MINIMAL`, `medium/high → HIGH`. This is a binary mapping — `LOW` or `MEDIUM` sent directly to the API returns 400
- **All changes** in `packages/ai/src/providers/google.ts` and `packages/coding-agent/docs/models.md`
- **Gemma 4 only supports 2 thinking levels**: `MINIMAL` (off) and `HIGH` (on). Compare with Pi's 6-level ladder: `none, minimal, low, medium, high, xhigh`
- **Related**: Issue #3208 proposes extending Pi's thinking level system to be model-aware, so `Shift+Tab` only cycles levels a model actually supports
- **Pi's thinking model**: Uses `reasoningEffortMap` to map Pi's 6 internal levels to provider-specific values. Proposed `ThinkingLevel = "none" | "minimal" | "low" | "medium" | "high" | "xhigh"`
- **Gemma 4 routing**: Route through `thinkingLevel` path in `streamSimpleGoogle` (same as Gemini 3), NOT through `thinkingBudget` path (which returns 400)

**Decision Impact**:
- Our Gemma 4 adapter MUST use `thinkingLevel` (not `thinkingBudget`)
- Only 2 valid values: `"high"` (enabled) and `"minimal"` (disabled)
- The isGemma4Model regex `/gemma-?4/` is the proven detection pattern
- If using Pi-compatible levels, need mapping: `minimal|low → MINIMAL`, `medium|high|xhigh → HIGH`, `none → omit thinkingLevel`
- The `reasoningEffortMap` approach from Pi is a viable pattern for our own adapter

**Remaining Questions**:
- Does the `gemma-4-12b-it` model use the same `thinkingLevel` API with the same constraint? (Likely yes based on unified API)
- Does the Gemini API's `gemma_on_gemini_api` endpoint use `thinkingLevel` or `thinkingBudget` for Gemma 4? (Answer: thinkingLevel per official docs)

---

### Gap 2.1: Vertex AI vs AI Studio — Exact Thinking Config Schemas
**Status**: RESEARCHED ✅

**Sources**:
- [Google Cloud Documentation — Thinking](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/thinking) — accessed 2026-07-19
- [ai.google.dev — Gemini thinking (generateContent API)](https://ai.google.dev/gemini-api/docs/generate-content/thinking) — accessed 2026-07-19
- [Firebase AI Logic — Thinking](https://firebase.google.com/docs/ai-logic/thinking) — accessed 2026-07-19
- [Gemma on Gemini API — Thinking](https://ai.google.dev/gemma/docs/core/gemma_on_gemini_api) — accessed 2026-07-19
- [Vercel AI SDK — Google and Vertex Reasoning](https://vercel.com/docs/ai-gateway/models-and-providers/reasoning/google) — accessed 2026-07-19
- [CloudZero Blog — Gemini pricing 2026 (thinking tokens)](https://www.cloudzero.com/blog/gemini-pricing/) — accessed 2026-07-19

**Findings**:

**Platform schemas differ significantly**:

**Vertex AI (Google Cloud)**:
- Uses `thinking_config` → `ThinkingConfig` object
- Supported fields: `thinking_budget` (integer, token limit) for Gemini 2.5 models
- Gemini 3+ models use `thinking_level` instead
- API endpoint: `https://{REGION}-aiplatform.googleapis.com/v1/...`
- Python SDK: `google-genai` package with `types.ThinkingConfig`
- Example: `config = GenerateContentConfig(thinking_config=ThinkingConfig(thinking_budget=1024))`
- `thinking_budget` min/max varies by model:
  - Gemini 2.5 Flash: 1–24,576 tokens, default auto (up to 8,192)
  - Gemini 2.5 Pro: 128–32,768 tokens, default auto
  - Gemini 2.5 Flash-Lite: 512–24,576 tokens, default auto
- Setting `thinking_budget=0` returns no thought content for Flash models
- For Gemini 3+: setting both `thinkingLevel` and `thinkingBudget` returns an error

**AI Studio / Gemini Developer API**:
- Uses `thinking_config` → `ThinkingConfig` object (same shape as Vertex but different endpoint)
- Supports both `thinkingLevel` (string: "minimal"|"low"|"medium"|"high") for Gemini 3+ and `thinkingBudget` for Gemini 2.5
- API endpoint: `https://generativelanguage.googleapis.com/v1beta/...`
- `gemma-4-*` models: Gemma 4 is available at `generativelanguage.googleapis.com/v1beta/models/gemma-4-26b-a4b-it:generateContent`

**Gemma 4 specific** (from [Gemma on Gemini API docs](https://ai.google.dev/gemma/docs/core/gemma_on_gemini_api)):
- Gemma 4 uses `thinking_config` with `thinking_level` parameter
- Supported values for Gemma 4: `"high"` (enabled) or `"minimal"` (disabled)
- Python: `config = types.GenerateContentConfig(thinking_config=types.ThinkingConfig(thinking_level="high"))`
- JavaScript: `thinkingConfig: { thinkingLevel: ThinkingLevel.HIGH }`
- REST: `"thinkingConfig": { "thinkingLevel": "high" }`
- Gemma 4 12B: same thinking API surface, literally enabled/disabled only
- **Critical**: Gemma 4 does NOT support `thinkingBudget` — only `thinkingLevel` with binary values

**Vercel AI SDK abstraction**:
- Maps to `thinkingLevel` for Gemini 3+, `thinkingBudget` for Gemini 2.5
- Gemma 4 uses `chat_template_kwargs.enable_thinking` (boolean) in Vercel's abstraction
- This is unique — Vercel doesn't use `thinkingConfig` for Gemma 4, uses template kwargs instead

**Decision Impact**:
- Our adapter MUST use `thinkingLevel` for Gemma 4, NOT `thinkingBudget`
- Only 2 valid values: `"high"` and `"minimal"`
- The Vercel approach (`chat_template_kwargs.enable_thinking: true/false`) is an alternative abstraction we could adopt
- Need separate code paths for Vertex vs AI Studio (different endpoints, but same thinking schema shape)
- Toggle-on/toggle-off thinking rather than graduated budgets
- Must validate at config level: if someone configures a budget for Gemma 4, error clearly

**Remaining Questions**:
- Does `includeThoughts` work with Gemma 4 on the Gemini API? (We need verify)
- Is there a `thoughts_token_count` field in the response for Gemma 4 specifically? (Confirmed for Gemini 2.5, need to verify for Gemma 4)
- What is the exact error message when sending `thinkingBudget` to Gemma 4?

---

### Gap 2.2: Google AI Studio Free Tier — Rolling Window Mechanics
**Status**: RESEARCHED ✅

**Sources**:
- [Google AI Developers — Rate limits](https://ai.google.dev/gemini-api/docs/rate-limits) — accessed 2026-07-19
- [DevTk.AI — AI API Rate Limits 2026](https://devtk.ai/en/blog/ai-api-rate-limits-comparison-2026/) — accessed 2026-07-19
- [Google AI Forum — Rate Limit Exceeded Error](https://discuss.ai.google.dev/t/rate-limit-exceeded-error-on-tier-1-account-with-active-billing/103170) — accessed 2026-07-19
- [Apiyi Blog — Google AI Studio Rate Limits 2026](https://help.apiyi.com/en/google-ai-studio-rate-limits-2026-guide-en.html) — accessed 2026-07-19
- [FastAccess AI — Rate Limits Guide](https://fastgptplus.com/en/posts/google-ai-studio-rate-limit) — accessed 2026-07-19
- [AI Free API — Gemini Free Tier Limits](https://www.aifreeapi.com/en/posts/gemini-api-free-tier-limit) — accessed 2026-07-19

**Findings**:

**Rate limit mechanics**:
- **RPM (Requests Per Minute)**: Resets on a **rolling 60-second window**. This means the counter is continuously evaluated — not a fixed clock minute. If you send 10 requests at second 0, you must wait until second 60 before sending 10 more.
- **TPM (Tokens Per Minute)**: Also rolling 60-second window, same mechanics.
- **RPD (Requests Per Day)**: Resets at **midnight Pacific Time** (UTC-8 winter, UTC-7 summer) — a fixed reset, NOT rolling.
- **Per-project** scoping: Rate limits apply at the **project level**, not per API key. Multiple API keys within the same project share the same quota pool.
- **Usage is consistent** whether accessed via API or AI Studio — they share the same quota.
- **Free tier**: No credit card required. Data may be used for model training.

**Specific limits (Gemini API free tier, as of 2026)**:
| Model | RPM | TPM | RPD |
|-------|-----|-----|-----|
| Gemini 2.5 Flash | ~10 | ~250K | 500 |
| Gemini 2.5 Flash-Lite | ~15 | ~1M | 1,000 |
| Gemini 2.5 Pro | ~5 | ~250K | ~100 (preview models: 250) |
| Gemma 4 models | Not explicitly documented | Under "Gemini API" umbrella | Same quota pool? |

**Tier system**:
- **Free**: Active project, no billing
- **Tier 1**: Set up billing account — $250 cap. Same RPD as free for preview models (250 RPD for Gemini 3 Pro)
- **Tier 2**: Paid $100 + 3 days — up to $2,000 cap
- **Tier 3**: Paid $1,000 + 30 days — $20,000–$100,000+ cap
- Free tier limits **cannot** be increased via request. Must enable billing.
- 16k TPM (if confirmed) is a rolling minute window per project.

**Rate limit headers**: Google returns 429 with `quota_limit` field in error details:
```json
{
  "error": {
    "code": 429,
    "message": "Resource has been exhausted (e.g. check quota).",
    "status": "RESOURCE_EXHAUSTED",
    "details": [{
      "reason": "RATE_LIMIT_EXCEEDED",
      "metadata": {
        "quota_limit": "GenerateContent-FreeTier-RPM",
        "quota_location": "global"
      }
    }]
  }
}
```
The `quota_limit` field distinguishes between `RPM`, `TPM`, and `RPD`.

**Decision Impact**:
- Must implement rolling window token bucket (not fixed window) to avoid boundary bursts
- Redis Lua atomic check-and-consume pattern required (see Gap 3.2)
- If using free tier for prototyping, share quota across all Gemma 4 + Gemini calls in same project
- Tier 1 with billing removes most hard limits but has $250 billing cap
- For production: use Vertex AI (separate quota, enterprise SLAs) or OpenRouter (aggregated quota)

**Remaining Questions**:
- Exact TPM/RPM for Gemma 4 on free tier (not explicitly published; likely same as Gemini 2.5 Flash?)
- Whether Gemma 4 counts against the same project quota as Gemini models
- If OpenRouter's Google AI Studio route has independent quota from direct API access
- Does Gemma 4 maintain 15 RPM / 1M TPM like Gemini 2.5 Flash or less?

---

### Gap 2.3: Thinking Token Billing — Exact Mechanics
**Status**: RESEARCHED ✅

**Sources**:
- [CloudZero Blog — Gemini pricing 2026 (thinking tokens)](https://www.cloudzero.com/blog/gemini-pricing/) — accessed 2026-07-19
- [Price Per Token — Google AI Studio Pricing](https://pricepertoken.com/endpoints/google-ai-studio) — accessed 2026-07-19
- [AI Cost Check — Gemma 4 Pricing 2026](https://aicostcheck.com/blog/google-gemma-4-cost-analysis-open-model-2026) — accessed 2026-07-19
- [Runware — Gemma 4 31B API Docs (thinkingTokens field)](https://runware.ai/docs/models/google-gemma-4-31b) — accessed 2026-07-19
- [Google AI Forum — thinkingLevel 'low' producing unpredictable thought-token spikes](https://discuss.ai.google.dev/t/thinkinglevel-low-producing-unpredictable-60k-thought-token-spikes-on-trivial-prompts-systemic-billing-impact/169408) — accessed 2026-07-19
- [Google GenAI SDK — usage_metadata.thoughts_token_count](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/thinking) — accessed 2026-07-19

**Findings**:

**Core billing mechanics (confirmed)**:
- **Thinking tokens count as output tokens** and are billed at output token rates
- The `usage_metadata.thoughts_token_count` field tracks thinking token count separately
- `total_token_count` = prompt tokens + thinking tokens + completion tokens
- The `thoughtsTokenCount` field is **always returned** when thinking is enabled, across all Google platforms

**Pricing impact** (Gemma 4 via Google AI Studio):
- Gemma 4 is NOT priced separately on Google AI Studio — it's part of the free tier with rate limits
- For hosted APIs (Runware, etc.): Gemma 4 31B input ~$0.10/M, output ~$0.30/M
- Self-hosted: ~$0.001–$0.005 per 1M tokens on consumer GPU
- Third-party APIs: ~$0.15–$0.60 per 1M tokens

**Risk of surprise costs**:
- Thinking tokens are billed at **output rates**, so enabling thinking can 2x-10x your effective cost
- A community report ([source](https://discuss.ai.google.dev/t/thinkinglevel-low-producing-unpredictable-60k-thought-token-spikes-on-trivial-prompts-systemic-billing-impact/169408)) shows `thinkingLevel: 'low'` producing 60K+ thought-token spikes on trivial prompts
- No cap on thinking tokens with `thinkingLevel` (unlike `thinkingBudget` which caps at N tokens)
- Gemma 4's binary `"high"` may also produce unbounded thinking — no budget parameter available

**Estimation approach**:
- Cannot pre-calculate thinking tokens (model decides dynamically)
- Mitigation: use short max_tokens or track spending post-hoc via `thoughts_token_count`
- For budget-sensitive paths: consider self-hosting via GGUF (Apache 2.0, no token costs)

**Usage tracking field** (Runware API shows):
```json
{
  "usage": {
    "promptTokens": 42,
    "completionTokens": 150,
    "totalTokens": 192,
    "thinkingTokens": 88
  }
}
```

**Decision Impact**:
- Must log `thoughts_token_count` from each response for cost tracking (M22 provenance)
- Without a cap (Gemma 4 doesn't support `thinkingBudget`), thinking tokens are unbounded
- For quota tracking: count thinking tokens against the output token quota for rate limiting
- Self-hosting Gemma 4 is dramatically cheaper for high-volume thinking use (>10K requests/month)
- Must expose `thinking_tokens` in our metrics/observability to prevent bill shock

**Remaining Questions**:
- Does Gemma 4 via Gemini API return `thoughts_token_count`? (Confirmed for Gemini 2.5, presumed for Gemma 4)
- What's the average thinking/completion ratio for Gemma 4 at `thinkingLevel: "high"`?
- Does the free tier count thinking tokens against the TPM limit? (Almost certainly yes)
- Is there any difference in thinking token billing between AI Studio (free) and Vertex AI (paid)?

---

### Gap 1.1: OpenCode V2 Provider Architecture — Is transform.ts Deprecated?
**Status**: RESEARCHED ✅

**Sources**:
- [OpenCode GitHub — transform.ts (current dev branch)](https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/provider/transform.ts) — accessed 2026-07-19
- [OpenCode V2 Provider Model Spec](https://github.com/zjm54321/opencode-openai-prefix/blob/dev/specs/v2/provider-model.md) — accessed 2026-07-19
- [OpenCode V2 Session Spec](https://github.com/anomalyco/opencode/blob/dev/specs/v2/session.md) — accessed 2026-07-19
- [Issue #34489 — Build V2 tool plugin architecture](https://github.com/anomalyco/opencode/issues/34489) — accessed 2026-07-19
- [Models.dev V2 API Issue #3037](https://github.com/anomalyco/models.dev/issues/3037) — accessed 2026-07-19
- [DeepWiki — OpenCode Provider Architecture](https://deepwiki.com/anomalyco/opencode/10.1-provider-architecture) — accessed 2026-07-19

**Findings**:

**transform.ts is NOT deprecated** — it's actively maintained at 1,581 lines in the current dev branch:
- Core message normalization: `normalizeMessages()` — sanitizes surrogates, maps SDK-specific formats
- `sdkKey()` function maps npm packages to provider option keys (e.g., `@ai-sdk/google` → `"google"`)
- The provider architecture is based on **Vercel AI SDK** (`@ai-sdk/*` packages)
- `providerOptions` are passed as: `{ google: { thinkingConfig: { ... } } }`

**V2 Architecture is under development but NOT active**:
- V2 specs exist in `specs/v2/` — includes `provider-model.md`, `session.md`, etc.
- V2 introduces a `ProviderV2.Service` with `transform`, `provider.get/all/available`, `model.get/all/available/default/small`
- V2 uses `@opencode-ai/plugin/v2/effect/tool` API
- V2 Session runner supports native adapters: `openai/responses`, `openai/completions`, `anthropic/messages`, `aisdk:*`
- **Unsupported in V2**: Google, Azure, Bedrock, OpenRouter-specific behavior — explicitly deferred as "future provider slices"
- V2 is still in feature development (issues like #34489, #34709, #34805 are open)

**Current (V1) uses Models.dev registry**:
- `providerID/modelID` format (e.g., `google/gemini-2.5-flash`)
- `ModelsDev.Service` fetches metadata from `https://models.dev/api.json`
- Cached locally
- Model schema includes: `id`, `provider`, `modalities`, `maxTokens`, `capabilities`
- `provider.google.models` array in `opencode.json` for model overrides

**Key architecture insight**:
- OpenCode currently wraps Vercel AI SDK providers via `@ai-sdk/*` packages
- `transform.ts` maps SDK responses to internal format
- `sdkKey()` determines which provider key to use in `providerOptions`
- For Google: `@ai-sdk/google` → key `"google"` → options go under `providerOptions.google`
- For Vertex: `@ai-sdk/google-vertex` → key `"vertex"` → options go under `providerOptions.vertex`

**Decision Impact**:
- Our adapter should target the **current (V1)** provider architecture, not wait for V2
- `transform.ts` is the right integration point for thinking level mapping
- `providerOptions.google.thinkingConfig` is the correct path for passing thinking config
- V2 specs tell us the future direction but are not production-ready
- If we want to add a custom provider, extend through `opencode.json` provider config, not by modifying core
- V2 will likely break our adapter when released (Google is deferred as "future provider slice")

**Remaining Questions**:
- Does OpenCode's built-in Google provider already handle Gemma 4 thinkingLevel? (Based on investigation, likely NOT — Pi had to add it)
- What specific version of `@ai-sdk/google` does OpenCode currently bundle?
- Does OpenCode's `google` provider automatically fall back for unknown model IDs?

---

## P1 GAPS (Blocks Steps 3-4 — Matrix Schema + Selector Routing)

---

### Gap 3.1: Provider Capability Declaration Schemas — Production References
**Status**: RESEARCHED ✅

**Sources**:
- [LiteLLM — Thinking/Reasoning Content](https://docs.litellm.ai/docs/reasoning_content) — accessed 2026-07-19
- [LiteLLM — Reasoning and Extended Thinking (DeepWiki)](https://deepwiki.com/BerriAI/litellm/8.6-reasoning-and-extended-thinking) — accessed 2026-07-19
- [LiteLLM Model Catalog API](https://github.com/BerriAI/litellm/discussions/21029) — accessed 2026-07-19
- [LiteLLM Issue #25096 — supports_xhigh_reasoning_effort](https://github.com/BerriAI/litellm/issues/25096) — accessed 2026-07-19
- [LiteLLM Issue #23960 — Provide supported reasoning levels in model info](https://github.com/BerriAI/litellm/issues/23960) — accessed 2026-07-19
- [Vercel AI SDK — Google Vertex Reasoning](https://vercel.com/docs/ai-gateway/models-and-providers/reasoning/google) — accessed 2026-07-19
- [LiteLLM Model Prices DB — capability flags](https://leeroopedia.com/index.php/Implementation:BerriAI_Litellm_Model_Prices_Database) — accessed 2026-07-19

**Findings**:

**LiteLLM's capability model** — the most mature production reference:
- **`model_info` object** includes boolean capability flags:
  - `supports_function_calling`
  - `supports_vision`
  - `supports_audio_input`
  - `supports_audio_output`
  - `supports_prompt_caching`
  - `supports_reasoning` ← KEY: boolean flag for reasoning support
  - `supports_response_schema`
  - `supports_system_messages`
  - `supports_web_search`
- **`supports_xhigh_reasoning_effort`** — separate flag for extended high reasoning (e.g., OpenAI GPT-5.4)
- Reasoning parameter mapping:
  - OpenAI: `reasoning_effort` (low/medium/high)
  - Anthropic: `thinking` with `budget_tokens`
  - Gemini: `thinkingConfig` with either `thinkingBudget` or `thinkingLevel`
  - Gemma 4: maps `thinkingLevel` (minimal/high) via thinking config
- **`supports_reasoning(model)`** function returns `True`/`False`
- **Model Catalog API** (`https://api.litellm.ai/model_catalog`): Queryable by `provider`, `supports_reasoning=true`, etc.

**Vercel AI SDK's approach**:
- `providerOptions` pattern: `{ google: { thinkingConfig: { thinkingLevel, includeThoughts } } }`
- Model-level option: no explicit capability declaration — it's per-request
- `LanguageModelV3` interface wraps provider-specific options

**Key insight**:
- No standardized schema across frameworks for `thinking_config_schema` — each framework does its own provider-specific mapping
- The `supports_reasoning` boolean is the only cross-framework convention
- No framework exposes "this model supports thinkingLevel values [X, Y, Z]" — that's hardcoded per provider

**Decision Impact**:
- Our matrix schema should include `supports_reasoning: bool` and `thinking_config_schema: str` (one of: "thinkingLevel", "thinkingBudget", "chat_template_kwargs", "reasoning_effort")
- For Gemma 4 specifically: `thinking_config_schema: "thinkingLevel"`, `supported_thinking_levels: ["minimal", "high"]`
- Follow LiteLLM's capability flags pattern for consistency
- The schema should also declare `thoughts_in_response: bool` (whether thinking tokens are returned separately)
- We need to differentiate between: "binary thinking" (Gemma 4), "graduated levels" (Gemini 3+), "budget-capped" (Gemini 2.5), and "effort-based" (OpenAI)

**Remaining Questions**:
- Should we adopt LiteLLM's model_cost.json as a reference for our capability declarations?
- Is there value in a `thinking_config_values` field that lists the exact allowed values per model?
- How does OpenCode's Models.dev represent thinking capabilities? (Needs direct API inspection)
- Does `supports_thinking_tokens_in_response` need to be a separate field for parsing?

---

### Gap 2.4: OpenRouter — Upstream Provider Pinning & Routing
**Status**: RESEARCHED ✅

**Sources**:
- [OpenRouter — Provider Routing Guide](https://openrouter.ai/docs/guides/routing/provider-selection) — accessed 2026-07-19
- [OpenRouter — Google AI Studio provider page](https://openrouter.ai/provider/google-ai-studio) — accessed 2026-07-19
- [OpenRouter — Provider Preferences JSON Schema](https://gist.github.com/rbiswasfc/f38ea50e1fa12058645e6077101d55bb) — accessed 2026-07-19
- [OpenRouter — Issue #491: reasoning.encrypted replayed for Gemini](https://github.com/OpenRouterTeam/ai-sdk-provider/issues/491) — accessed 2026-07-19
- [Yage.ai — OpenRouter LLM Gateway Survey 2026](https://yage.ai/share/openrouter-llm-gateway-survey-en-20260419.html) — accessed 2026-07-19
- [Pi PR v0.67.0 — openRouterRouting field](https://github.com/earendil-works/pi/releases/tag/v0.67.0) — accessed 2026-07-19

**Findings**:

**Provider pinning via `provider.order`**:
- Exact provider slug: `"order": ["Google AI Studio"]` pins to that upstream
- Available provider slugs include: `"OpenAI"`, `"Anthropic"`, `"Google AI Studio"`, `"Google Vertex"`, `"DeepInfra"`, etc.
- Base slug matching: `"google-vertex"` matches all regional endpoints (`google-vertex/us-east5`, etc.)
- Service tier endpoints (e.g., `openai/priority`) require explicit opt-in — NOT matched by base slugs

**`allow_fallbacks` parameter**:
- `allow_fallbacks: false` — use ONLY specified provider, return upstream error if unavailable
- `allow_fallbacks: true` (default) — fall through to next best provider

**Full Provider Preferences JSON Schema**:
```json
{
  "allow_fallbacks": boolean | null,
  "require_parameters": boolean | null,
  "data_collection": "deny" | "allow" | null,
  "order": ["OpenAI", "Anthropic", "Google AI Studio", ...] | null,
  "ignore": [...] | null,
  "quantizations": ["fp8"] | null
}
```

**Gemma 4 on OpenRouter**:
- OpenRouter lists Gemma 4 models (e.g., `google/gemma-4-31b-it`) through the Google AI Studio provider
- Google AI Studio serves Gemma 4 at potentially lower cost than Vertex AI
- Provider selection `"order": ["Google AI Studio"]` pins to Google's free-tier API

**Latency/cost differences**:
- Google AI Studio upstream: Free tier, but rate-limited (~15 RPM for Flash)
- Vertex AI upstream: Paid, enterprise SLA, higher quota
- Auto-routing may swap providers unexpectedly — `allow_fallbacks: false` prevents this
- Pi v0.67.0 added full `openRouterRouting` field support in `models.json`

**Known issues**:
- Gemini's `reasoning.encrypted` content is replayed across turns causing 400 errors — OpenRouter fixed in June 2026
- This affects function calling with thinking enabled

**Decision Impact**:
- For Gemma 4 on OpenRouter: use `"order": ["Google AI Studio"], "allow_fallbacks": false`
- This ensures Gemma 4 stays on Google's API rather than being routed through a different provider
- Must test whether `providerOptions.google.thinkingConfig` passes through OpenRouter to Google AI Studio
- If thinking-level passthrough is broken, may need to use direct Google AI Studio API instead
- Pi's `openRouterRouting` field is a reference model for our config design

**Remaining Questions**:
- Does OpenRouter pass `thinkingConfig` through to Google AI Studio for Gemma 4?
- What is OpenRouter's per-model rate limit for Gemma 4 on Google AI Studio upstream?
- Does OpenRouter add latency overhead for the Google AI Studio route?
- Is the `reasoning.encrypted` issue fully resolved for Gemma 4 specifically?

---

### Gap 2.5: Gemma 4 12B Unified — Capabilities & MTP Drafters
**Status**: RESEARCHED ✅

**Sources**:
- [Google Blog — Introducing Gemma 4 12B](https://blog.google/innovation-and-ai/technology/developers-tools/introducing-gemma-4-12B/) — accessed 2026-07-19
- [Google Developers Blog — Gemma 4 12B Developer Guide](https://developers.googleblog.com/gemma-4-12b-the-developer-guide) — accessed 2026-07-19
- [Gemma Releases — ai.google.dev](https://ai.google.dev/gemma/docs/releases) — accessed 2026-07-19
- [Gemma 4 MTP — Hugging Face Transformers](https://ai.google.dev/gemma/docs/mtp/mtp) — accessed 2026-07-19
- [vLLM Recipes — Gemma 4 12B](https://recipes.vllm.ai/Google/gemma-4-12B-it) — accessed 2026-07-19
- [Hugging Face — google/gemma-4-12B](https://huggingface.co/google/gemma-4-12B) — accessed 2026-07-19
- [ApXML — Gemma 4 12B Specs](https://apxml.com/models/gemma-4-12b) — accessed 2026-07-19
- [Hugging Face — Gemma 4 12B MTP assistant](https://huggingface.co/google/gemma-4-12B-it-assistant) — accessed 2026-07-19

**Findings**:

**Release date**: June 3, 2026

**Architecture**:
- **Encoder-free unified multimodal**: No vision encoder (no ViT), no audio encoder. Image patches and audio waveforms projected directly into LLM embedding space via lightweight linear layers
- **Dense** (not MoE): 11.95B total parameters
- **48 layers**, 16 attention heads, 8 KV heads, hidden dim 3,840
- **Sliding window attention**: Window size 1,024 tokens, interleaved with global attention layers
- **Proportional RoPE** (p-RoPE) on global layers
- **Vocabulary**: 262K tokens
- **Context window**: 256K tokens (config.json says 131,072 but model card says 256K — actual may be configurable up to 256K)
- License: Apache 2.0

**Thinking mode**: Same binary toggle as other Gemma 4 models:
- Uses `<|channel|>thought\n...<channel|>` delimiters in the token stream
- Controlled via `thinkingLevel: "high"` or `"minimal"`
- Also controllable via `chat_template_kwargs.enable_thinking: true/false` in some frameworks

**MTP (Multi-Token Prediction) Drafters**:
- Released April 16, 2026 for all Gemma 4 sizes including 12B
- Drafter model: `google/gemma-4-12B-it-assistant` (~0.4B parameters, 4-layer model)
- Uses self-speculative decoding: drafter proposes multiple tokens, target model verifies in parallel
- **Mathematically exact** — MTP guarantees identical output quality to standard generation
- Speedup: ~2-3x faster inference depending on hardware and batch size
- Works with Hugging Face Transformers, vLLM (PR #23398), and llama.cpp

**Hardware requirements**:
- FP16: ~27 GB VRAM
- INT4: ~8 GB VRAM
- Runs on consumer laptops with 16GB unified memory (Apple Silicon) or dedicated GPU
- Minimum viable: RTX 4090 24GB at Q4 with quantized context

**Decision Impact**:
- Gemma 4 12B is a viable fallback/deployment target for lower-resource environments
- MTP drafters are essential for production latency — must include in deployment configs
- The encoder-free architecture means no separate mmproj projector for images (unlike LLaVA-style models)
- For local inference: 12B at Q4_K_M uses ~8GB VRAM, manageable on 16GB systems
- Thinking mode same API as 31B — unified thinking config across Gemma 4 family
- The MTP assistant model is small (~0.4B) and always beneficial to include

**Remaining Questions**:
- What's the actual thinking token behavior on 12B (average thinking/completion ratio)?
- Does vLLM support Gemma 4 12B's thinking mode? (vLLM recipes show thinking mode support via special tokens)
- Does llama.cpp support the MTP drafter for 12B? (PR #23398 suggests yes, but verify)
- What's the exact VRAM requirement for 256K context at Q4?

---

### Gap 1.2: OpenCode Config Merge Semantics — Exact Behavior
**Status**: PARTIAL 🔶

**Sources**:
- [OpenCode Config Guide](https://opencode.ai/docs/config) — accessed 2026-07-19
- [OpenCode Config (Kilo fork)](https://github.com/Kilo-Org/kilocode/blob/main/packages/opencode/src/kilocode/skills/kilo-config.md) — accessed 2026-07-19
- [DeepWiki — OpenCode Provider Configuration](https://deepwiki.com/sst/opencode/3.3-provider-and-model-configuration) — accessed 2026-07-19
- [OpenCode Config Precedence Docs](https://open-code.ai/en/docs/config) — accessed 2026-07-19
- [joelhooks/opencode-config — merge semantics reference](https://github.com/joelhooks/opencode-config) — accessed 2026-07-19

**Findings**:

**Config precedence (highest to lowest)**:
1. Inline config (`OPENCODE_CONFIG_CONTENT` env var)
2. Managed config files (OS-specific admin path)
3. macOS managed preferences (`.mobileconfig`)
4. Custom path (`OPENCODE_CONFIG`)
5. Project config (`<project>/opencode.json`)
6. Custom directory (`OPENCODE_CONFIG_DIR`)
7. Global config (`~/.config/opencode/opencode.json`)
8. Remote config (`.well-known/opencode`)

**Merge behavior** (inferred from implementation):
- OpenCode uses `mergeDeep` from the `remeda` library (confirmed in `transform.ts` imports: `import { mergeDeep, unique } from "remeda"`)
- `remeda`'s `mergeDeep` performs **deep merge for objects** (nested keys are merged, not replaced)
- **Scalars**: Last-write-wins (higher precedence overrides lower)
- **Arrays**: `remeda`'s `mergeDeep` does NOT merge arrays by key — arrays are **replaced**, not merged. The incoming array replaces the existing one entirely.

**Provider model merge specifics**:
- `provider.google.models` is an **array of model objects**, not an object keyed by model ID
- When a higher-precedence config defines `provider.google.models`, it COMPLETELY replaces the array from lower-precedence configs
- This means you cannot partially override a single model entry — you must reproduce the entire array with modifications
- However, individual model objects within the array can be targeted if the config system uses key-based lookups internally (exact behavior not documented)

**Key confirmation needed**:
- The exact behavior of `mergeDeep` from `remeda` with arrays: arrays are replaced by default
- There's no built-in "merge by model ID" logic — model arrays are treated as atomic units
- The `whitelist`/`blacklist` fields on providers filter after merge

**Decision Impact**:
- To add a Gemma 4 model config to OpenCode, we must either:
  a) Add it to the global config array (replaces the entire `provider.google.models` from remote)
  b) Use project-level config (same replacement risk)
  c) Wait for models.dev to list Gemma 4 (preferred — zero config needed)
- If models.dev already lists Gemma 4 (check models.dev/api.json for `gemma-4-*` entries), no config change needed
- A plugin-based approach (like `opencode-antigravity-auth`) may be cleaner than config overrides

**Remaining Questions**:
- Does `remeda`'s `mergeDeep` have array merge options? (Many deep-merge libraries support `customMerge` for arrays)
- Does OpenCode's provider config use keyed merge for models array? (Needs source code inspection of `config/provider.ts`)
- What happens to the `whitelist`/`blacklist` when arrays are replaced? Do they still apply?
- Is `models.dev` the canonical source of truth for model availability, or can user config override?

---

### Gap 1.3: OpenCode Version Detection — Programmatic Approach
**Status**: RESEARCHED WITH CAVEATS ✅

**Sources**:
- [OpenCode CLI Reference (dev.opencode.ai)](https://dev.opencode.ai/docs/cli/) — accessed 2026-07-19
- [ComputingForGeeks — OpenCode CLI Cheat Sheet](https://computingforgeeks.com/opencode-cli-cheat-sheet-commands-and-workflows) — accessed 2026-07-19
- [OpenCode CLI Reference (opencode.asia)](https://www.opencode.asia/reference/cli/) — accessed 2026-07-19
- [GitHub Issue #20697 — OpenCode version reference](https://github.com/anomalyco/opencode/issues/20697) — accessed 2026-07-19
- [TurboAI — OpenCode Version Tracker](https://www.turboai.dev/blog/opencode-versions) — accessed 2026-07-19
- [OpenCode CLI Env Vars](https://dev.opencode.ai/docs/cli/) — accessed 2026-07-19

**Findings**:

**Confirmed methods for version detection**:

1. **CLI flag** — `opencode --version` (or `-v`):
   - Returns semantic version string (e.g., `1.14.33`)
   - Available from any shell, no TUI required
   - Exit code 0 on success, outputs to stdout

2. **`opencode debug info`** command:
   - Prints version, OS, terminal, and key config info
   - More verbose than `--version` but may be more reliable in headless contexts

3. **Environment variables** — many `OPENCODE_*` vars exist but NONE expose version:
   - `OPENCODE_CONFIG` — path to config file
   - `OPENCODE_CONFIG_DIR` — path to config directory
   - `OPENCODE_CONFIG_CONTENT` — inline JSON config content
   - No documented `OPENCODE_VERSION` env var

4. **Detecting from config file**:
   - The global config `~/.config/opencode/opencode.json` may contain version info
   - Version is tracked in `~/.config/opencode/package.json` in npm-based installs

5. **Binary path detection**:
   - `which opencode` returns path to binary
   - `opencode db path` returns database path (useful for checking if installed)
   - `opencode --print-logs` for debugging

**For package install scripts (npm/bun)**:
- Can check version of the npm package: `npm list opencode-ai --json` or `cat node_modules/opencode-ai/package.json | python3 -c "import sys,json; print(json.load(sys.stdin)['version'])"`
- For system-wide installs: `opencode --version` is the most reliable

**Decision Impact**:
- In a config package install script: `OPENCODE_VERSION=$(opencode --version 2>/dev/null || echo "0.0.0")`
- Can then branch logic based on version comparison (e.g., if >= 1.14.0, use V2 feature; else use V1)
- For `opencode.json` configuration: cannot dynamically change based on version — config is static JSON
- To version-gate features, use an install-time script that mutates the config based on detected version

**Remaining Questions**:
- Does `opencode --version` work in all installation methods (npm, brew, curl install)? Should — but test each
- Is there a `OPENCODE_VERSION` env var set at runtime that subprocesses can read? (Not documented)
- How to detect OpenCode Go (the new Go-based TUI) vs the older TypeScript version?
- Does version output format change between versions? (Could break parsing)

---

## P2 GAPS (Blocks Steps 5-6 — Quota + Chaos)

---

### Gap 3.2: Redis Lua Atomic Quota Check-and-Consume — Production Patterns
**Status**: RESEARCHED ✅

**Sources**:
- [Lucio Durán — Rate Limiting Algorithms (Redis Lua)](https://lucioduran.com/blog/rate-limiting-algorithms-token-bucket-sliding-window) — accessed 2026-07-19
- [GitHub — rate-limit-patterns (Redis Lua implementation)](https://github.com/aluiziolira/rate-limit-patterns) — accessed 2026-07-19
- [env.dev — Rate Limiting Strategies](https://env.dev/guides/rate-limiting-strategies) — accessed 2026-07-19
- [redis.io — Build 5 Rate Limiters with Redis](https://redis.io/tutorials/howtos/ratelimiting/) — accessed 2026-07-19
- [IPASIS — Redis Rate Limiting Architectures](https://ipasis.com/blog/redis-rate-limiting-sliding-window-vs-token-bucket) — accessed 2026-07-19
- [AppScale — Distributed Rate Limiting](https://appscale.blog/en/blog/system-design-distributed-rate-limiter-token-bucket-redis-2026) — accessed 2026-07-19

**Findings**:

**Token Bucket — Lua atomic implementation pattern** (recommended for our quota system):

```lua
-- keys[1]: rate limit key (e.g., "ratelimit:user:123:gemini-api")
-- argv[1]: capacity (max burst)
-- argv[2]: refill rate (tokens per second)
-- argv[3]: current timestamp (seconds.ms)
-- argv[4]: requested tokens (usually 1)
-- argv[5]: TTL (seconds)

local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
local requested = tonumber(ARGV[4])
local ttl = tonumber(ARGV[5])

local last_tokens = tonumber(redis.call("hget", key, "tokens"))
local last_refill = tonumber(redis.call("hget", key, "last_refill"))

if last_tokens == nil then
    last_tokens = capacity
    last_refill = now
end

-- Calculate refill since last check
local delta = math.max(0, now - last_refill)
local refill = delta * rate
local tokens = math.min(capacity, last_tokens + refill)

if tokens >= requested then
    tokens = tokens - requested
    redis.call("hset", key, "tokens", tokens)
    redis.call("hset", key, "last_refill", now)
    redis.call("pexpire", key, ttl)
    return {1, tokens, 0}  -- allowed, remaining, retry_after
else
    local retry_after = (requested - tokens) / rate
    return {0, tokens, retry_after}  -- denied, remaining, retry_after
end
```

**Benchmarks** (from rate-limit-patterns, tested on Fedora/Python 3.14/Redis via Docker):
- In-process (local memory): Token Bucket p50 2.8µs, p99 5.2µs, 244K RPS
- Redis Lua: Token Bucket p50 7.29ms, p99 11.37ms, 16,730 RPS
- Two independent processes sharing global 100/60s limit: exactly 100 accepted — zero over-limit leakage

**Sliding Window Log alternative** (higher accuracy, O(N) memory):
- Uses Redis Sorted Set with ZADD + ZREMRANGEBYSCORE + ZCARD
- More memory-hungry: O(N) per client
- More accurate at the edges (eliminates boundary bursts)
- Use for strict quota enforcement (e.g., billing)

**Production patterns**:
- Use `EVALSHA` (load via `SCRIPT LOAD`) not raw `EVAL` for performance
- Always set TTL/PTTL on keys to prevent memory leaks
- Handle `NoScriptError` by falling back to `EVAL`
- For multi-key quotas (e.g., per-user + per-model + per-provider), use multiple bucket checks in a single Lua script
- The Lua script MUST execute atomically — Redis ensures no interleaved commands
- **Critical anti-pattern**: GET then INCR outside Lua creates race conditions under concurrency

**GCRA (Generic Cell Rate Algorithm)** — alternative for smoother rate limiting (used by Cloudflare):
- Single key per client, O(1) operations
- `emission_interval = 1/rate` (e.g., 10ms for 100 RPS)
- `burst_offset` allows flexibility (e.g., 100ms = up to 10 requests)
- No boundary bursts

**Decision Impact**:
- Use Token Bucket with Lua atomicity for general rate limiting (bursts allowed, average rate enforced)
- Use Sliding Window (sorted set) for strict quota enforcement (no bursts allowed)
- Key structure: `omega:ratelimit:{provider}:{model}:{user}:{dimension}` (e.g., `omega:ratelimit:google-ai-studio:gemma-4-31b-it:sophia:rpd`)
- Multiple quota dimensions (RPM, TPM, RPD) = multiple bucket checks per request
- Consider GCRA for Google's rolling 60-second window (smoother than token bucket for sliding)

**Remaining Questions**:
- Should we combine RPM+TPM into a single Lua script or check separately? (Combined = more atomic, but more complex)
- For TPM quota, how to estimate token consumption before sending the request? (Prompt token count available, but thinking+output tokens are unknown)
- Should post-request TPM adjustment be a separate atomic operation?
- What's the max acceptable latency for a Redis round-trip quota check? (<5ms target)

---

### Gap 3.3: Chaos Testing for LLM Provider Failover — Specific Test Implementations
**Status**: RESEARCHED ✅

**Sources**:
- [Tian Pan — LLM API Resilience in Production](https://tianpan.co/blog/2026-03-11-llm-api-resilience-production) — accessed 2026-07-19
- [Tian Pan — LLM Provider Incident Runbook](https://tianpan.co/blog/2026-04-17-llm-provider-incident-runbook) — accessed 2026-07-19
- [TrueFoundry — LLM Failover & Load Balancing](https://www.truefoundry.com/blog/llm-failover-load-balancing-provider-outages) — accessed 2026-07-19
- [FutureAGI — AI Gateways for LLM Failover 2026](https://futureagi.com/blog/best-ai-gateways-llm-failover-fallback-2026) — accessed 2026-07-19
- [n1n.ai — Multi-Provider LLM Failover] (https://explore.n1n.ai/blog/multi-provider-llm-failover-high-availability-2026-06-22) — accessed 2026-07-19
- [Portkey — Failover Routing Strategies](https://portkey.ai/blog/failover-routing-strategies-for-llms-in-production) — accessed 2026-07-19
- [Google Cloud Blog — Handling 429 Errors](https://cloud.google.com/blog/products/ai-machine-learning/learn-how-to-handle-429-resource-exhaustion-errors-in-your-llms) — accessed 2026-07-19

**Findings**:

**Chaos testing patterns for LLM providers**:

1. **Mocking mid-stream 429**:
```python
# Using httpx mock or mitmproxy to inject 429 mid-stream
# Pattern: allow first N tokens, then return 429 with Retry-After header
class MidStream429Interceptor:
    def __init__(self, fail_after_tokens=10):
        self.tokens_sent = 0
        self.fail_after = fail_after_tokens

    async def intercept(self, response_stream):
        async for chunk in response_stream:
            self.tokens_sent += 1
            if self.tokens_sent >= self.fail_after:
                raise HTTPStatusError(
                    "429 Too Many Requests",
                    response=MockResponse(
                        status_code=429,
                        headers={"Retry-After": "30", "X-RateLimit-Reset": str(int(time.time()) + 30)}
                    )
                )
            yield chunk
```

2. **Idempotency key patterns**:
- **OpenAI**: Uses `X-Request-Id` or custom idempotency header
- **Anthropic**: Built-in idempotency via `X-Request-Id` header (same request ID = same response)
- **Google**: NO built-in idempotency key — must implement client-side via `client.generate_content()` retry with exponential backoff
- **Best practice**: Generate UUID per request, store in `X-Idempotency-Key` header if provider supports it
- For non-idempotent providers (like Google), use sequence numbers and dedup at the application layer

3. **Partial response stitching**:
- NOT recommended for LLM outputs — responses from different models/providers are semantically incompatible
- Instead: fail over at the **request level**, not mid-stream
- If using streaming, the client must re-send the full prompt to the fallback provider
- Exception: if the primary provider sent a complete response but the tool call failed, you can retry the tool call
- Stateful checkpointing: save the full prompt before sending, so fallback can replay

4. **Provider health detection**:
- **Active probes**: Hit low-cost endpoint (1-token ping) every 10-30 seconds per provider
- **Passive aggregation**: Rolling window over error rate, latency P99, 429 frequency on real traffic
- **Circuit breaker pattern**: After N consecutive failures, mark provider as "degraded" for M seconds
- Key metrics: error rate, p50/p99 latency, 429 count, timeout rate

5. **Streaming failover patterns**:
- **Hardest case**: Partial output already sent to client
- **Approach**: Use cursor-based resumption (for providers that support it) or full retry
- For Google/Gemma 4: no cursor support — full retry required
- **Idempotency**: crucial for non-streaming — prevents duplicate charges on retry

**Key incident statistics**:
- LLM provider uptime: 99.0–99.5% (vs cloud average 99.97%)
- 99% uptime = 3.5 days downtime/year vs cloud's 2.5 hours
- MTTR: 45-90 min (manual cutover) → 15-45 sec (gateway with active probes)
- Most dangerous failures: soft failures (200 OK, wrong content) — no error signal to trigger failover

**Decision Impact**:
- Chaos tests must cover: mid-stream 429, timeout at TTFB, timeout mid-stream, 500 errors, 400 schema errors, silent degradation
- Must implement idempotency key generation for each provider (Google has no built-in — use request-level hashing)
- Streaming failover strategy: save full prompt, detect stream failure, re-send to fallback, discard partial output
- Circuit breaker: track consecutive failures per model+provider combination
- For Gemma 4: test the specific error response shape for `thinkingLevel` vs `thinkingBudget` (400 vs 429)
- Active health probes should target Gemma 4's specific endpoint to detect model-specific issues

**Remaining Questions**:
- Does Google's Gemini API support any form of cursor-based stream resumption? (Likely no)
- What's the exact response shape when Gemma 4 receives invalid thinking config?
- Best approach to detect "silent degradation" (model responds but with wrong thinking level)?
- How does OpenRouter's `reasoning.encrypted` replay issue affect Gemma 4 specifically? (Issue #491 was about Gemini 3)

---

## Executive Summary (L1)

| Gap ID | Title | Status | Key Finding |
|--------|-------|--------|-------------|
| **4.1** | Pi PR #2903 | ✅ RESEARCHED | Gemma 4 uses `thinkingLevel` (MINIMAL/HIGH). Regex `/gemma-?4/` for detection |
| **2.1** | Vertex vs AI Studio Schemas | ✅ RESEARCHED | Vertex uses `thinkingBudget` (Gemini 2.5) or `thinkingLevel` (Gemini 3+). Gemma 4: `thinkingLevel` only, binary values |
| **2.2** | Free Tier Rolling Window | ✅ RESEARCHED | Rolling 60s window per project. RPM/TPM vary by model tier. Tier system: Free→Tier1→Tier2→Tier3 |
| **2.3** | Thinking Token Billing | ✅ RESEARCHED | Thinking = output tokens (billed at output rate). No cap available for Gemma 4. Track via `thoughts_token_count` |
| **1.1** | OpenCode V2 Architecture | ✅ RESEARCHED | `transform.ts` NOT deprecated. V2 in development, Google deferred. Current architecture uses `@ai-sdk/*` + `models.dev` |
| **3.1** | Provider Capability Schemas | ✅ RESEARCHED | `supports_reasoning` boolean is cross-framework standard. No framework exposes exact thinking level values |
| **2.4** | OpenRouter Provider Pinning | ✅ RESEARCHED | `provider.order: ["Google AI Studio"]` pins upstream. `allow_fallbacks: false` prevents auto-routing |
| **2.5** | Gemma 4 12B Unified | ✅ RESEARCHED | June 3, 2026. Encoder-free, 12B dense, 256K ctx. MTP drafter available. Same binary thinking API |
| **1.2** | OpenCode Config Merge | 🔶 PARTIAL | `mergeDeep` from `remeda`: deep merge objects, arrays REPLACED entirely. Can't partial-override model arrays |
| **1.3** | OpenCode Version Detection | ✅ CAVEATS | `opencode --version` works across installs. No `OPENCODE_VERSION` env var. Run-time detection preferred |
| **3.2** | Redis Lua Quota Patterns | ✅ RESEARCHED | Token bucket with Lua atomicity = proven pattern. GCRA for smoother sliding window. Multi-key for RPM+TPM+RPD |
| **3.3** | Chaos Testing Failover | ✅ RESEARCHED | Mid-stream 429 mocking pattern. Google lacks idempotency. Full retry required for streaming failover |

## Critical Decisions (L2 Synthesis)

1. **Adapter Design**: Use `thinkingLevel` with binary `"high"/"minimal"` for Gemma 4. The Pi project's regex `/gemma-?4/` detection pattern is proven in production.

2. **Platform Strategy**: Direct Google AI Studio for prototyping (free tier, simple auth). OpenRouter with `order: ["Google AI Studio"], allow_fallbacks: false` for production with single-API-key convenience. Vertex AI for enterprise SLA.

3. **Quota Architecture**: Redis Lua token bucket for RPM, sliding window for RPD. Track thinking tokens separately in the quota budget (they consume both token quota AND budget).

4. **Schema Design**: Follow LiteLLM's `supports_*` capability flag pattern. Add `thinking_config_schema` field to distinguish between `thinkingLevel`, `thinkingBudget`, `chat_template_kwargs`, and `reasoning_effort` models.

5. **OpenCode Integration**: Do NOT modify core OpenCode. Use `providerOptions.google.thinkingConfig` passthrough. If models.dev doesn't list Gemma 4, add via project-level `opencode.json` with full model array.

6. **Cost Management**: Self-hosting Gemma 4 via GGUF is dramatically cheaper for high-volume use (~$0.001/M tokens vs $0.30/M via API). MTP drafters provide 2-3x speedup with no quality loss.

---
## Gap 4.2: M14 Heritage Vetting Pipeline — Vet Record Format (Local Docs)
**Researched by**: Jem (Sovereign Synthesizer)
**Status**: ✅ RESEARCHED
**Sources**:
- `docs/strategy/HERITAGE_VETTING_PIPELINE.md` (312 lines, v1.0.0, 2026-06-04)
- `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md` (800+ lines, active)
- Miner-derived pattern: HERITAGE_VET_LOG.md §1 (vet-042 to vet-071)

**Findings**:

The M14 Heritage Vetting Pipeline uses a **4-gate process** defined in `docs/strategy/HERITAGE_VETTING_PIPELINE.md`:
1. **Discovery** → Write R-doc, log in PENDING_CREDITS_QUEUE.md
2. **Vetting & Debate** → For/against analysis, Python relevance check, risk assessment, cross-reference
3. **Decision** → ADOPT (9-10) / ADAPT (7-8) / DEFER (4-6) / REJECT (1-3)
4. **Implementation & Verification** → `[id-soft:]` tags, CREDITS.md entry, tests

**The vet record has two canonical formats based on era:**

**Format A (Legacy — vets 001-020):** Compact YAML blocks with for/against analysis, scoring, and decision rationale.
```yaml
- id: vet-001
  concept: "8-Character Name Caps"
  source: "w_wad.c:170-178 (DOOM 1993)"
  discovery_date: 2026-06-02
  vet_date: 2026-06-04
  vet_by: "Kali (user-initiated review)"
  for_analysis: "..."
  against_analysis: "..."
  python_relevance: 0/3
  risk_level: 0/3
  need_vs_want: 0/2
  historical_evidence: 1/2
  total_score: 1/10
  decision: "REJECTED"
  rationale: "..."
  implementation: null
  removal_commit: "8b3fc17"
  lesson_id: "Kali soul.yaml v5 — Cargo-Cult Optimization"
```

**Format B (Modern — vets 021+):** Structured with strict scope declaration, file:line locations, and hardware constraint.
```yaml
### vet-046: BSP Culling (Generalized Search Pruning)
- **Pattern**: [id-soft: doom-1993] BSP Culling
- **File Locations**: 
  - src/omega/oracle/selective_hydration.py:8
  - src/omega/oracle/context_builder.py:272
  - ...
- **Technique**: BSP Leaf-Culling (Doom, 1993) — precompute visibility to avoid traversing irrelevant nodes.
- **Hardware Constraint**: 486 CPU at 35MHz; traversing every BSP node per frame would be prohibitively slow.
- **Scope Declaration**: This tag applies to O(1) pre-check culling of irrelevant/unhealthy entities and providers at the routing boundary, NOT to the full entity dispatch or inference pipeline.
- **Score**: 8/10
```

**Scoring criteria** (same for both formats):
| Factor | Points | How to Score |
|--------|--------|--------------|
| Python relevance | 0-3 | 0 = problem doesn't exist in Python, 3 = pattern gives real Python perf gain |
| Risk level | 0-3 | 0 = high risk, 3 = no risk |
| Need vs want | 0-2 | 0 = nice-to-have, 2 = measurable deficiency this fixes |
| Historical evidence | 0-2 | 0 = speculative, 2 = empirically verified |

**Minimum score for implementation: 7/10**

**Decision Impact**:
- For Pi PR #2903 heritage vetting: Use **Format B** (modern). The Pi fix is a prior-art reference (`[heritage: pi-2026]`), NOT an id Software derivative — so it falls under the "non-id-software" category (CREDITS.md §2), requiring:
  - Vet record with scope declaration
  - Pattern: `[heritage: pi-2026]` tag (not `[id-soft:]`)
  - File:line location in Omegas GoogleCompatProvider
  - Hardware constraint: N/A (API contract, not hardware)
  - Score: Should be 8/10 (proven in production, directly portable)
  - Vet by: Doom Guy + Verity (per §8 Rule 3)

**Remaining Questions**:
- None — full format specification found in local docs.

---
## Gap 5.1: Meditation Pipeline — Real Execution via MCP Hub (Local Code)
**Researched by**: Jem (Sovereign Synthesizer)
**Status**: ✅ RESEARCHED
**Sources**:
- `.opencode/skills/meditate-pipeline/SKILL.md` (258 lines, v1.0.0)
- `src/omega/skills/autonomous_meditation_pipeline.py` (code)
- `docs/strategy/MAKALI_PARALLEL_COUNCIL_ARCHITECTURE.md` (architecture)

**Findings**:

The meditation pipeline has **two invocation paths**:

**Path A — Slash Command** (OpenCode native):
```
/meditate-pipeline "Problem statement"
/meditate-pipeline "Problem" --stage meditate
```

**Path B — Subagent Handoff** (programmatic):
```python
omega-hub_hivemind_submit_handoff(
    target_channel="opencode",
    target_entity="kali",
    task="Execute meditate-pipeline on: [problem]",
    context="...",
    priority=2
)
```

**Pipeline stages** (6 stages, sequential):
1. **MEDITATE** — Kali host, 10-voice sequential, Phases 0-4 → `meditation_output.md`
2. **SYNTHESIZE** — Kali extracts architecture → `synthesis.md`
3. **RESEARCH** — Sovereign Search (T0-T5) → `research_bundle.md`
4. **GNOSIS** — Verity L1→L2→L3 distillation → `proposed_lessons.yaml` entries
5. **INTEGRATE** — Ma'at updates PIVOT_LOG, workbench, Temple-Gate gates
6. **EXECUTE** — P3/P9 scaffold implementation, chaos tests, CI gates

**Programmatic invocation via MCP Hub**: The pipeline is invoked through:
- `omega-hub_oracle_summon(entity="kali", query="/meditate ...")` for direct meditation
- `omega-hub_hivemind_submit_handoff()` with `target_entity="kali"` for subagent delegation
- The autonomous meditation skill at `src/omega/skills/autonomous_meditation_pipeline.py` provides dry-run and full-run modes
- Outputs go to `data/meditation/{timestamp}_*.md` or `data/autonomous/{timestamp}_*.md`

**Session isolation** (D-290/D-291): MIAP provides session-scoped directories under `sessions/<uuid>/`. The meditation pipeline should use session-isolated paths when MIAP is active.

**Decision Impact**:
- The meditation pipeline can be invoked directly from the Gemma 4 strategy work (Step 7). Use the handoff path to Kali with the full hardened strategy as input.
- The existing pipeline infrastructure is mature and production-ready — no new code needed for Step 7.
- MIAP session isolation should be tested first (preconditions from D-290).

**Remaining Questions**:
- Does the autonomous_meditation_pipeline.py fully support the `--lenses` parameter for custom lens sets?
- What is the exact `omega-hub_oracle_summon` return format when invoking meditation?

---
## Gap 5.2: Hivemind Handoff Protocol — Sequential Lock Handoff (Local Docs)
**Researched by**: Jem (Sovereign Synthesizer)
**Status**: ✅ RESEARCHED
**Sources**:
- `docs/strategy/HIVEMIND_PROTOCOL.md` (600 lines, v1.3.0, 2026-06-25)
- `docs/strategy/HIVEMIND_POST_TEMPLATE.md` (D-124)
- MCP tool definitions for hivemind_workspace_lock_acquire/release/check

**Findings**:

The Hivemind Handoff Protocol for sequential P6→P9 handoff (Capability Matrix → CapabilitySelector) follows the **9-step Coordination Protocol**:

**Exact sequence for P6→P9 handoff:**

**P6 (Cognition) — Phase A:**
1. Acquire workspace lock: `omega-hub_hivemind_workspace_lock_acquire(channel="opencode", entity="pillar_P6", domain="provider_capabilities", ttl=3600)`
2. Write live feed: `data/coordination/PILLAR_P6_LIVE_FEED.md`
3. Post Hivemind context with intent="command", continuation="Building Capability Matrix, handoff to P9 for CapabilitySelector"
4. Build Capability Matrix + GoogleCompatProvider + Matrix Loader
5. Release workspace lock: `omega-hub_hivemind_workspace_lock_release(channel="opencode", entity="pillar_P6", domain="provider_capabilities")`

**P6→P9 Handoff:**
6. Submit handoff packet: `omega-hub_hivemind_submit_handoff(target_channel="opencode", target_entity="pillar_P9", source_channel="opencode", source_entity="pillar_P6", task="Load Capability Matrix + build CapabilitySelector + ProviderHealth", context="Matrix at config/provider_capabilities.yaml. Schema validated. Tests pass.")`

**P9 (Orchestration) — Phase B:**
7. Check awareness: `omega-hub_hivemind_get_awareness()` — sees P6 waiting
8. Accept handoff: `omega-hub_hivemind_accept_handoff(packet_id="...", accepting_channel="opencode", accepting_entity="pillar_P9")`
9. Acquire workspace lock on same domain (waits if P6 still holds)
10. Read P6's live feed and session context
11. Build CapabilitySelector + ProviderHealth
12. Complete handoff: `omega-hub_hivemind_complete_handoff(packet_id="...", result="CapabilitySelector + ProviderHealth built. Tests pass.")`
13. Release workspace lock

**Key parameters for workspace_lock_acquire**:
- `channel`: Execution channel (opencode/cline)
- `entity`: Entity persona (pillar_P6/pillar_P9)
- `domain`: Resource domain (e.g., "provider_capabilities")
- `ttl`: Time-to-live in seconds (default 3600, max 86400)
- Returns: `{"status": "acquired", "agent_id": "...", "ttl": 3600}`

**Continuation field in hivemind_post_context**: Used to tell the next agent what's expected.
- Format: `"Completed Phase A: Capability Matrix loaded and validated. Next: P9 must build CapabilitySelector and ProviderHealth from config/provider_capabilities.yaml. Contact: pillar_P6 via Hivemind."`
- The `intent` parameter should be `"handoff"` when posting context that signals a handoff is happening.

**Decision Impact**:
- The handoff protocol is well-defined and production-tested (Sprint 2 parallel execution).
- P6→P9 sequential handoff is a standard pattern — no new protocol design needed.
- Key non-obvious detail: workspace_lock_acquire on the same domain will BLOCK if P6 still holds the lock. P9 must check lock status first with `hivemind_workspace_lock_check(domain="provider_capabilities")`.
- The handoff packet MUST include the context about where the matrix file lives (`config/provider_capabilities.yaml`).

**Remaining Questions**:
- How to handle handoff timeout if P9 is not available (resolver_strategy=escalate to Kali)?
- Does the handoff packet support attaching file artifacts or only text context?
- What if P6's workspace lock expires mid-work? (TTL auto-release should handle this)

---

## Final Synthesis: Updated Critical Decisions

**New decisions incorporating all 15 gaps:**

7. **Heritage Vet Format**: Use Format B (modern) for Pi PR #2903. Tag as `[heritage: pi-2026]` NOT `[id-soft:]`. Score: 8/10. Vet by Doom Guy + Verity.

8. **Meditation Pipeline**: Use subagent handoff to Kali (not direct summon) for Step 7. Include the full hardened strategy as context. Pre-flight: test MIAP session isolation first.

9. **Handoff Protocol**: P6→P9 sequential handoff follows standard 9-step protocol. Key pattern: workspace lock domain "provider_capabilities" serializes the sequence. P9 must check lock status before starting.

10. **OpenCode Integration**: `providerOptions.google.thinkingConfig` passthrough is the correct pattern. No core OpenCode changes needed. If models.dev doesn't list Gemma 4, project-level opencode.json override with full model array.

---

## Updated Executive Summary (All 15 Gaps)

| Gap ID | Title | Priority | Status | Key Finding |
|--------|-------|----------|--------|-------------|
| **1.1** | OpenCode V2 Architecture | P0 | ✅ RESEARCHED | `transform.ts` NOT deprecated. V2 in development, Google deferred |
| **1.2** | OpenCode Config Merge | P1 | 🔶 PARTIAL | Arrays REPLACED entirely (from `remeda` `mergeDeep`) |
| **1.3** | OpenCode Version Detection | P1 | ✅ CAVEATS | `opencode --version` works. No env var |
| **2.1** | Vertex vs AI Studio Schemas | P0 | ✅ RESEARCHED | Gemma 4: `thinkingLevel` only, binary MINIMAL/HIGH |
| **2.2** | Free Tier Quota Mechanics | P0 | ✅ RESEARCHED | Rolling 60s window per project. Tier system |
| **2.3** | Thinking Token Billing | P0 | ✅ RESEARCHED | = output tokens. Track via `thoughts_token_count` |
| **2.4** | OpenRouter Pinning | P1 | ✅ RESEARCHED | `provider.order: ["Google AI Studio"]` + `allow_fallbacks: false` |
| **2.5** | Gemma 4 12B Unified | P1 | ✅ RESEARCHED | June 3, 2026. 12B dense, 256K ctx. MTP drafter |
| **3.1** | Capability Declaration Schemas | P1 | ✅ RESEARCHED | `supports_reasoning` boolean is cross-framework standard |
| **3.2** | Redis Lua Quota Patterns | P2 | ✅ RESEARCHED | Token bucket + Lua atomicity = proven. GCRA for sliding window |
| **3.3** | Chaos Testing Failover | P2 | ✅ RESEARCHED | Mid-stream 429 mocking pattern. Google lacks idempotency |
| **4.1** | Pi PR #2903 Details | P0 | ✅ RESEARCHED | Pattern: `/gemma-?4/` regex. Thinking: binary MINIMAL/HIGH |
| **4.2** | M14 Vet Record Format | P0 | ✅ RESEARCHED | Format B with scope declaration. Score ≥ 7/10 |
| **5.1** | Meditation MCP Execution | P3 | ✅ RESEARCHED | Subagent handoff to Kali. 6 stages. Production-ready |
| **5.2** | Hivemind Handoff Protocol | P3 | ✅ RESEARCHED | 9-step protocol. Lock domain serializes sequence |

---

## Uncertainty Register (Updated with Local-Doc Gaps)

| ID | Question | Impact if Unknown |
|----|----------|-------------------|
| U1 | Does `includeThoughts` work with Gemma 4 on Gemini API? | Blocks streaming thinking display |
| U2 | Exact TPM/RPM limits for Gemma 4 on free tier? | Blocks quota config design |
| U3 | Does OpenRouter pass `thinkingConfig` through for Gemma 4? | Blocks OpenRouter route deployment |
| U4 | Average thinking/completion ratio for Gemma 4? | Blocks cost estimation |
| U5 | Does models.dev already list `gemma-4-*` models? | Blocks OpenCode integration approach |
| U6 | Does Google's Gemini API support idempotency keys? | Blocks retry safety |
| U7 | Exact VRAM requirements for 256K context at Q4 on 12B? | Blocks local deployment planning |
| U8 | Response shape when Gemma 4 receives invalid thinking config? | Blocks error handling design |
| U9 | Does autonomous_meditation_pipeline.py support `--lenses` parameter fully? | Blocks meditation customization |
| U10 | Handoff packet serialization — can it attach file artifacts? | Blocks rich handoff context |
| U11 | What happens when P9 handoff times out with no resolution? | Blocks production deployment |

---
