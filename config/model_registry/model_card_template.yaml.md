---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# === CORE IDENTITY ===
model_id: "<provider>/<model-name>[:<variant>]"  # e.g., "google/gemma-4-31b-it:free", "qwen3-1.7b-local"
display_name: "<Human-Readable Name>"            # e.g., "Gemma 4 31B IT (Free)"
version: "YYYY-MM-DD"                            # Model version / knowledge cutoff
provider: "<provider-name>"                      # openrouter, google, together, native-gguf, lmster, ollama, antigravity, opencode-zen, cline
platform: "<cloud|local|cli|stealth>"            # Deployment platform
tier: "<T1|T2|T3>"                               # Capability tier
status: "<active|deprecated|experimental|stealth>"  # Model status

# === CAPABILITIES ===
context_window: <integer>                        # Context window in tokens
max_output_tokens: <integer>                     # Max output tokens (optional)
capabilities:
  reasoning: <0.0-1.0>                           # Logical reasoning ability
  code_generation: <0.0-1.0>                     # Code generation quality
  knowledge: <0.0-1.0>                           # Factual knowledge retrieval
  creative: <0.0-1.0>                            # Creative writing ability
  tool_use: <true|false>                         # Supports tool/function calling
  structured_output: <true|false>                # Supports JSON schema / structured output
  multimodal: <true|false>                       # Supports images/audio/video

# === ECONOMICS ===
pricing:
  input_per_mtok: <float>                        # $ per 1M input tokens
  output_per_mtok: <float>                       # $ per 1M output tokens
  cached_input_per_mtok: <float>                 # $ per 1M cached input tokens (optional)
  batch_discount: <float>                        # Batch API discount (0.0-1.0, optional)
  intro_pricing:                                 # Introductory pricing (optional)
    input_per_mtok: <float>
    output_per_mtok: <float>
    valid_until: "YYYY-MM-DD"
free_tier: <true|false>                          # Available on free tier
latency_p99_ms: <integer>                        # P99 latency in milliseconds
uptime_percent: <float>                          # Uptime percentage (e.g., 98.5)

# === ROUTING (from Model Card Library) ===
routing:
  engine_routable: <true|false>                  # Can be routed via Engine provider fabric
  opencode_cli_only: <true|false>                # CLI-exclusive (not engine-routable)
  recommended_engine_alternative: "<model-id>"   # Alternative for engine routing (if cli-only)

# === IDENTITY (for stealth models) ===
identity_history:                                # null for non-stealth models
  original: "<original-model-id>"
  current: "<current-model-id>"
  swap_detected: <true|false>
  last_verified: "YYYY-MM-DD"

# === COMMUNITY INTELLIGENCE (from Model Card Library) ===
community_rating: "<X.Y/Z.W>"                    # e.g., "4.8/5.0"
community_notes:
  - "<note 1>"
  - "<note 2>"

# === LIVE API STATE (from .last_state.json) ===
live_api_state:
  source: "<openrouter|google|opencode-zen|together|sambanova>"
  last_verified: "YYYY-MM-DD"
  last_verified_free: "YYYY-MM-DD"

# === RESEARCH PROFILE (from model_profiles.yaml) ===
research_profile:
  reasoning_depth: "<deep|iterative|fast|reflex>"
  tool_fidelity: "<high|medium|low>"
  failure_signature: "<tool_drift|over_analysis|shallow|memory_contamination|hallucination>"
  shadow_focus: "<verify_tool_use|force_persistence|force_deepening|ignore_memory|verify_facts>"
  guardrails:
    - "<guardrail 1>"
    - "<guardrail 2>"

