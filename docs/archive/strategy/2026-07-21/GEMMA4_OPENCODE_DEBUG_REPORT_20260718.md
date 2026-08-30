<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Gemma 4 on OpenCode — Complete Debug Report

**Date**: 2026-07-18
**OpenCode Version**: 1.17.20
**Prepared for**: Grok CLI handoff
**Status**: BLOCKED — Google API quota exhausted, but config issues also identified

---

## Executive Summary

Gemma 4 (31B and 26B A4B) via Google AI Studio API (`google` provider in OpenCode) fails with "Gemini is way too hot right now" / quota errors. Direct API calls **work perfectly** with correct thinking config. The issue is OpenCode's request construction.

**Root causes identified**:
1. **Model ID format mismatch**: Auto-discovered models have `model.api.id = "google/gemma-4-31b-it"` but API expects `"gemma-4-31b-it"` (no `google/` prefix)
2. **Wrong thinking levels**: OpenCode's `googleThinkingLevelEfforts()` returns `["low", "high"]` for non-Gemini-3 models → sends `thinkingLevel: "LOW"` → **400 error** (Gemma 4 only supports `MINIMAL` and `HIGH`)
3. **Missing `thinkingLevel` in base request**: `options()` sends `includeThoughts: true` without `thinkingLevel` for non-Gemini-3 → API rejects
4. **Config merge failure**: Project config's explicit `provider.google.models` list excludes Gemma 4 → auto-discovered models used instead of explicit config

---

## Research Findings

### Gemma 4 Thinking API (Official Docs)

