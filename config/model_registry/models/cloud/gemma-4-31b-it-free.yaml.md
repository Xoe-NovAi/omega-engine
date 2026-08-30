---
# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

model_id: google/gemma-4-31b-it:free
display_name: Gemma 4 31B IT (Free)
version: '2026-05-17'
provider: openrouter
platform: cloud
tier: T3
status: active
context_window: 262144
max_output_tokens: 262144
capabilities:
  reasoning: 0.92
  code_generation: 0.88
  knowledge: 0.96
  creative: 0.85
  tool_use: false
  structured_output: false
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
latency_p99_ms: 4200
uptime_percent: 98.5
routing:
  engine_routable: true
  opencode_cli_only: false
  recommended_engine_alternative: null
identity_history: null
community_rating: 4.8/5.0
community_notes:
- State-of-the-art reasoning for zero cost.
- Watch daily quota resets (00:00 UTC).
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
  - Write intermediate evidence to disk every 3 tool calls
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
- reasoning
- knowledge
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
  total: 31B
  active: 31B
  architecture: dense
  experts: 0
  active_experts: 0
  shared_experts: 0
  quantization: BF16
  training_tokens: 2T
  source: official
  verified: true
  verified_date: '2026-07-18'
---

# Gemma 4 31B IT (Free) — Model Card

## Overview
Google's Gemma 4 31B instruction-tuned model. Available free via OpenRouter. State-of-the-art reasoning for zero cost. 262K context window.

## Intended Use
- **Primary**: Deep reasoning, knowledge retrieval, complex synthesis
- **Secondary**: Code generation, multi-step logic
- **Avoid**: Creative writing, real-time interaction (latency ~4.2s)

## Cognitive Mode: Iterative Reasoning
Strong synthesis but needs forcing to deepen. 256K context allows holding full evidence sets. Guardrails required to prevent shallow single-pass research.

## Operational Metrics
| Metric | Value |
|--------|-------|
| Context Window | 262,144 |
| Latency (P99) | 4,200ms |
| Uptime | 98.5% |
| Community Rating | 4.8/5.0 |
| Cost | $0.00 (free tier) |

## Known Issues
1. **Shallow Research Tendency**: Context wealth creates illusion of depth; model summarizes instead of deepens.
2. **Daily Quota**: OpenRouter free tier resets at 00:00 UTC.
3. **Tool Fidelity**: Medium — drifts on >5 step chains.

## Research Profile
```yaml
reasoning_depth: iterative
tool_fidelity: medium
failure_signature: shallow
shadow_focus: force_deepening
guardrails:
  - "Force 3+ tool rounds before ANY synthesis"
  - "Require explicit 'deepen' pass after first draft"
  - "Write intermediate evidence to disk every 3 tool calls"
```

## Provider Access
Available via OpenRouter (priority 4) and Google AI Studio (priority 4). Not available via local provider fabric (cloud-only model).
