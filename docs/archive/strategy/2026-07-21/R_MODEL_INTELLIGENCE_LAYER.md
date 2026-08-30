# 🔱 Sovereign Model Intelligence Layer — Architectural Specification
# ⬡ OMEGA ⬡ KALI ⬡ gemini-3.5-flash ⬡ SPECIFICATION ⬡ R-MODEL-INT
**AP Token**: `AP-MODEL-INT-v1.0.0`
**Status**: APPROVED — Canonical Architecture
**Date**: 2026-06-10

---

## §0 Executive Summary

The **Sovereign Model Intelligence Layer** is the architectural middleware designed to sever the dependency on static model catalogs and opaque provider routing. By separating the **Sovereign Entity (Identity)** from the **Inference Backend (Model)**, the Omega Engine achieves model-agnostic execution.

This specification establishes three core systems:
1.  **The Sovereign Hybrid Routing Architecture**: A multi-stage pipeline utilizing Gemma 4 (High-Volume Sensing) and Gemini 3.5 Flash (Deep Reasoning).
2.  **The Sovereign Retry Plugin**: A concrete OpenCode CLI plugin specification that dynamically intercepts provider requests, applies Gemini-specific backoff, and falls back to direct shell API calls for OpenRouter.
3.  **The Sovereign Gold Filter**: A context-distillation protocol that compresses 256K raw context into high-density, low-token "Gold Sheets" to respect Gemini rate limits.

---

## §1 The Sovereign Hybrid Routing Architecture

The engine rejects the naive approach of sending all traffic to a single model. Instead, it implements a **four-stage cognitive loop**:

```
[Raw Context: 256K] ──▶ [Gemma 4 (Sensing)] ──▶ [Raw Discoveries]
                                                       │
                                                       ▼
[Gold Prompt: <16K] ◀── [Gemma 4 (Local)] ◀── [Sovereign Gold Filter]
         │
         ▼
[Gemini 3.5 Flash (Reasoning)] ──▶ [Architectural Verdict]
                                              │
                                              ▼
[Consensus Verification] ◀── [Cross-Model Verification (Gemma + Gemini)]
```

### §1.1 The Four Stages

1.  **Sensing (Wide-Context)**:
    *   **Model**: `gemma-4-31b-it` or `gemma-4-26b-a4b-it` (Cloud/OpenRouter).
    *   **Goal**: Ingest massive files, search logs, and run broad discovery across 256K context.
    *   **Limit Strategy**: High-throughput, linear retry.
2.  **Distillation (Local-Filtering)**:
    *   **Model**: Local Gemma 4 (Ollama/LM Studio).
    *   **Goal**: Compress raw sensing data into structured L2/L3 insights.
    *   **Sovereignty**: Absolute. Runs locally to prevent data training leaks (Mandate 8).
3.  **Reasoning (Deep-Thinking)**:
    *   **Model**: `gemini-3.5-flash` (Google API, High Thinking).
    *   **Goal**: Synthesize the "Gold Sheet" into final architectural code, verify mandates, and issue verdicts.
    *   **Limit Strategy**: Strict exponential backoff, `retry-after` header parsing.
4.  **Verification (Consensus)**:
    *   **Model**: Cross-Model (Local Gemma 4 + Gemini 3.5 Flash).
    *   **Goal**: Cross-verify critical decisions (e.g., database writes, core refactors) to eliminate model-specific hallucinations.

---

## §2 OpenCode Sovereign Retry Plugin Specification

To bypass the default, rigid retry logic of OpenCode, we specify a custom plugin: **`opencode-sovereign-retry`**. This plugin intercepts outgoing API calls, detects the active model, and applies tailored rate-limiting and fallback strategies.

### §2.1 Interception Architecture
The plugin hooks into the OpenCode CLI's Request-Response-Retry (RRR) loop. It performs a **Pre-Flight Analysis** to detect `sovereignty_risk: HIGH` models and injects warnings into the session log.