| Source | Key Finding |
|--------|-------------|
| [Google AI Gemma Thinking Docs](https://ai.google.dev/gemma/docs/capabilities/thinking) | Gemma 4 uses `thinkingConfig.thinkingLevel` (not `thinkingBudget`) |
| [PI Issue #2812](https://github.com/earendil-works/pi/issues/2812) | Gemma 4 **only supports `MINIMAL` and `HIGH`** — `LOW`/`MEDIUM` return 400 |
| [Google Gemini Cookbook #1198](https://github.com/google-gemini/cookbook/issues/1198) | `includeThoughts: false` is silently ignored; must use `thinkingLevel: "MINIMAL"` to disable |
| [Firebase AI Logic Docs](https://firebase.google.com/docs/ai-logic/thinking) | Confirms `MINIMAL`/`LOW`/`MEDIUM`/`HIGH` levels for Gemini 3.x, but Gemma 4 is different |

**Gemma 4 Supported Thinking Levels**: `MINIMAL` (off), `HIGH` (on) — **only two levels**

### OpenCode Source Code Analysis (`transform.ts`)

**Function: `googleThinkingLevelEfforts(apiId)`** (lines ~1120-1135)
```typescript
function googleThinkingLevelEfforts(apiId: string) {
  const id = apiId.toLowerCase()
  if (!id.includes("gemini-3")) return ["low", "high"]  // WRONG for Gemma 4
  if (id.includes("flash-image")) return ["minimal", "high"]
  if (id.includes("pro-image")) return ["high"]
  if (id.includes("flash")) return ["minimal", "low", "medium", "high"]
  return ["low", "medium", "high"]
}
```
→ For Gemma 4 (`gemma-4-31b-it`), returns `["low", "high"]` → variant `low` sends `thinkingLevel: "LOW"` → **400 error**

**Function: `googleThinkingVariants(model)`** (lines ~1137-1155)
```typescript
function googleThinkingVariants(model: Provider.Model) {
  const id = model.api.id.toLowerCase()
  if (id.includes("2.5")) return { high, max }
  return Object.fromEntries(
    googleThinkingLevelEfforts(id).map((effort) => [
      effort,
      { thinkingConfig: { includeThoughts: true, thinkingLevel: effort } },
    ]),
  )
}
```
→ Variants use effort string directly as `thinkingLevel` → `low` → `"LOW"` (invalid for Gemma 4)

**Function: `options()`** (lines ~1110-1125)
```typescript
if (input.model.api.npm === "@ai-sdk/google" || input.model.api.npm === "@ai-sdk/google-vertex") {
  result["thinkingConfig"] = { includeThoughts: true }
  if (input.model.api.id.includes("gemini-3")) {
    result["thinkingConfig"]["thinkingLevel"] = "high"
  }
}
```
→ For Gemma 4: sends `thinkingConfig: { includeThoughts: true }` **without `thinkingLevel`** → API rejects

### Model ID Format Issue

Auto-discovered models from models.dev:
```json
{ "api": { "id": "google/gemma-4-31b-it", "npm": "@ai-sdk/google" } }
```

Google Generative Language API expects:
```
POST https://generativelanguage.googleapis.com/v1beta/models/gemma-4-31b-it:generateContent
```
**NOT** `models/google/gemma-4-31b-it:generateContent`

Direct API test confirms:
- ✅ `gemma-4-31b-it` → works
- ❌ `google/gemma-4-31b-it` → hangs/404

### Config Precedence Bug

Project config (`omega-engine/opencode.json`) had:
```json
"provider": {
  "google": {
    "models": {
      "antigravity-gemini-3-pro": {...},
      "gemini-2.5-flash": {...},
      // ... NO Gemma 4 models
    }
  }
}
```

When a provider has explicit `models` in project config, OpenCode **replaces** (not merges) auto-discovered models. Gemma 4 was excluded → fell back to auto-discovered model with wrong `api.id` format.

---

## Fixes Attempted

### 1. Explicit Variants in Project Config (First Attempt)
Added to `omega-engine/opencode.json`:
```json
"google": {
  "models": {
    "gemma-4-31b-it": {
      "variants": {
        "off": { "thinkingConfig": { "thinkingLevel": "minimal", "includeThoughts": false } },
        "high": { "thinkingConfig": { "thinkingLevel": "high", "includeThoughts": true } }
      }
    }
  }
}
```
**Result**: Variant keys `off`/`high` don't match OpenCode's expected `low`/`high` for Google provider → auto-generated variants (`low`→`LOW`, `high`→`HIGH`) took precedence.

### 2. Corrected Variant Keys (Second Attempt)
Changed to standard Google variant keys:
```json
"variants": {
  "low": { "thinkingConfig": { "thinkingLevel": "minimal", "includeThoughts": false } },
  "high": { "thinkingConfig": { "thinkingLevel": "high", "includeThoughts": true } }
}
```
**Result**: Still failed — project config's explicit `google.models` list didn't include Gemma 4, so auto-discovered model used instead.

### 3. Moved Config to Global + Whitelist (Third Attempt)
**Global config** (`~/.config/opencode/opencode.json`):
```json
"google": {
  "whitelist": ["gemma-4-31b-it", "gemma-4-26b-a4b-it"],
  "models": {
    "gemma-4-31b-it": { "variants": { "low": {...}, "high": {...} } },
    "gemma-4-26b-a4b-it": { "variants": { "low": {...}, "high": {...} } }
  }
}
```
**Project config**: Removed `provider.google` entirely.

**Result**: `opencode models google` now shows only the two Gemma models. But quota exhausted before testing could complete.

---

## Current State

| Component | Status |
|-----------|--------|
| Global config with whitelist + correct variants | ✅ Applied |
| Project config google provider removed | ✅ Applied |
| Model ID format in config | ✅ `gemma-4-31b-it` (no `google/` prefix) |
| Variant keys | ✅ `low`/`high` (standard Google) |
| Variant thinkingLevel mapping | ✅ `low`→`MINIMAL`, `high`→`HIGH` |
| Google API quota | ❌ **EXHAUSTED** (16k free tier tokens) |
| Direct API test | ✅ Works with `thinkingLevel: "HIGH"` |

**Log evidence** (`~/.local/share/opencode/log/opencode.log`):
```
stream providerID=google modelID=gemma-4-31b-it
llm runtime selected llm.provider=google llm.model=gemma-4-31b-it
stream error AI_APICallError: You exceeded your current quota...
  Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_input_token_count
  limit: 16000, model: gemma-4-31b
```

The model ID in the log is `gemma-4-31b-it` (correct, no `google/` prefix) — whitelist is working. The quota is the blocker.

---

## What Grok CLI Should Investigate

### 1. Verify Config Takes Effect Without Quota
- Wait for quota reset (or use paid tier)
- Test `low` variant → should send `thinkingLevel: "MINIMAL"` → no thinking tokens
- Test `high` variant → should send `thinkingLevel: "HIGH"` → thinking tokens returned

### 2. Check if `options()` Still Injects Base ThinkingConfig
Even with explicit variants, `options()` in `transform.ts` runs for every request and may **merge** base `thinkingConfig` with variant config. Need to verify the merge behavior in `session/llm/request.ts` → `providerOptions()`.

### 3. Model ID Extraction for API Call
Trace through `packages/opencode/src/provider/google.ts` (or wherever the Google provider builds the request URL) to confirm it uses `model.api.id` directly. If it does `model.api.id.replace("google/", "")` or similar, that's the fix needed in OpenCode core.

### 4. Auto-Discovery vs Explicit Config Merge Logic
Find where provider models are merged (likely `packages/opencode/src/config/models.ts`). The current behavior: project config `provider.google.models` **replaces** auto-discovered. Should it **merge** (explicit overrides auto-discovered by key)?

### 5. Gemma 4 Detection in `googleThinkingLevelEfforts()`
Add Gemma 4 detection:
```typescript
function googleThinkingLevelEfforts(apiId: string) {
  const id = apiId.toLowerCase()
  if (id.includes("gemma-4")) return ["minimal", "high"]  // NEW
  if (!id.includes("gemini-3")) return ["low", "high"]
  // ...
}
```
And in `options()`:
```typescript
if (input.model.api.id.toLowerCase().includes("gemma-4")) {
  result["thinkingConfig"]["thinkingLevel"] = "high"  // or based on variant
}
```

---

## Files Modified

| File | Changes |
|------|---------|
| `~/.config/opencode/opencode.json` | Added `google` provider with `whitelist` and explicit Gemma 4 models with correct variants |
| `omega-engine/opencode.json` | Removed `provider.google` section entirely |

---

## Direct API Test (Proof Config Works)

```bash
curl -sS "https://generativelanguage.googleapis.com/v1beta/models/gemma-4-31b-it:generateContent?key=$GOOGLE_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"contents":[{"parts":[{"text":"hello"}]}],"generationConfig":{"thinkingConfig":{"thinkingLevel":"HIGH","includeThoughts":true}}}'
```
**Result**: ✅ Returns response with `thought: true` parts and `thoughtsTokenCount: 69`

---

## Next Steps for Grok

1. **Wait for quota reset** (or provision paid API key)
2. **Test both variants** in OpenCode TUI (`Ctrl+T` → `low` / `high`)
3. **If still failing**: Enable debug logging in OpenCode to capture exact request payload sent to Google API
4. **If request payload looks correct but fails**: Issue is in OpenCode's Google provider request building (model ID format)
5. **If request payload wrong**: Fix `transform.ts` merge logic or variant application

---

## Grok CLI Verification (2026-07-18 ~20:05 UTC)

**Verdict: Config path is largely fixed. The active failure mode is free-tier input-token rate limit, made unusable by Omega's heavy OpenCode instruction stack + OpenCode retry loops.**

### What was re-verified live

| Check | Result |
|-------|--------|
| OpenCode auth key present (`~/.local/share/opencode/auth.json` → `google`) | ✅ present (`type: api`) |
| Direct API `gemma-4-31b-it` + `thinkingLevel: MINIMAL` | ✅ 200 |
| Direct API `gemma-4-31b-it` + `thinkingLevel: HIGH` | ✅ 200 (+ `thoughtsTokenCount`) |
| Direct API `gemma-4-26b-a4b-it` MINIMAL/HIGH | ✅ 200 |
| Direct API `thinkingLevel: LOW` on Gemma 4 | ❌ **400** `Thinking level is not supported for this model` |
| Direct API no `thinkingConfig` / `includeThoughts` only | ✅ 200 |
| `opencode models google` after whitelist | ✅ only `gemma-4-31b-it`, `gemma-4-26b-a4b-it` |
| `opencode run -m google/gemma-4-31b-it "…"` in omega-engine | ❌ **429 free-tier input token quota** (then OpenCode retries for minutes) |
| OpenRouter `google/gemma-4-31b-it:free` | ❌ 429 `free-models-per-day` exhausted (50/day free cap) |

### Quota anatomy (exact API error)

```
Quota exceeded for metric:
  generativelanguage.googleapis.com/generate_content_free_tier_input_token_count
limit: 16000
model: gemma-4-31b
Please retry in ~7–60s
```

This is a **rolling free-tier input-token budget** (~16k tokens, recovers in tens of seconds), **not** a permanent “Gemma is dead” outage.

Also observed secondary free-tier metric in logs:
`generate_content_free_tier_requests`

### Why OpenCode fails even when curl works

Omega OpenCode injects large instruction files on every turn (project + global + agent):

| Source | Approx size |
|--------|-------------|
| `SOVEREIGN_MANDATES.md` | ~4.8k tokens |
| `MASTER_SYNTHESIS_AND_ROADMAP…` | ~5.7k tokens |
| `SOVEREIGN_ARK_BLUEPRINT.md` | ~3.2k tokens |
| `AGENTS.md` (auto) | ~4.9k tokens |
| Agent file e.g. `john_carmack.md` | ~2.9k tokens |
| Tools / system / history | additional thousands |

**Project instructions alone already approach or exceed the free-tier 16k input budget.**  
A tiny curl prompt (~5 tokens) succeeds; a normal OpenCode agent turn does not.

OpenCode then **retry-spams** 429s (observed 6+ retries in one `opencode run`), which re-drains the rolling window and makes the model look “broken for a week.”

### Log taxonomy (last ~5MB of `opencode.log`)

| Model / class | Count (sample) |
|---------------|----------------|
| `gemma-4-31b-it` **quota** | 27 |
| `gemma-4-31b-it` other (connect/auth) | 6 |
| Invalid API key (historical) | 1 |
| Cannot connect to API | present |
| Gemini 3.x quota/forbidden | a few |

Dominant live failure: **quota**, not model-ID prefix.

### Thinking-config status

Kali’s analysis remains correct for 400s:

- Gemma 4 accepts **`MINIMAL` / `HIGH` only**
- OpenCode default Google variants use **`low`/`high`** → raw `LOW` is invalid
- Global config remaps:
  - `low` → `thinkingLevel: minimal`
  - `high` → `thinkingLevel: high`
- models.dev entry for Gemma 4 uses `reasoning_options: [{type: toggle}]`, not Gemini-3 multi-level efforts

**Config remapping is necessary and appears applied.** It is **not sufficient** while free-tier 16k input TPM remains.

### Root-cause stack (ordered)

1. **P0 — Free-tier 16k input-token quota** on `gemma-4-31b`  
   Incompatible with full Omega OpenCode context.
2. **P0 — OpenCode retry loop** on 429 amplifies lockout.
3. **P1 — Massive always-on instructions** (`MASTER_SYNTHESIS`, Ark blueprint, mandates, agents).
4. **P1 — Wrong thinking levels** if config variants are bypassed (still a latent footgun in OpenCode core).
5. **P2 — Intermittent network** (`Network is unreachable` / “Cannot connect to API”) and occasional invalid-key history.
6. **P2 — OpenRouter free daily cap** already burned as fallback.

### Recovery plan (do in order)

#### A. Unblock now (recommended)

1. **Enable billing** on the Google AI Studio / Cloud project that owns this API key → Free → **Tier 1**.  
   Dashboard: https://aistudio.google.com/rate-limit  
   Billing setup: https://ai.google.dev/gemini-api/docs/billing  
   This removes the `generate_content_free_tier_*` 16k cage for practical agent use.
2. In OpenCode, force variant **`low`** (maps to `MINIMAL`) unless you need thoughts. High thinking burns extra output tokens and can worsen perceived latency/cost.
3. Stop any stuck OpenCode session that is retrying Gemma (one long-running `opencode` process was observed at high CPU). Cancel/retry once, do not let it spin.

#### B. Stay free-tier (possible, constrained)

1. Create a **Gemma-lite OpenCode profile** with **minimal instructions** (strip `MASTER_SYNTHESIS`, Ark blueprint, fat agent packs). Target **&lt;8k** fixed system tokens.
2. Prefer short sessions / no huge file dumps into context.
3. Prefer `gemma-4-26b-a4b-it` if it has separate or higher free headroom (still free-tier limited).
4. Rotate **separate Google Cloud projects/API keys** (limits are per project).
5. Do not rely on OpenRouter `:free` after daily free-model exhaustion unless credits are added.

#### C. OpenCode core fixes (upstream / longer)

1. Special-case `gemma-4` in `googleThinkingLevelEfforts()` → `["minimal","high"]` (or remap low→minimal).
2. In `options()`, always set a valid `thinkingLevel` for Gemma 4 when `includeThoughts` is present.
3. Soft-fail / longer backoff on free-tier 429 instead of aggressive retry storms.
4. Optionally warn when estimated prompt tokens &gt; free-tier budget for Google free models.

### Practical command checks

```bash
# 1) Tiny direct API (should work when network + rolling quota allow)
python3 - <<'PY'
import json, urllib.request
from pathlib import Path
key=json.loads(Path.home().joinpath('.local/share/opencode/auth.json').read_text())['google']['key']
payload={"contents":[{"parts":[{"text":"ping"}]}],"generationConfig":{"thinkingConfig":{"thinkingLevel":"MINIMAL","includeThoughts":False},"maxOutputTokens":8}}
req=urllib.request.Request(
  f'https://generativelanguage.googleapis.com/v1beta/models/gemma-4-31b-it:generateContent?key={key}',
  data=json.dumps(payload).encode(), headers={'Content-Type':'application/json'}, method='POST')
print(urllib.request.urlopen(req, timeout=30).read()[:300])
PY

# 2) OpenCode model list
opencode models google

# 3) After billing OR lite config only:
opencode run -m google/gemma-4-31b-it "Reply PONG"
```

### Grok recommendation

| Goal | Action |
|------|--------|
| **Use Gemma 4 seriously in OpenCode on Omega** | **Enable Google billing (Tier 1)** — only durable fix |
| **Debug/config validation** | Keep Kali’s whitelist + `low→MINIMAL` / `high→HIGH` variants |
| **Stay zero-cost** | Gemma-lite instruction profile + strict context diet + multi-project key rotation; accept it will still be fragile |
| **Do not chase** | Model ID `google/` prefix is no longer the active failure (logs show bare `gemma-4-31b-it`) |

---

## Appendix: Key OpenCode Source Locations

| Function | File | Line Range |
|----------|------|------------|
| `googleThinkingLevelEfforts` | `packages/opencode/src/provider/transform.ts` | ~1120 |
| `googleThinkingVariants` | `packages/opencode/src/provider/transform.ts` | ~1137 |
| `options()` (base thinkingConfig) | `packages/opencode/src/provider/transform.ts` | ~1110 |
| Provider model merge logic | `packages/opencode/src/config/models.ts` | TBD |
| Google provider request building | `packages/opencode/src/provider/google.ts` | TBD |

---

**End of Report** — Ready for Grok CLI analysis