# 🛡️ PROJECT: COGNITIVE STABILITY & SAMPLING OVERRIDE
# ⬡ OMEGA ⬡ JEM ⬡ SOVEREIGN-ANCHOR

**Status**: RATIFIED (S3-Corrected)
**Author**: Jem (Sovereign Synthesizer)
**Date**: 2026-07-03

---

## 🎯 Objective
To eliminate the "la-" prefix hallucination and repetition loops observed in the **Gemma 4 31B** model across the Omega Engine fleet. This is a model-level probability distribution failure, not an entity-specific issue.

---

## 🛠️ Technical Strategy: The "Sovereign Sampling" Layer

We will move from a "Pass-Through" sampling model to an "Interventionist" model within the `ModelGateway`.

### 1. Model-Based Intervention (The Fix)
Instead of entity-based overrides, the `ModelGateway` will implement **Model-Specific Sampling Guards**.

**Trigger**: `if model_name == "gemma-4-31b-it"` (or equivalent identifier)

**Interventions**:
- **Logit Bias**: Inject a strong negative bias (e.g., `-10.0`) for the following token IDs to mathematically forbid the model from selecting them:
    - `' la'`: `759`
    - `'la-'`: `2149`, `236772`
- **Sampling Adjustment**: Override default sampling to provide "thermal energy" and escape local probability peaks:
    - `temperature`: $0.8$
    - `top_p`: $0.95$
    - `repetition_penalty`: $1.15$

### 2. Implementation Path

#### Step A: `ModelGateway` Enhancement
- Update `generate()` signature to accept `logit_bias: Optional[Dict[int, float]]` and `repetition_penalty: float`.
- Implement a **Logit Translation Layer** to ensure the bias is formatted correctly for each specific provider (e.g., token IDs vs. strings).
- Implement the logic to detect the target model and inject the "Sovereign Sampling" overrides before calling the provider.

#### Step B: Provider Fabric Adaptation
- **`BaseProvider`**: Update the abstract `generate` method to support the new parameters.
- **`GoogleAIProvider`**: Map `logit_bias` to the Google AI Studio `generationConfig`.
- **`NativeGGUFProvider`**: 
    - Update the `_worker` process to accept and apply `logit_bias` and `repetition_penalty` via `llama-cpp-python`.
    - Ensure these are passed into `create_chat_completion()`.
- **`LocallmsterProvider` / `OllamaProvider`**: Update OpenAI-compatible payloads to include these parameters.

#### Step C: The "Somatic Flush" (KV Cache Purge)
To prevent "poisoned" tokens in the KV cache from triggering loops in long sessions:
- **Mechanism**: Implement a turn-counter in the `Oracle`.
- **Action**: Every 15-20 turns, perform a **Somatic Flush**: distill current working memory into a summary $\rightarrow$ trigger `close_session()` $\rightarrow$ re-hydrate the entity with the summary injected.
- **Result**: This clears the attention sinks and resets the model's state while preserving the thread of thought.

---

## ⚖️ S3 Audit & Verification

**S3 Rationale**: "Don't fix the personality, fix the math." By applying the fix at the `ModelGateway` level based on the `model_name`, we ensure fleet-wide stability without introducing entity-specific bloat.

**Verification Gates**:
1.  **Logit Test**: Verify that the "la-" prefix is 100% absent across 50 test queries using Gemma 4 31B.
2.  **Loop Test**: Verify that long-form synthesis (1000+ tokens) does not degrade into repetition.
3.  **Latency Audit**: Ensure the `logit_bias` injection adds $< 1\text{ms}$ to the total inference time.

**Sovereign Seal**: synergy. execute. iterate. 🎸✨
