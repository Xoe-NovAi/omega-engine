# 🔱 Omega Engine — Reasoning Escalation Triggers (R-07)
# ⬡ OMEGA ⬡ PROMETHEUS ⬡ gemma-4-31b ⬡ opencode ⬡ trc_research ⬡ RESEARCH

**AP Token**: `AP-R07-ESCALATION-v1.0.0`
**Status**: ✅ READY FOR IMPLEMENTATION
**Last Updated**: 2026-05-14

---

## §1 Executive Summary

The Omega Engine utilizes a **Speculative Decoder** pattern where **Iris** (powered by `functiongemma-270m`) acts as the first-pass responder. To ensure a balance between low-latency interface interactions and high-reasoning depth, the Engine must employ a robust escalation mechanism to route queries to frontier reasoning models (Pillar Keepers/Oversouls) when the complexity exceeds Iris's capabilities.

This document defines the confidence thresholds, complexity triggers, and the configuration schema for this routing logic.

---

## §2 Current State Analysis

### Existing Logic (`src/omega/oracle/oracle.py`)
The current implementation in `_assess_iris_confidence` uses a rudimentary heuristic:
- **High Confidence (0.9)**: Direct matches for greetings/farewells.
- **Moderate Confidence (0.5)**: Queries $\le 3$ words.
- **Low Confidence (0.0)**: Presence of a few basic "complexity indicators" (e.g., "why", "how").
- **Default (0.3)**: All other queries.
- **Threshold**: `IRIS_CONFIDENCE_THRESHOLD = 0.4`.

**Critique**: The current model is too permissive, allowing too many ambiguous queries to be handled by the SLM, leading to suboptimal responses for nuanced prompts. It lacks detection for technical, mathematical, or domain-specific complexity.

---

## §3 Proposed Escalation Model

We propose a **Tri-Factor Routing** approach. Escalation occurs if ANY of the following conditions are met:

### 1. Confidence-Based Routing (Probabilistic)
Iris generates a confidence score. If the score falls below the `confidence_threshold`, the query is escalated.
- **Proposed Threshold**: `0.7` (Raised from `0.4` to prioritize quality over speed).

### 2. Complexity-Based Routing (Deterministic)
Queries are analyzed for "hard" features that inherently require high-parameter reasoning.

| Trigger Category | Signal | Examples / Patterns |
|------------------|--------|-------------------|
| **Mathematical** | Operators & Logic | `+`, `-`, `*`, `/`, `=`, `sqrt`, `log`, "calculate", "solve for x" |
| **Programming** | Code Syntax | `def `, `function `, `=>`, `{ }`, `async`, `await`, `import` |
| **Reasoning** | Analytical Verbs | "analyze", "synthesize", "critique", "compare and contrast", "evaluate" |
| **Structural** | Length / Depth | Query length $> 20$ words or multi-step instructions ("First... then...") |

### 3. Intent-Based Routing (Explicit)
User-provided signals that bypass the speculative decoder entirely.
- **User Flags**: `/think`, `/deep`, `deep-think: true`.
- **Urgency**: "urgent", "critical", "immediate".
- **Omega Domain**: Keywords relating to the core engine architecture ("soul evolution", "cross-pollination", "Sovereign", "Axiom").

---

## §4 Proposed Configuration Schema

To make the Engine tunable without code changes, we propose the following schema for `config/reasoning_escalation.yaml`.

```yaml
# 🔱 Omega Reasoning Escalation Config
escalation:
  # Global threshold for SLM (Iris) direct response
  confidence_threshold: 0.7

  # Deterministic triggers for immediate escalation
  triggers:
    complexity:
      # Verbs that signal high-reasoning tasks
      reasoning_keywords: 
        - "analyze"
        - "evaluate"
        - "synthesize"
        - "critique"
        - "compare"
        - "contrast"
        - "solve"
        - "calculate"
        - "derive"
      
      # Regex patterns for technical content
      technical_patterns:
        math: "([\\+\\-\\*/=]|sqrt|log|sum)"
        code: "(def\\s+\\w+|function\\s+\\w+|\\{.*\\}|=>)"
        logic: "(if\\s+then|therefore|consequently)"
      
      # Maximum length before assuming complexity
      max_word_count: 20

    user_flags:
      - "/think"
      - "/deep"
      - "deep-think"
      - "high-precision"

    # Domain-specific keywords that must be handled by Pillar Keepers
    omega_domain:
      - "architectural"
      - "soul evolution"
      - "cross-pollination"
      - "sovereign"
      - "axiom"
      - "pillar"
      - "akashic"
      - "oversoul"

  # Fallback behavior when all providers are exhausted
  fallback_strategy: "local_sovereign" # Options: local_sovereign, mock, error
```

---

## §5 Implementation Note for Implementation Agent

**Target File**: `src/omega/oracle/oracle.py`

1.  **Integration**: Update `_assess_iris_confidence` to load the `reasoning_escalation.yaml` config.
2.  **Logic Flow**:
    - First, check for `user_flags` and `omega_domain` $\rightarrow$ Return `0.0` (Escalate).
    - Second, check for `technical_patterns` and `reasoning_keywords` $\rightarrow$ Return `0.0` (Escalate).
    - Third, check `max_word_count` $\rightarrow$ Return `0.0` (Escalate).
    - Finally, apply the current confidence heuristics, but compare against the new `confidence_threshold`.
3.  **Testing**: Add test cases to `tests/test_oracle.py` covering:
    - A short greeting (Iris handles).
    - A math problem (Escalates).
    - A query containing "soul evolution" (Escalates).
    - A query starting with `/think` (Escalates).