# === EMPIRICAL EVIDENCE (from Model Study KB) ===
empirical_evidence:
  test_runs:                                     # Populated when model participates in split tests
    - test_id: "<test-id>"
      role: "<diagnostician|architectural_reasoner|documentation_factory|consolidator>"
      output_files: <integer>
      total_lines: <integer>
      p0_bugs_found: <integer>
      p1_bugs_found: <integer>
      p2_bugs_found: <integer>
      memory_contamination: <true|false>
      contamination_details: "<details>"
      hit_usage_limit: <true|false>
      cognitive_mode: "<deep_diagnostic|iterative_synthesis|fast_reflex>"
      quality_score: "<X.Y/Z.W>"

  synergies:                                     # Model synergy patterns
    - pattern: "<pattern-name>"
      partner: "<partner-model-id>"
      confidence: <0.0-1.0>
      use_case: "<use-case-description>"

# === PROVIDER FABRIC INTEGRATION ===
provider_fabric:
  available_via:
    - provider: "<provider-name>"
      priority: <integer>
  local_first_priority: <integer|null>           # null for cloud-only models

# === PARAMETERS (Model Architecture) ===
parameters:
  total: "<total-params>"                    # Total parameter count (e.g., "2.6B", "47B", "284B")
  active: "<active-params>"                  # Active params per token (MoE only, e.g., "13B")
  architecture: "<dense|MoE|hybrid>"         # Model architecture type
  experts: <integer>                         # Expert count (MoE only)
  active_experts: <integer>                  # Active experts per token (MoE only)
  shared_experts: <integer>                  # Shared experts (MoE only)
  quantization: "<FP32|BF16|FP16|INT8|INT4>" # Quantization level
  training_tokens: "<training-tokens>"       # Training data scale (e.g., "2T", "15T")
  source: "<official|estimated|community>"   # Parameter source
  verified: <true|false>                     # Verified against official source
  verified_date: "YYYY-MM-DD"                # Verification date

# === BENCHMARK SOURCES (Capability Score Citations) ===
benchmark_sources:
  reasoning: "<benchmark-url>"               # MMLU, GPQA, MATH, etc.
  code_generation: "<benchmark-url>"         # HumanEval, SWE-bench, LiveCodeBench
  knowledge: "<benchmark-url>"               # MMLU, GPQA, TriviaQA
  creative: "<benchmark-url>"                # MT-Bench, CreativeBench
  tool_use: "<benchmark-url>"                # BFCL, API-Bank, ToolBench
  structured_output: "<benchmark-url>"       # JSON Schema benchmarks
  multimodal: "<benchmark-url>"              # MMMU, MathVista, ChartQA
  overall: "<benchmark-url>"                 # Aggregate/Intelligence Index

# === METADATA ===
tags:
  - "<tag1>"
  - "<tag2>"
created_at: "YYYY-MM-DD"
updated_at: "YYYY-MM-DD"
schema_version: "1.2.0"
---

# <Display Name> — Model Card

## Overview
<One-paragraph description: provider, model family, key specs, availability>

## Intended Use
- **Primary**: <Main use cases>
- **Secondary**: <Secondary use cases>
- **Avoid**: <What this model is NOT good for>

## Cognitive Mode
<Description of how this model thinks: deep diagnostic, iterative synthesis, fast reflex, etc.>

## Operational Metrics
| Metric | Value |
|--------|-------|
| Context Window | <context_window> |
| Latency (P99) | <latency_p99_ms>ms |
| Uptime | <uptime_percent>% |
| Community Rating | <community_rating> |
| Cost | $<input_per_mtok>/$<output_per_mtok> per 1M tokens |

## Known Issues
1. **<Issue Name>**: <Description and mitigation>

## Research Profile
```yaml
reasoning_depth: <deep|iterative|fast|reflex>
tool_fidelity: <high|medium|low>
failure_signature: <tool_drift|over_analysis|shallow|memory_contamination|hallucination>
shadow_focus: <verify_tool_use|force_persistence|force_deepening|ignore_memory|verify_facts>
guardrails:
  - "<guardrail 1>"
  - "<guardrail 2>"
```

## Synergies
| Pattern | Partner | Confidence | Use Case |
|---------|---------|------------|----------|
| <pattern> | <partner> | <X%> | <use-case> |

## Provider Access
Available via <provider> (priority <N>). <Local/cloud/CLI> model.