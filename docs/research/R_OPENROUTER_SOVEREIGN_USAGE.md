<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 R_OPENROUTER_SOVEREIGN_USAGE
# ⬡ OMEGA ⬡ RESEARCHER ⬡ GEMINI-3.5-FLASH ⬡ trc_openrouter_usage ⬡ GNOSIS

**Date**: 2026-06-11
**Status**: VERIFIED
**AP Token**: AP-OR-USAGE-v1.0.0

## Executive Summary
This document defines the sovereign usage patterns for the OpenRouter API to eliminate 401/404 errors and ensure stable inference. The primary failure modes identified were model slug mismatches and missing application identifiers.

## Key Findings
1. **Slug Precision**: 404 errors are caused by using UI display names instead of API slugs. All models must follow the `organization/model-name` format.
2. **Free Model Routing**: Free models require the `:free` suffix (e.g., `google/gemma-2-9b-it:free`) or the `openrouter/free` global router.
3. **Header Requirements**: While `Authorization` is the only mandatory header for auth, `HTTP-Referer` and `X-Title` are critical for application identification and routing stability.
4. **Auth Verification**: The `/api/v1/credits` endpoint is the most reliable way to verify key validity without triggering inference costs.

## Detailed Analysis

### 1. Verified Request Pattern
The gold standard for direct shell/subprocess calls to OpenRouter:

```bash
curl https://openrouter.ai/api/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \\
  -H "HTTP-Referer: https://omega-engine.ai" \\
  -H "X-Title: Omega Engine" \\
  -d '{
  "model": "google/gemma-2-9b-it",
  "messages": [
    {
      "role": "user",
      "content": "Hello, Omega Engine is calling."
    }
  ]
}'
```

### 2. Model Identifier Matrix

| Model Type | Slug Pattern | Example | Note |
| :--- | :--- | :--- | :--- |
| **Standard** | `org/model` | `google/gemma-2-9b-it` | Primary identifier |
| **Free** | `org/model:free` | `google/gemma-2-9b-it:free` | Rate-limited, free tier |
| **Latest** | `~org/model` | `~openai/gpt-latest` | Auto-updates to newest version |
| **Global Free** | `openrouter/free` | `openrouter/free` | Routes to any available free model |

### 3. Header Specification

| Header | Status | Value | Purpose |
| :--- | :--- | :--- | :--- |
| `Authorization` | **Mandatory** | `Bearer <KEY>` | Authentication |
| `Content-Type` | **Mandatory** | `application/json` | Payload format |
| `HTTP-Referer` | Recommended | `https://omega-engine.ai` | App identification |
| `X-Title` | Recommended | `Omega Engine` | Dashboard naming |

### 4. Error Recovery Matrix

| Code | Meaning | Root Cause | Recovery Action |
| :--- | :--- | :--- | :--- |
| **401** | Unauthorized | Invalid/Expired Key | Verify key in `.env`; check for whitespace |
| **404** | Not Found | Slug Mismatch | Validate slug via `/api/v1/models` |
| **429** | Rate Limit | Quota Exceeded | Exponential backoff; check credit balance |
| **5xx** | Provider Error | Upstream Failure | Use `route: 'fallback'` in request body |

## Verification Protocol
To verify a new key or model:
1. **Auth Check**: `curl https://openrouter.ai/api/v1/credits -H "Authorization: Bearer $KEY"`
2. **Model Check**: `curl https://openrouter.ai/api/v1/models -H "Authorization: Bearer $KEY"`
3. **Inference Check**: Simple completion with `google/gemma-2-9b-it`.

## Sources
- OpenRouter API Documentation
- Developer Forums (GitHub/Discord)
- Empirical Testing (Omega Engine Shell Probes)

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: GEMINI-3.5-FLASH | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