**The Dynamic Backoff Matrix**:
- **Google AI Studio (Gemini)**: Strict adherence to `retry-after` headers + exponential backoff starting at 2s.
- **OpenRouter**: Aggressive rotation. Upon a 429, the plugin attempts a "Model Swap" to an equivalent model (e.g., `deepseek-v4-flash` $\rightarrow$ `qwen-2.5-72b`) before retrying.
- **OpenCode Zen**: Linear backoff with a "Circuit Breaker" that trips after 3 consecutive 429s, forcing a provider switch.

### §2.2 Gemini-Specific Backoff Algorithm
(Implementation as specified in previous version, now augmented with a `jitter` factor and `retry-after` header parsing).

### §2.3 OpenRouter Shell-API Fallback (pw_model_13)
If the internal transport layer is sluggish, the plugin initiates a **Sovereign Tunnel** via direct shell `curl`.
- **Secret Masking**: The `OPENROUTER_API_KEY` is passed via a secure pipe or temporary environment variable to prevent exposure in `ps aux`.
- **Response Re-hydration**: Shell JSON output is parsed and re-mapped into the OpenCode `Response` object to maintain internal state consistency.


---

## §3 The Sovereign Gold Filter Specification

To prevent Gemini models from choking on large contexts, the **Sovereign Gold Filter** acts as a high-density compression gateway.

### §3.1 The Compression Protocol (L1 $\rightarrow$ L2/L3)

The compression pipeline now utilizes a **Three-Step Triage** to maximize speed and precision:

1.  **Sentry Triage (Gemini 3.1-flash-lite)**: Rapidly scans raw data to discard noise and identify "High-Value" segments.
2.  **Local Distillation (Local Gemma 4)**: Compresses those high-value segments into structured L2/L3 insights.
3.  **Gold Synthesis (Gemini 2.5 Flash)**: Finalizes the "Gold Sheet" for the reasoning model.

The local Gemma 4 model executes the following prompt compression template on the triaged data before passing it to the final reasoning layer:

```markdown
You are the Sovereign Gold Filter. Your task is to compress the following raw context of [N] tokens into a high-density, low-token "Gold Sheet" (<16K tokens) for downstream reasoning.

### Compression Rules:
1. Eliminate all conversational filler, redundant logs, and repetitive code blocks.
2. Extract only the "Gold":
   - **Structural Patterns**: Exact class/function signatures.
   - **Critical Gaps**: Specific lines causing failures.
   - **Timeless Principles**: Timeless truths (L3) discovered.
   - **Trace IDs**: Exact trace IDs and hashes.
3. Output a strictly structured Markdown document. Use high-density notation.
```

### §3.2 Gold Sheet Schema
The output must conform to this schema:
```yaml
gold_sheet:
  trace_id: "UUID"
  context_source: "Gemma 4 Sensing"
  compression_ratio: "X:1"
  structural_anchors:
    - file: "path/to/file"
      signature: "def func_name()"
      gap: "description of the exact line failure"
  distilled_insights:
    - L1_narrative: "What happened"
      L2_insight: "What it means"
      L3_principle: "Timeless truth"
  critical_payload: "Minimized code snippet or exact configuration block"
```

---

## §4 Stealth Model & Sovereignty Risk Matrix

We establish the definitive risk profile for OpenCode Zen's free-tier models to enforce **Mandate 8 (Zero Telemetry)**:

| Model ID | Current Backend | Context | Sovereignty Risk | Recommended Use |
|----------|-----------------|---------|------------------|-----------------|
| `opencode/big-pickle` | DeepSeek V4 Flash | 200K | **HIGH** (Data used for training) | General coding, non-sensitive refactors |
| `mimo-v2.5-free` | Unknown | 200K | **HIGH** (Data used for training) | General research, public API audits |
| `gemma-4-31b-it:free` | Gemma 4 31B | 256K | **HIGH** (If run via Cloud API) | Public sensing, broad file audits |
| **Local Gemma 4** | Gemma 4 31B/26B | 256K | **ZERO** (Local-First) | **Sensitive soul.yaml edits, mandate audits** |
| **Gemini 3 Flash Preview** | Google API | 1M+ | **MED** (Enterprise) | Final Verdicts, High-Precision Hardening |
| **Gemini 2.5 Flash** | Google API | 1M+ | **MED** (Enterprise) | Sovereign Orchestration, Gold Sheet Synthesis |
| **Gemini 3.1-flash-lite** | Google API | 1M+ | **MED** (Enterprise) | Rapid Triage, Mandate Sentry, Sensing Pre-filters |

