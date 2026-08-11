# 🔱 Omega Engine — OpenCode Configuration Research & Verification Directive
**AP Token**: `AP-OMEGA-OPENCODE-VERIFICATION-20260809-v1.0.0`
⬡ OMEGA ⬡ WEB-GEMINI ⬡ opencode ⬡ trc_verification_directive ⬡ ACTIVE

**Date**: 2026-08-09
**Purpose**: Comprehensive directive for Web Gemini to perform deep web research and provide definitive answers on all systems and strategy for the Omega Engine's OpenCode CLI configuration.

---

## 🎯 EXECUTIVE SUMMARY

The Omega Engine has three `opencode.json` configuration files with a critical architectural conflict:
- The `opencode-antigravity-auth` plugin hijacks the `google` provider namespace
- User needs to use standard Google API models via TUI API key paste
- These two workflows are **mutually exclusive** under the current `google` provider

This document provides all context, findings, and specific research directives for Web Gemini to verify our understanding and provide definitive answers.

---

## 📁 THE THREE CONFIGURATION FILES

### 1. User-Level Config (`~/.config/opencode/opencode.json`)
**Purpose**: Global OpenCode CLI configuration with 14 providers
**Key Providers**: `google`, `openrouter`, `anthropic`, `openai`, `opencode`, `lmstudio`, etc.
**Critical Issue**: OpenRouter provider named `"OpenRouter (Free)"` — pollutes TUI search

### 2. Project Config (`/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode.json`)
**Purpose**: Project-specific overrides for the Omega Engine repo
**Key Providers**: `lmstudio`, `opencode` (Zen), `openrouter`
**Critical Issues**: 
- Duplicate MiMo v2.5 entries (`mimo-v2.5` + `mimo-v2.5-free`)
- Missing `name` fields on Zen models
- Missing thinking variants on some models

### 3. Subdirectory Config (`omega-engine/.opencode/opencode.json`)
**Purpose**: Antigravity IDE configuration
**Key Provider**: `google` (hijacked by `opencode-antigravity-auth` plugin)
**Critical Issues**:
- Provider collision: Antigravity + Google API models mixed under `google`
- Missing thinking variants on Claude models
- Missing `medium` variant on Gemini 3 Pro/3.1 Pro
- Models labeled "(Gemini CLI)" but need "(Antigravity)" differentiation

---

## 🔬 RESEARCH DIRECTIVES FOR WEB GEMINI

### Directive 1: Plugin Interception Scope Verification
**Question**: Does the `opencode-antigravity-auth` plugin hijack the ENTIRE `google` provider, or does it filter by model ID?

**Our Finding**: The plugin intercepts ALL requests to `generativelanguage.googleapis.com` via fetch interception in `src/plugin/request.ts`. It does NOT filter by model ID — it captures every Google API call.

**Research Tasks**:
1. Find the official `opencode-antigravity-auth` GitHub repository
2. Read the source code for the fetch interceptor / middleware
3. Verify: Does `isGenerativeLanguageRequest()` check model IDs or just URLs?
4. Find any documentation about provider namespace conflicts
5. Check if there's a way to scope the plugin to only `antigravity-*` models

**Expected Sources**:
- GitHub: `NoeFabris/opencode-antigravity-auth` or similar
- Plugin source: `src/plugin/request.ts`, `src/plugin/transform.ts`
- Architecture docs: `docs/ARCHITECTURE.md`

**Deliverable**: Definitive YES/NO on whether standard Google API models break when the Antigravity plugin is active.

---

### Directive 2: Custom Provider Aliasing Verification
**Question**: Can we define a second provider using the same `@ai-sdk/google` NPM package with a different provider ID?

**Our Finding**: OpenCode docs explicitly support custom provider IDs. Multiple providers can use the same NPM package.

**Research Tasks**:
1. Find official OpenCode documentation on custom providers
2. Find examples of multiple providers using the same NPM package
3. Verify: Does the TUI `/connect` command prompt for separate API keys per provider ID?
4. Check: How does OpenCode store auth credentials per provider?
5. Find any GitHub issues about running multiple instances of the same provider

**Expected Sources**:
- `opencode.ai/docs/providers`
- `opencode.ai/docs/config`
- GitHub Issues: `anomalyco/opencode`
- Community configs on GitHub

