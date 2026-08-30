# Incident Report: Unexpected Compaction During Session
**Date**: 2026-07-21
**Entity**: grokster
**Session**: ses_7ae04edc8abb
**Model**: Nemotron 3 Super (free) via OpenRouter

---

## What Happened

1. **User requested**: "prepare for compaction. Make all needed updates to ensure continuity."
2. **Agent began**: Standard pre-compaction continuity work (M11/M15 mandated updates to session_gnosis.md, proposed_lessons.yaml, live feed, Hivemind context)
3. **System interrupted**: Displayed `▣ Grokster · Nemotron 3 Super (free) · interrupted` mid-operation
4. **Agent resumed**: Continued thought process post-interruption
5. **User noted**: Context reported at ~25% of advertised 1M window — far below expected autocompaction threshold

---

## OpenRouter API Metadata (Queried Post-Incident)

| Field | Paid Variant | Free Variant |
|-------|--------------|--------------|
| `context_length` (model spec) | 1,000,000 | 1,000,000 |
| `top_provider.context_length` | 262,144 | 262,144 |
| `reasoning.supported_efforts` | ["medium", "low"] | ["medium", "low"] |
| `reasoning.default_effort` | "medium" | "medium" |

**Source**: `GET https://openrouter.ai/api/v1/models` — entries for `nvidia/nemotron-3-super-120b-a12b` and `nvidia/nemotron-3-super-120b-a12b:free`

---

## Critical Distinction

> **API metadata ≠ verified runtime behavior**

The `top_provider.context_length` field reflects the *provider's advertised limit for that endpoint*, but:
- Actual enforcement may differ
- Provider routing may select different backends
- OpenCode's internal token accounting may differ from provider counts
- Free tier may have additional undocumented constraints

---

## User's Verified Experience (Ground Truth)

- **Nemotron 3 Ultra via OpenCode**: Regularly handles ~350K+ tokens without compaction
- **This session (Nemotron 3 Super free)**: Compaction at reported ~25% of 1M advertised
- **Cause**: **Unknown** — not yet determined whether provider limit, OpenCode accounting, or other factor

---

## Agent Error Log

| Error | Correction |
|-------|------------|
| Stated "Nemotron 3 Super free tier is capped at 256K" as fact | Was unverified hypothesis from API metadata only |
| Claimed "This explains your compaction at 25%" | Speculation presented as causation |
| Recorded conclusions in incident narrative | Should have recorded only observations + metadata with clear uncertainty labels |

---

## Open Questions

1. Does `top_provider.context_length` reflect hard enforcement or soft guideline?
2. Does OpenRouter's free variant routing select different providers under load?
3. Does OpenCode's token counter match provider's tokenization?
4. Is there a separate "free tier" compaction trigger independent of context %?
5. Why does Nemotron 3 Ultra (same provider family) behave differently?

---

## Next Steps (Deferred)

- [ ] Test actual runtime limit with controlled token injection
- [ ] Compare OpenCode token count vs. provider-reported usage
- [ ] Check if paid variant has different `top_provider.context_length` at runtime
- [ ] Query OpenRouter Discord/community for known free-tier behaviors

---

## Sovereignty Note

This incident demonstrates why **M23 (Failure Integrity)** and **M18 (Token Efficiency)** matter:
- Metadata was treated as ground truth without verification
- Speculation was recorded as fact
- User's direct experience was the correct check on agent overconfidence

**Lesson**: In sovereign systems, *only verified runtime behavior counts*. API specs, marketing pages, and provider metadata are hints — not contracts.

---

*Recorded per M15 (Sovereign Continuity) — incident anchor for future reference*