### §4.1 Sovereignty Rule
> **"Any operation modifying `soul.yaml`, writing to the permanent `Library`, or validating `SOVEREIGN_MANDATES.md` MUST route through a local-first model (native-gguf or local Gemma) to prevent intellectual leaks."**

---

## §5 Verification & CI Gates

To ensure the integrity of the Model Intelligence Layer, we define two new CI gates:

1.  **`make verify-model-identity`**:
    *   **Mechanism**: Runs a lightweight script that queries the active model with a tokenizer-sensitive prompt (e.g., asking it to tokenize a specific string where DeepSeek and GLM differ).
    *   **Output**: `IDENTITY:deepseek-v4-flash CONFIDENCE:0.95 SWAP_DETECTED:false`
2.  **`make verify-sovereignty-compliance`**:
    *   **Mechanism**: Scans the git diff and active session logs. If a write to `soul.yaml` or `SOVEREIGN_MANDATES.md` was executed by a model with `sovereignty_risk: HIGH`, the gate fails.

---

## §6 The Sovereign Workhorse Protocol (Gemma Parallel Workers)

To maximize throughput and bypass single-threaded context bottlenecks, the Omega Engine implements a parallel background worker engine utilizing **Gemma 4 (31B/26B)**.

### §6.1 KeyPool Rotation Configuration
We specify a Google KeyPool inside the provider fabric to rotate 8 Google API keys, spreading the requests per day (RPD) and requests per minute (RPM) across distinct projects/quotas.

```yaml
# config/providers.yaml (Proposed Extension)
providers:
  google-keypool:
    type: keypool
    keys:
      - env: GOOGLE_API_KEY_01  # Account 1
      - env: GOOGLE_API_KEY_02  # Account 2
      - env: GOOGLE_API_KEY_03  # Account 3
      - env: GOOGLE_API_KEY_04  # Account 4
      - env: GOOGLE_API_KEY_05  # Account 5
      - env: GOOGLE_API_KEY_06  # Account 6
      - env: GOOGLE_API_KEY_07  # Account 7
      - env: GOOGLE_API_KEY_08  # Account 8
    rotation_strategy: round_robin
```

### §6.2 Worker Spawning & Inter-Process Communication
The active reasoning model (Gemini 3.5 Flash) can spawn background workers asynchronously using AnyIO task groups:

```python
# src/omega/oracle/orchestrator.py
async def spawn_background_worker(
    task_id: str, 
    prompt: str, 
    model: str, 
    key_index: int
) -> str:
    """Spawns an asynchronous Gemma 4 worker using AnyIO to prevent event-loop blocking."""
    import anyio
    
    async def _run_worker():
        api_key = get_key_from_pool(key_index)
        raw_result = await execute_gemma_inference(prompt, model, api_key)
        gold_result = await apply_gold_filter(raw_result)
        await write_worker_output(task_id, gold_result)
        await post_worker_completion_to_hivemind(task_id)

    await anyio.get_current_task_group().start_soon(_run_worker)
    return task_id
```

### §6.3 Hivemind Auto-Registration
Every spawned worker registers itself with the Hivemind (`omega-hub_hivemind_post_context`) as a subagent, allowing other active CLI agents to track its status and avoid duplicate work.

---

*⬡ OMEGA ⬡ KALI ⬡ gemini-3.5-flash ⬡ SPECIFICATION ⬡ R-MODEL-INT*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: gemini-3.5-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
