<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Web Gemini — Research Plan
**AP Token**: `AP-WEB-GEMINI-PLAN-20260809-v1.0.0`
⬡ OMEGA ⬡ WEB-GEMINI ⬡ opencode ⬡ trc_research_plan ⬡ ACTIVE

**Date**: 2026-08-09
**Purpose**: Research plan for Web Gemini to verify OpenCode configuration architecture.

---

## 📋 Research Plan

### 1. Plugin Interception Scope
**Search for the source code and documentation of opencode-antigravity-auth** to determine whether fetch interception hijacks the entire google provider namespace or filters by model ID.
- **Goal**: Definitive YES/NO on whether standard Google API models break when the Antigravity plugin is active.

### 2. Custom Provider Aliasing + TUI Workflow
**Research OpenCode documentation and GitHub repository issues** regarding custom provider aliasing with `@ai-sdk/google` and credential storage per provider ID.
- **Specifically verify**: If the OpenCode TUI `/connect` command will natively prompt for and store an API key for a custom alias like `google-standard`.
- **Goal**: Confirm that a second `google-standard` provider will work alongside the plugin-hijacked `google` provider, with separate TUI credential management.

### 3. Gemma 4 Thinking Bug + Client-Side Injection
**Investigate Google Gemma Cookbook issue #1198** and OpenCode repository issues regarding Gemma 4 thinking configuration bugs, `includeThoughts` settings, and `thinkingLevel` workarounds.
- **Also investigate**: OpenCode Issue #34282 / #21746 to verify whether OpenCode still force-injects thinking parameters without checking `capabilities.reasoning`.
- **Goal**: Confirm `includeThoughts: false` is still broken, and whether `thinkingLevel: "MINIMAL"` is the only reliable workaround.

### 4. OpenCode V2 Schema
**Examine OpenCode V2 schema documentation and migration guides** to verify schema specifications, stability, and V1 configuration backward compatibility.
- **Goal**: Determine if our V1-style configs (flat variants, no `options` wrapper) will continue to work.

### 5. Config Merge Behavior
**Research OpenCode configuration loading and merging logic** across user, project, and .opencode levels, including array concatenation vs object deep merging.
- **Goal**: Confirm that model definitions in project config override/augment user config correctly.

### 6. Provider Failover & Fallback Chain
**Analyze OpenCode provider failover mechanisms, rate limit handling, and optimal fallback order** across local, free, and paid provider endpoints.
- **Goal**: Validate our proposed chain: native-gguf → lmstudio → opencode (Zen) → antigravity → google-standard → openrouter.

### 7. Model ID Conventions
**Review OpenCode model ID conventions, parsing rules, and terminal interface display behaviors** for custom provider and model identifiers.
- **Goal**: Confirm `provider_id/model_id` format and that `name` field controls TUI display.

### 8. Model Catalogs
**Research current model catalogs, specs, context limits, rate limits, and known issues** for Google Antigravity, OpenRouter free models, OpenCode Zen, Cerebras, and Groq.
- **Specifically investigate**: Forum reports of model identity mismatch/provenance issues for Antigravity.
- **Also include**: Exact provider config requirements for Cerebras and Groq.
- **Goal**: Complete, current model catalogs with specs, rate limits, and any identity/routing issues.

---

## 📦 Deliverable
A **Verification Report** that:
1. Addresses all 8 directives above
2. Cites authoritative sources with URLs and quotes
3. Provides YES/NO answers where possible
4. Flags confidence levels (High/Medium/Low)
5. Recommends exact configurations based on verified facts

---

*⬡ OMEGA ⬡ WEB-GEMINI ⬡ opencode ⬡ trc_research_plan ⬡ ACTIVE*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
