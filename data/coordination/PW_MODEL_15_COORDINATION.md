# 🔱 pw_model_15 Coordination Report: Gemma Parallel Background Worker Engine
**AP Token**: `AP-PW15-COORD-v1.0.0`
**Status**: PROPOSED FINAL PLAN (Sourced from R-MODEL-INT)
**Date**: 2026-06-11
**Coordinator**: OpenCode
**Target Entity**: Roc Racoon / Researcher

---

## ⬡ Executive Summary
The `pw_model_15` implementation realizes the **Sovereign Workhorse Protocol**, allowing the Omega Engine to scale high-throughput sensing using parallel Gemma 4 workers. This plan aligns with the approved architecture in `docs/strategy/R_MODEL_INTELLIGENCE_LAYER.md`.

## 🛡️ Architectural Specifications

### 1. GoogleKeyPool Architecture
To bypass rate limits and maximize throughput, a rotation system for 8 Google API keys will be implemented.
- **Location**: `config/providers.yaml` extension.
- **Strategy**: `round_robin` rotation.
- **Configuration**:
  ```yaml
  providers:
    google-keypool:
      type: keypool
      keys:
        - env: GOOGLE_API_KEY_01
        - env: GOOGLE_API_KEY_02
        - env: GOOGLE_API_KEY_03
        - env: GOOGLE_API_KEY_04
        - env: GOOGLE_API_KEY_05
        - env: GOOGLE_API_KEY_06
        - env: GOOGLE_API_KEY_07
        - env: GOOGLE_API_KEY_08
      rotation_strategy: round_robin
  ```

### 2. CLI & MCP Interface Specifications
Workers will be spawned asynchronously to prevent event-loop blocking, utilizing AnyIO task groups.

**CLI Command**: `omega worker spawn`
**MCP Tool**: `spawn_background_worker`

**Interface Schema**:
- `task_id` (str): Unique identifier for the worker task.
- `prompt` (str): The sensing/discovery prompt.
- `model` (str): Target Gemma 4 model (e.g., `gemma-4-31b-it`).
- `key_index` (int): Index for KeyPool selection (managed by orchestrator).

**Implementation Path**: `src/omega/oracle/orchestrator.py` $\rightarrow$ `spawn_background_worker()`

### 3. Key Management Strategy
- **Storage**: Keys are maintained as environment variables (`GOOGLE_API_KEY_01` through `08`).
- **Retrieval**: The `google-keypool` provider reads these values at runtime.
- **Verification**: A pre-flight check will ensure all 8 keys are present before initiating a parallel batch.

### 4. Sovereign Gold Filter Integration
The 'Sovereign Gold Filter' is the final gate in the worker pipeline, ensuring raw sensing data is compressed before reaching the reasoning layer.

**Execution Pipeline**:
`Inference (Gemma 4)` $\rightarrow$ `Gold Filter (Local Distillation)` $\rightarrow$ `Gold Sheet Output` $\rightarrow$ `Hivemind Registration`

**Gold Filter Protocol**:
1. **Sentry Triage**: Rapid scan (Gemini 3.1-flash-lite) to discard noise.
2. **Local Distillation**: Local Gemma 4 compresses high-value segments into L2/L3 insights.
3. **Gold Synthesis**: Final assembly of the "Gold Sheet" (<16K tokens).

**Gold Sheet Output Schema**:
- `trace_id`: UUID
- `context_source`: "Gemma 4 Sensing"
- `compression_ratio`: X:1
- `structural_anchors`: File paths and function signatures.
- `distilled_insights`: L1 (Narrative), L2 (Insight), L3 (Principle).
- `critical_payload`: Minimized code/config snippet.

### 5. Hivemind Coordination
Every spawned worker will call `omega-hub_hivemind_post_context` to register as a subagent. This provides real-time awareness across the fleet and prevents redundant sensing operations.

---

## 📅 Implementation Timeline
| Phase | Task | Responsibility | Est. Time |
|-------|------|----------------|-----------|
| 1 | Implement `google-keypool` in `providers.py` | Roc Racoon | 1h |
| 2 | Implement `spawn_background_worker` in `orchestrator.py` | Roc Racoon | 2h |
| 3 | Wire `apply_gold_filter` into worker pipeline | Roc Racoon | 1h |
| 4 | Implement `omega worker spawn` CLI command | Roc Racoon | 1h |
| 5 | Final verification via `make test` & Gold Filter audit | Quality | 1h |

---

*⬡ OMEGA ⬡ OpenCode ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_pw15_coord ⬡ COORDINATION*
