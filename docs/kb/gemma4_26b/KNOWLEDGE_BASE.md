# Gemma 4 26B (MoE) — Knowledge Base

**Model**: `gemma-4-26b-a4b-it`
**Architecture**: 26B total params, **4B active** (Mixture of Experts)
**Context window**: 256K tokens
**Release**: April 2, 2026
**API endpoint**: `generativelanguage.googleapis.com/v1beta/models/gemma-4-26b-a4b-it`

---

## Key Difference from 31B

The 26B is a **Mixture of Experts (MoE)** model — only 4B parameters are active per token. This means:
- **Faster inference** when warm (fewer active params = less compute)
- **Same total capacity** as a 26B dense model
- **Cold-start latency** can be significant (we saw 180s timeout on first request)

The 31B is **dense** — all 31B params are active every token. Slower but more consistent.

---

## Structured JSON Output

### Same Solution as 31B
The 26B has the same thinking behavior. You MUST use both `responseMimeType` AND `responseJsonSchema`:

```python
payload = {
    "contents": [{"parts": [{"text": prompt}]}],
    "generationConfig": {
        "temperature": 0.6,
        "maxOutputTokens": 8192,
        "responseMimeType": "application/json",
        "responseJsonSchema": EXTRACTION_SCHEMA
    }
}
```

### Critical: Separate API Key
**Always use a different API key** than the 31B to avoid rate limit collisions. The free tier is 50 requests/day per key. Running both models on the same key halves your throughput.

```python
MODELS = {
    "gemma4_31b": {"model": "gemma-4-31b-it", "env_key": "GOOGLE_API_KEY_1"},
    "gemma4_26b": {"model": "gemma-4-26b-a4b-it", "env_key": "GOOGLE_API_KEY_2"},
}
```

---

## Performance Benchmarks (Our Testing)

| Source | Chars | Latency | Items Extracted |
|--------|------:|--------:|----------------:|
| Masters of Doom (4.2K words) | 15,922 | 180.0s (timeout) | 0 |
| .plan 1996 (24K words) | 153,544 | 17.4s | 24 |
| Lex Fridman #309 (58K words) | 240,000 | 28.7s | 35 |

**Key observations**:
- Cold-start timeout on first request (180s limit hit)
- Once warm, faster than 31B (17.4s vs 28.7s on 24K source)
- Extracted MORE items than 31B on Lex transcript (35 vs 29)
- Extraction quality is competitive with 31B

---

## Cold-Start Behavior

The 26B MoE model exhibits significant cold-start latency:

1. **First request after idle**: Can take 60-180+ seconds (may timeout)
2. **Subsequent requests**: Normal latency (17-29s)
3. **No workaround**: This is inherent to the MoE architecture loading experts on demand

**Recommendation**: For pipeline workloads, batch requests to keep the model warm. Or accept cold-start timeouts and retry.

---

## API Configuration

### Authentication
```bash
curl -H "x-goog-api-key: $GOOGLE_API_KEY_2" \
  "https://generativelanguage.googleapis.com/v1beta/models/gemma-4-26b-a4b-it:generateContent"
```

### Model Name (Correct)
```
gemma-4-26b-a4b-it    # ✅ CORRECT — includes "a4b" suffix (4B active)
gemma-4-26b-it        # ❌ WRONG — returns 404
```

### Rate Limits (Free Tier)
- **50 requests/day** per API key
- Use separate keys from 31B to double your throughput
- Failed/cold-start requests count against limit

---

## When to Use 26B vs 31B

| Use Case | Recommended |
|----------|-------------|
| Structured JSON extraction | **31B** for reliability, **26B** for speed when warm |
| Large documents (>100K chars) | Either — both handle 240K chars |
| Quick extraction (small docs) | **31B** — avoids cold-start timeout |
| Maximum item count | **26B** extracted more on Lex (35 vs 29) but less on plan 1996 (24 vs 33) |
| Pipeline with warm model | **26B** — faster when warm (17.4s vs 28.7s) |
| Cold-start environments | **31B** — never times out |

---

## Extraction Schema (Our Standard)

Same schema as 31B — see [Gemma 4 31B KB](../gemma4_31b/KNOWLEDGE_BASE.md#extraction-schema-our-standard).

---

## MoE Architecture Notes

- **26B total params**: Full model capacity for learning
- **4B active per token**: Only 4B params fire for each token generated
- **Expert routing**: Different experts handle different types of tokens
- **Memory efficient**: Lower VRAM footprint than dense 31B
- **Speed**: When warm, generates tokens faster than 31B (fewer active params)

---

## References

- [Gemma 4 Model Card](https://ai.google.dev/gemma/docs/core/model_card_4)
- [Google AI: Structured Outputs](https://ai.google.dev/gemini-api/docs/generate-content/structured-output)
- [Gemma 4 API Guide](https://gemma4.dev/deploy/gemma-4-gemini-api)
- [DEV: responseJsonSchema Feature](https://dev.to/ai_made_tools/responsejsonschema-the-undocumented-gemma-4-feature-that-changed-everything-2obm)
- [Apidog: Gemma 4 API Guide](https://apidog.com/blog/gemma-4-api/)
