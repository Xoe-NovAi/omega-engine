---
# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

model_id: poolside/laguna-m.1:free
display_name: Laguna M.1 (Free)
version: '2026-05-17'
provider: openrouter
platform: cloud
tier: T2
status: active
context_window: 262144
max_output_tokens: 262144
capabilities:
  reasoning: 0.8
  code_generation: 0.9
  knowledge: 0.82
  creative: 0.75
  tool_use: true
  structured_output: true
  multimodal: false
  code_execution: false
  parallel_search: false
  workspace_integration: false
pricing:
  input_per_mtok: 0.0
  output_per_mtok: 0.0
  cost_per_1k_tokens_usd: 0.0
  cached_input_per_mtok: 0.0
free_tier: true
latency_p99_ms: 2500
uptime_percent: 99.0
routing:
  engine_routable: true
  opencode_cli_only: false
  recommended_engine_alternative: null
identity_history: null
community_rating: 4.3/5.0
community_notes:
- "Poolside's Laguna M.1 \u2014 code-specialized"
- 128K context window
- Strong code generation
live_api_state:
  source: openrouter-api-2026-07-19
  last_verified: '2026-07-18'
  last_verified_free: '2026-05-17'
  confidence: high
research_profile:
  reasoning_depth: iterative
  tool_fidelity: high
  failure_signature: hallucination
  shadow_focus: verify_facts
  guardrails:
  - Verify code against actual execution
  - Use RAG for API documentation
empirical_evidence:
  test_runs: []
  synergies: []
provider_fabric:
  available_via:
  - provider: openrouter
    priority: 4
  local_first_priority: null
tags:
- coding
- specialized
- free_tier
- openrouter
- poolside
- laguna
created_at: '2026-05-17'
updated_at: '2026-07-18'
schema_version: 1.2.0
parameters:
  temperature: 0.5
  top_p: 0.9
  top_k: 40
  repetition_penalty: 1.0
  stop_sequences: []
  presence_penalty: 0.0
  frequency_penalty: 0.0
benchmark_sources:
  reasoning: ''
  code_generation: ''
  knowledge: ''
  creative: ''
  tool_use: ''
  structured_output: ''
  multimodal: ''
  overall: ''
architecture:
  total: Unknown
  active: Unknown
  architecture: dense
  experts: 0
  active_experts: 0
  shared_experts: 0
  quantization: Unknown
  training_tokens: Unknown
  source: estimated
  verified: false
---

# Laguna M.1 (Free) — Model Card

## Overview
Poolside's Laguna M.1. Code-specialized. 128K context. Strong code generation. Free on OpenRouter.

## Intended Use
- **Primary**: Code generation, refactoring, debugging
- **Secondary**: Technical reasoning, API integration
- **Avoid**: Creative writing, general knowledge

## Cognitive Mode: Code-Specialized Reasoning
Optimized for code. Strong tool use for development workflows.

## Operational Metrics
| Metric | Value |
|--------|-------|
| Context Window | 131,072 |
| Latency (P99) | 2,500ms |
| Uptime | 99.0% |
| Community Rating | 4.3/5.0 |
| Cost | $0.00 (free tier) |

## Known Issues
1. **Specialized**: Not a generalist.
2. **Daily Quota**: OpenRouter free tier resets at 00:00 UTC.

## Research Profile
```yaml
reasoning_depth: iterative
tool_fidelity: high
failure_signature: hallucination
shadow_focus: verify_facts
guardrails:
  - "Verify code against actual execution"
  - "Use RAG for API documentation"
```

## Provider Access
Available via OpenRouter (priority 4). Engine-routable.
