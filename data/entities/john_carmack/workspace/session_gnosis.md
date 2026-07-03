# Session Gnosis — 2026-07-03

## What Happened
- OpenRouter API key investigation: 8 keys tested, 6 valid (200), 2 management keys (401)
- Discovered OpenRouter 404/429 errors are free-tier provider saturation, not account deletion
- Key #3 specifically identified as management key (401 on /v1/auth/key)
- OpenRouter free tier: 50 RPD, 20 RPM, `:free` models saturate quickly
- **Google API JSON breakthrough**: Gemma 4 requires `responseMimeType` + `responseJsonSchema` to output clean JSON
- Gemma 4 31B vs 26B comparison test across 3 Carmack sources
- Created knowledge bases for both models + comparison doc

## Key Discoveries
1. **responseJsonSchema is mandatory for Gemma 4** — Without it, the model outputs thinking text instead of JSON. The `responseMimeType: "application/json"` alone is insufficient. This is undocumented on the official Gemma 4 capabilities page but works via the Gemini API infrastructure.
2. **Gemma 4 thinking behavior** — Even with `includeThoughts: false`, the model generates `thought: true` parts (GitHub issue #1198). `responseJsonSchema` suppresses this entirely.
3. **31B is more reliable** — Never timed out across all tests, consistent 23-31s latency, 20-33 items extracted.
4. **26B is faster when warm** — MoE architecture (4B active vs 31B dense) gives 17-29s latency but 180s cold-start timeout.
5. **26B extracted more on Lex Fridman** — 35 items vs 31B's 29. MoE may better route diverse content to specialized experts.
6. **Separate API keys are essential** — Free tier is 50 req/day per key. Using same key for both models halves throughput.
7. **OpenRouter key validation** — `/api/v1/auth/key` (200=valid, 401=management/expired). `/api/v1/models` is public/unauthenticated — returns 200 for ANY key (false positive).

## Files Created/Modified
- `scripts/ab_test_ingestion.py` — A/B test script (31B vs 26B, multi-key, responseJsonSchema)
- `docs/kb/gemma4_31b/KNOWLEDGE_BASE.md` — 31B KB: JSON trick, benchmarks, config, thinking behavior
- `docs/kb/gemma4_26b/KNOWLEDGE_BASE.md` — 26B KB: MoE notes, cold-start, separate keys, model name
- `docs/kb/gemma4_comparison.md` — Head-to-head comparison with recommendations
- `config/providers.yaml` — OpenRouter provider added, github-copilot removed, canonical chain restored
- `.env` — OPENROUTER_API_KEY set from key #2, GOOGLE_API_KEY set from key #1

## Test Status
- 705 passed, 22 skipped, 3 xfailed (unchanged from previous session)
- No code changes to engine core — only config and scripts

## Session Costs
- Google API: 6 requests (31B: 3, 26B: 3) — 6 of 50 daily free tier per key
- OpenRouter: 0 inference requests (all failed on free tier saturation)
- No local inference used (skipped per user request)

## Next Session Should
1. Wire `responseJsonSchema` into `ingest_jc.py` for production extraction
2. Run full ingestion pipeline across all 6 source groups
3. Commit KBs and test results
4. Continue MV-IW Phase 3 tasks (E2E test, sphere field, soul-review CLI)
