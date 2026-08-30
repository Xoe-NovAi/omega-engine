# Gemma 4 Model Comparison — 31B vs 26B

**Date**: 2026-07-02
**Test environment**: Ryzen 7 5700U, free-tier Google API keys

---

## Head-to-Head Results

| Source | 31B Latency | 26B Latency | 31B Items | 26B Items | Winner |
|--------|------------:|------------:|----------:|----------:|--------|
| Masters of Doom (4.2K words) | 23.6s | 180.0s (timeout) | 20 | 0 | **31B** (26B cold-start) |
| .plan 1996 (24K words) | 28.7s | 17.4s | 33 | 24 | **31B** (yield), **26B** (speed) |
| Lex Fridman #309 (58K words) | 30.6s | 28.7s | 29 | 35 | **26B** (yield + speed) |

---

## Key Findings

### 1. Structured JSON: responseJsonSchema is Mandatory
Both models require `responseMimeType` + `responseJsonSchema` to output clean JSON. Without the schema, they output thinking text. This is an undocumented Gemma 4 feature (see [DEV.to article](https://dev.to/ai_made_tools/responsejsonschema-the-undocumented-gemma-4-feature-that-changed-everything-2obm)).

### 2. 31B is More Consistent
- Never timed out across all tests
- Consistent 23-31s latency range
- Reliable extraction yield (20-33 items)

### 3. 26B Has Cold-Start Issues
- First request timed out at 180s
- Once warm, faster than 31B (17-29s)
- MoE architecture loads experts on demand → cold-start penalty

### 4. 26B Can Extract More When Warm
- Extracted 35 items from Lex Fridman (vs 31B's 29)
- MoE architecture may better route diverse content types to specialized experts

### 5. Use Separate API Keys
- Free tier: 50 requests/day per key
- Running both models on same key = 25 each
- Separate keys = 50 each

---

## Recommendation

**For ingestion pipeline**: Use **31B as primary** (reliable, no cold-start), **26B as secondary** (faster when warm, higher yield on large sources). Use separate API keys for each.

**Batch strategy**: Run 31B first for reliable baseline, then 26B for higher yield. If 26B times out on cold-start, retry or skip.

---

## Common Gotchas

| Issue | Cause | Fix |
|-------|-------|-----|
| JSON parse fails, model outputs thinking text | Only `responseMimeType` set, no schema | Add `responseJsonSchema` with full schema |
| Cold-start timeout | 26B MoE loading experts | Retry or use 31B for first request |
| 404 on `gemma-4-26b-it` | Wrong model name | Use `gemma-4-26b-a4b-it` (note `a4b` suffix) |
| Rate limit (429) | Too many requests on one key | Use separate keys per model |
| `includeThoughts: false` ignored | Known bug (GitHub #1198) | Use `responseJsonSchema` instead |
