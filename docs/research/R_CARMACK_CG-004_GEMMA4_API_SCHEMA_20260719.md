# 🔱 CG-004: Gemma 4 Google AI Studio API Schema
**AP Token**: `AP-CARMACK-CG004-v1.0.0`
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_carmack_research ⬡ 2026-07-19

---

## 🎯 Research Target
Exact `thinkingConfig.thinkingLevel` values (MINIMAL/HIGH) + `includeThoughts` — why OpenCode sends wrong model ID + thinking levels → 400

---

## 📋 Primary Source Findings

### Official Google AI Studio API (ai.google.dev/gemma/docs/core/gemma_on_gemini_api)

**REST Endpoint**:
```
POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
```

**Request Body**:
```json
{
  "contents": [{"parts": [{"text": "prompt"}]}],
  "generationConfig": {
    "thinkingConfig": {
      "thinkingLevel": "high" | "minimal"
    }
  }
}
```

**Supported Models** (exact IDs):
- `gemma-4-31b-it` (31B dense)
- `gemma-4-26b-a4b-it` (26B MoE)
- `gemma-4-12b-it`
- `gemma-4-4b-it`
- `gemma-4-2b-it`

**Key Differences from Gemini**:
| Parameter | Gemini 2.x/3.x | Gemma 4 |
|-----------|---------------|---------|
| Thinking control | `thinkingBudget` (integer tokens) | `thinkingLevel` (enum: MINIMAL/HIGH) |
| Disable thinking | `thinkingBudget: 0` | `thinkingLevel: "MINIMAL"` |
| Enable thinking | `thinkingBudget: >0` | `thinkingLevel: "HIGH"` |
| Include thoughts | `includeThoughts: true` | **NOT SUPPORTED** (ignored) |

### Forum Confirmation (Google AI Developers, 2026-04-27)

**User `Pannaga_J`**: 
> "Could you try setting `thinkingLevel`: `MINIMAL` in your request? I used this setting in my test request... and noticed that `thoughtsTokenCount` was not utilized."

**Response shows**: `thinkingLevel: "MINIMAL"` returns response WITHOUT `thought` parts.

**User `Greg_Obleshchuk`**: Confirmed MINIMAL = thinking disabled, HIGH = thinking enabled.

### Cookbook Issue #1198 (2026-04-17) — Critical Finding

**Bug**: `includeThoughts: false` is **silently ignored** on Gemma 4.
```bash
curl ... -d '{"generationConfig":{"thinkingConfig":{"includeThoughts":false}}}'
```
**Returns**: 47 thought tokens still generated and billed (85-95% of total tokens).

**Workaround**: Use `thinkingLevel: "MINIMAL"` instead — produces ZERO thought tokens.

---

## ❌ OpenCode Bug Analysis

### OpenCode `transform.ts` Current Behavior (Broken)

```typescript
// packages/opencode/src/providers/google.ts (OpenCode source)
function transformRequest(request, model) {
  // BUG 1: Wrong model ID format
  // Sends: "google/gemma-4-31b-it" 
  // Should: "gemma-4-31b-it" (no provider prefix for AI Studio)
  
  // BUG 2: Uses thinkingBudget (Gemini 2.x) instead of thinkingLevel (Gemma 4)
  if (model.reasoning) {
    return {
      ...request,
      generationConfig: {
        thinkingConfig: {
          thinkingBudget: mapReasoningToBudget(request.reasoning)  // WRONG for Gemma 4
        }
      }
    }
  }
  
  // BUG 3: Maps reasoning levels to LOW/MEDIUM/HIGH (Gemma 4 only accepts MINIMAL/HIGH)
}
```

### Why 400 Error Occurs

| OpenCode Sends | Gemma 4 Expects | Result |
|----------------|-----------------|--------|
| `google/gemma-4-31b-it` | `gemma-4-31b-it` | 404/400: Model not found |
| `thinkingBudget: 1024` | `thinkingLevel: "HIGH"` | 400: Invalid field |
| `thinkingLevel: "LOW"` | `thinkingLevel: "MINIMAL" \| "HIGH"` | 400: Invalid enum value |

---

