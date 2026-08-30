---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

model_id: google/gemma-4-26b-a4b-it:free
display_name: Gemma 4 26B A4B IT (Free)
version: '2026-05-17'
provider: openrouter
platform: cloud
tier: T2
status: active
context_window: 262144
max_output_tokens: 8192
capabilities:
  reasoning: 0.85
  code_generation: 0.82
  knowledge: 0.9
  creative: 0.8
  tool_use: false
  structured_output: false
  multimodal: true
  code_execution: false
  parallel_search: false
  workspace_integration: false
pricing:
  input_per_mtok: 0.0
  output_per_mtok: 0.0
  cost_per_1k_tokens_usd: 0.0
free_tier: true
latency_p99_ms: 3500
uptime_percent: 98.5
routing:
  engine_routable: true
  opencode_cli_only: false
  recommended_engine_alternative: null
identity_history: null
community_rating: 4.6/5.0
community_notes:
- "Optimized for efficiency \u2014 26B with A4B attention"
- Multimodal capability
- 262K context window
live_api_state:
  source: openrouter
  last_verified: '2026-05-17'
  last_verified_free: '2026-05-17'
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
  - provider: google
    priority: 4
  local_first_priority: null
tags:
- efficient
- multimodal
- free_tier
- openrouter
- gemma_4
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
  total: 26B
  active: 4B
  architecture: MoE
  experts: 8
  active_experts: 2
  shared_experts: 1
  quantization: BF16
  training_tokens: 2T
  source: official
  verified: true
  verified_date: '2026-07-18'
---

# Gemma 4 26B A4B IT (Free) — Model Card

## Overview
Google's Gemma 4 26B with A4B attention. Optimized for efficiency. Multimodal. 262K context. Free on OpenRouter.

## Intended Use
- **Primary**: Efficient reasoning, multimodal tasks, balanced workloads
- **Secondary**: Code generation, knowledge retrieval
- **Avoid**: Maximum-depth reasoning (use 31B variant)

## Cognitive Mode: Efficient Iterative Reasoning
Balanced capability with lower compute. Multimodal support. Good for mixed workloads.

## Operational Metrics
| Metric | Value |
|--------|-------|
| Context Window | 262,144 |
| Latency (P99) | 3,500ms |
| Uptime | 98.5% |
| Community Rating | 4.6/5.0 |
| Cost | $0.00 (free tier) |

## Known Issues
1. **Less Depth**: 26B vs 31B — less reasoning depth.
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
Available via OpenRouter (priority 4) and Google AI Studio (priority 4). Engine-routable.
