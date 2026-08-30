---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

model_id: meta-llama/llama-3.3-70b-instruct:free
display_name: Llama 3.3 70B Instruct (Free)
version: '2026-05-17'
provider: openrouter
platform: cloud
tier: T3
status: active
context_window: 131072
max_output_tokens: 131072
capabilities:
  reasoning: 0.88
  code_generation: 0.85
  knowledge: 0.9
  creative: 0.82
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
latency_p99_ms: 3500
uptime_percent: 99.0
routing:
  engine_routable: true
  opencode_cli_only: false
  recommended_engine_alternative: null
identity_history: null
community_rating: 4.6/5.0
community_notes:
- 10-30 RPM on OpenRouter free tier
- High reliability
- 128K context window
- Strong generalist
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
  - Verify factual claims against sources
  - Use structured output for tool calls
empirical_evidence:
  test_runs: []
  synergies: []
provider_fabric:
  available_via:
  - provider: openrouter
    priority: 4
  - provider: sambanova
    priority: 3
  local_first_priority: null
tags:
- generalist
- reliable
- free_tier
- openrouter
- sambanova
- llama_3_3
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
  total: 70B
  active: 70B
  architecture: dense
  experts: 0
  active_experts: 0
  shared_experts: 0
  quantization: BF16
  training_tokens: 15T
  source: official
  verified: true
  verified_date: '2026-07-18'
---

# Llama 3.3 70B Instruct (Free) — Model Card

## Overview
Meta's Llama 3.3 70B Instruct. 128K context. High reliability on OpenRouter (10-30 RPM). Also available via SambaNova. Free tier.

## Intended Use
- **Primary**: General reasoning, code generation, knowledge tasks
- **Secondary**: Tool use, structured output
- **Avoid**: Specialized domains, massive context

## Cognitive Mode: Reliable Generalist
Strong across the board. High reliability makes it good for production free-tier workloads.

## Operational Metrics
| Metric | Value |
|--------|-------|
| Context Window | 131,072 |
| Latency (P99) | 3,500ms |
| Uptime | 99.0% |
| Community Rating | 4.6/5.0 |
| Cost | $0.00 (free tier) |
| Rate Limit | 10-30 RPM (OpenRouter) |

## Known Issues
1. **Rate Limited**: 10-30 RPM on OpenRouter free.
2. **Context**: 128K vs 262K+ on newer models.

## Research Profile
```yaml
reasoning_depth: deep
tool_fidelity: high
failure_signature: hallucination
shadow_focus: verify_facts
guardrails:
  - "Verify factual claims against sources"
  - "Use structured output for tool calls"
```

## Provider Access
Available via OpenRouter (priority 4) and SambaNova (priority 3). Engine-routable.
