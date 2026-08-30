---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

model_id: nvidia/nemotron-nano-9b-v2:free
display_name: Nemotron Nano 9B V2 (Free)
version: '2026-05-17'
provider: openrouter
platform: cloud
tier: T1
status: active
context_window: 128000
max_output_tokens: 128000
capabilities:
  reasoning: 0.65
  code_generation: 0.6
  knowledge: 0.75
  creative: 0.7
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
latency_p99_ms: 1200
uptime_percent: 99.5
routing:
  engine_routable: true
  opencode_cli_only: false
  recommended_engine_alternative: null
identity_history: null
community_rating: 4.0/5.0
community_notes:
- NVIDIA's Nemotron Nano 9B V2
- 128K context window
- Small but capable
live_api_state:
  source: openrouter-api-2026-07-19
  last_verified: '2026-07-18'
  last_verified_free: '2026-05-17'
  confidence: high
research_profile:
  reasoning_depth: reflex
  tool_fidelity: low
  failure_signature: shallow
  shadow_focus: force_deepening
  guardrails:
  - Do NOT use for reasoning tasks
  - Use for classification, extraction, simple QA
empirical_evidence:
  test_runs: []
  synergies: []
provider_fabric:
  available_via:
  - provider: openrouter
    priority: 4
  local_first_priority: null
tags:
- reflex
- fast
- small
- free_tier
- openrouter
- nemotron_nano
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
  total: 9B
  active: 9B
  architecture: dense
  experts: 0
  active_experts: 0
  shared_experts: 0
  quantization: BF16
  training_tokens: Unknown
  source: official
  verified: true
  verified_date: '2026-07-18'
---

# Nemotron Nano 9B V2 (Free) — Model Card

## Overview
NVIDIA's Nemotron Nano 9B V2. 128K context. Small but capable. Reflex tasks. Free on OpenRouter.

## Intended Use
- **Primary**: Classification, extraction, simple QA, reflex tasks
- **Secondary**: High-context simple tasks
- **Avoid**: Reasoning, code generation, complex synthesis

## Cognitive Mode: Reflex
Fast response. High context for size. Not a reasoning model.

## Operational Metrics
| Metric | Value |
|--------|-------|
| Context Window | 131,072 |
| Latency (P99) | 1,200ms |
| Uptime | 99.5% |
| Community Rating | 4.0/5.0 |
| Cost | $0.00 (free tier) |

## Known Issues
1. **Not for Reasoning**: Shallow on complex tasks.
2. **Daily Quota**: OpenRouter free tier resets at 00:00 UTC.

## Research Profile
```yaml
reasoning_depth: reflex
tool_fidelity: low
failure_signature: shallow
shadow_focus: force_deepening
guardrails:
  - "Do NOT use for reasoning tasks"
  - "Use for classification, extraction, simple QA"
```

## Provider Access
Available via OpenRouter (priority 4). Engine-routable.
