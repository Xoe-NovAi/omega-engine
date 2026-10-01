# 🔱 Nemotron 3 Ultra Teacher Pipeline Specification
# AP Token: `AP-NEMOTON-TEACHER-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_teacher_pipeline ⬡ SPEC

## 1. Overview
The Nemotron 3 Ultra Teacher Pipeline implements an Iterative Critique-Loop for generating DPO (Direct Preference Optimization) training pairs using the `nvidia/nemotron-3-ultra-550b-a55b` model via OpenRouter.

## 2. Architecture
```
Local Model (Gemma 4 31B) 
    ↓ Generate response
Nemotron 3 Ultra (Critique) 
    ↓ Identify issues
Local Model (Fix) 
    ↓ Generate improved response
Nemotron 3 Ultra (Final Verdict) 
    ↓ Accept/Reject
DPO Pair (prompt, chosen, rejected)
```

## 3. DPO Pair Capture
Each iteration captures:
- **prompt**: The original query
- **chosen**: The final improved response (accepted by Nemotron)
- **rejected**: The initial response (rejected by Nemotron)
- **metadata**: Model versions, iteration count, critique notes

## 4. Implementation Details
- **Provider**: OpenRouter with 8-account active-passive failover (D205)
- **Model**: `nvidia/nemotron-3-ultra-550b-a55b`
- **Storage**: `data/knowledge/dpo_pairs/` as JSONL files
- **Rate Limiting**: Respect 429 responses with exponential backoff

## 5. Usage
```python
from omega.teachers.nemotron_pipeline import NemotronTeacherPipeline

pipeline = NemotronTeacherPipeline()
dpo_pair = await pipeline.generate_dpo_pair(
    prompt="Explain the Zone Memory allocator in Quake",
    local_model="gemma-4-31b-it"
)
```

## 6. Verification
- **T9 (Teacher Pipeline)**: Verify DPO pair generation with mock Nemotron responses
- **T10 (DPO Storage)**: Verify JSONL files are correctly written to data/knowledge/

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: gemma-4-31b-it | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
