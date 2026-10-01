<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Gemma 4 31B — Knowledge Base

**Model**: `gemma-4-31b-it`
**Architecture**: 31B dense (all params active)
**Context window**: 256K tokens (API), 32K practical for structured output
**Release**: March 31, 2026
**API endpoint**: `generativelanguage.googleapis.com/v1beta/models/gemma-4-31b-it`

---

## Key Capability: Structured JSON Output

### The Problem
Gemma 4 31B has a **thinking behavior** — it generates internal reasoning before the actual JSON output. When you only set `responseMimeType: "application/json"` without a schema, the model ignores the mime type and outputs thinking text instead of JSON.

### The Solution
You MUST provide **BOTH** `responseMimeType` AND `responseJsonSchema` with a complete schema definition:

```python
payload = {
    "contents": [{"parts": [{"text": prompt}]}],
    "generationConfig": {
        "temperature": 0.6,
        "maxOutputTokens": 8192,
        "responseMimeType": "application/json",
        "responseJsonSchema": {
            "type": "object",
            "properties": {
                "field1": {"type": "string"},
                "field2": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["field1", "field2"]
        }
    }
}
```

### Why This Works
- Without `responseJsonSchema`: Model outputs thinking text → JSON parse fails (~0% success)
- With `responseJsonSchema`: Clean JSON every time (~100% success)
- The schema suppresses thinking entirely — no `thought: true` parts in response
- `temperature: 0.6` works well for structured extraction

### Source
- [DEV Community: responseJsonSchema](https://dev.to/ai_made_tools/responsejsonschema-the-undocumented-gemma-4-feature-that-changed-everything-2obm) — The `responseJsonSchema` parameter is documented for Gemini models but NOT listed on the official Gemma 4 capabilities page. It works perfectly via the same API infrastructure.

---

## Performance Benchmarks (Our Testing)

| Source | Chars | Latency | Items Extracted |
|--------|------:|--------:|----------------:|
| Masters of Doom (4.2K words) | 15,922 | 23.6s | 20 |
| .plan 1996 (24K words) | 153,544 | 28.7s | 33 |
| Lex Fridman #309 (58K words) | 240,000 | 30.6s | 29 |

**Average latency**: ~28s per extraction
**Average extraction yield**: ~27 items per source

---

## API Configuration

### Authentication
```bash
# Header (recommended)
curl -H "x-goog-api-key: $GOOGLE_API_KEY" ...

# Or query param
curl "?key=$GOOGLE_API_KEY" ...
```

### Rate Limits (Free Tier)
- **50 requests/day** per API key (free tier)
- **1000 requests/day** with $10+ credits purchased
- Use **separate API keys** for concurrent requests to different models
- Failed requests count against your daily limit

### Model Availability
```bash
# List available models
curl "https://generativelanguage.googleapis.com/v1beta/models?key=$GOOGLE_API_KEY"
```

Returns `gemma-4-31b-it` in the `models` array.

---

## Thinking Behavior

Gemma 4 31B generates `thought: true` parts even when `includeThoughts: false` is set. This is a known issue (GitHub issue #1198 on google-gemini/cookbook).

**Impact**: If you use streaming or don't use `responseJsonSchema`, you'll get thinking tokens in your output.

**Mitigation**: Always use `responseJsonSchema` — it suppresses thinking entirely.

---

## When to Use 31B vs 26B

| Use Case | Recommended |
|----------|-------------|
| Structured JSON extraction | **31B** — more consistent, never times out |
| Large documents (>100K chars) | **31B** — handles 262K context reliably |
| Quick extraction (small docs) | Either works |
| Maximum item count | Depends — 26B extracted more on Lex (35 vs 29) |
| Reliability | **31B** — 26B had cold-start timeout |

---

## Extraction Schema (Our Standard)

For Carmack ingestion pipeline, we use this schema:

```json
{
  "type": "object",
  "properties": {
    "technical_facts": {"type": "array", "items": {"type": "string"}},
    "personality_patterns": {"type": "array", "items": {"type": "string"}},
    "gnosis_principles": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "principle": {"type": "string"},
          "description": {"type": "string"}
        },
        "required": ["principle", "description"]
      }
    },
    "heritage_patterns": {"type": "array", "items": {"type": "string"}},
    "dpo_pairs": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "prompt": {"type": "string"},
          "chosen": {"type": "string"},
          "rejected": {"type": "string"}
        },
        "required": ["prompt", "chosen", "rejected"]
      }
    }
  },
  "required": ["technical_facts", "personality_patterns", "gnosis_principles", "heritage_patterns", "dpo_pairs"]
}
```

---

## References

- [Google AI: Structured Outputs](https://ai.google.dev/gemini-api/docs/generate-content/structured-output)
- [Gemma 4 Model Card](https://ai.google.dev/gemma/docs/core/model_card_4)
- [Function Calling with Gemma 4](https://ai.google.dev/gemma/docs/capabilities/text/function-calling-gemma4)
- [Firebase: Generate Structured Output](https://firebase.google.com/docs/ai-logic/generate-structured-output)
- [Gemma 4 API Guide](https://gemma4.dev/deploy/gemma-4-gemini-api)
- [DEV: responseJsonSchema Feature](https://dev.to/ai_made_tools/responsejsonschema-the-undocumented-gemma-4-feature-that-changed-everything-2obm)
- [GitHub Issue #1198: includeThoughts bug](https://github.com/google-gemini/cookbook/issues/1198)
