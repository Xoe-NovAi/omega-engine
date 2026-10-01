# 🔱 Model Registry Reality Engine - Implementation Plan
**Status**: 🚀 READY FOR EXECUTION
**Date**: 2026-07-19

---

## 🎯 The Problem (Hard Facts)

After querying OpenRouter API (344 models), **15/35 models** have incorrect data:
- **Context windows**: 6 wrong
- **Pricing**: 13 wrong (incorrect or missing)
- **Local models**: 4 have NOTHING verified (need HuggingFace API)
- **Capability scores**: ALL fabricated

---

## 🏗️ Authoritative Sources

| Source | API | Covers | Auth |
|--------|-----|--------|------|
| OpenRouter | `/api/v1/models` | 22/35 cloud models | No |
| HuggingFace | `/api/models/{repo}` | 4/35 local models | No |
| Google AI | list models | Gemini models | Yes |
| Anthropic | `/v1/models` | Claude models | Yes |
| xAI | `/v1/models` | Grok models | Yes |

---

## 🚀 Execution

```bash
# 1. Query all APIs
make model-reality-check

# 2. Review corrections
cat data/reality_corrections.json

# 3. Apply corrections
make model-reality-apply

# 4. Rebuild index
make model-index

# 5. Validate
make model-validate
```

---

## 📋 Corrections Needed (15 models)

| Model | Context Fix | Pricing |
|-------|-------------|---------|
| minimax/minimax-m2.5:free | 204800→1048576 | $0→$0.0003 |
| gemini-2.5-pro | 1000000→1048576 | Verified |
| gemini-2.5-flash | Mismatched | Fixed |
| claude-haiku-4.5-extended | 200000→1000000 | $0.25→$0.002 |
| ... (11 more) | ... | ... |

---

*⬡ OMEGA ⬡ REALITY-ENGINE PLAN ⬡ 2026-07-19*
