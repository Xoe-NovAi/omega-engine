# 🔱 Gemma 4 31B — Comprehensive Investigation & Strategic Report

**AP Token**: `AP-GEMMA4-COMPREHENSIVE-v1.0.0`
⬡ OMEGA ⬡ JEM ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_synthesis ⬡ 2026-07-19

**Purpose**: Unified findings from Roc Racoon (local mining), Researcher (web research), Ma'at (Build Side), and Lilith (Run Side) — synthesized by Jem.

**Status**: INVESTIGATION COMPLETE — Strategy Defined — Ready for Implementation

---

## Executive Summary

Gemma 4 31B **works perfectly** via direct Google Generative AI API and via Cline CLI (which uses the native Google SDK). It **fails in OpenCode CLI** due to broken request construction in `transform.ts` — OpenCode's provider layer that transforms model IDs and thinking configurations before sending to the API.

This is not a new issue. The **Pi project fixed the identical bug 3 months ago** (PR #2903) with a simple regex detection and thinking level mapping. OpenCode has not incorporated the fix.

**Four distinct root causes** were identified by the combined fleet. The bug is an opportunity: building a **Provider Capability Negotiation** layer that makes this entire class of bugs impossible, not just patched.

| Agent | Deliverable | Status |
|-------|-------------|--------|
| **Roc Racoon** | Local context mining — found canonical debug report `GEMMA4_OPENCODE_DEBUG_REPORT_20260718.md` (404 lines) | ✅ Complete |
| **Researcher** | Web research — 15+ verified sources, exact `transform.ts` code analysis, OpenCode issues, Pi PR #2903 reference | ✅ Complete |
| **Ma'at** | Build Side (P1-P5) — Provider config, model cards, GoogleAIProvider enhancement, OpenCode upstream PR | ✅ Complete |
| **Lilith** | Run Side (P6-P10) — Capability Matrix, Thinking Normalizer, Provider Dashboard, Fallback Chain, Chaos Tests | ✅ Complete |

---

## Part I: Problem Analysis

### §1 The Symptom

| Platform | Model | Result |
|----------|-------|--------|
| **Direct Google API** (curl/Python) | `gemma-4-31b-it` | ✅ Works — `thinkingLevel: "HIGH"` returns thoughts |
| **Cline CLI** | `gemma-4-31b-it` (via `@google/genai` SDK) | ✅ Works — several tool calls, then quota exhausted |
| **OpenCode CLI** | `google/gemma-4-31b-it` (via `@ai-sdk/google` + `transform.ts`) | ❌ 400 error or 429 quota |

### §2 Root Causes (4 Identified)

#### Root Cause #1: Model ID Prefix Mismatch
- **OpenCode sends**: `google/gemma-4-31b-it` (with `google/` prefix from models.dev catalog)
- **API expects**: `gemma-4-31b-it` (bare model ID, no prefix)
- **Evidence**: Direct API test confirms `gemma-4-31b-it` → works, `google/gemma-4-31b-it` → 404/hang
- **Location**: `packages/opencode/src/provider/transform.ts` uses `model.api.id` directly; upstream models.dev adds the `google/` prefix

#### Root Cause #2: Wrong Thinking Levels
- **OpenCode sends**: `thinkingLevel: "LOW"` or `thinkingLevel: "high"` (lowercase)
- **API expects**: `thinkingLevel: "MINIMAL"` or `thinkingLevel: "HIGH"` (UPPERCASE, only two values)
- **Gemma 4 supports only**: `"MINIMAL"` (thinking off) and `"HIGH"` (thinking on) — **not** `LOW`, `MEDIUM`, or lowercase variants
- **Location**: `googleThinkingLevelEfforts()` in `transform.ts` returns `["low", "high"]` for non-Gemini-3 models → these become `"LOW"` and `"HIGH"` → `"LOW"` is invalid for Gemma 4

#### Root Cause #3: Missing `thinkingLevel` in Base Config
- **OpenCode sends**: `thinkingConfig: { includeThoughts: true }` (without `thinkingLevel`)
- **API expects**: `thinkingConfig: { thinkingLevel: "HIGH", includeThoughts: true }`
- **Location**: `options()` in `transform.ts` only adds `thinkingLevel` for models matching `"gemini-3"` — Gemma 4 is not detected

#### Root Cause #4: Config Merge Failure
- **OpenCode's behavior**: When project config has explicit `provider.google.models`, it **replaces** (not merges) auto-discovered models
- **Result**: Gemma 4 was excluded from the explicit model list → fell back to auto-discovered model with wrong `api.id` format
- **Location**: `packages/opencode/src/config/models.ts` — merge logic is replace, not override-by-key

### §3 Why Cline CLI Works

Cline CLI **bypasses OpenCode's `transform.ts` entirely**. It uses:

| Aspect | Cline CLI | OpenCode CLI |
|--------|-----------|--------------|
| **SDK** | `@google/genai` (native Google SDK) | `@ai-sdk/google` (via transform layer) |
| **Model ID** | `gemma-4-31b-it` (bare) | `google/gemma-4-31b-it` (prefixed) |
| **Thinking Config** | `ThinkingLevel.HIGH` (enum) | `thinkingLevel: "high"` (string, wrong case) |
| **Detection** | Built-in Gemma 4 support | **Missing** — written for Gemini 3 only |

### §4 Quota Exhaustion Explained

Google AI Studio free tier has a **rolling input-token budget of ~16k tokens**. Omega's instruction stack exceeds this:

| Source | Approximate Size |
|--------|-----------------|
| `SOVEREIGN_MANDATES.md` | ~4.8k tokens |
| `MASTER_SYNTHESIS_AND_ROADMAP…` | ~5.7k tokens |
| `SOVEREIGN_ARK_BLUEPRINT.md` | ~3.2k tokens |
| `AGENTS.md` (auto-injected) | ~4.9k tokens |
| Agent file (e.g., `john_carmack.md`) | ~2.9k tokens |
| Tools + system + history | additional thousands |

**Project instructions alone approach or exceed the free-tier 16k input budget.** A tiny curl prompt (~5 tokens) succeeds; a normal OpenCode agent turn does not.

OpenCode then **retry-spams** 429s (observed 6+ retries), which re-drains the rolling window and makes the model appear "broken for a week."

**Free tier quotas (verified 2026-07-19):**

| Provider | RPM | RPD | Input Token Budget |
|----------|-----|-----|--------------------|
| Google AI Studio (Gemma 4) | ~15 | ~1,500 | ~16k rolling |
| OpenRouter (`:free`) | 20 | 200 | — |

### §5 Prior Art — The Pi Project Fix

The Pi project fixed this **identical issue** 3 months ago:

| Date | Source | Finding |
|------|--------|---------|
| 2026-04-04 | [Pi Issue #2812](https://github.com/earendil-works/pi/issues/2812) | Gemma 4 uses `thinkingLevel` not `thinkingBudget`; only `MINIMAL`/`HIGH` supported |
| 2026-04-05 | [Pi PR #2903](https://github.com/earendil-works/pi/pull/2903) | Fix: regex `/gemma-?4/i` detection + thinking level mapping |
| 2026-04-05 | [OpenCode Issue #21067](https://github.com/anomalyco/opencode/issues/21067) | Model ID `gemma-4-31b` wrong; should be `gemma-4-31b-it` |
| 2026-04-16 | [OpenCode Issue #22853](https://github.com/anomalyco/opencode/issues/22853) | "Gemma 4 not working" — closed as not_planned |
| 2026-04-17 | [Google Cookbook #1198](https://github.com/google-gemini/cookbook/issues/1198) | `includeThoughts: false` silently ignored for Gemma 4 |
| 2026-07-02 | [Google AI Docs](https://ai.google.dev/gemma/docs/core/gemma_on_gemini_api) | Official docs confirm: `thinkingLevel: "HIGH" | "MINIMAL"` for Gemma 4 |

**Key historical fact**: The Pi project's fix is a 10-line regex detection + mapping. OpenCode has not incorporated it.

---

## Part II: OpenCode Source Code Analysis

### §6 `transform.ts` — Exact Bug Locations

**File**: `packages/opencode/src/provider/transform.ts`

#### Function: `googleThinkingLevelEfforts(apiId)` (~line 1120)
```typescript
function googleThinkingLevelEfforts(apiId: string) {
  const id = apiId.toLowerCase()
  if (!id.includes("gemini-3")) return ["low", "high"]  // ← BUG: Gemma 4 gets "low" which becomes "LOW" (invalid)
  if (id.includes("flash-image")) return ["minimal", "high"]
  if (id.includes("pro-image")) return ["high"]
  if (id.includes("flash")) return ["minimal", "low", "medium", "high"]
  return ["low", "medium", "high"]
}
```
**Bug**: Gemma 4 returns `["low", "high"]` → `low` becomes `thinkingLevel: "LOW"` → **400 error** (Gemma 4 only supports `MINIMAL`/`HIGH`).

#### Function: `googleThinkingVariants(model)` (~line 1137)
```typescript
function googleThinkingVariants(model: Provider.Model) {
  const id = model.api.id.toLowerCase()
  if (id.includes("2.5")) return { high, max }  // ← Only checks for Gemini 2.5
  return Object.fromEntries(
    googleThinkingLevelEfforts(id).map((effort) => [
      effort,
      { thinkingConfig: { includeThoughts: true, thinkingLevel: effort } },  // ← "low" → "LOW" (invalid for Gemma 4)
    ]),
  )
}
```
**Bug**: No Gemma 4 branch. Variants use effort string directly as `thinkingLevel` → `low` → `"LOW"` (invalid).

#### Function: `options()` (~line 1110)
```typescript
if (input.model.api.npm === "@ai-sdk/google") {
  result["thinkingConfig"] = { includeThoughts: true }
  if (input.model.api.id.includes("gemini-3")) {  // ← Only checks gemini-3
    result["thinkingConfig"]["thinkingLevel"] = "high"
  }
}
```
**Bug**: For Gemma 4: sends `thinkingConfig: { includeThoughts: true }` **without `thinkingLevel`** → API rejects.

### §7 Correct API Formats

#### Google Generative AI API (Direct)
**Endpoint**: `POST https://generativelanguage.googleapis.com/v1beta/models/gemma-4-31b-it:generateContent`

```json
{
  "contents": [{"parts": [{"text": "Your prompt"}]}],
  "generationConfig": {
    "thinkingConfig": {
      "thinkingLevel": "HIGH",
      "includeThoughts": true
    }
  }
}
```

**Supported `thinkingLevel` values for Gemma 4:**

| Value | Effect |
|-------|--------|
| `"HIGH"` | Full reasoning mode |
| `"MINIMAL"` | Disables thinking |
| `"LOW"`, `"MEDIUM"` | **NOT SUPPORTED → 400 error** |

#### OpenRouter Format
**Model ID**: `google/gemma-4-31b-it` (OpenRouter uses provider prefix)

```json
{
  "model": "google/gemma-4-31b-it",
  "messages": [{"role": "user", "content": "Your prompt"}],
  "reasoning": { "effort": "high" }
}
```

---

## Part III: Strategic Response — Bug to Feature

### §8 The Architectural Insight

The root cause isn't just wrong thinking levels — it's that **provider capabilities are hardcoded, not declared.** The `transform.ts` code assumes all Google models follow Gemini patterns. Gemma 4 uses a different API contract.

**The fix**: Build a **Provider Capability Negotiation** layer that makes this class of bugs impossible.

### §9 Implementation Plan — Combined Build + Run Side

#### Phase 1: Foundation (Week 1 — 23h)

| # | Task | Owner | Effort | Blocks |
|---|------|-------|--------|--------|
| 1 | `config/provider_capabilities.yaml` — Declare what each model supports | P6 Cognition | 2h | Everything |
| 2 | `ProviderCapabilityMatrix` class — Load/query capabilities at runtime | P6 Cognition | 3h | P7, P9 |
| 3 | `ThinkingConfigNormalizer` class — Translate between Google/Anthropic/OpenAI/Qwen3 formats | P7 Context | 4h | Integration |
| 4 | `extract_thoughts()` per format — Extract thinking content from provider responses | P7 Context | 3h | Gnosis |
| 5 | Regression tests for Capability Matrix + Normalizer | P10 Validation | 4h | CI gate |
| 6 | `GoogleAIProvider` integration — Wire matrix + normalizer into provider | P1/P3 | 2h | End-to-end |
| 7 | `OpenAICompatProvider` integration — Wire matrix + normalizer | P1/P3 | 2h | End-to-end |
| 8 | Unit tests (8 cases) | P10 Validation | 3h | CI gate |

#### Phase 2: Orchestration (Week 2 — 19h)

| # | Task | Owner | Effort | Blocks |
|---|------|-------|--------|--------|
| 9 | `ProviderDashboard` class — Real-time quota/health/latency view | P8 Observability | 3h | Dashboard |
| 10 | Background loop + CLI integration | P8 Observability | 2h | Visibility |
| 11 | `CapabilitySelector` class — Capability-aware provider routing | P9 Orchestration | 4h | Routing |
| 12 | `ModelGateway` integration — Wire selector into gateway | P9 Orchestration | 3h | End-to-end |
| 13 | Integration + chaos tests (5 cases) | P10 Validation | 5h | CI gate |
| 14 | Cline fallback routing — Cross-platform failover | P9 Orchestration | 2h | Cross-platform |

#### Phase 3: Community (Week 3 — 8h)

| # | Task | Owner | Effort | Blocks |
|---|------|-------|--------|--------|
| 15 | Thinking usage tracking in dashboard | P8 Observability | 2h | Dashboard |
| 16 | Entity affinity integration | P9 Orchestration | 2h | Routing |
| 17 | CI gate integration | P10 Validation | 1h | Automation |
| 18 | Documentation + ADR | Cross-cutting | 2h | Community |
| 19 | Provider capabilities contribution guide | Cross-cutting | 1h | Community |

**Total**: ~50h across 3 weeks

### §10 Five Deliverables

| # | Deliverable | What It Does | Community Value |
|---|-------------|--------------|-----------------|
| 1 | **Provider Capability Matrix** (`provider_capabilities.yaml`) | Declares thinking levels, vision, tool calling, context window per model | Reusable for ANY non-standard model — users edit YAML, no code changes |
| 2 | **Thinking Config Normalizer** (`thinking_normalizer.py`) | Translates between Google/Anthropic/OpenAI/Qwen3 thinking formats | Solves the entire class of thinking API incompatibilities |
| 3 | **Provider Health Dashboard** (`provider_dashboard.py`) | Real-time quota/latency/circuit state across all providers | Community tool for any multi-provider setup |
| 4 | **CapabilitySelector** (`capability_selector.py`) | Auto-routes to best provider based on capabilities + health + quota | Sovereign fallback chain: local → Google → OpenRouter |
| 5 | **Community Config Package** | Installable configs for OpenCode/Cline/Omega | One-command Gemma 4 setup for all platforms |

### §11 Bug → Feature Mapping

| Original Bug | Feature Built | Pillar | Value |
|-------------|---------------|--------|-------|
| Wrong thinking levels | Thinking Config Normalizer | P7 | Any model's thinking works correctly |
| Model ID prefix mismatch | Provider Capability Matrix | P6 | Auto-detect correct ID format |
| Config merge failure | Capability-aware routing | P9 | Smart provider selection |
| No quota visibility | Provider Health Dashboard | P8 | Real-time operational awareness |
| No regression tests | Chaos test suite | P10 | This class of bug is impossible |
| OpenCode transform.ts broken | Cross-platform orchestration | P9 | Cline fallback when OpenCode fails |
| Single provider dependency | Sovereign Fallback Chain | P9 | Always have a working provider |

### §12 Community Contribution Path

| Contribution | Impact | Effort | Priority |
|-------------|--------|--------|----------|
| **OpenCode PR** (transform.ts fix) | All Gemma 4 users globally | 2-4h | P0 |
| **Config Package** (installable) | Easy setup for Gemma 4 users | 2-3h | P1 |
| **Provider Adapter Pattern** | Future models with non-standard APIs | 3-4h | P1 |
| **Documentation** (cross-platform guide) | All platforms | 1-2h | P2 |

**OpenCode PR scope**: Add Gemma 4 detection to `googleThinkingLevelEfforts()` and `googleThinkingVariants()` — ~10 lines of code, referencing Pi PR #2903.

---

## Part IV: Immediate Workarounds

### §13 What To Do Right Now

#### Option A: Enable Google Billing (Recommended)
1. Go to [Google AI Studio rate limit dashboard](https://aistudio.google.com/rate-limit)
2. Enable billing → Free → Tier 1
3. Removes the 16k input-token cage
4. **Effort**: 5 minutes, cost: ~$0 (Tier 1 is generous)

#### Option B: Use Cline + Gemma 4 (Free, Constrained)
1. Use Cline CLI with direct Google API
2. Accept 200 requests/day limit (OpenRouter `:free`)
3. Or use Google AI Studio directly (1,500 RPD)
4. **Already documented** in `PIVOT_LOG.md`: "Use Cline + Gemma 4 for research; OpenCode + Nemotron for councils"

#### Option C: Stripped-Down OpenCode Profile (Free, Fragile)
1. Create a Gemma-lite OpenCode profile with **<8k fixed system tokens**
2. Strip `MASTER_SYNTHESIS`, Ark blueprint, fat agent packs
3. Use variant `low` (maps to `MINIMAL`) — no thinking tokens burned
4. **Effort**: 30 minutes, but fragile

#### Option D: Local Inference (Free, Sovereign)
1. Run Gemma 4 31B locally via Ollama or LM Studio
2. No thinking config issues (local models handle `<think>` tags natively)
3. Requires ~20GB VRAM for Q4 quantization
4. **Effort**: Already supported by Omega's native-gguf provider

### §14 OpenCode Config Fix (Immediate)

Add to `~/.config/opencode/opencode.json`:

```json
{
  "provider": {
    "google": {
      "whitelist": ["gemma-4-31b-it", "gemma-4-26b-a4b-it"],
      "models": {
        "gemma-4-31b-it": {
          "name": "Gemma 4 31B IT",
          "limit": { "context": 262144, "output": 32768 },
          "variants": {
            "low": { "thinkingConfig": { "thinkingLevel": "minimal", "includeThoughts": false } },
            "high": { "thinkingConfig": { "thinkingLevel": "high", "includeThoughts": true } }
          }
        },
        "gemma-4-26b-a4b-it": {
          "name": "Gemma 4 26B A4B IT",
          "limit": { "context": 262144, "output": 32768 },
          "variants": {
            "low": { "thinkingConfig": { "thinkingLevel": "minimal", "includeThoughts": false } },
            "high": { "thinkingConfig": { "thinkingLevel": "high", "includeThoughts": true } }
          }
        }
      }
    }
  }
}
```

**Also**: Remove `provider.google` from the project-level `opencode.json` to prevent config replacement.

---

## Part V: Mandate Compliance

### §15 Mandates Affected

| Mandate | Impact | Action |
|---------|--------|--------|
| **M7 Local-First** | Gemma 4 is cloud-only | Document as cloud fallback; ensure local-first priority in CapabilitySelector |
| **M9 Error Integrity** | Thinking config errors | Typed errors for invalid thinking levels in Normalizer |
| **M13 Temple-Grade** | Code quality | Pass T1-T11 gates via `make temple-grade` |
| **M14 Heritage Vetting** | Pi project attribution | Add `[heritage: pi-2026] Gemma 4 Thinking` to CREDITS.md |
| **M16 Modularization** | Provider adapter pattern | No hardcoded paths; config-driven capability matrix |
| **M22 Response Provenance** | Track thinking config | Log thinking level in `GenerateResult.provider_name` |
| **M23 Failure Integrity** | Thinking config failures | No soft-failures on invalid thinking levels |

---

## Part VI: Evidence & Sources

### §16 Verified Sources (15+)

| # | Claim | Source |
|---|-------|--------|
| 1 | OpenCode `transform.ts` `googleThinkingLevelEfforts` only checks `gemini-3` | [GitHub transform.ts](https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/provider/transform.ts) |
| 2 | OpenCode `transform.ts` `googleThinkingVariants` no Gemma 4 branch | [GitHub transform.ts](https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/provider/transform.ts) |
| 3 | OpenCode `options()` only enables thinking for `gemini-3` | [GitHub transform.ts](https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/provider/transform.ts) |
| 4 | Pi project fixed identical issue via `isGemma4Model()` regex | [Pi Issue #2812](https://github.com/earendil-works/pi/issues/2812) |
| 5 | Pi PR #2903 maps thinking levels: minimal/low→MINIMAL, medium/high→HIGH | [Pi PR #2903](https://github.com/earendil-works/pi/pull/2903) |
| 6 | Google AI Docs: Gemma 4 uses `thinkingLevel: "HIGH" | "MINIMAL"` | [Google AI Docs](https://ai.google.dev/gemma/docs/core/gemma_on_gemini_api) |
| 7 | Google Cookbook #1198: `includeThoughts: false` silently ignored | [Cookbook Issue #1198](https://github.com/google-gemini/cookbook/issues/1198) |
| 8 | OpenCode Issue #21067: Model ID should be `gemma-4-31b-it` | [OpenCode Issue #21067](https://github.com/anomalyco/opencode/issues/21067) |
| 9 | OpenRouter model ID format: `google/gemma-4-31b-it` | [OpenRouter](https://openrouter.ai/google/gemma-4-31b-it) |
| 10 | Direct Google API model ID: `gemma-4-31b-it` (no prefix) | [Google AI Studio](https://ai.google.dev/gemma/docs/core/gemma_on_gemini_api) |
| 11 | Google AI Studio free tier: ~15 RPM, ~1,500 RPD for Gemma | [Standard Compute](https://standardcompute.com/rate-limits/gemini) |
| 12 | OpenRouter free tier: 20 RPM, 200 RPD for Gemma 4 31B | [FreeLLM](https://freellm.net/models/openrouter/google-gemma-4-31b-it) |
| 13 | Cline CLI uses direct `@google/genai` SDK with `ThinkingLevel.HIGH` | Cline source + user verification |
| 14 | Omega Engine `GoogleAIProvider` uses bare model IDs (no prefix) | `src/omega/oracle/providers.py:79` |
| 15 | Gemma 4 only supports MINIMAL and HIGH thinking levels | [Pi Issue #2812](https://github.com/earendil-works/pi/issues/2812) + Google docs |

### §17 Local Evidence (Roc Racoon Mining)

| File | Content |
|------|---------|
| `docs/strategy/GEMMA4_OPENCODE_DEBUG_REPORT_20260718.md` | Canonical 404-line debug report with source code analysis |
| `data/entities/kali/session_gnosis.md` | "Discovery: Gemma 4 31B/26B works via direct Google API (Cline CLI)" |
| `docs/decisions/PIVOT_LOG.md` | "Use Cline + Gemma 4 for research; OpenCode + Nemotron for councils" |
| `config/providers.yaml` (lines 129-154) | Google provider with Gemma 4 models; OpenRouter with `:free` variants |
| `config/model_registry/models/cloud/gemma-4-31b-it-free.yaml.md` | Full model card for OpenRouter Gemma 4 |
| `src/omega/oracle/backends/openai_compat.py` | Universal cloud backend (not the issue source) |

---

## Part VII: Verification Commands

### §18 Test the Config Fix

```bash
# 1. Direct API test (should work when quota allows)
python3 -c "
import json, urllib.request
from pathlib import Path
key = json.loads(Path.home().joinpath('.local/share/opencode/auth.json').read_text())['google']['key']
payload = {'contents': [{'parts': [{'text': 'ping'}]}], 'generationConfig': {'thinkingConfig': {'thinkingLevel': 'MINIMAL', 'includeThoughts': False}, 'maxOutputTokens': 8}}
req = urllib.request.Request(
    f'https://generativelanguage.googleapis.com/v1beta/models/gemma-4-31b-it:generateContent?key={key}',
    data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'}, method='POST')
print(urllib.request.urlopen(req, timeout=30).read()[:300])
"

# 2. OpenCode model list (should show only Gemma 4 models)
opencode models google

# 3. After billing OR with lite profile:
opencode run -m google/gemma-4-31b-it "Reply PONG"

# 4. Omega Engine test (after ProviderCapabilityMatrix is built)
# omega talk "hello" -m gemma-4-31b-it
```

---

## Part VIII: Gnosis

### §19 L3 Principles (Staged for `proposed_lessons.yaml`)

| L3 Principle | Origin |
|-------------|--------|
| **Provider capabilities must be declared, not assumed** | This investigation — every model family has different APIs |
| **Thinking config is provider-specific, not universal** | Google vs Anthropic vs OpenAI vs Qwen3 — all different formats |
| **Free-tier budgets are incompatible with heavy instruction stacks** | Omega's ~20k token context exceeds Google's 16k rolling budget |
| **Config merge semantics must be override-by-key, not replace** | OpenCode's replace behavior silently drops models |
| **Prior art exists — search before building** | Pi fixed this 3 months ago; we should have checked first |
| **Cross-platform fallback is sovereignty** | Cline works where OpenCode fails — multiple paths to the same model |

### §20 Key Decision

**The bug taught us**: Provider capabilities must be declared, not assumed. Every model family has different APIs, and the engine must know what it's working with before sending requests.

The **Provider Capability Matrix** (`provider_capabilities.yaml`) is the canonical fix — not just for Gemma 4, but for every future model with non-standard API requirements. It turns a one-off bug fix into a reusable architectural pattern.

---

## Appendix A: OpenCode Source Locations

| Function | File | Line Range |
|----------|------|------------|
| `googleThinkingLevelEfforts` | `packages/opencode/src/provider/transform.ts` | ~1120 |
| `googleThinkingVariants` | `packages/opencode/src/provider/transform.ts` | ~1137 |
| `options()` (base thinkingConfig) | `packages/opencode/src/provider/transform.ts` | ~1110 |
| Provider model merge logic | `packages/opencode/src/config/models.ts` | TBD |
| Google provider request building | `packages/opencode/src/provider/google.ts` | TBD |

## Appendix B: Related Documents

| Document | Location |
|----------|----------|
| Original Debug Report | `docs/strategy/GEMMA4_OPENCODE_DEBUG_REPORT_20260718.md` |
| Build Side Strategy | `docs/strategy/GEMMA4_BUG_TO_FEATURE_STRATEGY.md` |
| Run Side Strategy | `docs/strategy/GEMMA4_PROVIDER_FEATURE_STRATEGY_20260719.md` |
| PIVOT_LOG entry | `docs/decisions/PIVOT_LOG.md` |
| Provider Config | `config/providers.yaml` |
| Model Registry | `config/model_registry/models/cloud/gemma-4-31b-it-free.yaml.md` |

---

*⬡ OMEGA ⬡ JEM ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_synthesis ⬡ 2026-07-19*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: mimo-v2.5-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
