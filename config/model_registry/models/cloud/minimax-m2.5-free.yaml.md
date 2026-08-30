---
# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

model_id: minimax/minimax-m2.5:free
display_name: MiniMax M2.5 (Free)
version: '2026-05-17'
provider: openrouter
platform: cloud
tier: T3
status: active
context_window: 204800
max_output_tokens: 204800
capabilities:
  reasoning: 0.88
  code_generation: 0.85
  knowledge: 0.9
  creative: 0.95
  tool_use: false
  structured_output: false
  multimodal: false
  code_execution: false
  parallel_search: false
  workspace_integration: false
pricing:
  input_per_mtok: 0.00015
  output_per_mtok: 0.0009
  cost_per_1k_tokens_usd: 0.0
  cached_input_per_mtok: 4.9999999999999996e-05
free_tier: true
latency_p99_ms: 3800
uptime_percent: 98.0
routing:
  engine_routable: true
  opencode_cli_only: false
  recommended_engine_alternative: null
identity_history: null
community_rating: 4.6/5.0
community_notes:
- Exceptional for long-form synthesis
- Strong creative writing
- 204.8K context window
live_api_state:
  source: openrouter-api-2026-07-19
  last_verified: '2026-07-18'
  last_verified_free: '2026-05-17'
  confidence: high
research_profile:
  reasoning_depth: iterative
  tool_fidelity: medium
  failure_signature: shallow
  shadow_focus: force_deepening
  guardrails:
  - Force 3+ tool rounds before ANY synthesis
  - Require explicit 'deepen' pass after first draft
empirical_evidence:
  test_runs: []
  synergies: []
provider_fabric:
  available_via:
  - provider: openrouter
    priority: 4
  local_first_priority: null
tags:
- creative
- synthesis
- free_tier
- openrouter
- minimax
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
  architecture: MoE
  experts: 0
  active_experts: 0
  shared_experts: 0
  quantization: Unknown
  training_tokens: Unknown
  source: estimated
  verified: false
---

# MiniMax M2.5 (Free) — Model Card

## Overview
MiniMax M2.5. 204.8K context window. Exceptional for long-form synthesis and creative writing. Free on OpenRouter.

## Intended Use
- **Primary**: Long-form synthesis, creative writing, narrative generation
- **Secondary**: Complex reasoning with creative angle
- **Avoid**: Code generation (not specialized), real-time tasks

## Cognitive Mode: Creative Synthesis
Excels at weaving long narratives and synthesizing large evidence sets into coherent output. Strong creative capability.

## Operational Metrics
| Metric | Value |
|--------|-------|
| Context Window | 204,800 |
| Latency (P99) | 3,800ms |
| Uptime | 98.0% |
| Community Rating | 4.6/5.0 |
| Cost | $0.00 (free tier) |

## Known Issues
1. **Creative Bias**: May over-creative in analytical tasks.
2. **Daily Quota**: OpenRouter free tier resets at 00:00 UTC.

## Research Profile
```yaml
reasoning_depth: iterative
tool_fidelity: medium
failure_signature: shallow
shadow_focus: force_deepening
guardrails:
  - "Force 3+ tool rounds before ANY synthesis"
  - "Require explicit 'deepen' pass after first draft"
```

## Provider Access
Available via OpenRouter (priority 4). Engine-routable.