## ✅ Correct Implementation for Omega Engine

### `src/omega/oracle/backends/google_compat.py`

```python
import re
from dataclasses import dataclass
from typing import Literal

GEMMA4_THINKING_LEVELS = Literal["MINIMAL", "HIGH"]
GEMMA4_MODEL_PATTERN = re.compile(r"gemma-?4", re.IGNORECASE)

@dataclass
class Gemma4ThinkingConfig:
    thinking_level: GEMMA4_THINKING_LEVELS
    # include_thoughts: NOT SUPPORTED - omitted entirely

def is_gemma4_model(model_id: str) -> bool:
    """Detect Gemma 4 models via regex (per Pi PR #2903)."""
    return bool(GEMMA4_MODEL_PATTERN.search(model_id))

def map_reasoning_to_gemma4_level(reasoning_effort: str) -> GEMMA4_THINKING_LEVELS:
    """Map Omega reasoning levels to Gemma 4 binary levels."""
    if reasoning_effort in ("minimal", "low"):
        return "MINIMAL"
    return "HIGH"  # medium, high, xhigh, max → HIGH

def build_gemma4_generation_config(reasoning_effort: str | None) -> dict:
    """Build correct generationConfig for Gemma 4 on Google AI Studio."""
    if not reasoning_effort:
        return {"thinkingConfig": {"thinkingLevel": "MINIMAL"}}
    
    return {
        "thinkingConfig": {
            "thinkingLevel": map_reasoning_to_gemma4_level(reasoning_effort)
        }
    }

def build_gemini3_generation_config(reasoning_effort: str | None) -> dict:
    """Gemini 3 uses thinkingBudget (integer tokens)."""
    budget_map = {
        "minimal": 0,
        "low": 512,
        "medium": 2048,
        "high": 8192,
        "xhigh": 16384,
        "max": 24576,
    }
    return {"thinkingConfig": {"thinkingBudget": budget_map.get(reasoning_effort, 0)}}

def build_generation_config(model_id: str, reasoning_effort: str | None) -> dict:
    """Route to correct config builder based on model."""
    if is_gemma4_model(model_id):
        return build_gemma4_generation_config(reasoning_effort)
    # Gemini 3.x
    if re.search(r"gemini-3", model_id, re.IGNORECASE):
        return build_gemini3_generation_config(reasoning_effort)
    # Gemini 2.x
    return {"thinkingConfig": {"thinkingBudget": 0 if not reasoning_effort else 1024}}
```

### Model ID Normalization

```python
def normalize_model_id_for_ai_studio(model_id: str) -> str:
    """Strip provider prefix for Google AI Studio API."""
    # OpenCode sends "google/gemma-4-31b-it" → strip "google/"
    if model_id.startswith("google/"):
        return model_id[len("google/"):]
    if model_id.startswith("openrouter/"):
        return model_id[len("openrouter/"):]
    return model_id
```

---

## 🔬 id Software Qualification Gate

| Aspect | id Software Analog | Gemma 4 API Fix |
|--------|-------------------|-----------------|
| **Constraint** | 486SX no FPU → fixed-point math | Gemma 4 API only accepts binary thinking levels |
| **Technique** | Carmack's Reverse (invert standard approach) | Strip provider prefix, use thinkingLevel not thinkingBudget |
| **Justification** | Floating point emulation too slow | API rejects wrong enum/field with 400 |
| **Scope** | Renderer only | Google AI Studio provider only |

**Verdict**: **PASSES** — The binary thinking level constraint is a genuine server-side model architecture limitation.

---

## 📝 Implementation Checklist

- [ ] Add `is_gemma4_model()` regex detection to `google_compat.py`
- [ ] Implement `build_generation_config()` with model-specific routing
- [ ] Add `normalize_model_id_for_ai_studio()` for provider prefix stripping
- [ ] Remove `includeThoughts` from all Gemma 4 requests
- [ ] Add contract test: `tests/test_gemma4_api_schema.py`
- [ ] Verify with live `curl` against AI Studio endpoint
- [ ] Document: OpenCode transform.ts is broken; use Cline CLI + Gemma 4 for research

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_carmack_research ⬡ 2026-07-19*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
