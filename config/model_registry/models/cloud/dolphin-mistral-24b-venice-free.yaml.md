---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

model_id: cognitivecomputations/dolphin-mistral-24b-venice-edition:free
display_name: Dolphin Mistral 24B Venice Edition (Free)
version: '2026-05-17'
provider: openrouter
platform: cloud
tier: T2
status: active
context_window: 32768
max_output_tokens: 16384
capabilities:
  reasoning: 0.75
  code_generation: 0.8
  knowledge: 0.8
  creative: 0.85
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
free_tier: true
latency_p99_ms: 2200
uptime_percent: 99.0
routing:
  engine_routable: true
  opencode_cli_only: false
  recommended_engine_alternative: null
identity_history: null
community_rating: 4.2/5.0
community_notes:
- "Cognitive Computations' Dolphin \u2014 uncensored"
- "Venice edition \u2014 24B parameters"
- 32K context window
live_api_state:
  source: openrouter
  last_verified: '2026-05-17'
  last_verified_free: '2026-05-17'
research_profile:
  reasoning_depth: iterative
  tool_fidelity: medium
  failure_signature: hallucination
  shadow_focus: verify_facts
  guardrails:
  - Verify claims against source documents
  - "Uncensored \u2014 may generate unsafe content"
empirical_evidence:
  test_runs: []
  synergies: []
provider_fabric:
  available_via:
  - provider: openrouter
    priority: 4
  local_first_priority: null
tags:
- uncensored
- free_tier
- openrouter
- dolphin
- venice
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
  total: 24B
  active: 24B
  architecture: dense
  experts: 0
  active_experts: 0
  shared_experts: 0
  quantization: FP16
  training_tokens: Unknown
  source: community
  verified: false
---

# Dolphin Mistral 24B Venice Edition (Free) — Model Card

## Overview
Cognitive Computations' Dolphin Mistral 24B Venice Edition. Uncensored. 32K context. Free on OpenRouter.

## Intended Use
- **Primary**: Uncensored reasoning, creative tasks
- **Secondary**: Code generation, tool use
- **Avoid**: Production use without safety review

## Cognitive Mode: Uncensored Iterative Reasoning
No safety filters. Venice edition. Use with caution in production.

## Operational Metrics
| Metric | Value |
|--------|-------|
| Context Window | 32,768 |
| Latency (P99) | 2,200ms |
| Uptime | 99.0% |
| Community Rating | 4.2/5.0 |
| Cost | $0.00 (free tier) |

## Known Issues
1. **Uncensored**: No safety filters — may generate unsafe content.
2. **Daily Quota**: OpenRouter free tier resets at 00:00 UTC.

## Research Profile
```yaml
reasoning_depth: iterative
tool_fidelity: medium
failure_signature: hallucination
shadow_focus: verify_facts
guardrails:
  - "Verify claims against source documents"
  - "Uncensored — may generate unsafe content"
```

## Provider Access
Available via OpenRouter (priority 4). Engine-routable.