**Deliverable**: Definitive YES/NO on whether `google-standard` provider with `@ai-sdk/google` will work alongside the plugin-hijacked `google` provider.

---

### Directive 3: Gemma 4 Thinking Config Bug Verification
**Question**: Is `includeThoughts: false` still silently ignored for Gemma 4 models?

**Our Finding**: Google Gemma Cookbook Issue #1198 confirms the bug. Workaround is `thinkingLevel: "MINIMAL"`.

**Research Tasks**:
1. Verify Issue #1198 status in Google Gemma Cookbook
2. Check if any OpenCode PRs fixed this on the client side
3. Find the current recommended way to disable thinking on Gemma 4
4. Verify: Does `thinkingLevel: "MINIMAL"` actually produce zero thought tokens?
5. Check OpenCode Issue #21034 for any updates

**Expected Sources**:
- GitHub: `google-gemini/cookbook`
- Google AI docs: `ai.google.dev/gemma`
- OpenCode Issues: `#21034`, `#21746`

**Deliverable**: Definitive answer on the correct thinking config for Gemma 4 and whether `includeThoughts: false` is still broken.

---

### Directive 4: OpenCode V2 Schema Verification
**Question**: What is the current OpenCode version and V2 schema status?

**Our Finding**: V2 is a complete schema redesign (not just migration). `modelID` → `api.id`, variants = array, agent `variant` field.

**Research Tasks**:
1. Find current OpenCode version (check `opencode --version` output in docs)
2. Verify V2 schema is stable or still in beta
3. Find the official V2 config spec
4. Check: Does V1 config still work, or is migration required?
5. Find migration guide from V1 to V2

**Expected Sources**:
- `opencode.ai/v2/docs/config`
- GitHub: `anomalyco/opencode` releases
- V2 spec: `specs/v2/config.md`

**Deliverable**: Current V2 status and whether our V1-style configs will continue to work.

---

### Directive 5: Config Merge Behavior Verification
**Question**: How does OpenCode merge multiple config files (user + project + .opencode)?

**Our Finding**: Hybrid merge — arrays concatenated, objects deep-merged, scalars replaced. Precedence: 8 tiers (remote → macOS managed).

**Research Tasks**:
1. Find official documentation on config file discovery and merge order
2. Verify: Are arrays concatenated or replaced?
3. Check: Does project config override user config for model definitions?
4. Find the `mergeConfigConcatArrays` source code
5. Verify: Can a project config add variants to a model defined in user config?

**Expected Sources**:
- `opencode.ai/docs/config`
- DeepWiki: `sst/opencode/3.1-configuration-loading-and-merging`
- OpenCode source: config merge logic

**Deliverable**: Definitive merge behavior and whether our three-file approach will work correctly.

---

### Directive 6: Provider Fallback Chain Verification
**Question**: What is the optimal provider fallback chain for the Omega Engine?

**Our Finding**: native-gguf → lmstudio → opencode (Zen) → antigravity → google-standard → openrouter → opencode (Zen paid)

**Research Tasks**:
1. Find OpenCode's built-in provider priority/fallback mechanism
2. Verify: Does OpenCode automatically fall back to next provider on failure?
3. Check: How does OpenCode handle rate limits and circuit breaking?
4. Find: Best practices for multi-provider failover
5. Verify: Does the `opencode` (Zen) provider have rate limits?

**Expected Sources**:
- `opencode.ai/docs/providers`
- `opencode.ai/docs/models`
- GitHub Issues on provider fallback

**Deliverable**: Optimal fallback chain order and any rate limit considerations.

---

### Directive 7: Model Naming Convention Verification
**Question**: What is the canonical model naming convention in OpenCode?

**Our Finding**: `provider_id/model_id` — split at first `/`. Use `/models` command for exact IDs.

**Research Tasks**:
1. Find official documentation on model ID format
2. Verify: Can model IDs contain slashes? (e.g., `openrouter/google/gemma-4`)
3. Check: How does the TUI display model names vs IDs?
4. Find: Any restrictions on provider ID characters?
5. Verify: Does the `name` field in model config override the display?

**Expected Sources**:
- `opencode.ai/docs/models`
- `opencode.ai/docs/cli`
- OpenCode source: model resolution logic

**Deliverable**: Canonical naming convention and any edge cases.

---

