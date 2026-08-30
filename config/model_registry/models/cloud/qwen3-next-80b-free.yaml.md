---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

model_id: qwen/qwen3-next-80b-a3b-instruct:free
display_name: Qwen3 Next 80B A3B Instruct (Free)
version: '2026-05-17'
provider: openrouter
platform: cloud
tier: T3
status: active
context_window: 1000000
max_output_tokens: 1000000
capabilities:
  reasoning: 0.9
  code_generation: 0.88
  knowledge: 0.92
  creative: 0.85
  tool_use: true
  structured_output: true
  multimodal: false
  code_execution: false
  parallel_search: false
  workspace_integration: false
pricing:
  input_per_mtok: 0.000325
  output_per_mtok: 0.00195
  cost_per_1k_tokens_usd: 0.0
  cached_input_per_mtok: 0.0
free_tier: true
latency_p99_ms: 4000
uptime_percent: 98.5
routing:
  engine_routable: true
  opencode_cli_only: false
  recommended_engine_alternative: null
identity_history: null
community_rating: 4.6/5.0
community_notes:
- "Qwen3 Next \u2014 80B A3B MoE"
- 262K context window
- New generation Qwen
live_api_state:
  source: openrouter-api-2026-07-19
  last_verified: '2026-07-18'
  last_verified_free: '2026-05-17'
  confidence: high
research_profile:
  reasoning_depth: deep
  tool_fidelity: high
  failure_signature: hallucination
  shadow_focus: verify_facts
  guardrails:
  - Verify claims against source documents
  - Use RAG for factual grounding
  - Monitor MoE routing stability
empirical_evidence:
  test_runs: []
  synergies: []
provider_fabric:
  available_via:
  - provider: openrouter
    priority: 4
  local_first_priority: null
tags:
- moe
- reasoning
- free_tier
- openrouter
- qwen3_next
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
  total: 80B
  active: 3B
  architecture: MoE
  experts: 27
  active_experts: 1
  shared_experts: 0
  quantization: BF16
  training_tokens: Unknown
  source: official
  verified: true
  verified_date: '2026-07-18'
---

# Qwen3 Next 80B A3B Instruct (Free) — Model Card

## Overview
Alibaba's Qwen3 Next. 80B A3B MoE. 262K context. New generation Qwen. Free on OpenRouter.

## Intended Use
- **Primary**: Deep reasoning, complex synthesis, code generation
- **Secondary**: Tool use, structured output
- **Avoid**: Real-time tasks (latency), multimodal

## Cognitive Mode: MoE Deep Reasoning
Mixture of Experts architecture. 80B total, 3B active. 262K context for massive evidence.

## Operational Metrics
| Metric | Value |
|--------|-------|
| Context Window | 262,144 |
| Latency (P99) | 4,000ms |
| Uptime | 98.5% |
| Community Rating | 4.6/5.0 |
| Cost | $0.00 (free tier) |

## Known Issues
1. **MoE Routing**: Can have routing instability.
2. **Daily Quota**: OpenRouter free tier resets at 00:00 UTC.

## Research Profile
```yaml
reasoning_depth: deep
tool_fidelity: high
failure_signature: hallucination
shadow_focus: verify_facts
guardrails:
  - "Verify claims against source documents"
  - "Use RAG for factual grounding"
  - "Monitor MoE routing stability"
```

## Provider Access
Available via OpenRouter (priority 4). Engine-routable.