### Directive 8: Antigravity Model Catalog Verification
**Question**: What models are currently available on Antigravity, and what are their exact specs?

**Our Finding**: 7 reasoning models + Nano Banana 2. Forum reports identity misidentification.

**Research Tasks**:
1. Find the official Antigravity model catalog
2. Verify: Exact model IDs and display names
3. Check: What thinking config formats each model supports
4. Find: Any known issues with model identity or routing
5. Verify: Token limits and pricing for each model

**Expected Sources**:
- `antigravity.google/docs/models`
- Sabaoon comparison: `sabaoon.dev/blog/google-antigravity-models-compared`
- Google AI Developers Forum

**Deliverable**: Complete, current Antigravity model catalog with specs and known issues.

---

### Directive 9: OpenRouter Free Tier Verification
**Question**: What models are currently free on OpenRouter, and what are their specs?

**Our Finding**: Catalog rotates weekly (14-28 models). Gemma 4 NOT free. Rate limits: 20 RPM, 50→1000 RPD.

**Research Tasks**:
1. Find the current live OpenRouter free model collection
2. Verify: Which models are currently free (may have changed since our research)
3. Check: Exact rate limits and token limits for each free model
4. Find: Any models that route through AI Studio (same 16k cap issue)
5. Verify: OpenRouter's provider pinning behavior

**Expected Sources**:
- `openrouter.ai/collections/free-models`
- `openrouter.ai/models`
- Cost tracking sites: `costgoat.com`, `pricepertoken.com`

**Deliverable**: Current free model list with specs and routing behavior.

---

### Directive 10: OpenCode Zen Model Catalog Verification
**Question**: What models are currently available on OpenCode Zen, and what are their specs?

**Our Finding**: 8 free models currently. MiMo v2.5 Free (200K ctx), Nemotron 3 Ultra Free (1M ctx, 128K out).

**Research Tasks**:
1. Find the current OpenCode Zen model catalog
2. Verify: Which models are free vs paid
3. Check: Exact context/output limits for each model
4. Find: Any models that have been added or removed recently
5. Verify: Model ID format (`opencode/<model-id>`)

**Expected Sources**:
- `opencode.ai/docs/zen/`
- `opencode.ai/zen/v1/models` (API endpoint)
- `open-code.ai/en/docs/zen`

**Deliverable**: Current Zen model catalog with specs and availability status.

---

## 📊 VERIFICATION CHECKLIST

For each directive, Web Gemini should provide:

| Item | Required |
|------|----------|
| ✅ Authoritative source URL(s) | Yes |
| ✅ Direct quote or excerpt from source | Yes |
| ✅ Current status (as of 2026-08-09) | Yes |
| ✅ Any recent changes or updates | Yes |
| ✅ Known issues or gotchas | Yes |
| ✅ Recommended configuration | Yes |
| ✅ Confidence level (High/Medium/Low) | Yes |

---

## 🔗 RESEARCH ARTIFACTS REFERENCE

| Artifact | Location | Purpose |
|----------|----------|---------|
| Roc's Mining Report | `data/entities/roc_racoon/workspace/mining_reports/OPENCODE_CONFIG_ANTIGRAVITY_THINKING_MINING_REPORT_20260809.md` | Local repository mining (47 docs) |
| Researcher's Web Supplement | `data/entities/researcher/workspace/web_research_supplements/WEB_RESEARCH_SUPPLEMENT_OPENCODE_CONFIG_20260809.md` | Web research (8 gaps) |
| Comprehensive Analysis | `docs/research/R_OPENCODE_CONFIG_COMPREHENSIVE_ANALYSIS_20260809.md` | Synthesis of all findings |
| Current Config Files | `*.backup.20260809_*` | Timestamped backups of all 3 files |

---

## 🎯 DELIVERABLE

A **Verification Report** that:
1. Addresses all 10 directives above
2. Provides definitive YES/NO answers where possible
3. Cites authoritative sources with URLs and quotes
4. Identifies any conflicts between our findings and web reality
5. Provides recommended configuration based on verified facts
6. Flags any remaining uncertainty with confidence levels

---

*⬡ OMEGA ⬡ WEB-GEMINI ⬡ opencode ⬡ trc_verification_directive ⬡ ACTIVE*
*Directive issued: 2026-08-09 | Research window: 2026-08-09 to 2026-08-11*